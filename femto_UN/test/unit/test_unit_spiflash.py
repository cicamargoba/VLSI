# SPDX-License-Identifier: Apache-2.0
"""
PRUEBAS UNITARIAS de src/MappedSPIFlash.v   (RTL del silicio, commit f15fccd)

Interfaz: clk, reset(activo en bajo), rstrb, word_address[19:0], rdata[31:0], rbusy,
          CLK, CS_N, MOSI, MISO.   Parámetro divisor = 2  =>  SCK = clk/3.

Especificación bajo prueba (flash NOR estándar, p. ej. W25Qxx, SPI modo 0, comando 0x03):
    0x03 + dirección de 24 bits ({2'b00, word_address, 2'b00}) -> datos MSB primero
    La flash guarda las palabras en little-endian; rdata debe ser la palabra LE (swizzle).

El esclavo SPI es el modelo `standard` de spimodels.py (conforme al datasheet de una flash).
Un FAIL en este archivo es un DEFECTO del controlador (ver defects.py), no del banco de pruebas.
"""
import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge
from cocotb.utils import get_sim_time

from spimodels import DirectPins, SpiTarget, geti

PROFILE = os.environ.get("MEM_PROFILE", "standard")
SYS_NS = 20
DIVISOR = 2
SCK_PERIOD = DIVISOR + 1


class FlashBench:
    def __init__(self, dut, miso_delay_ns=0.0):
        self.dut = dut
        self.slave = SpiTarget(DirectPins(dut), kind="flash", profile=PROFILE,
                               miso_delay_ns=miso_delay_ns, size=1 << 22)

    async def start(self):
        d = self.dut
        cocotb.start_soon(Clock(d.clk, SYS_NS, unit="ns").start())
        d.reset.value = 0
        d.rstrb.value = 0
        d.word_address.value = 0
        d.MISO.value = 0
        cocotb.start_soon(self.slave.run())
        await ClockCycles(d.clk, 6)
        await FallingEdge(d.clk)
        d.reset.value = 1
        await ClockCycles(d.clk, 3)

    async def idle(self, n):
        await ClockCycles(self.dut.clk, n)

    def put_word(self, word_addr, value):
        self.slave.mem[4 * word_addr:4 * word_addr + 4] = value.to_bytes(4, "little")

    async def read(self, word_addr, maxc=4000):
        d = self.dut
        await RisingEdge(d.clk)
        phase = geti(d.div_counter, -1)
        d.word_address.value = word_addr
        d.rstrb.value = 1
        await RisingEdge(d.clk)
        d.rstrb.value = 0
        info = dict(phase=phase, busy_first_edge=geti(d.rbusy))
        n = 0
        while geti(d.rbusy) == 1:
            await RisingEdge(d.clk)
            n += 1
            assert n < maxc, "timeout esperando fin de lectura"
        info.update(cycles=n, rdata=geti(d.rdata), cs_n_after=geti(d.CS_N),
                    t=self.slave.transactions[-1] if self.slave.transactions else None)
        return info


async def make_bench(dut, **kw):
    b = FlashBench(dut, **kw)
    await b.start()
    return b


def le(b, wa):
    return int.from_bytes(b.slave.mem[4 * wa:4 * wa + 4], "little")


@cocotb.test()
async def test_reset_idle(dut):
    """Tras reset: CS_N=1, rbusy=0 y sin actividad SPI mientras no haya rstrb."""
    b = await make_bench(dut)
    for _ in range(300):
        await RisingEdge(dut.clk)
        assert geti(dut.CS_N) == 1 and geti(dut.rbusy) == 0
    assert not b.slave.transactions


@cocotb.test()
async def test_sck_period_and_duty(dut):
    """SCK durante una lectura: periodo (divisor+1)=3 ciclos; alto/bajo difieren como máximo 1 ciclo."""
    b = await make_bench(dut)
    b.put_word(5, 0x11223344)
    await b.read(5)
    await b.idle(20)
    t = b.slave.transactions[-1]
    periods = {round((r1 - r0) / SYS_NS) for r0, r1 in zip(t["rises"], t["rises"][1:])}
    assert periods == {SCK_PERIOD}, f"periodos de SCK (ciclos) = {sorted(periods)}, esperado {SCK_PERIOD}"
    ev = sorted([(x, "r") for x in t["rises"]] + [(x, "f") for x in t["falls"]])
    hi = {round((t1 - t0) / SYS_NS) for (t0, k0), (t1, k1) in zip(ev, ev[1:]) if k0 == "r" and k1 == "f"}
    lo = {round((t1 - t0) / SYS_NS) for (t0, k0), (t1, k1) in zip(ev, ev[1:]) if k0 == "f" and k1 == "r"}
    dut._log.info(f"SCK alto={sorted(hi)} bajo={sorted(lo)} ciclos")
    assert abs(max(hi) - max(lo)) <= 1


