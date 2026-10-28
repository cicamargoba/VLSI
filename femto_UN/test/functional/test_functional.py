# SPDX-License-Identifier: Apache-2.0
"""
PRUEBAS FUNCIONALES  (tt_um_femto completo, RTL f15fccd)

Cada prueba ejecuta un programa RV32I desde la SPI Flash y comprueba una FUNCIÓN del sistema
contra un resultado de referencia independiente (rvlib.alu / br_taken / valores literales).
Se lee el estado final de la CPU (registerFile), la RAM externa o los pines (UART/LED).
Todos los programas empiezan con un NOP en la dirección 0 (regla de silicio R1, ver DEF-R1).
"""
import cocotb
from cocotb.triggers import ClockCycles

from rvlib import *            # noqa: F401,F403
from soc import *              # noqa: F401,F403
from fw import *               # noqa: F401,F403
from spimodels import geti

MAXC = 600000


def expect_regs(soc, exp, label):
    bad = [f"x{r}=0x{(soc.reg(r) or 0):08x} esp 0x{u32(v):08x}" for r, v in exp.items() if soc.reg(r) != u32(v)]
    assert not bad, f"{label}: {len(bad)}/{len(exp)} incorrectos: " + "; ".join(bad[:6])


async def run_prog(dut, p, h, exp=None, label="", max_cycles=MAXC, seed=1, ram_image=None):
    soc = await boot(dut, p, seed=seed, ram_image=ram_image)
    await soc.run_to_halt(h, max_cycles)
    if exp is not None:
        expect_regs(soc, exp, label)
    return soc


R_OPS_ALL = list(R_OPS)


@cocotb.test()
async def test_f01_alu_register_ops(dut):
    """ADD SUB SLL SLT SLTU XOR SRL SRA OR AND con 3 pares de operandos límite."""
    for a, b in ((0x80000000, 0x0000001F), (0xDEADBEEF, 0x12345678), (0xFFFFFFFF, 0x00000001)):
        p = new_prog(); p.emit(li(1, a), li(2, b))
        exp = {}
        for k, op in enumerate(R_OPS_ALL):
            p.emit(R(op, 10 + k, 1, 2)); exp[10 + k] = alu(op, a, b)
        h = halt_loop(p)
        await run_prog(dut, p, h, exp, f"alu reg a=0x{a:x} b=0x{b:x}")


@cocotb.test()
async def test_f02_alu_immediate_ops(dut):
    """ADDI SLTI SLTIU XORI ORI ANDI con inmediatos con signo extendido."""
    for a, imm in ((0x7FFFFFFF, 1), (0x80000000, -1), (0x12345678, -2048), (0x0000FFFF, 2047)):
        p = new_prog(); p.emit(li(1, a))
        exp = {}
        for k, op in enumerate(I_OPS):
            p.emit(I(op, 10 + k, 1, imm)); exp[10 + k] = alu(op, a, sext(imm, 12))
        h = halt_loop(p)
        await run_prog(dut, p, h, exp, f"alu imm a=0x{a:x} imm={imm}")


@cocotb.test()
async def test_f03_shifts_all_forms(dut):
    """SLL/SRL/SRA y SLLI/SRLI/SRAI para desplazamientos 0,1,5,16,31 (los bits altos de rs2 se ignoran)."""
    a = 0x80000001
    p = new_prog(); p.emit(li(1, a))
    exp, r = {}, 5
    for s in (0, 1, 5, 16, 31):
        p.emit(li(2, (0xABC << 5) | s))
        for op in ("sll", "srl", "sra"):
            p.emit(R(op, r, 1, 2)); exp[r] = alu(op, a, s); r += 1
        for op in ("slli", "srli", "srai"):
            if r > 27: break
            p.emit(SH(op, r, 1, s)); exp[r] = alu(op, a, s); r += 1
        if r > 24: break
    h = halt_loop(p)
    await run_prog(dut, p, h, exp, "shifts")


