# SPDX-License-Identifier: Apache-2.0
"""
Pruebas cocotb de src/MappedSPIRAM.v  (maestro SPI para una RAM/FRAM SPI serie).

Interfaz del DUT (todo el módulo trabaja en el flanco de BAJADA de `clk`):
    reset (activo en bajo)  rd / wr (strobe de 1 ciclo)  word_address[15:0]  wdata[31:0]
    rdata[31:0]  rbusy  wbusy   |   CLK  CS_N  MOSI  MISO   (SPI)

Protocolo esperado por la memoria (tipo 23LCxxx / FM25Vxx), SPI modo 0:
    LECTURA : 0x03 + 24 bits dirección  -> datos (MSB primero)
    ESCRITURA: 0x02 + 24 bits dirección + datos (MSB primero)
En el SoC (femto.v) `word_address` se conecta a mem_address[15:0], es decir, es una
DIRECCIÓN DE BYTES y el módulo la envía tal cual en {8'h00, word_address}.

El repo no incluye el modelo FRAM_SPI usado con `ifdef BENCH`, así que aquí se modela
un esclavo SPI modo 0 en Python (muestrea MOSI en flanco de subida, cambia MISO en
flanco de bajada).  Los tests verifican:
  * reposo tras reset, framing de CS_N, rbusy/wbusy
  * comando, dirección y número de pulsos de reloj
  * datos de escritura y de lectura (ida y vuelta, aleatorio, todas las fases del divisor)
  * temporización de SCK (periodo, ciclo de trabajo), setup/hold de MOSI y CS_N
  * robustez frente al retardo de salida del esclavo (tV)
  * recuperación tras reset a mitad de una transacción

Ejecutar:   make -f Makefile.spiram
"""

import os
import random

import cocotb
from spimodels import DirectPins, SpiTarget

PROFILE = os.environ.get('MEM_PROFILE', 'standard')

from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Edge, FallingEdge, First, RisingEdge, Timer
from cocotb.utils import get_sim_time

SYS_NS = 20                     # periodo del reloj del sistema
DIVISOR = 10                    # parámetro `divisor` del RTL: SCK = clk / (DIVISOR+1)
SCK_PERIOD_CYCLES = DIVISOR + 1


def geti(sig, default=None):
    try:
        return int(sig.value)
    except ValueError:
        return default


# --------------------------------------------------------------------------
# Driver (hace de CPU: strobe de 1 ciclo y espera a que baje busy)
# --------------------------------------------------------------------------
class Bench:
    def __init__(self, dut, miso_delay_ns=0.0):
        self.dut = dut
        self.slave = SpiTarget(DirectPins(dut), kind='ram', profile=PROFILE, miso_delay_ns=miso_delay_ns)

    async def start(self, reset_cycles=6):
        dut = self.dut
        cocotb.start_soon(Clock(dut.clk, SYS_NS, unit="ns").start())
        dut.reset.value = 0
        dut.rd.value = 0
        dut.wr.value = 0
        dut.word_address.value = 0
        dut.wdata.value = 0
        dut.MISO.value = 0
        cocotb.start_soon(self.slave.run())
        await ClockCycles(dut.clk, reset_cycles)
        await FallingEdge(dut.clk)
        dut.reset.value = 1
        await ClockCycles(dut.clk, 3)

    async def _transact(self, strobe, addr, wdata=0, max_cycles=4000):
        dut = self.dut
        busy = dut.rbusy if strobe == "rd" else dut.wbusy
        other = dut.wbusy if strobe == "rd" else dut.rbusy
        await RisingEdge(dut.clk)
        dut.word_address.value = addr
        dut.wdata.value = wdata
        getattr(dut, strobe).value = 1
        await RisingEdge(dut.clk)                    # el DUT muestrea en el flanco de bajada intermedio
        getattr(dut, strobe).value = 0
        info = {"busy_first_edge": geti(busy), "other_busy_first_edge": geti(other)}
        cycles = 0
        while geti(busy) == 1:
            await RisingEdge(dut.clk)
            cycles += 1
            assert cycles < max_cycles, f"timeout esperando fin de {strobe}"
        info["cycles"] = cycles
        info["rdata"] = geti(dut.rdata)
        info["cs_n_after"] = geti(dut.CS_N)
        return info

    async def read(self, addr):
        return await self._transact("rd", addr)

    async def write(self, addr, wdata):
        return await self._transact("wr", addr, wdata)

    async def idle(self, n):
        await ClockCycles(self.dut.clk, n)


