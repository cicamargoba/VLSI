# SPDX-License-Identifier: Apache-2.0
"""
PRUEBAS END-TO-END  (chip completo tt_um_femto visto sólo por sus PINES)

El banco de pruebas se comporta como la placa: aplica clk/rst_n, aporta la flash y la RAM externas
(modelos SPI), cablea ui_in[2]=RXD y observa uo_out[7]=TXD, uo_out[6]=LED. No se lee ningún
registro interno: sólo lo que vería un usuario con un analizador lógico o una terminal serie.
"""
import cocotb
from cocotb.triggers import ClockCycles, FallingEdge

from rvlib import *            # noqa: F401,F403
from soc import *              # noqa: F401,F403
from fw import *               # noqa: F401,F403
from spimodels import geti


async def reset_pulse(dut, n=12):
    await FallingEdge(dut.clk)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, n)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1


@cocotb.test()
async def test_e01_hello_world(dut):
    """Arranca desde la flash e imprime un saludo por la UART."""
    p = new_prog(); prologue(p); uart_puts(p, "Hello, RISC-V!\n"); uart_wait_idle(p); halt_loop(p)
    soc = await boot(dut, p)
    used = await soc.run_until_uart("Hello, RISC-V!\n", 400000)
    assert used is not None, f"salida UART incompleta: {soc.uart.text()!r}"
    assert not soc.uart.errors


@cocotb.test()
async def test_e02_compute_and_print_fibonacci(dut):
    """fib(10) = 55 = 0x37 calculado en el chip e impreso como 'FIB=37'."""
    p = new_prog(); prologue(p)
    p.emit(I("addi", 5, 0, 0), I("addi", 6, 0, 1), I("addi", 7, 0, 10))
    lp = p.pc
    p.emit(R("add", 8, 5, 6), I("addi", 5, 6, 0), I("addi", 6, 8, 0), I("addi", 7, 7, -1))
    p.emit(B("bne", 7, 0, lp - p.pc))
    for c in "FIB=":
        put_char(p, c)
    put_hex(p, 5, 2)
    put_char(p, "\n")
    uart_wait_idle(p); halt_loop(p)
    soc = await boot(dut, p)
    used = await soc.run_until_uart("FIB=37\n", 500000)
    assert used is not None, f"UART: {soc.uart.text()!r}"


@cocotb.test()
async def test_e03_uart_echo(dut):
    """Eco: cada byte recibido por RXD se retransmite por TXD."""
    p = new_prog(); prologue(p)
    top = p.pc
    p.emit(L("lw", 5, 28, 0x10)); p.emit(I("andi", 5, 5, 0x100)); p.emit(B("beq", 5, 0, top - p.pc))
    p.emit(L("lw", 10, 28, 0x08), I("addi", 6, 0, 1), S("sw", 6, 28, 0x10), S("sw", 0, 28, 0x10))
    uart_putc(p, 10, 28)
    p.emit(JAL(0, top - p.pc))
    soc = await boot(dut, p)
    await soc.run_cycles(3000)
    for byte in b"Hi!":
        for b in [0] + [(byte >> i) & 1 for i in range(8)] + [1]:
            soc.set_ui(2, b); await soc.run_cycles(208)
        await soc.run_cycles(12000)                                    # hueco entre caracteres
    assert soc.uart.text() == "Hi!", f"eco = {soc.uart.text()!r}"


@cocotb.test()
async def test_e04_led_blink(dut):
    """El firmware hace parpadear el LED 3 veces; en el pin se ven 3 pulsos."""
    p = new_prog(); prologue(p)
    for _ in range(3):
        p.emit(I("addi", 5, 0, 4), S("sw", 5, 28, 0x10))
        p.emit(I("addi", 6, 0, 8)); l1 = p.pc; p.emit(I("addi", 6, 6, -1)); p.emit(B("bne", 6, 0, l1 - p.pc))
        p.emit(S("sw", 0, 28, 0x10))
        p.emit(I("addi", 6, 0, 8)); l2 = p.pc; p.emit(I("addi", 6, 6, -1)); p.emit(B("bne", 6, 0, l2 - p.pc))
    halt_loop(p)
    soc = await boot(dut, p)
    await soc.run_cycles(60000)
    ups = [t for t, v in soc.led_events if v == 1]
    assert len(ups) == 3, f"pulsos de LED = {len(ups)}  eventos={soc.led_events}"


@cocotb.test()
async def test_e05_reset_restarts_program(dut):
    """Un reset a mitad de ejecución reinicia el firmware: el banner aparece dos veces."""
    p = new_prog(); prologue(p); uart_puts(p, "BOOT\n"); uart_wait_idle(p); halt_loop(p)
    soc = await boot(dut, p)
    assert await soc.run_until_uart("BOOT\n", 200000) is not None
    await soc.run_cycles(3000)
    n0 = soc.uart.text().count("BOOT")
    await reset_pulse(dut)
    await soc.run_cycles(120000)
    assert soc.uart.text().count("BOOT") == n0 + 1, f"{soc.uart.text()!r}"


@cocotb.test()
async def test_e06_isa_selftest(dut):
    """Firmware autocomprobable con las 37 instrucciones RV32I del núcleo: imprime 'ISA ' + 10 letras P/F."""
    p, h, extra = build_isa_selftest()
    soc = await boot(dut, p, flash_extra=extra)
    used = await soc.run_until(lambda: soc.uart.text().count("\n") >= 1, 2_500_000)
    assert used is not None, f"autotest sin respuesta: {soc.uart.text()!r}"
    line = soc.uart.text().strip()
    dut._log.info("salida del autotest: " + line)
    assert line.startswith("ISA ") and len(line) == 14, f"formato inesperado: {line!r}"
    res = line[4:]
    bad = [f"{ISA_GROUPS[i]}" for i, c in enumerate(res) if c != "P"]
    assert not bad, "grupos de instrucciones con FALLO: " + ", ".join(bad)
