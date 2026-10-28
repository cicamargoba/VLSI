"""rvlib: mini-ensamblador RV32I, ISS de referencia y generador de programas aleatorios (sin cocotb)."""
import random

# --------------------------------------------------------------------------
# Parámetros del entorno
# --------------------------------------------------------------------------
ADDR_WIDTH = 24
ADDR_MASK = (1 << ADDR_WIDTH) - 1
MEM_SIZE = 0x40000          # 256 KiB de memoria simulada
DATA_BASE = 0x20000         # zona de datos / resultados
RES_BASE = DATA_BASE        # buffer de resultados de las pruebas dirigidas
MASK32 = 0xFFFFFFFF
CPU_CLK_NS = 20


def u32(x):
    return x & MASK32


def s32(x):
    x &= MASK32
    return x - (1 << 32) if x & 0x80000000 else x


def sext(x, bits):
    x &= (1 << bits) - 1
    return x - (1 << bits) if x >> (bits - 1) else x


# --------------------------------------------------------------------------
# Mini-ensamblador RV32I
# --------------------------------------------------------------------------
OP_LOAD, OP_ALUI, OP_AUIPC, OP_STORE = 0x03, 0x13, 0x17, 0x23
OP_ALU, OP_LUI, OP_BRANCH, OP_JALR, OP_JAL, OP_SYSTEM = 0x33, 0x37, 0x63, 0x67, 0x6F, 0x73

R_OPS = {  # nombre: (funct7, funct3)
    "add": (0x00, 0), "sub": (0x20, 0), "sll": (0x00, 1), "slt": (0x00, 2),
    "sltu": (0x00, 3), "xor": (0x00, 4), "srl": (0x00, 5), "sra": (0x20, 5),
    "or": (0x00, 6), "and": (0x00, 7),
}
I_OPS = {"addi": 0, "slti": 2, "sltiu": 3, "xori": 4, "ori": 6, "andi": 7}
SH_OPS = {"slli": (0x00, 1), "srli": (0x00, 5), "srai": (0x20, 5)}
BR_OPS = {"beq": 0, "bne": 1, "blt": 4, "bge": 5, "bltu": 6, "bgeu": 7}
LD_OPS = {"lb": 0, "lh": 1, "lw": 2, "lbu": 4, "lhu": 5}
ST_OPS = {"sb": 0, "sh": 1, "sw": 2}


def _chk(v, lo, hi, what):
    assert lo <= v <= hi, f"{what}={v} fuera de rango [{lo},{hi}]"


def R(op, rd, rs1, rs2):
    f7, f3 = R_OPS[op]
    return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | OP_ALU


def I(op, rd, rs1, imm):
    _chk(imm, -2048, 2047, "imm")
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (I_OPS[op] << 12) | (rd << 7) | OP_ALUI


