# Bugs de MappedSPIFlash / MappedSPIRAM — tt_um_femto (SKY25b)

## 1. 65 flancos de SCK con CS_N bajo

`MappedSPIFlash` genera el reloj SPI como:

```verilog
assign CLK = !CS_N && !clk;
```

La FSM del controlador corre en `negedge clk`. Cada `negedge clk` produce un flanco en CLK.

### Conteo de flancos

| Fase | Ciclos | Descripción |
|---|---|---|
| Envío comando + dirección | 32 | `snd_bitcount` 32→0 |
| Recepción datos | 32 | `rcv_bitcount` 32→0 |
| Ciclo extra | 1 | Entre último shift y subida de CS_N |
| **Total** | **65** | Flancos con CS_N bajo |

### Por qué la simulación funciona

`spiflash.v` muestrea MOSI en **negedge** de CLK. Con 65 flancos descendentes captura 65 bits:

- Bits 1–64: 8 bytes completos (comando 0x03 + 3 bytes dirección + 4 bytes dummy).
- Bit 65: inicia un byte incompleto (1/8).

Cuando CS_N sube, el `always @(csb)` resetea `buffer/bitcount/bytecount` y descarta el byte incompleto. El comando y la dirección ya fueron procesados.

`spiflash.v` cambia MISO en negedge de CLK con retardo `assign #1 io1`. `MappedSPIFlash` muestrea MISO en negedge de `clk` del sistema (≈posedge de CLK), cuando el dato ya está estable gracias al retardo `#1`.

### Por qué el chip físico falla

La flash física muestrea MOSI en **posedge** de CLK.

| Transacción | CS_N↓ (ps) | SCK↓ (ps) | Setup antes del primer posedge | Comando leído |
|---|---|---|---|---|
| 1 | 361 | 361 | ~0 (simultáneo) | 0x06 (WREN) |
| 2 | 8161 | 8161 | ~0 (simultáneo) | 0x06 (WREN) |
| 3 | 16001 | 15961 | 40 ps (SCK ya estable) | 0x03 (READ) |

En las transacciones 1 y 2, `CS_N↓` coincide con `SCK↓` en el mismo timestamp. El primer posedge de SCK ocurre 80 ps después, pero MOSI ya está cambiando — el setup es casi nulo. La flash puede capturar el primer bit incorrectamente, leyendo `0x06` (WREN) en lugar de `0x03` (READ).

En la transacción 3, `SCK` ya está estable en 0 cuando `CS_N` baja (40 ps antes). Hay setup completo antes del primer posedge → la flash lee correctamente `0x03`.

### Raíz

`spiflash.v` usa **negedge**; la flash física usa **posedge**. La diferencia es inocua cuando hay setup adecuado, pero las transacciones 1 y 2 no lo tienen porque `CS_N` y `SCK` caen simultáneamente.

---

## 2. MappedSPIRAM: captura de 31 bits en lectura

`MappedSPIRAM` inicializa `rcv_bitcount` en 32, pero termina cuando `rcv_bitcount <= 1`. Esto significa que solo ejecuta 31 shifts de MISO, no 32.

- El bit 31 de `rcv_data` no se actualiza; retiene el valor de la lectura anterior.
- Ejemplo observado en VCD: `0xFFFFFFFF` esperado, `0x7FFFFFFF` observado (bit 31 quedó en 0 de la lectura anterior).

---

## 3. MappedSPIRAM: WRITE sin WREN

`MappedSPIRAM` envía el comando `0x02` (WRITE) sin enviar antes `0x06` (WREN). El modelo `spiram.v` oculta esta omisión al forzar `realStatusRegister = 0x42` en cada posedge de SCK, manteniendo WEL=1 artificialmente.

La FRAM física requiere WREN antes de WRITE. Sin WREN, la escritura se ignora.

---

## Archivos relevantes

- `tinytapeout/cores/spi_flash/MappedSPIFlash.v` — controlador SPI flash
- `tinytapeout/cores/sim_spi_flash/spiflash.v` — modelo de simulación flash
- `tinytapeout/cores/spi_ram/MappedSPIRAM.v` — controlador SPI RAM
- `tinytapeout/cores/sim_spi_ram/spiram.v` — modelo de simulación RAM
- `tinytapeout/tt_um_femto_TB.vcd` — VCD del post-layout
- `tinytapeout/spi_flash_vcd_findings.json` — diagrama WaveDrom flash
- `tinytapeout/spi_ram_vcd_findings.json` — diagrama WaveDrom RAM
