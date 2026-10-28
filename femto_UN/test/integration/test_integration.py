# SPDX-License-Identifier: Apache-2.0
"""
PRUEBAS DE INTEGRACIÓN  (tt_um_femto completo, RTL f15fccd)

Verifican las INTERFACES entre bloques: CPU <-> decodificador <-> {SPI Flash, SPI RAM, UART}.
Se observan señales internas (mem_address, cs, rstrb, wmask, busy) y los pines SPI.
Perfiles de memoria: standard (chips comerciales) | silicon_aware (ver spimodels.py).
Si la CPU no puede ni leer su primera instrucción, el test falla de inmediato (BootFailure).
"""
import cocotb
from cocotb.triggers import ClockCycles, FallingEdge

from rvlib import *            # noqa: F401,F403
from soc import *              # noqa: F401,F403
from fw import *               # noqa: F401,F403
from spimodels import geti


class BusMonitor:
    """Registra cada acceso de la CPU: (tipo, dirección, cs[6:0], wmask, ciclo)."""

    def __init__(self, dut):
        self.dut, self.events, self.cycle = dut, [], 0

    async def run(self):
        d = self.dut.femto0
        while True:
            await FallingEdge(self.dut.clk)
            self.cycle += 1
            rs, wm = geti(d.mem_rstrb, 0), geti(d.mem_wmask, 0)
            if rs or wm:
                self.events.append(dict(kind="W" if wm else "R", addr=geti(d.mem_address), cs=geti(d.cs),
                                        wmask=wm, wdata=geti(d.mem_wdata), cyc=self.cycle,
                                        state=geti(d.CPU.state)))


def data_accesses(mon):
    """Accesos que no son búsqueda de instrucción (state != FETCH)."""
    return [e for e in mon.events if e["state"] != 1]


@cocotb.test()
async def test_i01_first_fetch_comes_from_flash_at_reset_address(dut):
    """Tras reset la CPU pide la dirección 0 y el decodificador selecciona la flash (cs[0])."""
    p = new_prog(); p.emit(I("addi", 5, 0, 7)); h = halt_loop(p)
    mon = BusMonitor(dut); cocotb.start_soon(mon.run())
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 20000)
    f = mon.events[0]
    assert f["addr"] == 0 and f["cs"] == 0b0000001, f"primer acceso: addr=0x{f['addr']:x} cs={f['cs']:07b}"
    assert soc.flash.transactions[0]["cmd"] == 0x03
    assert soc.reg(5) == 7


@cocotb.test()
async def test_i00_first_instruction_after_reset_is_executed(dut):
    """La instrucción de la dirección 0 debe ejecutarse (RV32: PC de reset = RESET_ADDR)."""
    p = Prog(); p.emit(I("addi", 5, 0, 11), I("addi", 6, 0, 22)); h = halt_loop(p)
    soc = await boot(dut, p, check=False)
    await soc.run_to_halt(h, 60000)
    assert soc.reg(6) == 22
    assert soc.reg(5) == 11, (f"x5=0x{soc.reg(5):x}: la instrucción de la dirección 0 NO se ejecutó "
                              f"(el 1er rstrb llega con la flash aún en START)")


@cocotb.test()
async def test_i02_instruction_stream_integrity(dut):
    """40 instrucciones consecutivas leídas de la flash se ejecutan en orden y producen el resultado esperado."""
    p = new_prog()
    for i in range(1, 21):
        p.emit(I("addi", 5, 5 if i > 1 else 0, i)) if i > 1 else p.emit(I("addi", 5, 0, 1))
    for i in range(20):
        p.emit(I("xori", 6, 6 if i else 0, 0x55 + i))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 60000)
    s5 = 1 + sum(range(2, 21))
    x6 = 0
    for i in range(20):
        x6 ^= (0x55 + i)
    assert soc.reg(5) == s5 and soc.reg(6) == x6, f"x5={soc.reg(5)} (esp {s5}) x6=0x{soc.reg(6):x} (esp 0x{x6:x})"
    pcs = [t["addr"] for t in soc.flash.transactions[:len(p.words)]]
    assert pcs == [4 * i for i in range(len(pcs))], "secuencia de direcciones pedidas a la flash incorrecta"