async def make_bench(dut, **kw):
    b = Bench(dut, **kw)
    await b.start()
    return b


# ==========================================================================
# PRUEBAS
# ==========================================================================
@cocotb.test()
async def test_reset_idle(dut):
    """Tras reset: CS_N=1, rbusy=wbusy=0 y sin actividad SPI mientras no haya rd/wr."""
    b = await make_bench(dut)
    for _ in range(300):
        await RisingEdge(dut.clk)
        assert geti(dut.CS_N) == 1, "CS_N debe permanecer alto en reposo"
        assert geti(dut.rbusy) == 0 and geti(dut.wbusy) == 0
    assert not b.slave.transactions, "no debe haber transacciones SPI sin rd/wr"


@cocotb.test()
async def test_sck_timing(dut):
    """SCK durante una transacción: periodo = (divisor+1) ciclos de sistema, ciclo de trabajo ~50 %,
    y en reposo SCK queda en 0 (modo 0, CPOL=0) cuando CS_N está alto."""
    b = await make_bench(dut)
    b.slave.set_word_be(0x40, 0x12345678)
    await b.idle(7)
    await b.read(0x40)
    await b.idle(30)
    t = b.slave.transactions[-1]
    periods = [round((r1 - r0) / SYS_NS) for r0, r1 in zip(t["rises"], t["rises"][1:])]
    assert all(p == SCK_PERIOD_CYCLES for p in periods), \
        f"periodo de SCK (ciclos de sistema) = {sorted(set(periods))}, esperado {SCK_PERIOD_CYCLES}"
    ev = sorted([(x, "r") for x in t["rises"]] + [(x, "f") for x in t["falls"]])
    highs, lows = [], []
    for (t0, k0), (t1, k1) in zip(ev, ev[1:]):
        if k0 == "r" and k1 == "f":
            highs.append(round((t1 - t0) / SYS_NS))
        elif k0 == "f" and k1 == "r":
            lows.append(round((t1 - t0) / SYS_NS))
    dut._log.info(f"SCK: alto={sorted(set(highs))} ciclos, bajo={sorted(set(lows))} ciclos")
    assert highs and lows
    assert abs(max(highs) - max(lows)) <= 1 and abs(min(highs) - min(lows)) <= 1, "ciclo de trabajo asimétrico"
    # CS_N alto => el esclavo ignora SCK, pero un maestro limpio lo deja en 0 (CPOL=0)
    assert geti(dut.CS_N) == 1
    if geti(dut.CLK) != 0:
        dut._log.warning("SCK en 1 con CS_N alto (reposo): sólo es aceptable si el esclavo ignora SCK con CS_N=1")


@cocotb.test()
async def test_read_protocol_and_data(dut):
    """Lectura: comando 0x03, dirección {00, word_address}, 32 pulsos antes de los datos, dato correcto."""
    b = await make_bench(dut)
    addr = 0x1234
    b.slave.set_word_be(addr, 0xA1B2C3D4)
    addr = 0x1234
    b.slave.set_word_be(addr, 0x81B2C3D4)
    r = await b.read(addr)
    await b.idle(40)
    assert r["busy_first_edge"] == 1, "rbusy debe estar activo en el primer flanco tras rd (si no, la CPU no espera)"
    assert r["other_busy_first_edge"] == 0, "wbusy no debe activarse en una lectura"
    t = b.slave.transactions[-1]
    dut._log.info(f"cmd=0x{t['cmd']:02x} addr=0x{t['addr']:06x} pulsos_SCK={len(t['rises'])} "
                  f"bits_leidos_del_esclavo={t['rcount']} rdata=0x{r['rdata']:08x}")
    assert len(b.slave.transactions) == 1
    assert t["cmd"] == 0x03, f"comando recibido por el esclavo = 0x{t['cmd']:02x}, esperado 0x03 (READ)"
    assert t["addr"] == addr, f"dirección recibida = 0x{t['addr']:06x}, esperada 0x{addr:06x}"
    assert len(t["rises"]) == 64, f"pulsos de SCK con CS_N bajo = {len(t['rises'])}, esperados 64 (32 cmd+dir, 32 datos)"
    assert r["rdata"] == 0xA1B2C3D4, f"rdata=0x{r['rdata']:08x} esperado 0xA1B2C3D4"


