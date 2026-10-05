import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, First, RisingEdge


PROGRAM = bytes([
    0x37, 0x03, 0x40, 0x00, #lui x6, 64
    0x37, 0x03, 0x40, 0x00, #lui x6, 64
    0x6F, 0x00, 0x00, 0x00, #jal x0, 0
])


class SpiFlash:
    def __init__(self, dut, contents):
        self.dut = dut
        self.contents = contents
        self.reads = []

    def read_byte(self, address):
        if address < len(self.contents):
            return self.contents[address]
        return 0

    async def run(self):
        self.dut.flash_miso.value = 0

        while True:
            await FallingEdge(self.dut.flash_cs_n)
            request = 0

            for _ in range(32):
                await RisingEdge(self.dut.flash_clk)
                request = (request << 1) | int(self.dut.flash_mosi.value)

            command = (request >> 24) & 0xFF
            address = request & 0xFFFFFF
            assert command == 0x03, f"Comando SPI inesperado: 0x{command:02x}"
            self.reads.append((command, address))

            while not int(self.dut.flash_cs_n.value):
                value = self.read_byte(address)
                address += 1

                for bit in range(7, -1, -1):
                    event = await First(
                        FallingEdge(self.dut.flash_clk),
                        RisingEdge(self.dut.flash_cs_n),
                    )
                    if int(self.dut.flash_cs_n.value):
                        self.dut.flash_miso.value = 0
                        break
                    self.dut.flash_miso.value = (value >> bit) & 1
                else:
                    continue
                break


@cocotb.test()
async def execute_lui_from_cocotb_spi_flash(dut):
    dut.rst_n.value = 0
    dut.uart_rx.value = 1
    dut.ram_miso.value = 0
    dut.flash_miso.value = 0

    clock = Clock(dut.clk, 37038, unit="ps")
    cocotb.start_soon(clock.start())

    flash = SpiFlash(dut, PROGRAM)
    cocotb.start_soon(flash.run())

    await ClockCycles(dut.clk, 8)
    dut.rst_n.value = 1

    history = []
    previous = None
    for _ in range(5000):
        await RisingEdge(dut.clk)
        sample = (
            str(dut.debug_pc.value),
            str(dut.debug_instr.value),
            str(dut.debug_x6.value),
        )
        if sample != previous and len(history) < 20:
            history.append(sample)
            previous = sample
        if int(dut.debug_x6.value) == 0x00400000:
            break
    else:
        raise AssertionError(
            f"t1 no recibió 0x00400000; valor final: 0x{int(dut.debug_x6.value):08x}, "
            f"PC=0x{int(dut.debug_pc.value):06x}, "
            f"flash_rdata=0x{int(dut.debug_flash_rdata.value):08x}, "
            f"flash_raw=0x{int(dut.debug_flash_raw.value):08x}, "
            f"instr[31:2]=0x{int(dut.debug_instr.value):08x}, "
            f"lecturas SPI={flash.reads}, historial={history}"
        )

    assert flash.reads, "El controlador no inició ninguna lectura SPI"
    assert flash.reads[:2] == [(0x03, 0), (0x03, 4)], (
        f"Secuencia inicial de lecturas SPI inesperada: {flash.reads[:2]}"
    )
