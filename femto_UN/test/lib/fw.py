# SPDX-License-Identifier: Apache-2.0
"""fw: rutinas de firmware (ensamblador rvlib) para pruebas a nivel SoC."""
from rvlib import B, I, JAL, L, LUI, Prog, R, S, SH, li, u32, s32, alu, br_taken, AUIPC, JALR
from soc import new_prog, UART_BASE, crt0, uart_init_regs, uart_putc, uart_puts, uart_wait_idle, halt_loop


def put_hex(p: Prog, src, ndig=2, base=28, t=26, u=25):
    """Imprime `ndig` dígitos hexadecimales de `src` (mayúsculas) por la UART. Usa x25,x26,x27,x29,x30."""
    for i in range(ndig):
        sh = 4 * (ndig - 1 - i)
        if sh:
            p.emit(SH("srli", t, src, sh))
            p.emit(I("andi", t, t, 15))
        else:
            p.emit(I("andi", t, src, 15))
        p.emit(I("addi", t, t, 48))
        p.emit(I("slti", u, t, 58))
        p.emit(B("bne", u, 0, 8))
        p.emit(I("addi", t, t, 7))
        uart_putc(p, t, base)


def put_char(p: Prog, c: str, base=28, ch=27):
    p.emit(I("addi", ch, 0, ord(c)))
    uart_putc(p, ch, base)


def prologue(p: Prog, full_init=True):
    if full_init:
        crt0(p)
    else:
        p.emit(li(2, 0x1FFFC))
    uart_init_regs(p)


# --------------------------------------------------------------------------
# Autotest de ISA completa (un único firmware que reporta por UART)
# --------------------------------------------------------------------------
from rvlib import R_OPS, I_OPS, SH_OPS, BR_OPS, sext, ADDR_MASK
from soc import S, L

ISA_GROUPS = ["ALU reg-reg", "ALU inmediato", "Desplazamientos", "Branches", "JAL/JALR", "LUI/AUIPC",
              "Loads (flash)", "SW/LW (RAM 31b)", "SB/SH (RAM)", "LB/LH/LBU/LHU (RAM)"]
FLASH_DATA = 0x3000
FLASH_DATA_BYTES = bytes([0x01, 0x82, 0xFF, 0x7F, 0x80, 0x00, 0xFE, 0xCA, 0x78, 0x56, 0x34, 0x92])


def _chk(p, rd, exp, g):
    """Si rd != exp marca el bit g de x31."""
    p.emit(li(4, exp))
    p.emit(B("beq", rd, 4, 8))
    p.emit(I("ori", 31, 31, 1 << g))