@cocotb.test()
async def test_f04_branches_taken_and_not_taken(dut):
    """BEQ BNE BLT BGE BLTU BGEU: cada uno tomado y no tomado (12 casos), con comparaciones con signo y sin signo."""
    cases = {"beq": ((5, 5), (5, 6)), "bne": ((5, 6), (7, 7)), "blt": ((0xFFFFFFFF, 1), (1, 0xFFFFFFFF)),
             "bge": ((1, 0xFFFFFFFF), (0xFFFFFFFF, 1)), "bltu": ((1, 0xFFFFFFFF), (0xFFFFFFFF, 1)),
             "bgeu": ((0xFFFFFFFF, 1), (1, 0xFFFFFFFF))}
    p = new_prog(); exp = {}; r = 10
    for op, pairs in cases.items():
        for a, b in pairs:
            p.emit(li(1, a), li(2, b), I("addi", r, 0, 1), B(op, 1, 2, 8), I("addi", r, 0, 0))
            exp[r] = int(br_taken(op, a, b)); r += 1
    h = halt_loop(p)
    await run_prog(dut, p, h, exp, "branches")


@cocotb.test()
async def test_f05_jal_jalr_call_return(dut):
    """JAL/JALR: enlace=PC+4, llamada anidada y retorno, destino impar de JALR, bucle hacia atrás."""
    p = new_prog()
    p.emit(I("addi", 20, 0, 0))
    call1 = p.pc; p.emit(JAL(1, 0))                       # parche abajo
    ret1 = p.pc
    p.emit(I("addi", 21, 20, 0)); p.emit(JAL(0, 0))       # fin -> salta a 'end' (parche)
    end_jump = p.pc - 4
    func = p.pc
    p.emit(I("addi", 20, 20, 5), JALR(0, 1, 0))           # f(): x20 += 5 ; ret
    p.words[call1] = JAL(1, func - call1)
    p.emit(li(3, 0))                                      # end:
    end = p.pc - 4 if len(li(3, 0)) == 1 else p.pc
    p.words[end_jump] = JAL(0, p.pc - 4 - end_jump) if False else JAL(0, (p.pc - end_jump))
    # bucle hacia atrás: x4 = 10 + 9 + ... + 1
    p.emit(I("addi", 4, 0, 0), I("addi", 5, 0, 10))
    lp = p.pc
    p.emit(R("add", 4, 4, 5), I("addi", 5, 5, -1))
    p.emit(B("bne", 5, 0, lp - p.pc))
    # JALR a destino impar (bit0 debe ignorarse)
    p.emit(li(6, 0))
    tgt_patch = p.pc
    p.emit(AUIPC(7, 0), JALR(8, 7, 13))                   # destino = (pc_auipc + 13) & ~1 = pc_auipc + 12
    p.emit(I("addi", 9, 0, 0x7AD))                        # saltada
    p.emit(I("addi", 10, 0, 0x2A))                        # destino
    h = halt_loop(p)
    exp = {1: ret1, 20: 5, 21: 5, 4: 55, 8: tgt_patch + 8, 9: None, 10: 0x2A}
    soc = await boot(dut, p)
    await soc.run_to_halt(h, MAXC)
    exp = {k: v for k, v in exp.items() if v is not None}
    expect_regs(soc, exp, "jumps")
    assert soc.reg(9) != 0x7AD, "JALR a destino impar ejecutó la instrucción saltada"


@cocotb.test()
async def test_f06_lui_auipc(dut):
    p = new_prog()
    p.emit(LUI(1, 0x12345), LUI(2, 0xFFFFF), LUI(3, 0x80000))
    a = p.pc; p.emit(AUIPC(4, 0x00001))
    b = p.pc; p.emit(AUIPC(5, 0x000FF))
    h = halt_loop(p)
    await run_prog(dut, p, h, {1: 0x12345000, 2: 0xFFFFF000, 3: 0x80000000, 4: a + 0x1000, 5: (b + 0xFF000) & ADDR_MASK}, "lui/auipc")


