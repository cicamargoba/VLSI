# SPDX-License-Identifier: Apache-2.0
"""
CO-SIMULACIÓN DEL WORKAROUND DE HARDWARE: chip (RTL del silicio f15fccd) + silicon_spi_mem.v (RTL sintetizable)

Aquí NO se usan los modelos Python de memoria: la flash y la RAM son el módulo Verilog `silicon_spi_mem`,
tal como se implementaría en una FPGA/CPLD colocada en la placa en lugar de los chips SPI comerciales.
Se observa sólo TXD/LED y el contenido de las memorias del emulador.
"""
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Edge, FallingEdge, Timer

from rvlib import *            # noqa: F401,F403
from soc import new_prog, flash_image, halt_loop, crt0, uart_init_regs, uart_putc, uart_wait_idle, uart_puts, UART_BASE
from fw import *               # noqa: F401,F403
from spimodels import geti

CPB = 208
CLK_NS = 20


class HwBench:
    def __init__(self, dut):
        self.dut = dut
        self.rx = bytearray()
        self.seed = 1

    async def start(self):
        cocotb.start_soon(Clock(self.dut.clk, CLK_NS, unit="ns").start())
        self.dut.rst_n.value = 0
        self.dut.rxd.value = 1
        cocotb.start_soon(self._uart())

    async def _uart(self):
        d = self.dut
        while True:
            while True:
                await Edge(d.txd)
                if geti(d.txd, 1) == 0:
                    break
            await Timer(int(CPB * CLK_NS * 1.5), unit="ns")
            v = 0
            for i in range(8):
                v |= (geti(d.txd, 1) & 1) << i
                await Timer(CPB * CLK_NS, unit="ns")
            self.rx.append(v)

    def text(self):
        return self.rx.decode("latin1")

    async def load(self, img: bytes):
        f = self.dut.emu.fmem
        for i, b in enumerate(img):
            f[i].value = b
        await Timer(1, unit="ns")

    def randomize(self, seed):
        rng = random.Random(seed)
        cpu = self.dut.dut.femto0.CPU
        for i in range(32):
            cpu.registerFile[i].value = rng.getrandbits(32)

    async def reset(self, n=12):
        self.rx.clear()
        await FallingEdge(self.dut.clk)
        self.dut.rst_n.value = 0
        await ClockCycles(self.dut.clk, n)
        await FallingEdge(self.dut.clk)
        self.dut.rst_n.value = 1

    async def wait_text(self, s, max_cycles, step=200):
        used = 0
        while used < max_cycles:
            if s in self.text():
                return used
            await ClockCycles(self.dut.clk, step)
            used += step
        return None


def image(p, extra=None):
    img = bytearray(flash_image(p))
    if extra:
        for a, d in extra.items():
            img = img.ljust(a + len(d), b"\0"); img[a:a + len(d)] = d
    return bytes(img)


@cocotb.test()
async def test_hw1_hello_with_rtl_memory_emulator(dut):
    """Con el emulador RTL en lugar de las memorias, el chip arranca e imprime."""
    p = new_prog(); prologue(p); uart_puts(p, "RTL OK\n"); uart_wait_idle(p); halt_loop(p)
    b = HwBench(dut); await b.start(); b.randomize(5); await b.load(image(p)); await b.reset()
    assert await b.wait_text("RTL OK\n", 200_000) is not None, f"UART={b.text()!r}"


@cocotb.test()
async def test_hw2_isa_selftest_with_rtl_memory_emulator(dut):
    """Autotest RV32I completo: 8/10 grupos OK; sólo fallan SB/SH y LB/LH sobre RAM (DEF-S3, del silicio)."""
    p, h, extra = build_isa_selftest()
    b = HwBench(dut); await b.start(); b.randomize(9); await b.load(image(p, extra)); await b.reset()
    assert await b.wait_text("\n", 2_500_000) is not None, f"UART={b.text()!r}"
    line = b.text().strip()
    dut._log.info("autotest: " + line)
    assert line == "ISA PPPPPPPPFF", line


@cocotb.test()
async def test_hw3_ram_contents_big_endian_in_emulator(dut):
    """sw a la SPI RAM deja la palabra en el emulador, MSB primero (big-endian) y lw devuelve los 31 bits bajos."""
    vals = [0x12345678, 0x7FFFFFFF, 0x00000001, 0x55555555]
    p = new_prog(); prologue(p); p.emit(li(10, 0x10000))
    for i, v in enumerate(vals):
        p.emit(li(11, v), S("sw", 11, 10, 4 * i))
    for i in range(4):
        p.emit(L("lw", 12, 10, 4 * i), li(13, 0x7FFFFFFF), R("and", 12, 12, 13))
        put_hex(p, 12, 8); put_char(p, " ")
    uart_wait_idle(p); halt_loop(p)
    b = HwBench(dut); await b.start(); b.randomize(3); await b.load(image(p)); await b.reset()
    exp = " ".join(f"{v & 0x7FFFFFFF:08X}" for v in vals) + " "
    assert await b.wait_text(exp, 3_000_000) is not None, f"UART={b.text()!r} esperado={exp!r}"
    got = [int.from_bytes(bytes(int(dut.emu.rmem[4 * i + j].value) for j in range(4)), "big") for i in range(4)]
    assert got == vals, [hex(g) for g in got]


@cocotb.test()
async def test_hw4_phase_sweep_flash_and_ram(dut):
    """Barrido de fases: un relleno `slli x0,x0,s` (s=0..10) desplaza las fases de los divisores de flash (3) y RAM (11)
    de todas las formas posibles; el resultado debe ser siempre correcto."""
    bad = []
    b = HwBench(dut); await b.start()
    for s in range(11):
        p = new_prog(); p.emit(SH("slli", 0, 0, s)); prologue(p, full_init=False)
        p.emit(li(10, 0x10100), li(11, 0x2A5A5A5), S("sw", 11, 10, 0), L("lw", 12, 10, 0))
        p.emit(li(13, 0x7FFFFFFF), R("and", 12, 12, 13)); put_hex(p, 12, 8); put_char(p, "\n")
        uart_wait_idle(p); halt_loop(p)
        b.randomize(40 + s); await b.load(image(p)); await b.reset()
        if await b.wait_text("\n", 400_000) is None or b.text().strip() != "02A5A5A5":
            bad.append(f"s={s}: {b.text()!r}")
    assert not bad, "fases con error: " + "; ".join(bad)


@cocotb.test()
async def test_hw5_compiled_c_firmware(dut):
    """Firmware en C (gcc rv32i, firmware/hello.c) ejecutado desde la flash del emulador: llamadas, recursión con pila
    en SPI RAM, bucles, MMIO de la UART y LED."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "firmware", "hello.bin")
    img = open(path, "rb").read()
    b = HwBench(dut); await b.start(); b.randomize(77); await b.load(img); await b.reset()
    exp = "C on femto_UN\nfib(10)=37\nram31sum=011D\nprimes<50=0F\n"
    assert await b.wait_text(exp, 6_000_000) is not None, f"UART={b.text()!r}"
    await ClockCycles(dut.clk, 3000)
    assert geti(dut.led) == 1, "el LED no se encendió al final del programa"