def build_isa_selftest(banner="ISA "):
    """Devuelve (Prog, halt_addr, expected_letters_if_all_ok). x31 = máscara de fallos."""
    p = new_prog()
    crt0(p)
    uart_init_regs(p)
    p.emit(I("addi", 31, 0, 0))
    # G0 ALU reg-reg
    for a, b in ((0x80000000, 0x1F), (0xDEADBEEF, 0x12345678), (0xFFFFFFFF, 1)):
        for op in R_OPS:
            p.emit(li(1, a), li(2, b), R(op, 3, 1, 2)); _chk(p, 3, alu(op, a, b), 0)
    # G1 ALU inmediato
    for a, imm in ((0x7FFFFFFF, 1), (0x80000000, -1), (0x12345678, -2048)):
        for op in I_OPS:
            p.emit(li(1, a), I(op, 3, 1, imm)); _chk(p, 3, alu(op, a, sext(imm, 12)), 1)
    # G2 desplazamientos
    a = 0x80000001
    for s in (0, 1, 15, 31):
        for op in ("slli", "srli", "srai"):
            p.emit(li(1, a), SH(op, 3, 1, s)); _chk(p, 3, alu(op, a, s), 2)
        for op in ("sll", "srl", "sra"):
            p.emit(li(1, a), li(2, 0xABC0 | s), R(op, 3, 1, 2)); _chk(p, 3, alu(op, a, s), 2)
    # G3 branches
    cases = {"beq": ((5, 5), (5, 6)), "bne": ((5, 6), (7, 7)), "blt": ((0xFFFFFFFF, 1), (1, 0xFFFFFFFF)),
             "bge": ((1, 0xFFFFFFFF), (0xFFFFFFFF, 1)), "bltu": ((1, 0xFFFFFFFF), (0xFFFFFFFF, 1)),
             "bgeu": ((0xFFFFFFFF, 1), (1, 0xFFFFFFFF))}
    for op, pairs in cases.items():
        for a1, b1 in pairs:
            p.emit(li(1, a1), li(2, b1), I("addi", 3, 0, 1), B(op, 1, 2, 8), I("addi", 3, 0, 0))
            _chk(p, 3, int(br_taken(op, a1, b1)), 3)
    # G4 JAL / JALR
    j = p.pc; p.emit(JAL(5, 8)); p.emit(I("ori", 31, 31, 1 << 4))
    p.emit(AUIPC(6, 0), I("addi", 6, 6, -4)); p.emit(B("beq", 5, 6, 8)); p.emit(I("ori", 31, 31, 1 << 4))
    au = p.pc; p.emit(AUIPC(7, 0), JALR(8, 7, 13)); p.emit(I("ori", 31, 31, 1 << 4))   # destino impar: +12
    _chk(p, 8, au + 8, 4)
    # G5 LUI / AUIPC
    p.emit(LUI(1, 0xABCDE)); _chk(p, 1, 0xABCDE000, 5)
    au2 = p.pc; p.emit(AUIPC(1, 0x00003)); _chk(p, 1, (au2 + 0x3000) & ADDR_MASK, 5)
    # G6 loads desde flash (little-endian)
    p.emit(li(1, FLASH_DATA))
    for op, size in (("lb", 1), ("lbu", 1), ("lh", 2), ("lhu", 2), ("lw", 4)):
        for off in range(0, 12, size):
            p.emit(L(op, 3, 1, off))
            raw = int.from_bytes(FLASH_DATA_BYTES[off:off + size], "little")
            _chk(p, 3, sext(raw, 8 * size) if op in ("lb", "lh") else raw, 6)
    # G7 SW/LW en SPI RAM (bits [30:0])
    p.emit(li(1, 0x10000), li(9, 0x7FFFFFFF))
    for k, v in enumerate((0x12345678, 0x7FFFFFFF, 0x00000001, 0x55555555)):
        p.emit(li(2, v), S("sw", 2, 1, 4 * k))
    for k, v in enumerate((0x12345678, 0x7FFFFFFF, 0x00000001, 0x55555555)):
        p.emit(L("lw", 3, 1, 4 * k), R("and", 3, 3, 9)); _chk(p, 3, v, 7)
    # G8 SB / SH en SPI RAM (sólo el byte/halfword indicado debe cambiar)
    p.emit(li(1, 0x10100), li(2, 0x11223344), S("sw", 2, 1, 0), li(2, 0x7F), S("sb", 2, 1, 3))
    p.emit(L("lw", 3, 1, 0), R("and", 3, 3, 9)); _chk(p, 3, 0x7F223344, 8)
    p.emit(li(2, 0x5566), S("sh", 2, 1, 0))
    p.emit(L("lw", 3, 1, 0), R("and", 3, 3, 9)); _chk(p, 3, 0x7F225566, 8)
    # G9 LB / LBU / LH / LHU en SPI RAM
    p.emit(li(1, 0x10200), li(2, 0x40FF7F81), S("sw", 2, 1, 0))
    for op, off, exp in (("lbu", 0, 0x81), ("lb", 0, sext(0x81, 8)), ("lbu", 1, 0x7F), ("lhu", 0, 0x7F81),
                         ("lh", 0, sext(0x7F81, 16)), ("lbu", 3, 0x40)):
        p.emit(L(op, 3, 1, off)); _chk(p, 3, exp, 9)
    # --- informe por UART ---
    for ch in banner:
        p.emit(I("addi", 27, 0, ord(ch))); uart_putc(p, 27, 28)
    for g in range(10):
        p.emit(I("andi", 5, 31, 1 << g), I("addi", 27, 0, ord("P")), B("beq", 5, 0, 8), I("addi", 27, 0, ord("F")))
        uart_putc(p, 27, 28)
    p.emit(I("addi", 27, 0, 10)); uart_putc(p, 27, 28)
    uart_wait_idle(p, 28)
    h = halt_loop(p)
    # datos constantes en la flash
    img_extra = {FLASH_DATA: FLASH_DATA_BYTES}
    return p, h, img_extra
