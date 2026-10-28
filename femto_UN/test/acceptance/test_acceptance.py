# SPDX-License-Identifier: Apache-2.0
"""
PRUEBAS DE ACEPTACIÓN  (chip completo, criterios medibles desde el punto de vista del usuario)

Cada prueba verifica un REQUISITO (REQ-xx) con un criterio de aceptación cuantitativo.
Reloj de placa de referencia: 24 MHz (el que hace exacto el baud 115200 de este silicio, ver REQ-05).

  REQ-01  Arranque: tras liberar reset el chip debe imprimir su banner en <= 50 000 ciclos (2 ms @24 MHz).
  REQ-02  ISA: el autotest de RV32I debe reportar PASS en los 10 grupos de instrucciones.
  REQ-03  Memoria de datos: 32 bits íntegros en la SPI RAM (palabras con cualquier valor).
  REQ-04  Velocidad de CPU: >= 100 kIPS a 24 MHz (ciclos/instrucción <= 240).
  REQ-05  UART TX: 115200 baud ±3 % con el reloj de placa (24 MHz) [y con 27 MHz, el valor del diseño].
  REQ-06  UART RX: recibir bytes de un PC a 115200 baud ±3 %; tramas consecutivas sin error.
  REQ-07  Robustez al encendido: arranca correctamente con 3 estados iniciales aleatorios distintos.
  REQ-08  Memorias comerciales: arranca con una flash y una RAM SPI estándar sin lógica adicional.
"""
import cocotb
from cocotb.triggers import ClockCycles, Edge
from cocotb.utils import get_sim_time

from rvlib import *            # noqa: F401,F403
from soc import *              # noqa: F401,F403
from fw import *               # noqa: F401,F403
from spimodels import geti

F_BOARD = 24_000_000


def banner_prog(text="OK\n"):
    p = new_prog(); prologue(p); uart_puts(p, text); uart_wait_idle(p); halt_loop(p)
    return p


@cocotb.test()
async def test_req01_boot_banner_within_budget(dut):
    """REQ-01: banner 'OK' <= 50 000 ciclos tras el reset."""
    soc = await boot(dut, banner_prog())
    used = await soc.run_until_uart("OK\n", 50_000, step=50)
    assert used is not None, f"sin banner en 50 000 ciclos (UART={soc.uart.text()!r})"
    dut._log.info(f"banner tras {used} ciclos = {1e3 * used / F_BOARD:.2f} ms @ 24 MHz")


@cocotb.test()
async def test_req02_isa_selftest_all_groups_pass(dut):
    """REQ-02: autotest RV32I (37 instrucciones) -> 10/10 grupos P."""
    p, h, extra = build_isa_selftest()
    soc = await boot(dut, p, flash_extra=extra)
    assert await soc.run_until(lambda: soc.uart.text().count("\n") >= 1, 2_500_000) is not None, soc.uart.text()
    res = soc.uart.text().strip()[4:]
    bad = [ISA_GROUPS[i] for i, c in enumerate(res) if c != "P"]
    assert not bad, f"ISA {res}: fallan {', '.join(bad)}"


@cocotb.test()
async def test_req03_spiram_32bit_data_integrity(dut):
    """REQ-03: 8 palabras de 32 bits (con bit 31 a 0 y a 1) escritas y leídas de la SPI RAM sin errores."""
    vals = [0x80000001, 0xFFFFFFFF, 0xDEADBEEF, 0x12345678, 0x80000000, 0x7FFFFFFF, 0xAAAAAAAA, 0x55555555]
    p = new_prog(); prologue(p)
    p.emit(li(10, 0x10000), I("addi", 20, 0, 0))
    for i, v in enumerate(vals):
        p.emit(li(11, v), S("sw", 11, 10, 4 * i))
    for i, v in enumerate(vals):
        p.emit(L("lw", 12, 10, 4 * i), li(13, v), B("beq", 12, 13, 8), I("addi", 20, 20, 1))
    for c in "MEM=":
        put_char(p, c)
    put_hex(p, 20, 2); put_char(p, "\n"); uart_wait_idle(p); halt_loop(p)
    soc = await boot(dut, p)
    used = await soc.run_until(lambda: soc.uart.text().count("\n") >= 1, 3_000_000)
    assert used is not None, soc.uart.text()
    n = int(soc.uart.text().strip().split("=")[1], 16)
    assert n == 0, f"{n}/8 palabras de 32 bits leídas incorrectamente de la SPI RAM"


@cocotb.test()
async def test_req04_cpu_throughput(dut):
    """REQ-04: ciclos por instrucción medidos con RDCYCLE sobre 100 instrucciones ALU <= 240."""
    p = new_prog(); prologue(p)
    p.emit(RDCYCLE(5))
    for _ in range(100):
        p.emit(I("addi", 7, 7, 1))
    p.emit(RDCYCLE(6), R("sub", 8, 6, 5))
    for c in "CY=":
        put_char(p, c)
    put_hex(p, 8, 4); put_char(p, "\n"); uart_wait_idle(p); halt_loop(p)
    soc = await boot(dut, p)
    used = await soc.run_until(lambda: soc.uart.text().count("\n") >= 1, 400_000)
    assert used is not None, soc.uart.text()
    d = int(soc.uart.text().strip().split("=")[1], 16)
    cpi = d / 101
    ips = F_BOARD / cpi
    dut._log.info(f"{cpi:.1f} ciclos/instrucción -> {ips / 1e3:.0f} kIPS @ 24 MHz")
    assert cpi <= 240 and ips >= 100e3, f"{cpi:.1f} ciclos/instr = {ips/1e3:.0f} kIPS"