@cocotb.test()
async def test_read_protocol_and_data(dut):
    """Comando 0x03, dirección = 4*word_address, 64 pulsos de SCK (32 cmd+dir, 32 datos), dato LE exacto."""
    b = await make_bench(dut)
    wa = 0x0123
    b.put_word(wa, 0xA1B2C3D4)
    r = await b.read(wa)
    await b.idle(20)
    t = r["t"]
    dut._log.info(f"cmd=0x{t['cmd']:02x} addr=0x{t['addr']:06x} pulsos={len(t['rises'])} "
                  f"rdata=0x{r['rdata']:08x} ciclos={r['cycles']}")
    assert r["busy_first_edge"] == 1, "rbusy debe estar activo en el primer flanco tras rstrb"
    assert t["cmd"] == 0x03, f"comando = 0x{t['cmd']:02x}, esperado 0x03"
    assert t["addr"] == 4 * wa, f"dirección = 0x{t['addr']:06x}, esperada 0x{4 * wa:06x}"
    assert len(t["rises"]) == 64, f"pulsos de SCK = {len(t['rises'])}, esperados 64"
    assert r["rdata"] == 0xA1B2C3D4, f"rdata=0x{r['rdata']:08x}, esperado 0xA1B2C3D4"


@cocotb.test()
async def test_byte_order_little_endian(dut):
    """La flash guarda bytes 01 02 03 04 (dirección creciente); rdata debe ser 0x04030201."""
    b = await make_bench(dut)
    b.slave.mem[0:4] = bytes([1, 2, 3, 4])
    r = await b.read(0)
    await b.idle(10)
    assert r["rdata"] == 0x04030201, f"rdata=0x{r['rdata']:08x}"


@cocotb.test()
async def test_sequential_reads_distinct_words(dut):
    """32 palabras consecutivas leídas una tras otra deben ser exactas."""
    b = await make_bench(dut)
    rng = random.Random(2)
    for w in range(32):
        b.put_word(w, rng.getrandbits(32))
    bad = []
    for w in range(32):
        r = await b.read(w)
        await b.idle(rng.randint(1, 4))
        if r["rdata"] != le(b, w):
            bad.append(f"palabra {w}: 0x{r['rdata']:08x} != 0x{le(b, w):08x}")
    assert not bad, f"{len(bad)}/32 incorrectas:\n  " + "\n  ".join(bad[:6])


@cocotb.test()
async def test_command_and_address_integrity_all_phases(dut):
    """El esclavo debe recibir SIEMPRE 0x03 + dirección correcta, sin importar en qué fase del divisor
    llegue rstrb (el SCK corre libre y CS_N baja en cualquier fase)."""
    b = await make_bench(dut)
    rng = random.Random(9)
    seen = {}
    for i in range(90):
        await b.idle(rng.randint(0, 12))
        wa = rng.randint(0, 200)
        r = await b.read(wa)
        t = r["t"]
        ok = (t["cmd"] == 0x03 and t["addr"] == 4 * wa)
        seen.setdefault(r["phase"], []).append(ok)
        await b.idle(3)
    dut._log.info("fase del divisor -> (ok, total): " + str({p: (sum(v), len(v)) for p, v in sorted(seen.items())}))
    bad = {p: v for p, v in seen.items() if not all(v)}
    assert not bad, ("comando/dirección corrompidos en fases " + str(sorted(bad)) +
                     f" ({sum(not x for v in bad.values() for x in v)} de {sum(len(v) for v in seen.values())} accesos)")


@cocotb.test()
async def test_data_integrity_all_phases(dut):
    """Datos exactos en todas las fases del divisor."""
    b = await make_bench(dut)
    rng = random.Random(10)
    for w in range(256):
        b.put_word(w, rng.getrandbits(32))
    stat = {}
    for i in range(90):
        await b.idle(rng.randint(0, 12))
        wa = rng.randint(0, 255)
        r = await b.read(wa)
        stat.setdefault(r["phase"], []).append(r["rdata"] == le(b, wa))
        await b.idle(3)
    dut._log.info("fase -> (ok,total): " + str({p: (sum(v), len(v)) for p, v in sorted(stat.items())}))
    tot = sum(len(v) for v in stat.values())
    ok = sum(sum(v) for v in stat.values())
    assert ok == tot, f"{tot - ok}/{tot} lecturas con dato incorrecto"