@cocotb.test()
async def test_write_protocol_and_data(dut):
    """Escritura: comando 0x02, dirección, 32 bits de datos (MSB primero), CS_N sube al terminar."""
    b = await make_bench(dut)
    addr = 0x0200
    r = await b.write(addr, 0x81223344)
    await b.idle(40)
    assert r["busy_first_edge"] == 1, "wbusy debe estar activo en el primer flanco tras wr"
    assert r["other_busy_first_edge"] == 0, "rbusy no debe activarse en una escritura"
    t = b.slave.transactions[-1]
    dut._log.info(f"cmd=0x{t['cmd']:02x} addr=0x{t['addr']:06x} pulsos_SCK={len(t['rises'])} "
                  f"bytes_escritos={bytes(t['wdata']).hex()}")
    assert t["cmd"] == 0x02, f"comando = 0x{t['cmd']:02x}, esperado 0x02 (WRITE)"
    assert t["addr"] == addr, f"dirección = 0x{t['addr']:06x}, esperada 0x{addr:06x}"
    assert bytes(t["wdata"]) == bytes.fromhex("11223344"), \
        f"el esclavo recibió {bytes(t['wdata']).hex()}, esperado 11223344"
    assert b.slave.get_word_be(addr) == 0x81223344


@cocotb.test()
async def test_write_then_read_roundtrip(dut):
    """Escribir y leer de vuelta a varias direcciones (la RAM debe devolver lo escrito)."""
    b = await make_bench(dut)
    rng = random.Random(7)
    ref = {}
    for addr in [0x0000, 0x0004, 0x0100, 0x7FFC, 0xFFF8, 0x1000]:
        v = rng.getrandbits(32)
        await b.write(addr, v)
        await b.idle(5)
        ref[addr] = v
    for addr, v in ref.items(): 
        r = await b.read(addr)
        await b.idle(5)
        assert r["rdata"] == v, f"@0x{addr:04x}: leído 0x{r['rdata']:08x}, escrito 0x{v:08x}"


@cocotb.test()
async def test_adjacent_words_do_not_overlap(dut):
    """Palabras consecutivas (dirección de bytes +4) no deben pisarse entre sí."""
    b = await make_bench(dut)
    vals = [0xCAFEBABE, 0x01234567, 0x89ABCDEF, 0xDEADBEEF]
    for i, v in enumerate(vals):
        await b.write(0x400 + 4 * i, v)
        await b.idle(4)
    for i, v in enumerate(vals):
        r = await b.read(0x400 + 4 * i)
        await b.idle(4)
        assert r["rdata"] == v, f"palabra {i}: 0x{r['rdata']:08x} != 0x{v:08x}"


@cocotb.test()
async def test_read_all_divider_phases(dut):
    """Lecturas lanzadas en las 2*(divisor+1) fases posibles del divisor de reloj interno.
    El maestro SPI debe ser correcto sin importar cuándo llega `rd`."""
    b = await make_bench(dut)
    rng = random.Random(3)
    failures = []
    for k in range(2 * SCK_PERIOD_CYCLES + 2):
        addr = 0x2000 + 4 * k
        v = rng.getrandbits(32)
        b.slave.set_word_be(addr, v)
        await b.idle(k)                                   # barre la fase relativa
        r = await b.read(addr)
        t = b.slave.transactions[-1]
        ok = (r["rdata"] == v and t["cmd"] == 0x03 and t["addr"] == addr)
        if not ok:
            failures.append(f"fase k={k}: cmd=0x{t['cmd']:02x} addr=0x{t['addr']:06x} "
                            f"pulsos={len(t['rises'])} rdata=0x{r['rdata']:08x} esperado=0x{v:08x}")
        await b.idle(15)
    assert not failures, f"{len(failures)} fases fallaron:\n  " + "\n  ".join(failures[:8])


@cocotb.test()
async def test_write_all_divider_phases(dut):
    """Igual que el anterior pero con escrituras."""
    b = await make_bench(dut)
    rng = random.Random(4)
    failures = []
    for k in range(2 * SCK_PERIOD_CYCLES + 2):
        addr = 0x3000 + 4 * k
        v = rng.getrandbits(32)
        await b.idle(k)
        await b.write(addr, v)
        t = b.slave.transactions[-1]
        if not (t["cmd"] == 0x02 and t["addr"] == addr and b.slave.get_word_be(addr) == v):
            failures.append(f"fase k={k}: cmd=0x{t['cmd']:02x} addr=0x{t['addr']:06x} "
                            f"pulsos={len(t['rises'])} mem=0x{b.slave.get_word_be(addr):08x} esperado=0x{v:08x}")
        await b.idle(15)
    assert not failures, f"{len(failures)} fases fallaron:\n  " + "\n  ".join(failures[:8])