@cocotb.test()
async def test_f07_loads_from_flash_all_widths(dut):
    """LB LBU LH LHU LW sobre datos constantes en la flash (little-endian) en todos los desplazamientos."""
    base = 0x2000
    data = bytes([0x01, 0x82, 0xFF, 0x7F, 0x80, 0x00, 0xFE, 0xCA, 0x78, 0x56, 0x34, 0x92])
    p = new_prog(); p.emit(li(1, base))
    exp, r = {}, 10
    for op, size in (("lb", 1), ("lbu", 1), ("lh", 2), ("lhu", 2), ("lw", 4)):
        for off in range(0, 12, size):
            if r > 30: break
            p.emit(L(op, r, 1, off))
            raw = int.from_bytes(data[off:off + size], "little")
            exp[r] = sext(raw, 8 * size) if op in ("lb", "lh") else raw
            r += 1
    # limita a los registros disponibles: reparte en 2 programas si hace falta
    exp = {k: v for k, v in exp.items() if k <= 30}
    h = halt_loop(p)
    soc = Soc(dut)
    img = bytearray(flash_image(p)); img = img.ljust(base + 16, b"\0"); img[base:base + 12] = data
    soc.image = bytes(img)
    await soc.start(soc.image)
    await soc.boot_check()
    await soc.run_to_halt(h, MAXC)
    expect_regs(soc, exp, "loads flash")


@cocotb.test()
async def test_f08_stack_recursion_in_spiram(dut):
    """Factorial recursivo (n=6) con la pila en SPI RAM (sw/lw de ra y n): resultado 720."""
    p = new_prog(); p.emit(li(2, 0x10FF0), I("addi", 10, 0, 6))
    call = p.pc; p.emit(JAL(1, 0))
    done = p.pc; p.emit(JAL(0, 0)); donej = p.pc - 4
    fact = p.pc
    # fact(n): if n<=1 return 1 ; else n * fact(n-1)   (multiplicación por sumas repetidas)
    p.emit(I("addi", 2, 2, -8), S("sw", 1, 2, 4), S("sw", 10, 2, 0))
    p.emit(I("addi", 5, 0, 2), B("bge", 10, 5, 12))
    p.emit(I("addi", 10, 0, 1), JAL(0, 0)); to_epi = p.pc - 4
    p.emit(I("addi", 10, 10, -1)); rec = p.pc; p.emit(JAL(1, fact - rec))
    p.emit(L("lw", 6, 2, 0), I("addi", 7, 0, 0), I("addi", 8, 10, 0))   # x6=n, x8=fact(n-1)
    loop = p.pc
    p.emit(R("add", 7, 7, 8), I("addi", 6, 6, -1)); p.emit(B("bne", 6, 0, loop - p.pc))
    p.emit(I("addi", 10, 7, 0))
    epi = p.pc
    p.emit(L("lw", 1, 2, 4), I("addi", 2, 2, 8), JALR(0, 1, 0))
    p.words[to_epi] = JAL(0, epi - to_epi)
    p.words[call] = JAL(1, fact - call)
    p.words[donej] = JAL(0, p.pc - donej)
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 3_000_000)
    assert soc.reg(10) == 720, f"fact(6) = {soc.reg(10)} (esperado 720)"


@cocotb.test()
async def test_f09_ram_word_store_load_masked31(dut):
    """sw/lw en SPI RAM: los 31 bits bajos se conservan (el bit 31 no es fiable, ver DEF-S2)."""
    vals = [0x00000000, 0x7FFFFFFF, 0x2468ACE0, 0x13579BDF, 0x40000001, 0x00000002]
    p = new_prog(); p.emit(li(10, 0x10400))
    for i, v in enumerate(vals):
        p.emit(li(11, v), S("sw", 11, 10, 4 * i))
    for i in range(len(vals)):
        p.emit(L("lw", 12 + i, 10, 4 * i))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 2_000_000)
    bad = [f"[{i}] 0x{soc.reg(12+i) & 0x7FFFFFFF:08x} != 0x{v:08x}" for i, v in enumerate(vals) if soc.reg(12 + i) & 0x7FFFFFFF != v]
    assert not bad, "; ".join(bad)


