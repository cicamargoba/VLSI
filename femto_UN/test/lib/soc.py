# SPDX-License-Identifier: Apache-2.0
"""
soc: banco de pruebas a nivel SoC para tt_um_femto (silicio f15fccd).

Pines (según info.yaml):
  uo_out[0]=MOSI flash  [1]=MOSI RAM  [2]=CS_N flash  [3]=CS_N RAM  [4]=SCK RAM  [5]=SCK flash
  uo_out[6]=LED         [7]=TXD
  ui_in[0]=MISO flash   [1]=MISO RAM  [2]=RXD

Mapa de memoria visto por la CPU (femto.v):
  0x0000_0000..0x0000_FFFF  SPI Flash (código)      (cualquier dirección no listada también cae en la flash)
  0x0001_0000..0x0001_FFFF  SPI RAM  (datos, pila)
  0x0040_0000               UART:  +0x08 dato TX / RX ;  +0x10 control/estado
"""
import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge, Timer

from rvlib import (AUIPC, B, I, JAL, JALR, L, LUI, NOP, Prog, R, S, SH, li, u32)
from spimodels import SocPins, SpiTarget, UartMonitor, geti

UART_BASE = 0x400000
UART_DATA = UART_BASE + 0x08
UART_CTRL = UART_BASE + 0x10
RAM_BASE = 0x10000
RAM_TOP = 0x20000
FLASH_SIZE = 1 << 22
UART_CYCLES_PER_BIT = 208            # medido en uart.v (ver test_unit_uart): 16 * (divisor-1) con divisor=14
CLK_NS = 20


class Soc:
    def __init__(self, dut, profile=None, clk_ns=CLK_NS):
        self.dut = dut
        self.profile = profile or os.environ.get("MEM_PROFILE", "standard")
        self.clk_ns = clk_ns
        self.ui = 0x04                         # RXD en reposo = 1
        self.flash = SpiTarget(SocPins(self, "flash"), kind="flash", profile=self.profile, size=FLASH_SIZE)
        self.ram = SpiTarget(SocPins(self, "ram"), kind="ram", profile=self.profile, size=1 << 16)
        self.uart = UartMonitor(self, bit=7, cycles_per_bit=UART_CYCLES_PER_BIT, clk_ns=clk_ns)
        self.led_events = []                   # (tiempo_ns, valor)
        self.cpu = dut.femto0.CPU

    # ---- pines de entrada -------------------------------------------------
    def set_ui(self, bit, v):
        self.ui = (self.ui & ~(1 << bit)) | ((v & 1) << bit)
        self.dut.ui_in.value = self.ui

    # ---- arranque -----------------------------------------------------------
    async def start(self, flash_image=b"", ram_image=None, seed=1, hold_cycles=12, randomize_regs=True):
        d = self.dut
        cocotb.start_soon(Clock(d.clk, self.clk_ns, unit="ns").start())
        d.ena.value = 1
        d.uio_in.value = 0
        d.ui_in.value = self.ui
        d.rst_n.value = 0
        self.flash.mem[0:len(flash_image)] = flash_image
        if ram_image:
            self.ram.mem[0:len(ram_image)] = ram_image
        rng = random.Random(seed)
        if randomize_regs:                         # el silicio arranca con basura
            for i in range(32):
                try:
                    self.cpu.registerFile[i].value = rng.getrandbits(32)
                except Exception:
                    break
            try:
                self.cpu.cycles.value = rng.getrandbits(32)
            except Exception:
                pass
        cocotb.start_soon(self.flash.run())
        cocotb.start_soon(self.ram.run())
        cocotb.start_soon(self.uart.run())
        cocotb.start_soon(self._led_watch())
        await ClockCycles(d.clk, hold_cycles)
        await FallingEdge(d.clk)
        d.rst_n.value = 1
        self.t_reset = cocotb.utils.get_sim_time("ns")

    async def _led_watch(self):
        from cocotb.triggers import Edge
        last = None
        while True:
            await Edge(self.dut.uo_out)
            v = (geti(self.dut.uo_out, 0) >> 6) & 1
            if v != last:
                self.led_events.append((cocotb.utils.get_sim_time("ns"), v))
                last = v

    # ---- ejecución ------------------------------------------------------------
    async def run_cycles(self, n):
        await ClockCycles(self.dut.clk, n)

    async def run_until(self, cond, max_cycles, step=200):
        """Avanza hasta que cond() sea cierto. Devuelve nº de ciclos usados o None si timeout."""
        used = 0
        while used < max_cycles:
            if cond():
                return used
            await ClockCycles(self.dut.clk, step)
            used += step
        return used if cond() else None

    async def run_until_uart(self, text, max_cycles, step=200):
        return await self.run_until(lambda: text.encode() in bytes(self.uart.bytes), max_cycles, step=step)

    # ---- visibilidad interna (sólo pruebas de integración / depuración) ------------
    def pc(self):
        return geti(self.cpu.PC)

    def state(self):
        return geti(self.cpu.state)

    def reg(self, i):
        return geti(self.cpu.registerFile[i])


# --------------------------------------------------------------------------
# Firmware: pequeñas rutinas en el ensamblador de rvlib
# --------------------------------------------------------------------------
def flash_image(prog: Prog, size=None):
    """Prog -> bytes little-endian para la flash (dirección 0)."""
    end = max(prog.words) + 4 if prog.words else 0
    img = bytearray(size or end)
    for a, w in prog.words.items():
        img[a:a + 4] = w.to_bytes(4, "little")
    return bytes(img)


