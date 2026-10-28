# SPDX-License-Identifier: Apache-2.0
"""
spimodels: modelos de memorias SPI y periféricos de pines para cocotb.

Perfiles de memoria externa
---------------------------
standard       Memoria SPI comercial (tipo W25Qxx / 23LCxxx / FM25Vxx), SPI modo 0:
               * muestrea MOSI en el flanco de SUBIDA de SCK, cambia MISO en el de BAJADA;
               * READ (0x03) + 24 bits de dirección, el primer bit de dato aparece en el
                 flanco de bajada siguiente al 32º pulso;
               * un comando desconocido (p. ej. 0x06/0x04 por bit perdido) se ignora.
silicon_aware  "Emulador" (MCU / FPGA / CPLD en la placa) que conoce los defectos del silicio
               (commit f15fccd) y los compensa del lado de la memoria:
               * cuenta flancos de BAJADA de SCK desde que CS_N baja (no pulsos de subida);
               * tolera que se pierda el primer bit del comando (detecta 0x06/0x04);
               * flash: entrega el primer bit de dato un flanco de bajada más tarde
                 (equivale a 1 ciclo "dummy"): el controlador entonces captura 32 bits exactos;
               * RAM: mantiene la alineación estándar (el controlador sólo captura 31 bits).
"""
import cocotb
from cocotb.triggers import Edge, First, Timer
from cocotb.utils import get_sim_time


def geti(sig, default=None):
    try:
        return int(sig.value)
    except (ValueError, TypeError):
        return default


# --------------------------------------------------------------------------
# Abstracción de pines
# --------------------------------------------------------------------------
class DirectPins:
    """Pines SPI como señales sueltas del DUT (pruebas unitarias)."""

    def __init__(self, dut, sck="CLK", cs="CS_N", mosi="MOSI", miso="MISO"):
        self.dut = dut
        self._sck, self._cs, self._mosi, self._miso = (getattr(dut, n) for n in (sck, cs, mosi, miso))
        self.triggers = [Edge(self._sck), Edge(self._cs), Edge(self._mosi)]

    def read(self):
        return geti(self._sck, 0), geti(self._cs, 1), geti(self._mosi, 0)

    def drive_miso(self, bit):
        self._miso.value = bit


class SocPins:
    """Pines SPI como bits de uo_out / ui_in del wrapper tt_um_femto."""

    # (sck, cs_n, mosi) en uo_out y bit de MISO en ui_in
    FLASH = dict(sck=5, cs=2, mosi=0, miso=0)
    RAM = dict(sck=4, cs=3, mosi=1, miso=1)

    def __init__(self, soc, which):
        self.soc = soc
        self.m = self.FLASH if which == "flash" else self.RAM
        self.triggers = [Edge(soc.dut.uo_out)]

    def read(self):
        v = geti(self.soc.dut.uo_out, 0xFF)
        m = self.m
        return (v >> m["sck"]) & 1, (v >> m["cs"]) & 1, (v >> m["mosi"]) & 1

    def drive_miso(self, bit):
        self.soc.set_ui(self.m["miso"], bit)