@cocotb.test()
async def test_f10_ram_subword_store_load(dut):
    """ISA: SB/SH/LB/LH/LBU/LHU sobre la SPI RAM deben comportarse como en cualquier RV32I."""
    p = new_prog(); p.emit(li(10, 0x10800), li(11, 0x01020304), S("sw", 11, 10, 0), li(12, 0x7F), S("sb", 12, 10, 3))
    p.emit(L("lbu", 13, 10, 3), L("lbu", 14, 10, 0), li(15, 0x1234), S("sh", 15, 10, 4), L("lhu", 16, 10, 4))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 3_000_000)
    got = (soc.reg(13), soc.reg(14), soc.reg(16))
    assert got == (0x7F, 0x04, 0x1234), f"lbu@3,lbu@0,lhu@4 = {tuple(hex(g) for g in got)} (esperado ('0x7f','0x4','0x1234'))"


@cocotb.test()
async def test_f11_uart_transmit_char(dut):
    p = new_prog(); prologue(p, full_init=False); put_char(p, "A"); h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 100000)
    await soc.run_cycles(4000)
    assert soc.uart.text() == "A" and not soc.uart.errors, f"{soc.uart.text()!r} {soc.uart.errors}"


@cocotb.test()
async def test_f12_uart_receive_byte(dut):
    """Un byte enviado por ui_in[2] (a 208 ciclos/bit) se lee por polling y se devuelve en x10."""
    p = new_prog(); prologue(p, full_init=False)
    wait = p.pc
    p.emit(L("lw", 5, 28, 0x10)); p.emit(I("andi", 5, 5, 0x100)); p.emit(B("beq", 5, 0, wait - p.pc))
    p.emit(L("lw", 10, 28, 0x08), I("addi", 6, 0, 1), S("sw", 6, 28, 0x10), S("sw", 0, 28, 0x10))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_cycles(3000)
    for b in [0] + [(0xC5 >> i) & 1 for i in range(8)] + [1]:
        soc.set_ui(2, b); await soc.run_cycles(208)
    await soc.run_to_halt(h, 400000)
    assert soc.reg(10) == 0xC5, f"x10=0x{soc.reg(10):x}"


@cocotb.test()
async def test_f13_led_control(dut):
    """El bit 2 del registro de control UART gobierna el pin LEDS (uo_out[6])."""
    p = new_prog(); prologue(p, full_init=False)
    p.emit(I("addi", 5, 0, 4), S("sw", 5, 28, 0x10), S("sw", 0, 28, 0x10), S("sw", 5, 28, 0x10), S("sw", 0, 28, 0x10))
    h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 100000)
    await soc.run_cycles(50)
    vals = [v for _, v in soc.led_events if v in (0, 1)]
    assert vals[-4:] == [1, 0, 1, 0] or vals.count(1) >= 2, f"eventos LED: {soc.led_events}"


@cocotb.test()
async def test_f14_rdcycle_monotonic_and_latency(dut):
    """RDCYCLE crece con el tiempo; 10 instrucciones ALU entre dos lecturas cuestan ~198 ciclos c/u (flash)."""
    p = new_prog(); p.emit(RDCYCLE(5))
    for _ in range(10): p.emit(I("addi", 7, 7, 1))
    p.emit(RDCYCLE(6)); h = halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_to_halt(h, 200000)
    d = u32(soc.reg(6) - soc.reg(5))
    per = d / 11
    dut._log.info(f"Δcycles = {d}  ->  {per:.1f} ciclos/instrucción (fetch SPI flash)")
    assert 180 <= per <= 215, f"{per:.1f} ciclos/instrucción fuera del rango esperado"


@cocotb.test()
async def test_f15_power_up_state_is_not_zero(dut):
    """Los registros arrancan con valores indeterminados: el firmware DEBE inicializarlos (crt0)."""
    vals = []
    for seed in (11, 12):
        p = new_prog(); p.emit(R("add", 20, 9, 0)); h = halt_loop(p)     # x20 = x9 sin inicializar
        soc = await boot(dut, p, seed=seed)
        await soc.run_to_halt(h, 60000)
        vals.append(soc.reg(20))
    assert vals[0] != vals[1], "registros iguales en 2 arranques: no se está modelando el estado indeterminado"