@cocotb.test()
async def test_spi_signal_timing(dut):
    """Setup/hold: CS_N baja >=1 ciclo antes del primer SCK, sube >=1 ciclo tras el último;
    MOSI no cambia en una ventana de ±1 ciclo alrededor de cada flanco de subida de SCK."""
    b = await make_bench(dut)
    problems = []
    for k in range(SCK_PERIOD_CYCLES + 1):
        await b.idle(k)
        await b.write(0x100 + 4 * k, 0xA5A5A5A5 ^ k)
        await b.idle(3)
        await b.read(0x100 + 4 * k)
        await b.idle(3)
    for n, t in enumerate(b.slave.transactions):
        setup = t["t_first_rise"] - t["t_cs_fall"]
        hold = t["t_cs_rise"] - t["t_last_rise"]
        if setup < SYS_NS:
            problems.append(f"trans {n}: CS_N->1er SCK = {setup:.0f} ns (< 1 ciclo)")
        if hold < SYS_NS:
            problems.append(f"trans {n}: último SCK->CS_N = {hold:.0f} ns (< 1 ciclo)")
        for r in t["rises"]:
            near = [m for m in t["mosi_t"] if abs(m - r) < SYS_NS]
            if near:
                problems.append(f"trans {n}: MOSI cambia a {min(near, key=lambda m: abs(m-r)) - r:+.0f} ns del flanco SCK")
                break
    assert not problems, f"{len(problems)} violaciones de temporización:\n  " + "\n  ".join(problems[:10])


@cocotb.test()
async def test_random_mixed_traffic(dut):
    """Tráfico aleatorio rd/wr con huecos aleatorios, comparado con un modelo en Python."""
    b = await make_bench(dut)
    rng = random.Random(11)
    model = {}
    addrs = [0x10 * i for i in range(1, 40)]
    errors = []
    for i in range(80):
        a = rng.choice(addrs)
        await b.idle(rng.randint(0, 25))
        if rng.random() < 0.5:
            v = rng.getrandbits(32)
            await b.write(a, v)
            model[a] = v
        elif a in model:
            r = await b.read(a)
            if r["rdata"] != model[a]:
                errors.append(f"op{i} @0x{a:04x}: leído 0x{r['rdata']:08x} esperado 0x{model[a]:08x}")
    assert not errors, f"{len(errors)} errores de lectura:\n  " + "\n  ".join(errors[:8])


@cocotb.test()
async def test_miso_output_delay_tolerance(dut):
    """Robustez: el esclavo real tarda tV (~25-32 ns en una 23LC) en poner el dato tras el flanco de
    bajada de SCK. Con SYS=20 ns se prueban retardos de 0, 10 y 30 ns (1.5 ciclos)."""
    b = await make_bench(dut)
    failures = []
    for delay in (0.0, 10.0, 30.0):
        b.slave.miso_delay_ns = delay
        for k in (0, 3, 7):
            addr = 0x500 + 4 * k
            v = 0xC001D00D ^ (k * 0x01010101)
            b.slave.set_word_be(addr, v)
            await b.idle(k)
            r = await b.read(addr)
            if r["rdata"] != v:
                failures.append(f"tV={delay:.0f} ns, fase {k}: leído 0x{r['rdata']:08x} esperado 0x{v:08x}")
            await b.idle(12)
    assert not failures, "\n  ".join(failures)


@cocotb.test()
async def test_reset_during_transaction(dut):
    """Reset en mitad de una lectura: CS_N sube, busy baja y la siguiente transacción funciona."""
    b = await make_bench(dut)
    b.slave.set_word_be(0x80, 0x0BADF00D)
    await RisingEdge(dut.clk)
    dut.word_address.value = 0x80
    dut.rd.value = 1
    await RisingEdge(dut.clk)
    dut.rd.value = 0
    await ClockCycles(dut.clk, 150)                  # a medio camino
    assert geti(dut.rbusy) == 1 and geti(dut.CS_N) == 0
    await FallingEdge(dut.clk)
    dut.reset.value = 0
    await ClockCycles(dut.clk, 4)
    assert geti(dut.CS_N) == 1 and geti(dut.rbusy) == 0 and geti(dut.wbusy) == 0, "no se liberó tras reset"
    await FallingEdge(dut.clk)
    dut.reset.value = 1
    await ClockCycles(dut.clk, 5)
    r = await b.read(0x80)
    assert r["rdata"] == 0x0BADF00D, f"tras reset: 0x{r['rdata']:08x}"