# --------------------------------------------------------------------------
# Esclavo SPI genérico
# --------------------------------------------------------------------------
class SpiTarget:
    READ, WRITE = 0x03, 0x02

    def __init__(self, pins, kind="ram", profile="standard", miso_delay_ns=0.0, size=1 << 17):
        assert kind in ("ram", "flash") and profile in ("standard", "silicon_aware")
        self.pins, self.kind, self.profile = pins, kind, profile
        self.miso_delay_ns = miso_delay_ns
        self.mem = bytearray(size)
        self.transactions = []
        self.cur = None
        self._mosi_changes = []
        self.log = []

    @property
    def dut(self):               # compat. con las pruebas unitarias
        return self.pins.dut

    def _t(self):
        return get_sim_time("ns")

    async def _drive(self, bit):
        if self.miso_delay_ns:
            await Timer(self.miso_delay_ns, unit="ns")
        self.pins.drive_miso(bit)

    # -- utilidades de memoria ------------------------------------------------
    def set_word_be(self, addr, value):
        self.mem[addr:addr + 4] = value.to_bytes(4, "big")

    def get_word_be(self, addr):
        return int.from_bytes(self.mem[addr:addr + 4], "big")

    def load_image(self, base, data):
        self.mem[base:base + len(data)] = data

    # -- bucle principal ----------------------------------------------------------
    async def run(self):
        pins = self.pins
        pins.drive_miso(0)
        await Timer(1, unit="ns")
        prev_clk, prev_cs, prev_mosi = pins.read()
        while True:
            await First(*pins.triggers)
            await Timer(1, unit="ps")            # deja asentar cambios simultáneos
            clk, cs, mosi = pins.read()
            now = self._t()
            if mosi != prev_mosi and self.cur is not None:
                self._mosi_changes.append(now)
            if cs != prev_cs:
                if cs == 0:
                    self._start(now)
                else:
                    self._end(now)
            if clk != prev_clk and self.cur is not None and cs == 0:
                (self._rising if clk == 1 else self._falling)(now, mosi)
            prev_clk, prev_cs, prev_mosi = clk, cs, mosi

    def _start(self, now):
        self._mosi_changes = []
        self.cur = dict(t_cs_fall=now, rises=[], falls=[], bits=[], cmd=0, addr=0, nf=0,
                        wdata=bytearray(), rbits=[], rcount=0, wshift=0, wcount=0, t_first_rise=None,
                        t_last_rise=None, mosi_t=[], t_cs_rise=None, slip=False, mode=None,
                        addr_done=False, out_started=False, rbyte_addr=0)

    def _end(self, now):
        c = self.cur
        if c is not None:
            c["t_cs_rise"] = now
            c["mosi_t"] = list(self._mosi_changes)
            self.transactions.append(c)
        self.cur = None
        self.pins.drive_miso(0)

    # -- flancos ------------------------------------------------------------------
    def _rising(self, now, mosi):
        c = self.cur
        n = len(c["rises"])
        c["rises"].append(now)
        c["bits"].append(mosi)
        c["t_first_rise"] = c["t_first_rise"] or now
        c["t_last_rise"] = now
        if self.profile == "standard":
            if n < 8:
                c["cmd"] = (c["cmd"] << 1) | mosi
            elif n < 32:
                c["addr"] = (c["addr"] << 1) | mosi
                if n == 31:
                    c["addr_done"] = True
            else:
                self._rx_data_bit(c, mosi)
        else:  # silicon_aware: el parseo de comando/dirección ocurre en el flanco de bajada nº 32
            if c["addr_done"]:
                self._rx_data_bit(c, mosi)

    def _rx_data_bit(self, c, mosi):
        if c["cmd"] != self.WRITE or self.kind != "ram":
            return
        c["wshift"] = (c["wshift"] << 1) | mosi
        c["wcount"] += 1
        if c["wcount"] % 8 == 0:
            a = (c["addr"] + c["wcount"] // 8 - 1) % len(self.mem)
            self.mem[a] = c["wshift"] & 0xFF
            c["wdata"].append(c["wshift"] & 0xFF)

    def _falling(self, now, mosi):
        c = self.cur
        c["falls"].append(now)
        # El controlador de la RAM pasa por un estado extra (WAIT_SCLK) tras ver `rd`: un flanco de bajada de SCK
        # que coincide con la bajada de CS_N NO genera "tick" de desplazamiento; en la flash sí.
        if self.kind == "ram" and now == c["t_cs_fall"]:
            return
        c["nf"] += 1
        if self.profile == "standard":
            if c["cmd"] == self.READ and len(c["rises"]) >= 32:
                self._present_next(c)
            return
        # ---- silicon_aware ----
        if c["nf"] == 32:
            self._parse_aware(c)
        if c["addr_done"] and c["cmd"] == self.READ:
            first = 33 if self.kind == "flash" else 32      # flash: +1 ciclo dummy
            if c["nf"] >= first:
                self._present_next(c)

    def _parse_aware(self, c):
        b = c["bits"]
        n = len(b)
        if n == 32:
            cmd = int("".join(map(str, b[:8])), 2); addr = int("".join(map(str, b[8:32])), 2)
        elif n == 31:       # se perdió b0 (siempre 0): el flujo visto es b1..b7 (comando) + b8..b31 (dirección)
            cmd = int("".join(map(str, [0] + b[:7])), 2)
            addr = int("".join(map(str, b[7:31])), 2)
            c["slip"] = True
        else:
            return
        if cmd in (self.READ, self.WRITE):
            c["cmd"], c["addr"], c["addr_done"] = cmd, addr, True
            c["rbyte_addr"] = addr

    def _present_next(self, c):
        k = c["rcount"]
        a = (c["addr"] + k // 8) % len(self.mem)
        bit = (self.mem[a] >> (7 - (k % 8))) & 1
        c["rbits"].append(bit)
        c["rcount"] += 1
        cocotb.start_soon(self._drive(bit))


# --------------------------------------------------------------------------
# Monitor / generador UART (pines)
# --------------------------------------------------------------------------
class UartMonitor:
    """Decodifica 8N1 en una línea (bit de uo_out) midiendo ciclos de reloj."""

    def __init__(self, soc, bit=7, cycles_per_bit=208, clk_ns=20):
        self.soc, self.bit, self.cpb, self.clk_ns = soc, bit, cycles_per_bit, clk_ns
        self.bytes = bytearray()
        self.errors = []
        self.t_first_start = None
        self.edges = []

    def text(self):
        return self.bytes.decode("latin1")

    async def run(self):
        from cocotb.triggers import ClockCycles, RisingEdge
        dut = self.soc.dut
        bit_ns = self.cpb * self.clk_ns
        while True:
            # espera flanco de bajada (bit de inicio)
            while True:
                await Edge(dut.uo_out)
                v = geti(dut.uo_out, 0xFF)
                if not (v >> self.bit) & 1:
                    break
            t0 = get_sim_time("ns")
            if self.t_first_start is None:
                self.t_first_start = t0
            await Timer(bit_ns * 1.5, unit="ns")
            val = 0
            for i in range(8):
                v = geti(dut.uo_out, 0xFF)
                val |= ((v >> self.bit) & 1) << i
                await Timer(bit_ns, unit="ns")
            v = geti(dut.uo_out, 0xFF)
            if not (v >> self.bit) & 1:
                self.errors.append(f"stop bit inválido tras 0x{val:02x}")
            self.bytes.append(val)
            self.edges.append(t0)
