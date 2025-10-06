# SPDX-FileCopyrightText: © 2024 Michael Bell
# SPDX-License-Identifier: MIT

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer, FallingEdge, RisingEdge
from cocotb.utils import get_sim_time

from riscvmodel.insn import *

from riscvmodel.regnames import x0, x1, x2, sp, gp, tp, a0, a1, a2, a3, a4
from riscvmodel import csrnames
from riscvmodel.variant import RV32E

from test_util import reset, start_read, send_instr, start_nops, stop_nops, read_byte, read_reg, load_reg, expect_load, expect_store, get_pc, set_pc

@cocotb.test()
async def test_start(dut):
  dut._log.info("Start")
  
  clock = Clock(dut.clk, 15.624, units="ns")
  cocotb.start_soon(clock.start())

  # Reset
  await reset(dut)
  
  # Read cycles
  await send_instr(dut, InstructionCSRRS(x1, x0, csrnames.cycle - 0x1000).encode())
  assert 30 < await read_reg(dut, x1, False) < 200

  # Do some maths
  a = random.randint(0, 0x7fffffff)
  b = random.randint(0, 0x7fffffff)
  await load_reg(dut, x1, a)
  await load_reg(dut, x2, b)
  await send_instr(dut, InstructionADD(x1, x1, x2).encode())
  assert await read_reg(dut, x1) == a + b

### Random operation testing ###
reg = [0] * 32

OP_SIMPLE = 1
OP_MEM = 2
OP_J = 3
OP_JR = 4

# Each Op does reg[d] = fn(a, b)
# fn will access reg global array
class SimpleOp:
    def __init__(self, rvm_insn, fn, name):
        self.rvm_insn = rvm_insn
        self.fn = fn
        self.name = name
        self.op_type = OP_SIMPLE

    def randomize(self):
        self.rvm_insn_inst = self.rvm_insn()
        self.rvm_insn_inst.randomize(variant=RV32E)
    
    def execute_fn(self, rd, rs1, arg2):
        if rd != 0:
            reg[rd] = self.fn(rs1, arg2)
            while reg[rd] < -0x80000000: reg[rd] += 0x100000000
            while reg[rd] > 0x7FFFFFFF:  reg[rd] -= 0x100000000

    def encode(self, rd, rs1, arg2):
        return self.rvm_insn(rd, rs1, arg2).encode()
    
    def get_valid_rd(self):
        rd = random.randint(0, 30)
        if rd == 3: rd += 1
        return rd

    def get_valid_rs1(self):
        return random.randint(0, 31)

    def get_valid_arg2(self):
        return (random.randint(0, 31) if issubclass(self.rvm_insn, InstructionRType) else 
                self.rvm_insn_inst.shamt.value if issubclass(self.rvm_insn, InstructionISType) else
                self.rvm_insn_inst.imm.value)