@cocotb.test()
async def test_i03_address_decoder_map(dut):
    """Mapa: 0x0000_xxxx flash | 0x0001_xxxx SPI RAM | 0x0040_xxxx UART | otras -> flash (alias)."""
    p = new_prog()
    p.emit(li(10, 0x00001000), L("lw", 11, 10, 0))          # flash (datos)
    p.emit(li(10, 0x00010000), L("lw", 11, 10, 0))          # SPI RAM
    p.emit(li(10, 0x00400010), L("lw", 11, 10, 0))          # UART estado
    p.emit(li(10, 0x00020000), L("lw", 11, 10, 0))          # no mapeada -> flash
    p.emit(li(10, 0x01400010), L("lw", 11, 10, 0))          # bus de datos de 24 bits: 0x01400010 -> 0x400010 (UART)
    h = halt_loop(p)
    mon = BusMonitor(dut); cocotb.start_soon(mon.run())
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 400000)
    acc = {e["addr"]: e["cs"] for e in data_accesses(mon)}
    acc_all = [hex(e["addr"]) for e in data_accesses(mon)]
    exp = {0x1000: 0b0000001, 0x10000: 0b1000000, 0x400010: 0b0100000, 0x20000: 0b0000001}
    assert acc.get(0x400010) == 0b0100000, "0x01400010 debería alias a la UART (mem_address es de 24 bits)"
    bad = {hex(a): f"{acc.get(a, 0):07b}!={c:07b}" for a, c in exp.items() if acc.get(a) != c}
    assert not bad, f"decodificación incorrecta: {bad}"


@cocotb.test()
async def test_i04_cpu_spiram_word_roundtrip(dut):
    """sw/lw a 0x10000 (SPI RAM) con valores de 31 bits: la RAM externa recibe la palabra y la CPU lee de vuelta los bits [30:0]."""
    vals = [0x00000001, 0x12345678, 0x7FFFFFFF, 0x55555555, 0x2AAAAAAA]
    p = new_prog(); p.emit(li(10, 0x10000))
    for i, v in enumerate(vals):
        p.emit(li(11, v), S("sw", 11, 10, 4 * i))
    for i, v in enumerate(vals):
        p.emit(L("lw", 12 + i, 10, 4 * i))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 600000)
    for i, v in enumerate(vals):
        assert soc.ram.get_word_be(4 * i) == v, f"RAM[{4*i}] = 0x{soc.ram.get_word_be(4*i):08x} != 0x{v:08x}"
        assert soc.reg(12 + i) & 0x7FFFFFFF == v, f"lw #{i}: x{12+i}=0x{soc.reg(12+i):08x} (bits[30:0]) != 0x{v:08x}"


@cocotb.test()
async def test_i05_cpu_spiram_full_32bit_words(dut):
    """sw/lw de palabras de 32 bits con el bit 31 en 1 (p. ej. enteros negativos): deben volver intactas."""
    vals = [0x80000000, 0xFFFFFFFF, 0xDEADBEEF, 0x80000001]
    p = new_prog(); p.emit(li(10, 0x10100))
    for i, v in enumerate(vals):
        p.emit(li(11, v), S("sw", 11, 10, 4 * i))
    for i in range(len(vals)):
        p.emit(L("lw", 12 + i, 10, 4 * i))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 600000)
    bad = [f"x{12+i}=0x{soc.reg(12+i):08x} esp 0x{v:08x}" for i, v in enumerate(vals) if soc.reg(12 + i) != v]
    assert not bad, "bit 31 corrupto en lecturas de SPI RAM: " + "; ".join(bad)


@cocotb.test()
async def test_i06_cpu_spiram_byte_halfword_access(dut):
    """sb/sh y lb/lbu/lh/lhu sobre SPI RAM deben respetar el carril de byte (wmask) y el desplazamiento."""
    p = new_prog(); p.emit(li(10, 0x10200), li(11, 0x11223344), S("sw", 11, 10, 0))
    p.emit(li(12, 0xAA), S("sb", 12, 10, 1))                  # debe cambiar sólo el byte 1
    p.emit(L("lw", 13, 10, 0))                                # esperado 0x1122AA44... (31 bits: 0x11 bit31=0 ok)
    p.emit(L("lbu", 14, 10, 2), L("lhu", 15, 10, 2))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 900000)
    # RAM guarda palabras big-endian (MSB primero) y la CPU es little-endian: sb en +1 modifica el byte de bits [15:8]
    exp_w = 0x1122AA44
    got = soc.reg(13)
    assert got == exp_w, (f"tras sb @+1: lw=0x{got:08x} esperado 0x{exp_w:08x}; "
                         f"lbu@+2=0x{soc.reg(14):02x} (esp 0x22) lhu@+2=0x{soc.reg(15):04x} (esp 0x1122)")