def crt0(p: Prog, sp=RAM_TOP - 4):
    """Arranque mínimo: no se puede suponer ningún registro (el silicio arranca con basura)."""
    for r in range(1, 32):
        p.emit(I("addi", r, 0, 0))
    p.emit(li(2, sp))                       # sp


def uart_init_regs(p: Prog, base_reg=28):
    p.emit(li(base_reg, UART_BASE))


def uart_putc(p: Prog, ch_reg, base_reg=28, tmp=29, tmp2=30):
    """Escribe el byte de ch_reg por la UART. Usa base_reg=UART_BASE y 2 temporales."""
    wait = p.pc
    p.emit(L("lw", tmp, base_reg, 0x10))                 # estado
    p.emit(I("andi", tmp, tmp, 0x200))                   # tx_busy = bit 9
    p.emit(B("bne", tmp, 0, wait - p.pc))
    p.emit(S("sw", ch_reg, base_reg, 0x08))              # dato
    p.emit(I("addi", tmp2, 0, 0x08))
    p.emit(S("sw", tmp2, base_reg, 0x10))                # tx_wr = 1
    p.emit(S("sw", 0, base_reg, 0x10))                   # tx_wr = 0


def uart_puts(p: Prog, text: str, base_reg=28, ch=27):
    for c in text.encode():
        p.emit(I("addi", ch, 0, c))
        uart_putc(p, ch, base_reg)


def uart_wait_idle(p: Prog, base_reg=28, tmp=29):
    wait = p.pc
    p.emit(L("lw", tmp, base_reg, 0x10))
    p.emit(I("andi", tmp, tmp, 0x200))
    p.emit(B("bne", tmp, 0, wait - p.pc))


def halt_loop(p: Prog):
    a = p.pc
    p.emit(JAL(0, 0))
    return a


# --------------------------------------------------------------------------
# Utilidades de arranque / ejecución
# --------------------------------------------------------------------------
class BootFailure(AssertionError):
    pass


def new_prog():
    """Programa para el silicio: la dirección 0 lleva un NOP sacrificial (DEF-R1: la 1ª lectura tras reset se pierde)."""
    p = Prog()
    p.emit(NOP)
    return p


async def boot(dut, prog: Prog, ram_image=None, seed=1, profile=None, check=True, clk_ns=CLK_NS, flash_extra=None):
    """Crea el SoC, carga la flash con `prog`, libera reset y (opcional) verifica que la CPU lee su 1ª instrucción."""
    soc = Soc(dut, profile=profile, clk_ns=clk_ns)
    img = flash_image(prog)
    if flash_extra:                                  # datos constantes en la flash {dirección: bytes}
        buf = bytearray(img.ljust(max(a + len(d) for a, d in flash_extra.items()), b"\0"))
        for a, d in flash_extra.items():
            buf[a:a + len(d)] = d
        img = bytes(buf)
    soc.image = img
    soc.prog = prog
    await soc.start(img, ram_image=ram_image, seed=seed)
    if check:
        await soc.boot_check()
    return soc


async def _boot_check(self, max_cycles=900):
    """Falla rápido: la CPU debe traer la instrucción 0 de la flash. Si no, el silicio con este tipo de
    memoria no arranca (DEF-F1: bit de comando perdido / DEF-F2: dato desplazado 1 bit)."""
    want = int.from_bytes(self.image[4:8], "little")     # instrucción en 0x4 (la de 0x0 se pierde, DEF-R1)
    got = None
    for _ in range(max_cycles):
        await ClockCycles(self.dut.clk, 1)
        if self.state() == 4 and self.pc() == 4:   # EXECUTE de la instrucción @4: instr ya está latcheada
            v = geti(self.cpu.instr)                # el RTL guarda sólo instr[31:2]
            got = None if v is None else (v << 2) | 3
            break
    t0 = self.flash.transactions[0] if self.flash.transactions else None
    cmd = None if t0 is None else t0["cmd"]
    if got != want:
        raise BootFailure(f"la CPU no arranca: 1ª instrucción leída={None if got is None else hex(got)} "
                          f"esperada={hex(want)}; comando visto por la flash={None if cmd is None else hex(cmd)} "
                          f"(esperado 0x3). Perfil de memoria: {self.profile}")


def _cpu_started(self):
    # tras la primera lectura completa la CPU sale de FETCH/WAIT_INSTR hacia EXECUTE/WAIT_ALU
    return geti(self.cpu.state) in (4, 8) or (self.pc() or 0) >= 4


async def _run_to_halt(self, halt_addr, max_cycles, settle=40):
    """Espera a que la CPU esté BUSCANDO/EJECUTANDO la instrucción de halt: PC se actualiza en EXECUTE
    antes de que terminen loads/stores/shifts, así que además se exige state != WAIT_ALU_OR_MEM."""
    used = await self.run_until(lambda: self.pc() == halt_addr and self.state() in (1, 2, 4), max_cycles, step=1)
    assert used is not None, f"timeout: PC={self.pc()} no alcanzó el halt 0x{halt_addr:x} en {max_cycles} ciclos"
    await ClockCycles(self.dut.clk, settle)
    return used


Soc.boot_check = _boot_check
Soc.cpu_started = _cpu_started
Soc.run_to_halt = _run_to_halt
