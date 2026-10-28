# SPDX-License-Identifier: Apache-2.0
"""
PRUEBAS UNITARIAS de src/perip_uart.v + src/uart.v  (RTL del silicio f15fccd)

Se instancia como en femto.v:  clk_freq = 27 MHz, baud = 115200  (-P en COMPILE_ARGS).
Mapa de registros (addr = mem_address[4:0]):
  0x08  escritura: dato TX    | lectura: dato RX
  0x10  escritura: control    bit0 rx_ack, bit2 LED, bit3 tx_wr (nivel, no pulso)
        lectura : estado      bit9 tx_busy, bit8 rx_avail, bit7 rx_error
"""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

from spimodels import geti

CLK_FREQ, BAUD = 24_000_000, 115200
IDEAL_CPB = CLK_FREQ / BAUD                 # 234.375 ciclos/bit esperados por la especificación
DATA, CTRL = 0x08, 0x10


async def setup(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    dut.rst.value = 1
    dut.cs.value = 0
    dut.wr.value = 0
    dut.addr.value = 0
    dut.d_in.value = 0
    dut.uart_rx.value = 1
    await ClockCycles(dut.clk, 5)
    await FallingEdge(dut.clk)
    dut.rst.value = 0
    await ClockCycles(dut.clk, 3)


async def bus_write(dut, addr, val):
    await RisingEdge(dut.clk)
    dut.cs.value = 1
    dut.addr.value = addr
    dut.d_in.value = val
    dut.wr.value = 1
    await RisingEdge(dut.clk)
    dut.cs.value = 0
    dut.wr.value = 0


async def bus_read(dut, addr):
    await RisingEdge(dut.clk)
    dut.cs.value = 1
    dut.addr.value = addr
    dut.wr.value = 0
    await FallingEdge(dut.clk)
    v = geti(dut.d_out)
    await RisingEdge(dut.clk)
    dut.cs.value = 0
    return v


async def send_byte(dut, val):
    await bus_write(dut, DATA, val)
    await bus_write(dut, CTRL, 0x08)
    await bus_write(dut, CTRL, 0x00)


async def capture_frame(dut, timeout=6000):
    """Devuelve (byte, cycles_per_bit_medido, bits) midiendo flancos de uart_tx."""
    n = 0
    while geti(dut.uart_tx) == 1:
        await RisingEdge(dut.clk)
        n += 1
        assert n < timeout, "no apareció bit de inicio"
    t0 = 0
    edges = []
    prev, c = 0, 0
    levels = []
    for _ in range(12 * 260):
        await RisingEdge(dut.clk)
        c += 1
        v = geti(dut.uart_tx)
        if v != prev:
            edges.append(c)
            prev = v
        levels.append(v)
    return edges, levels


def decode(levels, cpb):
    """Muestrea en el centro de cada bit a partir del bit de inicio (índice 0 = tras el flanco)."""
    bits = []
    for i in range(10):
        idx = int(cpb * (i + 0.5)) - 1
        bits.append(levels[idx] if idx < len(levels) else 1)
    return bits


@cocotb.test()
async def test_reset_state(dut):
    """Tras reset: uart_tx=1 (reposo), estado=0, LED=0."""
    await setup(dut)
    assert geti(dut.uart_tx) == 1
    assert await bus_read(dut, CTRL) == 0
    assert geti(dut.ledout) == 0


@cocotb.test()
async def test_register_map_and_led(dut):
    """El bit 2 del registro de control enciende el LED; lecturas de otros offsets devuelven 0."""
    await setup(dut)
    await bus_write(dut, CTRL, 0x04)
    await ClockCycles(dut.clk, 4)
    assert geti(dut.ledout) == 1, "LED no encendió"
    await bus_write(dut, CTRL, 0x00)
    await ClockCycles(dut.clk, 4)
    assert geti(dut.ledout) == 0, "LED no apagó"
    assert await bus_read(dut, 0x00) == 0 and await bus_read(dut, 0x18) == 0


@cocotb.test()
async def test_tx_frame_format(dut):
    """Trama 8N1: bit de inicio 0, 8 bits LSB primero, bit de parada 1, para varios bytes."""
    await setup(dut)
    for val in (0x55, 0xA3, 0x00, 0xFF, 0x41):
        await send_byte(dut, val)
        edges, levels = await capture_frame(dut)
        # el primer elemento de `levels` es 1 ciclo después del flanco de bajada de inicio
        cpb = round(sum(b - a for a, b in zip(edges, edges[1:])) / max(1, len(edges) - 1)) if len(edges) > 2 else 208
        bits = decode([0] + levels, 208)
        got = sum(b << i for i, b in enumerate(bits[1:9]))
        assert bits[0] == 0 and bits[9] == 1, f"inicio/parada incorrectos para 0x{val:02x}: {bits}"
        assert got == val, f"TX 0x{val:02x} -> 0x{got:02x}"
        await ClockCycles(dut.clk, 400)


@cocotb.test()
async def test_tx_baud_rate_vs_spec(dut):
    """Velocidad de TX: ciclos/bit debe ser clk_freq/baud = 234.4 (±3 %). Se mide en el RTL."""
    await setup(dut)
    await send_byte(dut, 0x55)
    edges, levels = await capture_frame(dut)
    widths = [b - a for a, b in zip(edges, edges[1:])]
    cpb = sum(widths) / len(widths)
    err = 100 * (IDEAL_CPB - cpb) / IDEAL_CPB
    f_ok = cpb * BAUD
    dut._log.info(f"ciclos/bit medidos = {cpb:.1f}  (ideal {IDEAL_CPB:.1f})  error de baud = {-err:+.1f} %  "
                  f"-> baud exacto sólo con clk = {f_ok/1e6:.3f} MHz")
    assert abs(err) <= 3.0, (f"ciclos/bit = {cpb:.1f} vs {IDEAL_CPB:.1f} ideal: baud real a 27 MHz = "
                              f"{CLK_FREQ / cpb:.0f} ({-err:+.1f} %). Correcto sólo a {f_ok / 1e6:.2f} MHz")


@cocotb.test()
async def test_tx_busy_and_ignored_write(dut):
    """tx_busy (bit 9) sube al transmitir y baja al terminar; una escritura mientras está ocupado no la interrumpe."""
    await setup(dut)
    await send_byte(dut, 0x31)
    await ClockCycles(dut.clk, 5)
    assert (await bus_read(dut, CTRL)) & 0x200, "tx_busy debería estar activo"
    await bus_write(dut, DATA, 0x32)
    await bus_write(dut, CTRL, 0x08)
    await bus_write(dut, CTRL, 0x00)
    edges, levels = await capture_frame(dut)          # la 1ª trama aún en curso o la siguiente
    await ClockCycles(dut.clk, 3000)
    assert not (await bus_read(dut, CTRL)) & 0x200, "tx_busy no bajó"


async def send_rx_frame(dut, val, cpb, stop=1):
    bits = [0] + [(val >> i) & 1 for i in range(8)] + [stop]
    for b in bits:
        dut.uart_rx.value = b
        await ClockCycles(dut.clk, int(round(cpb)))
    dut.uart_rx.value = 1


@cocotb.test()
async def test_rx_at_own_timebase(dut):
    """Recepción con el periodo de bit del propio RTL (208 ciclos): rx_avail, dato y rx_ack."""
    await setup(dut)
    await send_rx_frame(dut, 0xA7, 208)
    await ClockCycles(dut.clk, 400)
    st = await bus_read(dut, CTRL)
    assert st & 0x100, f"rx_avail no se activó (estado=0x{st:03x})"
    assert (await bus_read(dut, DATA)) == 0xA7
    await bus_write(dut, CTRL, 0x01)
    await bus_write(dut, CTRL, 0x00)
    await ClockCycles(dut.clk, 4)
    assert not (await bus_read(dut, CTRL)) & 0x100, "rx_ack no limpió rx_avail"


@cocotb.test()
async def test_rx_from_ideal_115200_sender(dut):
    """Un PC/adaptador a 115200 exactos con clk=27 MHz envía bits de 234.4 ciclos. Debe recibirse bien."""
    await setup(dut)
    ok = 0
    vals = (0x55, 0xA7, 0x3C, 0xFF, 0x00)
    for v in vals:
        bits = [0] + [(v >> i) & 1 for i in range(8)] + [1]
        t = 0.0
        for b in bits:
            dut.uart_rx.value = b
            t += IDEAL_CPB
            await ClockCycles(dut.clk, 1)
            # espera hasta completar t ciclos acumulados (evita error de redondeo acumulado)
            target = int(round(t))
            await ClockCycles(dut.clk, max(0, target - int(round(t - IDEAL_CPB)) - 1))
        dut.uart_rx.value = 1
        await ClockCycles(dut.clk, 400)
        st = await bus_read(dut, CTRL)
        if (st & 0x100) and not (st & 0x80) and (await bus_read(dut, DATA)) == v:
            ok += 1
        await bus_write(dut, CTRL, 0x01)
        await bus_write(dut, CTRL, 0x00)
        await ClockCycles(dut.clk, 300)
    assert ok == len(vals), f"sólo {ok}/{len(vals)} bytes recibidos correctamente a 115200 nominal (clk=27 MHz)"


@cocotb.test()
async def test_rx_framing_error(dut):
    """Bit de parada = 0 => rx_error (bit 7) y no se marca rx_avail."""
    await setup(dut)
    await send_rx_frame(dut, 0x5A, 208, stop=0)
    await ClockCycles(dut.clk, 400)
    st = await bus_read(dut, CTRL)
    assert st & 0x80, f"rx_error no se activó (estado=0x{st:03x})"
    assert not st & 0x100


@cocotb.test()
async def test_rx_back_to_back_frames(dut):
    """Dos bytes consecutivos con 1 bit de parada (lo que envía un PC/USB-UART): ambos deben recibirse.
    Se usa el periodo de bit propio del RTL (208) para aislar el defecto de la deriva de baud."""
    await setup(dut)
    got = []
    async def reader():
        for _ in range(4000):
            await ClockCycles(dut.clk, 1)
            st = geti(dut.d_out) if False else None
    await send_rx_frame(dut, 0x11, 208)
    await ClockCycles(dut.clk, 1)
    await send_rx_frame(dut, 0x22, 208)           # sin hueco: inicio inmediatamente tras la parada
    await ClockCycles(dut.clk, 500)
    st = await bus_read(dut, CTRL)
    d = await bus_read(dut, DATA)
    dut._log.info(f"estado=0x{st:03x} dato=0x{d:02x}")
    assert not (st & 0x80), "rx_error: se marcó error de trama en tramas consecutivas válidas"
    assert d == 0x22, f"se esperaba 0x22 (segundo byte), llegó 0x{d:02x}"