ops_alu = [
    SimpleOp(InstructionADDI, lambda rs1, imm: reg[rs1] + imm, "+i"),
    SimpleOp(InstructionADD, lambda rs1, rs2: reg[rs1] + reg[rs2], "+"),
    SimpleOp(InstructionSUB, lambda rs1, rs2: reg[rs1] - reg[rs2], "-"),
    SimpleOp(InstructionANDI, lambda rs1, imm: reg[rs1] & imm, "&i"),
    SimpleOp(InstructionAND, lambda rs1, rs2: reg[rs1] & reg[rs2], "&"),
    SimpleOp(InstructionORI, lambda rs1, imm: reg[rs1] | imm, "|i"),
    SimpleOp(InstructionOR, lambda rs1, rs2: reg[rs1] | reg[rs2], "|"),
    SimpleOp(InstructionXORI, lambda rs1, imm: reg[rs1] ^ imm, "^i"),
    SimpleOp(InstructionXOR, lambda rs1, rs2: reg[rs1] ^ reg[rs2], "^"),
    SimpleOp(InstructionSLTI, lambda rs1, imm: 1 if reg[rs1] < imm else 0, "<i"),
    SimpleOp(InstructionSLT, lambda rs1, rs2: 1 if reg[rs1] < reg[rs2] else 0, "<"),
    SimpleOp(InstructionSLTIU, lambda rs1, imm: 1 if (reg[rs1] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0, "<iu"),
    SimpleOp(InstructionSLTU, lambda rs1, rs2: 1 if (reg[rs1] & 0xFFFFFFFF) < (reg[rs2] & 0xFFFFFFFF) else 0, "<u"),
    SimpleOp(InstructionSLLI, lambda rs1, imm: reg[rs1] << imm, "<<i"),
    SimpleOp(InstructionSLL, lambda rs1, rs2: reg[rs1] << (reg[rs2] & 0x1F), "<<"),
    SimpleOp(InstructionSRLI, lambda rs1, imm: (reg[rs1] & 0xFFFFFFFF) >> imm, ">>li"),
    SimpleOp(InstructionSRL, lambda rs1, rs2: (reg[rs1] & 0xFFFFFFFF) >> (reg[rs2] & 0x1F), ">>l"),
    SimpleOp(InstructionSRAI, lambda rs1, imm: reg[rs1] >> imm, ">>i"),
    SimpleOp(InstructionSRA, lambda rs1, rs2: reg[rs1] >> (reg[rs2] & 0x1F), ">>"),
]

@cocotb.test()
async def test_random_alu(dut):
    dut._log.info("Start")
  
    clock = Clock(dut.clk, 15.624, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    await reset(dut)

    seed = random.randint(0, 0xFFFFFFFF)
    #seed = 1508125843
    debug = False
    for test in range(20):
        random.seed(seed + test)
        dut._log.info("Running test with seed {}".format(seed + test))
        for i in range(1, 32):
            if i == 3: reg[i] = 0x1000400
            else:
                reg[i] = random.randint(-0x80000000, 0x7FFFFFFF)
                if debug: print("Set reg {} to {}".format(i, reg[i]))
                await load_reg(dut, i, reg[i])

        if False:
            for i in range(32):
                reg_value = (await read_reg(dut, i)).signed_integer
                if debug: print("Reg {} is {}".format(i, reg_value))
                assert reg_value == reg[i]

        last_instr = ops_alu[0]
        for i in range(200):
            while True:
                try:
                    instr = random.choice(ops_alu)
                    instr.randomize()
                    rd = instr.get_valid_rd()
                    rs1 = instr.get_valid_rs1()
                    arg2 = instr.get_valid_arg2()

                    instr.execute_fn(rd, rs1, arg2)
                    break
                except ValueError:
                    pass

            if debug: print("x{} = x{} {} {}, now {} {:08x}".format(rd, rs1, arg2, instr.name, reg[rd], instr.encode(rd, rs1, arg2)))
            await send_instr(dut, instr.encode(rd, rs1, arg2))
            #if debug:
            #    assert await read_reg(dut, rd) == reg[rd] & 0xFFFFFFFF

        for i in range(32):
            reg_value = (await read_reg(dut, i))
            if debug: print("Reg x{} = {} should be {}".format(i, reg_value, reg[i]))
            assert reg_value & 0xFFFFFFFF == reg[i] & 0xFFFFFFFF

async def set_reg(dut, rd, value):
    await send_instr(dut, InstructionLUI(rd, (value + 0x800) >> 12).encode())
    await send_instr(dut, InstructionADDI(rd, rd, ((value + 0x800) & 0xFFF) - 0x800).encode())
    reg[rd] = value

class LoadOp:
    def __init__(self, instr, min_imm, max_imm, imm_mul, bytes, fn, name):
        self.instr = instr
        self.fn = fn
        self.name = name
        self.op_type = OP_MEM
        self.min_imm = min_imm
        self.max_imm = max_imm
        self.imm_mul = imm_mul
        self.bytes = bytes

    def randomize(self):
        self.rd = random.randint(0, 30)
        if self.rd == 3: self.rd += 1
        while True:
            self.base_reg = random.randint(1, 31)
            if self.base_reg != gp:
                break
        self.imm = random.randint(self.min_imm, self.max_imm) * self.imm_mul
        self.val = random.randint(-0x80000000, 0x7fffffff)

    def execute_fn(self, rd, rs1, arg2):
        if rd != 0:
            reg[rd] = self.fn(self.val)

    def encode(self, rd, rs1, arg2):
        return self.instr(rd, rs1, arg2).encode()
    
    def get_valid_rd(self):
        return self.rd

    def get_valid_rs1(self):
        return self.base_reg

    def get_valid_arg2(self):
        return self.imm
    
    async def do_mem_op(self, dut, addr):
        #print("Load {} from addr {:08x}".format(self.val, addr))
        await expect_load(dut, addr, self.val, abs(self.bytes))

class StoreOp:
    def __init__(self, instr, min_imm, max_imm, imm_mul, bytes, fn, name):
        self.instr = instr
        self.fn = fn
        self.name = name
        self.op_type = OP_MEM
        self.min_imm = min_imm
        self.max_imm = max_imm
        self.imm_mul = imm_mul
        self.bytes = bytes

    def randomize(self):
        self.rs1 = random.randint(0, 31)
        while True:
            self.base_reg = random.randint(1, 31)
            if self.base_reg not in (self.rs1, gp):
                break
        self.imm = random.randint(self.min_imm, self.max_imm) * self.imm_mul

    def execute_fn(self, rd, rs1, arg2):
        pass

    def encode(self, rd, rs1, arg2):
        return self.instr(self.base_reg, self.rs1, arg2).encode()
    
    def get_valid_rd(self):
        return self.base_reg

    def get_valid_rs1(self):
        return self.rs1

    def get_valid_arg2(self):
        return self.imm
    
    async def do_mem_op(self, dut, addr):
        #print("Load {} from addr {:08x}".format(self.val, addr))
        assert await expect_store(dut, addr, self.bytes) == self.fn(self.rs1)

class JumpOpBase:
    def __init__(self, instr, min_imm, max_imm, imm_mul, name):
        self.instr = instr
        self.name = name
        self.op_type = OP_J
        self.min_imm = min_imm
        self.max_imm = max_imm
        self.imm_mul = imm_mul

    def randomize(self):
        self.rs1 = random.randint(1, 31)
        while True:
            self.rd = random.randint(0, 31)
            if self.rd != gp:
                break
        self.imm = random.randint(self.min_imm, self.max_imm) * self.imm_mul

    def execute_fn(self, rd, rs1, arg2):
        pass

    def get_valid_rd(self):
        return self.rd

    def get_valid_rs1(self):
        return self.rs1

    def get_valid_arg2(self):
        return self.imm

class JumpOp(JumpOpBase):
    def __init__(self):
        super().__init__(InstructionJAL, -0x80000, 0x7ffff, 2, "jal")

    def encode(self, rd, rs1, arg2):
        return self.instr(rd, arg2).encode()
    
    def jump(self, rd, rs1, arg2):
        pc = get_pc()
        set_pc(pc - 4 + arg2)
        if rd != 0:
            reg[rd] = pc

    def randomize(self):
        super().randomize()
        self.imm = random.randint(max(-get_pc() // self.imm_mul, self.min_imm), min((0xfffffc - get_pc()) // self.imm_mul, self.max_imm)) * self.imm_mul
        self.imm -= self.imm & 2

class JROp(JumpOpBase):
    def __init__(self):
        super().__init__(InstructionJALR, -0x800, 0x7ff, 1, "jalr")
        self.op_type = OP_JR

    def encode(self, rd, rs1, arg2):
        return self.instr(rd, rs1, arg2).encode()
    
    def jump(self, rd, rs1, arg2):
        pc = get_pc()
        set_pc(reg[rs1] + arg2)
        if rd != 0:
            reg[rd] = pc

    def randomize(self):
        super().randomize()
        while self.rs1 == gp:
            self.rs1 = random.randint(1, 31)

ops = [
    SimpleOp(InstructionADDI, lambda rs1, imm: reg[rs1] + imm, "+i"),
    SimpleOp(InstructionADD, lambda rs1, rs2: reg[rs1] + reg[rs2], "+"),
    SimpleOp(InstructionSUB, lambda rs1, rs2: reg[rs1] - reg[rs2], "-"),
    SimpleOp(InstructionANDI, lambda rs1, imm: reg[rs1] & imm, "&i"),
    SimpleOp(InstructionAND, lambda rs1, rs2: reg[rs1] & reg[rs2], "&"),
    SimpleOp(InstructionORI, lambda rs1, imm: reg[rs1] | imm, "|i"),
    SimpleOp(InstructionOR, lambda rs1, rs2: reg[rs1] | reg[rs2], "|"),
    SimpleOp(InstructionXORI, lambda rs1, imm: reg[rs1] ^ imm, "^i"),
    SimpleOp(InstructionXOR, lambda rs1, rs2: reg[rs1] ^ reg[rs2], "^"),
    SimpleOp(InstructionSLTI, lambda rs1, imm: 1 if reg[rs1] < imm else 0, "<i"),
    SimpleOp(InstructionSLT, lambda rs1, rs2: 1 if reg[rs1] < reg[rs2] else 0, "<"),
    SimpleOp(InstructionSLTIU, lambda rs1, imm: 1 if (reg[rs1] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0, "<iu"),
    SimpleOp(InstructionSLTU, lambda rs1, rs2: 1 if (reg[rs1] & 0xFFFFFFFF) < (reg[rs2] & 0xFFFFFFFF) else 0, "<u"),
    SimpleOp(InstructionSLLI, lambda rs1, imm: reg[rs1] << imm, "<<i"),
    SimpleOp(InstructionSLL, lambda rs1, rs2: reg[rs1] << (reg[rs2] & 0x1F), "<<"),
    SimpleOp(InstructionSRLI, lambda rs1, imm: (reg[rs1] & 0xFFFFFFFF) >> imm, ">>li"),
    SimpleOp(InstructionSRL, lambda rs1, rs2: (reg[rs1] & 0xFFFFFFFF) >> (reg[rs2] & 0x1F), ">>l"),
    SimpleOp(InstructionSRAI, lambda rs1, imm: reg[rs1] >> imm, ">>i"),
    SimpleOp(InstructionSRA, lambda rs1, rs2: reg[rs1] >> (reg[rs2] & 0x1F), ">>"),
    LoadOp(InstructionLW, -0x800, 0x7ff, 1, 4, lambda val: val, "lw"),
    LoadOp(InstructionLH, -0x800, 0x7ff, 1, -2, lambda val: (val & 0xFFFF) - 0x10000 if (val & 0x8000) != 0 else val & 0xFFFF, "lh"),
    LoadOp(InstructionLB, -0x800, 0x7ff, 1, -1, lambda val: (val & 0xFF) - 0x100 if (val & 0x80) != 0 else val & 0xFF, "lb"),
    LoadOp(InstructionLHU, -0x800, 0x7ff, 1, 2, lambda val: val & 0xFFFF, "lhu"),
    LoadOp(InstructionLBU, -0x800, 0x7ff, 1, 1, lambda val: val & 0xFF, "lbu"),
    StoreOp(InstructionSW, -0x800, 0x7ff, 1, 4, lambda rs1: reg[rs1] & 0xFFFFFFFF, "sw"),
    StoreOp(InstructionSH, -0x800, 0x7ff, 1, 2, lambda rs1: reg[rs1] & 0xFFFF, "sh"),
    StoreOp(InstructionSB, -0x800, 0x7ff, 1, 1, lambda rs1: reg[rs1] & 0xFF, "sb"),
    JumpOp(),
    JROp()
]

@cocotb.test()
async def test_random(dut):
    dut._log.info("Start")
  
    clock = Clock(dut.clk, 15.624, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    await reset(dut)

    seed = random.randint(0, 0xFFFFFFFF)
    #seed = 3928128166

    latch_ram = False
    if latch_ram:
        RAM_SIZE = 32
        RAM = []
        for i in range(0, RAM_SIZE, 4):
            val = random.randint(0, 0xFFFFFFFF)
            await set_reg(dut, x1, val)
            await send_instr(dut, InstructionSW(tp, x1, i-0x100).encode())
            RAM.append(val & 0xFF)
            RAM.append((val >> 8) & 0xFF)
            RAM.append((val >> 16) & 0xFF)
            RAM.append((val >> 24) & 0xFF)
    
    debug = False
    if debug and latch_ram: print("RAM: ", RAM)

    for test in range(8):
        random.seed(seed + test)
        dut._log.info("Running test with seed {}".format(seed + test))
        for i in range(1, 32):
            if i == 3: reg[i] = 0x1000400
            else:
                reg[i] = random.randint(-0x80000000, 0x7FFFFFFF)
                if debug: print("Set reg {} to {}".format(i, reg[i]))
                await load_reg(dut, i, reg[i])

        if False:
            for i in range(32):
                reg_value = (await read_reg(dut, i)).signed_integer
                if debug: print("Reg {} is {}".format(i, reg_value))
                assert reg_value == reg[i]

        last_instr = ops[0]
        for i in range(1000):
            while True:
                try:
                    instr = random.choice(ops)
                    instr.randomize()
                    rd = instr.get_valid_rd()
                    rs1 = instr.get_valid_rs1()
                    arg2 = instr.get_valid_arg2()

                    if instr.op_type == OP_MEM:
                        if latch_ram and random.randint(0, 2) == 2:
                            # Use latch RAM
                            addr = random.randint(0x7ffff00-instr.imm, 0x7ffff3c-instr.imm)
                            if instr.name[0] == 'l':
                                val = 0
                                for i in range(abs(instr.bytes)-1, -1, -1):
                                    val <<= 8
                                    val |= RAM[(addr + instr.imm + 0x1000 + i) % RAM_SIZE] 
                                instr.val = val
                                if debug: print(f"val {val} addr {addr + instr.imm:x}")
                        else:
                            # Use PSRAM
                            addr = random.randint(0x1000000-instr.imm, 0x1fffffc-instr.imm)
                            if debug: print(f"Mem addr {addr + instr.imm:x}")
                        await set_reg(dut, instr.base_reg, addr)
                    if instr.op_type == OP_JR:
                        addr = random.randint(-instr.imm+3, 0xfffffc-instr.imm)
                        addr -= (addr + instr.imm) & 3
                        if debug: print("Jump addr:", addr + instr.imm)
                        await set_reg(dut, instr.rs1, addr)

                    instr.execute_fn(rd, rs1, arg2)
                    break
                except ValueError:
                    pass

            if debug: print("x{} = x{} {} {}, now {} {:08x}".format(rd, rs1, arg2, instr.name, reg[rd], instr.encode(rd, rs1, arg2)))
            await send_instr(dut, instr.encode(rd, rs1, arg2))
            if instr.op_type == OP_MEM:
                if addr < 0x4000000:
                    assert addr + instr.imm >= 0
                    assert addr + instr.imm < 0x2000000
                    await instr.do_mem_op(dut, addr + instr.imm)
                elif instr.name[0] == 's':
                    val = instr.fn(instr.rs1)
                    for i in range(instr.bytes):
                        RAM[(addr + instr.imm + 0x1000 + i) % RAM_SIZE] = val & 0xFF
                        val >>= 8
            if instr.op_type == OP_JR or instr.op_type == OP_J:
                instr.jump(rd, rs1, arg2)
                for _ in range(3):
                    if dut.qspi_flash_select.value == 1:
                        break
                    await ClockCycles(dut.clk, 1, False)
                for _ in range(2):
                    if dut.qspi_flash_select.value == 0:
                        break
                    await ClockCycles(dut.clk, 1, False)
                await start_read(dut, get_pc())
            #if True:
            #    assert await read_reg(dut, rd) == reg[rd] & 0xFFFFFFFF

        for i in range(32):
            reg_value = (await read_reg(dut, i))
            if debug: print("Reg x{} = {} should be {}".format(i, reg_value, reg[i]))
            assert reg_value & 0xFFFFFFFF == reg[i] & 0xFFFFFFFF