@cocotb.test()
async def test_i07_busy_handshake_stalls_cpu(dut):
    """La CPU debe quedar detenida mientras rbusy: un acceso a SPI RAM tarda >600 ciclos y el UART casi nada."""
    p = new_prog(); p.emit(li(10, 0x10000), li(11, 5))
    p.emit(S("sw", 11, 10, 0))                                # escritura SPI RAM
    p.emit(li(12, UART_BASE), S("sw", 0, 12, 0x10))          # escritura UART (sin espera)
    h = halt_loop(p)
    mon = BusMonitor(dut); cocotb.start_soon(mon.run())
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 300000)
    w = [e for e in mon.events if e["kind"] == "W"]
    assert len(w) >= 2
    ram_w, uart_w = w[0], w[1]
    dt = uart_w["cyc"] - ram_w["cyc"]
    dut._log.info(f"ciclos entre sw->RAM y sw->UART = {dt} (incluye fetch de 2 instrucciones)")
    assert dt > 600, "la CPU no esperó a wbusy de la SPI RAM"
    assert ram_w["cs"] == 0b1000000 and uart_w["cs"] == 0b0100000


@cocotb.test()
async def test_i08_uart_write_path(dut):
    """sw a UART_DATA + UART_CTRL(tx_wr) produce el byte en el pin TXD."""
    p = new_prog(); prologue(p, full_init=False)
    p.emit(I("addi", 5, 0, ord("Z")), S("sw", 5, 28, 0x08), I("addi", 6, 0, 8), S("sw", 6, 28, 0x10), S("sw", 0, 28, 0x10))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 60000)
    await soc.run_cycles(3000)
    assert soc.uart.text() == "Z", f"UART recibió {soc.uart.text()!r}"


@cocotb.test()
async def test_i09_uart_status_read_path(dut):
    """lw del registro de estado devuelve tx_busy (bit 9) mientras transmite y 0 después."""
    p = new_prog(); prologue(p, full_init=False)
    p.emit(I("addi", 5, 0, 0x55), S("sw", 5, 28, 0x08), I("addi", 6, 0, 8), S("sw", 6, 28, 0x10), S("sw", 0, 28, 0x10))
    p.emit(L("lw", 7, 28, 0x10))                               # justo después: ocupado
    wait = p.pc
    p.emit(L("lw", 8, 28, 0x10))
    p.emit(B("bne", 8, 0, wait - p.pc))
    p.emit(L("lw", 9, 28, 0x10))                               # libre
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 100000)
    assert soc.reg(7) & 0x200, f"tx_busy no visto: 0x{soc.reg(7):x}"
    assert soc.reg(9) == 0, f"estado tras TX = 0x{soc.reg(9):x}"


@cocotb.test()
async def test_i10_no_crosstalk_between_flash_and_ram(dut):
    """Mientras la CPU accede a la SPI RAM, la flash no tiene CS activo (y viceversa)."""
    p = new_prog(); p.emit(li(10, 0x10000), li(11, 9), S("sw", 11, 10, 0), L("lw", 12, 10, 0))
    h = halt_loop(p)
    soc = await boot(dut, p)
    both = []

    async def watch():
        while True:
            await FallingEdge(dut.clk)
            v = geti(dut.uo_out, 0)
            if not (v >> 2) & 1 and not (v >> 3) & 1:
                both.append(cocotb.utils.get_sim_time("ns"))
    cocotb.start_soon(watch())
    await soc.run_to_halt(h, 600000)
    assert not both, f"CS_N de flash y RAM simultáneamente bajos en {len(both)} muestras"
    assert len(soc.ram.transactions) >= 2


@cocotb.test()
async def test_i11_store_to_flash_space_is_ignored(dut):
    """Una escritura al espacio de la flash no genera tráfico SPI de escritura ni bloquea la CPU."""
    p = new_prog(); p.emit(li(10, 0x2000), li(11, 0x1234), S("sw", 11, 10, 0), I("addi", 5, 0, 77))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 200000)
    assert soc.reg(5) == 77
    assert all(t["cmd"] == 0x03 for t in soc.flash.transactions), "la flash recibió un comando distinto de READ"
    assert not soc.ram.transactions


@cocotb.test()
async def test_i12_unmapped_addresses_alias_to_flash(dut):
    """INFORMATIVO: una lectura fuera del mapa (0x0050_0000) devuelve datos de la flash (alias, bits [21:2])."""
    p = new_prog(); p.emit(li(10, 0x00500000), L("lw", 5, 10, 0), li(10, 0x00100000), L("lw", 6, 10, 0))
    h = halt_loop(p)
    soc = await boot(dut, p)
    # datos distintos en la flash en el offset 0x100000 (el alias de 0x500000 es 0x500000 & 0x3FFFFF = 0x100000)
    soc.flash.mem[0x100000:0x100004] = (0xC0FFEE11).to_bytes(4, "little")
    await soc.run_to_halt(h, 200000)
    assert soc.reg(5) == soc.reg(6) == 0xC0FFEE11, f"x5=0x{soc.reg(5):x} x6=0x{soc.reg(6):x}"