def SH(op, rd, rs1, shamt):
    _chk(shamt, 0, 31, "shamt")
    f7, f3 = SH_OPS[op]
    return (f7 << 25) | (shamt << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | OP_ALUI


def L(op, rd, rs1, imm):
    _chk(imm, -2048, 2047, "imm")
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (LD_OPS[op] << 12) | (rd << 7) | OP_LOAD


def S(op, rs2, rs1, imm):
    _chk(imm, -2048, 2047, "imm")
    return (((imm >> 5) & 0x7F) << 25) | (rs2 << 20) | (rs1 << 15) | (ST_OPS[op] << 12) \
        | ((imm & 0x1F) << 7) | OP_STORE


def B(op, rs1, rs2, off):
    _chk(off, -4096, 4094, "branch off")
    assert off % 2 == 0
    o = off & 0x1FFF
    return (((o >> 12) & 1) << 31) | (((o >> 5) & 0x3F) << 25) | (rs2 << 20) | (rs1 << 15) \
        | (BR_OPS[op] << 12) | (((o >> 1) & 0xF) << 8) | (((o >> 11) & 1) << 7) | OP_BRANCH


def LUI(rd, imm20):
    return ((imm20 & 0xFFFFF) << 12) | (rd << 7) | OP_LUI


def AUIPC(rd, imm20):
    return ((imm20 & 0xFFFFF) << 12) | (rd << 7) | OP_AUIPC


def JAL(rd, off):
    _chk(off, -(1 << 20), (1 << 20) - 2, "jal off")
    assert off % 2 == 0
    o = off & 0x1FFFFF
    return (((o >> 20) & 1) << 31) | (((o >> 1) & 0x3FF) << 21) | (((o >> 11) & 1) << 20) \
        | (((o >> 12) & 0xFF) << 12) | (rd << 7) | OP_JAL


def JALR(rd, rs1, imm):
    _chk(imm, -2048, 2047, "imm")
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (0 << 12) | (rd << 7) | OP_JALR


def RDCYCLE(rd):          # csrrs rd, cycle, x0
    return (0xC00 << 20) | (0 << 15) | (2 << 12) | (rd << 7) | OP_SYSTEM


ECALL = 0x00000073
EBREAK = 0x00100073
NOP = I("addi", 0, 0, 0)


def li(rd, val):
    """Carga inmediata de 32 bits (LUI+ADDI según haga falta)."""
    val = u32(val)
    lo = sext(val & 0xFFF, 12)
    hi = ((val - lo) >> 12) & 0xFFFFF
    if hi == 0:
        return [I("addi", rd, 0, lo)]
    if lo == 0:
        return [LUI(rd, hi)]
    return [LUI(rd, hi), I("addi", rd, rd, lo)]


class Prog:
    """Constructor de programas: dict {dirección: palabra}."""

    def __init__(self, base=0):
        self.words = {}
        self.pc = base
        self.n_res = 0

    def org(self, addr):
        self.pc = addr

    def emit(self, *ws):
        for w in ws:
            if isinstance(w, (list, tuple)):
                self.emit(*w)
            else:
                self.words[self.pc] = u32(w)
                self.pc += 4

    def init_results(self):
        """x31 apunta al buffer de resultados."""
        self.emit(li(31, RES_BASE))
        self.n_res = 0

    def store_result(self, rs):
        """sw rs -> siguiente posición del buffer de resultados (contiguo)."""
        off = (self.n_res % 256) * 4
        self.emit(S("sw", rs, 31, off))
        self.n_res += 1
        if self.n_res % 256 == 0:
            self.emit(I("addi", 31, 31, 1024))

    def halt(self):
        addr = self.pc
        self.emit(JAL(0, 0))     # bucle infinito: fin de programa
        return addr


# --------------------------------------------------------------------------
# Modelo de referencia (funciones puras + ISS)
# --------------------------------------------------------------------------
def alu(op, a, b):
    a, b = u32(a), u32(b)
    op = {"addi": "add", "slti": "slt", "sltiu": "sltu", "xori": "xor", "ori": "or",
          "andi": "and", "slli": "sll", "srli": "srl", "srai": "sra"}.get(op, op)
    if op == "add":
        r = a + b
    elif op == "sub":
        r = a - b
    elif op == "sll":
        r = a << (b & 31)
    elif op == "slt":
        r = int(s32(a) < s32(b))
    elif op == "sltu":
        r = int(a < b)
    elif op == "xor":
        r = a ^ b
    elif op == "srl":
        r = a >> (b & 31)
    elif op == "sra":
        r = s32(a) >> (b & 31)
    elif op == "or":
        r = a | b
    elif op == "and":
        r = a & b
    else:
        raise ValueError(op)
    return u32(r)


def br_taken(op, a, b):
    a, b = u32(a), u32(b)
    return {"beq": a == b, "bne": a != b, "blt": s32(a) < s32(b), "bge": s32(a) >= s32(b),
            "bltu": a < b, "bgeu": a >= b}[op]


_R_BY_F = {v: k for k, v in R_OPS.items()}
_I_BY_F3 = {v: k for k, v in I_OPS.items()}
_BR_BY_F3 = {v: k for k, v in BR_OPS.items()}


class ISS:
    """Simulador RV32I de referencia (decodificación independiente del ensamblador)."""

    def __init__(self, mem, pc=0):
        self.x = [0] * 32
        self.pc = pc
        self.mem = mem
        self.trace = []

    def _rd_mem(self, a, n, signed):
        a &= ADDR_MASK
        v = int.from_bytes(self.mem[a:a + n], "little")
        return sext(v, 8 * n) if signed else v

    def _wr_mem(self, a, n, v):
        a &= ADDR_MASK
        self.mem[a:a + n] = (v & ((1 << (8 * n)) - 1)).to_bytes(n, "little")

    def step(self):
        pc = self.pc
        self.trace.append(pc)
        ins = int.from_bytes(self.mem[pc:pc + 4], "little")
        op = ins & 0x7F
        rd, f3, rs1, rs2, f7 = (ins >> 7) & 31, (ins >> 12) & 7, (ins >> 15) & 31, (ins >> 20) & 31, ins >> 25
        a, b = self.x[rs1], self.x[rs2]
        iimm = sext(ins >> 20, 12)
        simm = sext(((ins >> 25) << 5) | ((ins >> 7) & 0x1F), 12)
        bimm = sext((((ins >> 31) & 1) << 12) | (((ins >> 7) & 1) << 11)
                    | (((ins >> 25) & 0x3F) << 5) | (((ins >> 8) & 0xF) << 1), 13)
        jimm = sext((((ins >> 31) & 1) << 20) | (((ins >> 12) & 0xFF) << 12)
                    | (((ins >> 20) & 1) << 11) | (((ins >> 21) & 0x3FF) << 1), 21)
        uimm = ins & 0xFFFFF000
        nxt = (pc + 4) & ADDR_MASK
        wr = None
        if op == OP_LUI:
            wr = uimm
        elif op == OP_AUIPC:
            wr = (pc + uimm) & ADDR_MASK          # el núcleo trunca a ADDR_WIDTH
        elif op == OP_JAL:
            wr, nxt = nxt, (pc + jimm) & ADDR_MASK
        elif op == OP_JALR:
            wr, nxt = nxt, ((a + iimm) & ADDR_MASK) & ~1
        elif op == OP_BRANCH:
            if br_taken(_BR_BY_F3[f3], a, b):
                nxt = (pc + bimm) & ADDR_MASK
        elif op == OP_LOAD:
            addr = a + iimm
            wr = {0: lambda: self._rd_mem(addr, 1, True), 1: lambda: self._rd_mem(addr, 2, True),
                  2: lambda: self._rd_mem(addr, 4, False), 4: lambda: self._rd_mem(addr, 1, False),
                  5: lambda: self._rd_mem(addr, 2, False)}[f3]()
        elif op == OP_STORE:
            self._wr_mem(a + simm, {0: 1, 1: 2, 2: 4}[f3], b)
        elif op == OP_ALUI:
            if f3 in (1, 5):
                name = {(0, 1): "slli", (0, 5): "srli", (0x20, 5): "srai"}[(f7, f3)]
                wr = alu(name, a, rs2)
            else:
                wr = alu(_I_BY_F3[f3], a, iimm)
        elif op == OP_ALU:
            wr = alu(_R_BY_F[(f7, f3)], a, b)
        else:
            raise AssertionError(f"ISS: opcode no soportado {ins:08x} @ {pc:x}")
        if wr is not None and rd != 0:
            self.x[rd] = u32(wr)
        self.pc = nxt

    def run(self, halt_addr, max_steps=200000):
        for _ in range(max_steps):
            if self.pc == halt_addr:
                self.trace.append(self.pc)
                return
            self.step()
        raise AssertionError("ISS: no llegó al halt")


# Valores de operandos "difíciles"
CORNERS = [0, 1, 2, 0x7FFFFFFF, 0x80000000, 0x80000001, 0xFFFFFFFF, 0xFFFFFFFE,
           0x0000FFFF, 0xFFFF0000, 0x12345678, 0xDEADBEEF, 0x55555555, 0xAAAAAAAA]
IMM_CORNERS = [0, 1, -1, 2, -2, 2047, -2048, 0x7FF, 0x555, -0x556, 0x123, -0x321]


# ==========================================================================
# ALEATORIO DIFERENCIAL CONTRA EL ISS
# ==========================================================================
def rand_val(rng):
    return rng.choice(CORNERS) if rng.random() < 0.5 else rng.getrandbits(32)


def rand_imm(rng):
    return rng.choice(IMM_CORNERS) if rng.random() < 0.4 else rng.randint(-2048, 2047)


def gen_random_program(rng, n_items):
    """Programa aleatorio con avance garantizado (sólo saltos hacia adelante).
    x30 = temporal para JALR, x31 = puntero base de datos (nunca se sobrescriben)."""
    base_ptr = DATA_BASE + 0x200
    items = []

    def reg_any():
        return rng.randint(0, 31)

    def reg_dst():
        return rng.choice([0] + list(range(1, 30)) * 3)

    for _ in range(n_items):
        k = rng.random()
        if k < 0.22:
            items.append(("w", [R(rng.choice(list(R_OPS)), reg_dst(), reg_any(), reg_any())]))
        elif k < 0.36:
            items.append(("w", [I(rng.choice(list(I_OPS)), reg_dst(), reg_any(), rand_imm(rng))]))
        elif k < 0.46:
            items.append(("w", [SH(rng.choice(list(SH_OPS)), reg_dst(), reg_any(), rng.randint(0, 31))]))
        elif k < 0.52:
            items.append(("w", [LUI(reg_dst(), rng.getrandbits(20))]))
        elif k < 0.56:
            items.append(("w", [AUIPC(reg_dst(), rng.getrandbits(20))]))
        elif k < 0.68:
            op = rng.choice(list(LD_OPS))
            sz = {"lb": 1, "lbu": 1, "lh": 2, "lhu": 2, "lw": 4}[op]
            off = rng.randrange(-0x200, 0x200, sz)
            items.append(("w", [L(op, reg_dst(), 31, off)]))
        elif k < 0.80:
            op = rng.choice(list(ST_OPS))
            sz = {"sb": 1, "sh": 2, "sw": 4}[op]
            off = rng.randrange(-0x200, 0x200, sz)
            items.append(("w", [S(op, reg_any(), 31, off)]))
        elif k < 0.90:
            items.append(("br", rng.choice(list(BR_OPS)), reg_any(), reg_any(), rng.randint(1, 4)))
        elif k < 0.95:
            items.append(("jal", reg_dst(), rng.randint(0, 3)))
        else:
            items.append(("jalr", reg_dst(), rng.randint(0, 3), rng.randint(0, 1)))
    items.append(("halt",))

    def nwords(it):
        return 2 if it[0] == "jalr" else 1

    p = Prog()
    for r in range(1, 31):
        p.emit(li(r, rand_val(rng)))
    p.emit(li(31, base_ptr))
    start = p.pc
    addrs, a = [], start
    for it in items:
        addrs.append(a)
        a += 4 * nwords(it)
    halt_addr = addrs[-1]
    n = len(items)
    for idx, it in enumerate(items):
        assert p.pc == addrs[idx]
        if it[0] == "w":
            p.emit(it[1])
        elif it[0] == "br":
            _, op, r1, r2, skip = it
            tgt = addrs[min(idx + 1 + skip, n - 1)]
            p.emit(B(op, r1, r2, tgt - p.pc))
        elif it[0] == "jal":
            _, rd, skip = it
            tgt = addrs[min(idx + 1 + skip, n - 1)]
            p.emit(JAL(rd, tgt - p.pc))
        elif it[0] == "jalr":
            _, rd, skip, odd = it
            tgt = addrs[min(idx + 1 + skip, n - 1)]
            p.emit(AUIPC(30, 0))
            p.emit(JALR(rd, 30, (tgt - p.pc + 4) + odd))
        else:
            p.emit(JAL(0, 0))
    return p, halt_addr