@cocotb.test()
async def test_address_range(dut):
    """Direcciones extremas: 0, 1, 0x7FFFF y 0xFFFFF (hasta 4 MiB)."""
    b = await make_bench(dut)
    bad = []
    for wa in (0, 1, 0x7FFFF, 0xFFFFF):
        b.put_word(wa, 0x5A5AC3C3 ^ wa)
        await b.idle(wa % 5)
        r = await b.read(wa)
        await b.idle(3)
        if r["t"]["addr"] != 4 * wa or r["rdata"] != (0x5A5AC3C3 ^ wa):
            bad.append(f"wa=0x{wa:05x}: addr=0x{r['t']['addr']:06x} rdata=0x{r['rdata']:08x}")
    assert not bad, "\n  ".join(bad)


@cocotb.test()
async def test_busy_handshake(dut):
    """rbusy sube en el primer flanco tras rstrb, baja con CS_N ya en alto, y la latencia es acotada."""
    b = await make_bench(dut)
    b.put_word(3, 0xCAFEF00D)
    r = await b.read(3)
    assert r["busy_first_edge"] == 1
    assert r["cs_n_after"] == 1, "CS_N debe estar en alto cuando rbusy baja"
    dut._log.info(f"latencia de lectura = {r['cycles']} ciclos")
    assert 180 <= r["cycles"] <= 230


@cocotb.test()
async def test_spi_signal_timing(dut):
    """Setup/hold: CS_N baja >=1 ciclo antes del primer SCK y sube >=1 ciclo tras el último;
    MOSI estable en una ventana de ±1 ciclo alrededor de cada flanco de subida."""
    b = await make_bench(dut)
    for k in range(2 * SCK_PERIOD + 1):
        await b.idle(k)
        b.put_word(k, 0xA5A50000 + k)
        await b.read(k)
        await b.idle(2)
    problems = []
    for n, t in enumerate(b.slave.transactions):
        if t["t_first_rise"] - t["t_cs_fall"] < SYS_NS:
            problems.append(f"trans {n}: CS_N->1er SCK = {t['t_first_rise'] - t['t_cs_fall']:.0f} ns")
        if t["t_cs_rise"] - t["t_last_rise"] < SYS_NS:
            problems.append(f"trans {n}: último SCK->CS_N = {t['t_cs_rise'] - t['t_last_rise']:.0f} ns")
        for r in t["rises"]:
            if any(abs(m - r) < SYS_NS for m in t["mosi_t"]):
                problems.append(f"trans {n}: MOSI cambia cerca de un flanco de SCK")
                break
    assert not problems, f"{len(problems)} violaciones:\n  " + "\n  ".join(problems[:8])


@cocotb.test()
async def test_miso_output_delay_tolerance(dut):
    """Una flash real tarda tV (≈6-8 ns, hasta 12 ns a 2.7 V) en presentar el dato. Con SYS=20 ns:
    retardos de 0, 8 y 15 ns no deben alterar la lectura."""
    b = await make_bench(dut)
    rng = random.Random(4)
    fails = []
    for delay in (0.0, 8.0, 15.0):
        b.slave.miso_delay_ns = delay
        for k in range(4):
            wa = 10 + k
            b.put_word(wa, rng.getrandbits(32))
            await b.idle(k)
            r = await b.read(wa)
            if r["rdata"] != le(b, wa):
                fails.append(f"tV={delay:.0f} ns fase {k}: 0x{r['rdata']:08x} != 0x{le(b, wa):08x}")
            await b.idle(4)
    assert not fails, "\n  ".join(fails)


@cocotb.test()
async def test_reset_during_transaction(dut):
    """Reset a mitad de lectura: CS_N sube, rbusy baja y la siguiente lectura funciona."""
    b = await make_bench(dut)
    b.put_word(9, 0x0BADF00D)
    await RisingEdge(dut.clk)
    dut.word_address.value = 9
    dut.rstrb.value = 1
    await RisingEdge(dut.clk)
    dut.rstrb.value = 0
    await ClockCycles(dut.clk, 80)
    assert geti(dut.rbusy) == 1 and geti(dut.CS_N) == 0
    await FallingEdge(dut.clk)
    dut.reset.value = 0
    await ClockCycles(dut.clk, 4)
    assert geti(dut.CS_N) == 1 and geti(dut.rbusy) == 0, "no se liberó tras reset"
    await FallingEdge(dut.clk)
    dut.reset.value = 1
    await ClockCycles(dut.clk, 5)
    r = await b.read(9)
    assert r["rdata"] == 0x0BADF00D, f"tras reset: 0x{r['rdata']:08x}"