async def measure_tx_cycles_per_bit(dut, soc):
    """Mide el periodo de bit de TXD (ciclos) transmitiendo 0x55 (todas las transiciones)."""
    edges = []
    async def watch():
        last = 1
        while True:
            await Edge(dut.uo_out)
            v = (geti(dut.uo_out, 0xFF) >> 7) & 1
            if v != last:
                edges.append(get_sim_time("ns")); last = v
    cocotb.start_soon(watch())
    await soc.run_cycles(14000)
    return edges


def uart_u_prog():
    p = new_prog(); prologue(p); I0 = I("addi", 27, 0, 0x55); p.emit(I0); uart_putc(p, 27, 28); uart_wait_idle(p); halt_loop(p)
    return p


@cocotb.test()
async def test_req05a_uart_tx_baud_at_24mhz(dut):
    """REQ-05a: baud TX con reloj de placa 24 MHz dentro de ±3 % de 115200."""
    soc = await boot(dut, uart_u_prog())
    edges = await measure_tx_cycles_per_bit(dut, soc)
    ws = [(b - a) / CLK_NS for a, b in zip(edges, edges[1:])][:8]
    cpb = sum(ws) / len(ws)
    baud = F_BOARD / cpb
    err = 100 * (baud - 115200) / 115200
    dut._log.info(f"cpb={cpb:.1f}  baud={baud:.0f}  error={err:+.2f} %")
    assert abs(err) <= 3.0, f"baud={baud:.0f} ({err:+.2f} %)"


@cocotb.test()
async def test_req05b_uart_tx_baud_at_27mhz(dut):
    """REQ-05b: baud TX con 27 MHz (valor del parámetro clk_freq del diseño) dentro de ±3 % de 115200."""
    soc = await boot(dut, uart_u_prog())
    edges = await measure_tx_cycles_per_bit(dut, soc)
    ws = [(b - a) / CLK_NS for a, b in zip(edges, edges[1:])][:8]
    cpb = sum(ws) / len(ws)
    baud = 27e6 / cpb
    err = 100 * (baud - 115200) / 115200
    dut._log.info(f"cpb={cpb:.1f}  baud={baud:.0f}  error={err:+.2f} %")
    assert abs(err) <= 3.0, f"baud={baud:.0f} ({err:+.2f} %) con reloj 27 MHz"


def echo_prog():
    p = new_prog(); prologue(p)
    top = p.pc
    p.emit(L("lw", 5, 28, 0x10)); p.emit(I("andi", 5, 5, 0x100)); p.emit(B("beq", 5, 0, top - p.pc))
    p.emit(L("lw", 10, 28, 0x08), I("addi", 6, 0, 1), S("sw", 6, 28, 0x10), S("sw", 0, 28, 0x10))
    uart_putc(p, 10, 28)
    p.emit(JAL(0, top - p.pc))
    return p


async def pc_send(soc, data, f_clk, gap_cycles):
    cpb = f_clk / 115200.0
    for byte in data:
        t = 0.0
        for b in [0] + [(byte >> i) & 1 for i in range(8)] + [1]:
            soc.set_ui(2, b)
            n0 = int(round(t)); t += cpb
            await soc.run_cycles(max(1, int(round(t)) - n0))
        await soc.run_cycles(gap_cycles)


@cocotb.test()
async def test_req06a_uart_rx_from_pc_24mhz_spaced(dut):
    """REQ-06a: bytes de un PC a 115200 (reloj 24 MHz), con un carácter de pausa entre ellos."""
    soc = await boot(dut, echo_prog())
    await soc.run_cycles(3000)
    await pc_send(soc, b"RV32", F_BOARD, 12000)
    assert soc.uart.text() == "RV32", f"eco={soc.uart.text()!r}"


@cocotb.test()
async def test_req06b_uart_rx_back_to_back(dut):
    """REQ-06b: dos bytes consecutivos sin pausa (como un envío de archivo) se reciben ambos."""
    soc = await boot(dut, echo_prog())
    await soc.run_cycles(3000)
    await pc_send(soc, b"AB", F_BOARD, 0)
    await soc.run_cycles(20000)
    assert soc.uart.text() == "AB", f"eco={soc.uart.text()!r}"


@cocotb.test()
async def test_req06c_uart_rx_from_pc_27mhz(dut):
    """REQ-06c: con reloj de 27 MHz (diseño nominal) el PC a 115200 exactos debe poder comunicarse."""
    soc = await boot(dut, echo_prog())
    await soc.run_cycles(3000)
    await pc_send(soc, b"RV32", 27_000_000, 12000)
    assert soc.uart.text() == "RV32", f"eco={soc.uart.text()!r}"


@cocotb.test()
async def test_req07_power_up_robustness(dut):
    """REQ-07: 3 estados iniciales aleatorios (registros y contador) -> siempre el mismo banner."""
    for seed in (101, 202, 303):
        soc = await boot(dut, banner_prog("OK\n"), seed=seed)
        used = await soc.run_until_uart("OK\n", 60_000, step=100)
        assert used is not None, f"seed={seed}: UART={soc.uart.text()!r}"


@cocotb.test()
async def test_req08_commercial_spi_memories(dut):
    """REQ-08: con el perfil de memoria 'standard' (flash W25Q + RAM 23LC reales) el chip debe arrancar.
    Se prueba SIEMPRE con memorias estándar, independientemente de MEM_PROFILE."""
    soc = await boot(dut, banner_prog("OK\n"), profile="standard")
    used = await soc.run_until_uart("OK\n", 60_000, step=100)
    assert used is not None, f"UART={soc.uart.text()!r}"
