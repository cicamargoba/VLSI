import json, os
import cocotb
from cocotb.triggers import RisingEdge
from test_unit_spiflash import FlashBench, geti, make_bench

OUT = os.environ["OUTJSON"]

@cocotb.test()
async def collect(dut):
    b = await make_bench(dut)
    word, wa = 0xB09490B8, 7
    b.put_word(wa, word)
    out = {"profile": os.environ.get("MEM_PROFILE")}
    # esperar a la fase c=0 del divisor (período 3): lanzar justo cuando div_counter == 2 (se muestrea 1 ciclo después)
    for _ in range(12):
        await RisingEdge(dut.clk)
        if geti(dut.div_counter) == 2:
            break
    await RisingEdge(dut.clk)
    phase = geti(dut.div_counter)
    dut.word_address.value = wa; dut.rstrb.value = 1
    await RisingEdge(dut.clk); dut.rstrb.value = 0
    s = {k: [] for k in ("CS_N", "CLK", "MOSI", "MISO")}
    n = 0
    while True:
        for k in s: s[k].append(geti(getattr(dut, k), 0))
        if geti(dut.rbusy) == 0 and n > 3: break
        await RisingEdge(dut.clk); n += 1
    t = b.slave.transactions[-1]
    out.update(wave=s, phase=phase, rdata=geti(dut.rdata), exp=word, cmd=t["cmd"], pulses=len(t["rises"]),
               rbits=t["rbits"][:34], cycles=n)
    json.dump(out, open(OUT, "w"))
    dut._log.info(f"phase={phase} cmd=0x{t['cmd']:x} rdata=0x{out['rdata']:08x} exp=0x{word:08x}")
