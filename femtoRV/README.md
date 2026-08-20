# Demo completo — `tt_um_femto` (UNAL's RISCV, Tiny Tapeout SKY 25b)

Este README documenta cómo reproducir el demo completo validado en silicio: envío de string por UART, parpadeo de LED, y eco de recepción — usando `uart_full_demo.s`.

---

## 1. Hardware necesario

- Demo board Tiny Tapeout v3.2 (RP2040) con `tt_um_femto` seleccionado (mux address 238, shuttle SKY 25b)
- Flash SPI programada con el firmware (ver sección 4)
- Adaptador USB-serial (3.3V) conectado a:
  - `RXD` del adaptador ← `TXD` del ASIC (`uo_out[7]`)
  - `TXD` del adaptador → `RXD` del ASIC (`ui_in[2]`)
  - GND común

---

## 2. Configuración del RP2040 (MicroPython)

Correr en el REPL de la demo board:

```python
from ttboard.demoboard import DemoBoard
from ttboard.mode import RPMode
from machine import Pin

tt = DemoBoard.get()
tt.clock_project_stop()
tt.mode = RPMode.ASIC_RP_CONTROL
tt.shuttle.tt_um_femto.enable()
tt.shuttle.enabled

tt.pins.ui_in0.init(Pin.IN)   # libera MISO flash para memoria real
tt.pins.ui_in1.init(Pin.IN)   # libera MISO RAM para memoria real

tt.pins.uo_out2.init(Pin.IN)  # CS_N flash -- entrada de alta impedancia en el RP2040
tt.pins.uo_out5.init(Pin.IN)  # CLK flash
tt.pins.uo_out3.init(Pin.IN)  # CS_N RAM
tt.pins.uo_out4.init(Pin.IN)  # CLK RAM

tt.reset_project(True)
tt.clock_project_PWM(25000000)
tt.reset_project(False)

print(tt.auto_clocking_freq)
```

### Puntos de operación validados (`clk_sys` ↔ baud terminal)

Debido a inestabilidad conocida del PWM del RP2040, el baud real no coincide con el valor teórico (`clk_sys / 224`). Usa una de estas combinaciones confirmadas en hardware real:

| `clk_sys` (Hz) | Baud en terminal | Notas |
|---|---|---|
| 22,500,000 | ~89,286 | Fetch de instrucciones limpio y repetible |
| **24,000,000** | **90,000** | **RX + TX simultáneos confirmados — recomendado** |
| 25,000,000 | 100,000 / 115,000 / **115,200** | RX + TX confirmados en corridas distintas — ver nota de variabilidad abajo. **115,200 es baud estándar — habilita el M5Stack Chain RGB sin ajuste custom en el PC** |

---

## 3. Terminal serial

```bash
minicom -b 90000 -D /dev/ttyUSB0 -H
```
(`-H` activa vista hex, útil para diagnóstico; `Ctrl-A H` la alterna dentro de una sesión ya abierta)

Ajusta `90000` si usas otra de las combinaciones de la tabla, y `/dev/ttyUSB0` según tu adaptador.

⚠️ Se observó que la misma frecuencia nominal (25MHz) puede requerir baudios distintos entre una sesión y otra (jitter del PWM del RP2040) — **verifica empíricamente el baud en cada sesión**, no asumas que un valor previamente validado seguirá siendo exacto.

---

## 4. Compilar y programar el firmware

```bash
cd femtoRV/firmware/asm/
cp <ruta>/uart_full_demo.s .
```

Edita el `Makefile`:
```makefile
OBJECTS = uart_full_demo.o
```

```bash
make
```

Esto ejecuta automáticamente: ensamblado, enlazado (`bram.ld`), y programación vía `flashrom -p ch341a_spi` sobre un CH341A.

⚠️ **Importante:** el `Makefile` aplica `fix_shift.py --dir right --fill 0` sobre el binario completo antes de programar — esta compensación fue calibrada para firmwares con timing constante (como `blink.s`). Si modificas `uart_full_demo.s` agregando loops con timing variable, revisa si sigue siendo válida (ver notas en `bugs_MappedSPIFlash.md`, Bug 2).

---

## 5. Qué hace el demo

1. **Envía** `"Hello World from femto UN\n\r"` por UART, un carácter a la vez, embebido como inmediato en el código (`li t4,'X'`) — **no usa `lbu`/`lw` hacia la flash**, ver Bug 6.
2. **Parpadea el LED** (`uo_out[6]`) 2 veces (~0.5s por semiciclo, calibrado para el rango de frecuencias de la tabla).
3. Entra en **loop de eco**: recibe caracteres por UART y los retransmite. Si se detecta un error de trama (`rx_error`), transmite `!` como marca visual y sigue esperando — así los errores de recepción intermitentes (atribuibles al jitter del PWM del RP2040) quedan visibles en vez de perderse en silencio.

---

## 6. Limitaciones conocidas (ver `bugs_MappedSPIFlash.md` para detalle completo)

- **Bug 2**: la primera transacción SPI tras el reset puede salir con corrimiento de fase — mitigado en este firmware al no depender de que el primer fetch sea perfecto.
- **Bug 6**: toda instrucción de carga (`lb`/`lbu`/`lh`/`lhu`/`lw`) hacia la **flash** falla sistemáticamente, independiente de dirección/frecuencia — por eso el string va embebido como inmediatos, no como `.rodata` leído con puntero. Pendiente confirmar si aplica igual a la RAM SPI (`test_ram_load.s`).
- **RX ocasionalmente pierde bytes** por jitter del reloj PWM del RP2040 al muestrear una señal externa de baud fijo — visible en este demo como marcas `!` en la terminal.

---

## 7. Troubleshooting rápido

| Síntoma | Causa probable |
|---|---|
| Solo se recibe `0xFF` | Firmware viejo aún en `OBJECTS`, o intento de leer `.rodata` con `lbu`/`lw` (Bug 6) |
| Caracteres ilegibles / basura consistente | Baud del terminal no coincide con la frecuencia real de `clk_sys` — verifica con la tabla de la sección 2 |
| LED no cambia de estado | Delay del blink muy largo para la frecuencia actual — recalcula con `~200 ciclos/instrucción` de referencia |
| `!` frecuentes en el eco | Jitter normal del PWM del RP2040 — considera oscilador externo si necesitas RX 100% confiable |

---

## 8. Chain RGB (M5Stack) — ahora viable

`25,000,000 Hz` produjo **`115200` baud real**, el valor estándar fijo que el M5Stack Chain RGB requiere (su STM32G031 no es ajustable). Con esto, `chain_rgb_scroll_hello.S` / `chain_rgb_diagonal.s` deberían funcionar sin necesidad de baud custom — pendiente de prueba directa contra el módulo real.

```python
tt.clock_project_PWM(25000000)
```

Dada la variabilidad ya documentada del PWM del RP2040, **repite la verificación cada sesión** antes de conectar el Chain RGB — no asumas que el valor se mantiene idéntico entre encendidos.
