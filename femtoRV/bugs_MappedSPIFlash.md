# Bugs identificados en `MappedSPIFlash.v` — bring-up de silicio `tt_um_femto`

**Proyecto:** UNAL's RISCV (Tiny Tapeout, shuttle SKY 25b, mux 238)
**Repo:** `cicamargoba/femto_UN`
**Módulo afectado:** `src/MappedSPIFlash.v` (aplica también, potencialmente, a `MappedSPIRAM.v`, que comparte el mismo mecanismo de generación de `CLK`)
**Metodología de detección:** captura con analizador lógico durante bring-up en demo board Tiny Tapeout v3.2 (RP2040), correlacionada con lectura línea a línea del RTL.

## Puntos de operación empíricamente validados (RX + TX estables)

Dada la inestabilidad conocida del PWM del RP2040 como fuente de `clk_sys` (ver nota en Bug 2), el baud rate real efectivo no siempre coincide con el valor teórico calculado (`224 ciclos/bit / clk_sys`). Las siguientes combinaciones fueron confirmadas funcionando de forma estable en hardware real:

| `clk_sys` (RP2040 PWM) | Baud configurado en terminal | Notas |
|---|---|---|
| 22,500,000 Hz | ~89,286 (calculado) | Fetch de instrucciones confirmado limpio y repetible |
| 24,000,000 Hz | 90,000 | RX + TX simultáneos confirmados limpios |
| 25,000,000 Hz | 100,000 | RX + TX simultáneos confirmados limpios |
| 25,000,000 Hz | 115,000 | RX + TX simultáneos confirmados limpios — muy cerca del baud fijo (115200) que necesita el M5Stack Chain RGB |

El baud real medido se desvía del valor teórico (`clk_sys/224`) en todos los casos — evidencia adicional de que el reloj real entregado al chip no coincide exactamente con el valor solicitado por software al RP2040.

**Nota de variabilidad**: a la misma frecuencia nominal (25,000,000 Hz) se observaron dos baudios distintos funcionando en corridas separadas (100,000 y 115,000) — una diferencia de ~15%, mayor a lo que la tolerancia normal de framing UART explicaría para una única frecuencia real fija. Esto sugiere que el PWM del RP2040 no entrega la misma frecuencia real de forma consistente entre distintas invocaciones de `clock_project_PWM()`, incluso pidiendo el mismo valor nominal. Recomendación práctica: **verificar empíricamente el baud en cada sesión de bring-up**, no asumir que una combinación validada previamente seguirá siendo exacta.

---

## Bug 1 — Ciclo de reloj adicional (33 en vez de 32) al final del estado `RECEIVE`

### Descripción del RTL

El módulo maneja dos contadores de bits simétricos en apariencia — `snd_bitcount` (envío de comando+dirección) y `rcv_bitcount` (recepción de datos) — pero con lógicas de salida **asimétricas**:

```verilog
// Estado SEND (correcto, sin desperdicio de ciclo)
if (snd_bitcount == 1) begin
    rcv_bitcount <= 32;
    state <= RECEIVE;              // transiciona anticipando el último bit
end

// Estado RECEIVE (bug)
if (rcv_bitcount == 0) begin
    state <= START;                // solo transiciona DESPUÉS de llegar a 0
end
else begin
    rcv_bitcount <= rcv_bitcount - 1;
    rcv_data     <= {rcv_data[30:0], MISO};
end
```

`SEND` anticipa la transición verificando `==1` (el penúltimo valor), por lo que el cambio de estado ocurre en el mismo pulso de reloj en que se transmite el último bit — sin ciclos perdidos.

`RECEIVE` no tiene esa anticipación: verifica `==0`, condición que solo es cierta **después** de haber decrementado en el pulso anterior. Esto obliga a un pulso de reloj SPI adicional (el 33) solo para *detectar* que ya se recibieron los 32 bits, antes de bajar `CS_N`.

### Evidencia empírica

Con `CS_N` todavía en bajo durante ese pulso 33, la flash (en modo de lectura secuencial estándar) ya expone el primer bit del **siguiente** byte en su memoria interna. Se capturó exactamente esto:

- Instrucción esperada en `0x00`: `0x004000B7` (`lui t1,0x400`)
- Instrucción real en `0x04`: `0x01008093` (`addi t1,t1,16`) → primer byte transmitido (little-endian) = `0x93` = `1001 0011`, MSB = `1`
- Bit extra capturado en el pulso 33: **`1`** — coincide exactamente con el MSB de `0x93`

Esto confirma el mecanismo: el pulso 33 no corrompe el dato ya capturado (los 32 bits de `rcv_data` son correctos), pero desperdicia un ciclo de bus y expone (sin capturar) un bit de la siguiente dirección de memoria.

### Impacto

- **No corrompe datos.** Los 32 bits recibidos en cada transacción son siempre correctos una vez la fase del reloj está estabilizada (ver Bug 2).
- Agrega **1 ciclo de latencia** por cada acceso a flash — penalización de rendimiento, no de corrección funcional.
- No es bloqueante para el bring-up actual; confirmado por ejecución correcta del firmware de prueba (blink).

### Fix propuesto (para el próximo tapeout)

Espejar la misma técnica de anticipación que ya usa `SEND`:

```verilog
RECEIVE: begin
  if (clk_div) begin
    if (rcv_bitcount == 1) begin
      rcv_data <= {rcv_data[30:0], MISO};
      state    <= START;
    end
    else begin
      rcv_bitcount <= rcv_bitcount - 6'd1;
      rcv_data     <= {rcv_data[30:0], MISO};
      state        <= RECEIVE;
    end
  end
end
```

### Verificación recomendada tras el fix

Simulación con testbench dirigido: contar ciclos de `CLK` entre flanco de bajada y subida de `CS_N` en una transacción de lectura — debe dar exactamente 64 (32 SEND + 32 RECEIVE), no 65.

---

## Bug 2 — Generador de `CLK` no sincronizado con `CS_N` (corrimiento de fase tras reset)

### Descripción del RTL

El generador de reloj SPI corre libre desde que se libera el reset, independientemente del estado de la FSM (`WAIT_STRB` / `SEND` / `RECEIVE`) y de si `CS_N` está activo o no:

```verilog
always @(negedge clk) begin
    if (!reset)
        CLK <= 0;
    else if ((div_counter == divisor/2) | (div_counter == divisor))
        CLK <= ~CLK;
end
```

`div_counter` incrementa continuamente tras el reset. Como la duración de `WAIT_STRB` (tiempo entre el reset y el primer `rstrb`, o entre transacciones consecutivas) depende del comportamiento del core — arranque de pipeline, CPI variable por tipo de instrucción — **no está garantizado que sea múltiplo exacto del período del divisor**. El resultado es que el primer flanco de `CLK` de una transacción puede caer en una fase arbitraria relativa al momento en que `CS_N` baja y el primer bit de `MOSI` se vuelve válido.

### Evidencia empírica

En la primera transacción tras reset, se capturó el comando `0x03` (READ) saliendo corrido 1 bit, leído por la flash como `0x06` — comando no válido, la flash no respondió (`MISO=0` sostenido). En transacciones posteriores, una vez que el conteo de ciclos coincidió con la fase correcta del divisor, el comando salió correctamente como `0x03` y las lecturas fueron válidas.

### Análisis de riesgo (por qué es más serio que un simple reintento)

Un corrimiento de 1 bit no siempre produce un patrón inofensivo. Se verificó con la propia instrucción capturada (`0xB7` = `1011 0111`, opcode `LUI` = `0110111`):

| Bit insertado | Resultado del corrimiento | Consecuencia |
|---|---|---|
| `0` | `bits[1:0] = 10` | Viola la regla RV32 (`inst[1:0]` debe ser `11`) → opcode ilegal, detectable/benigno en la mayoría de decodificadores |
| `1` | `bits[1:0] = 11`, `opcode = 0x6F` | **`JAL`** — instrucción válida pero incorrecta: el core ejecutaría un salto incondicional a una dirección arbitraria, sin ningún síntoma visible en el bus |

Es decir, dependiendo del bit que se inserte por el corrimiento, el resultado puede ir desde "inofensivo y detectable" hasta "silenciosamente destructivo para el flujo del programa".

### Impacto

- Afecta únicamente la **primera transacción tras el reset** (o tras cualquier periodo suficientemente largo en `WAIT_STRB` cuya duración no sea múltiplo del período del divisor).
- En las pruebas realizadas, el resultado observado fue benigno (opcode ilegal / `MISO=0`), pero el análisis confirma que no está garantizado que siempre lo sea.
- Aplica igualmente a `MappedSPIRAM.v`, que usa el mismo patrón de generación de `CLK` — pendiente de verificar en ese módulo.

### Mitigación para el hardware ya fabricado (no requiere volver a fabricar)

**Opción A — Instrucción sacrificable en la dirección 0:**
```asm
nop
lui   t1, 0x400
...  # programa real
```
Si el primer fetch sale corrompido, se pierde un `nop` sin consecuencia — para cuando el core llega a la segunda instrucción, la fase ya se estabilizó.

**Opción B — Margen de tiempo antes de liberar el reset del proyecto**, para permitir que el contador del divisor se asiente:
```python
tt.reset_project(True)
tt.clock_project_PWM(freq)
time.sleep(0.1)          # margen sobre tPUW de la flash y estabilización de fase
tt.reset_project(False)
```
No elimina la causa raíz (la fase sigue dependiendo del conteo de ciclos), pero reduce la ventana de riesgo práctico junto con el margen de arranque de la flash (`tPUW`).

### Fix propuesto (para el próximo tapeout)

Forzar que el generador de `CLK` y su divisor se mantengan en un estado conocido mientras la FSM está en `WAIT_STRB` (`CS_N` inactivo), y solo comiencen a correr al iniciar una transacción real:

```verilog
always @(negedge clk) begin
    if (!reset || state == WAIT_STRB) begin
        div_counter <= 0;
        CLK         <= 0;
    end
    else if (state == SEND || state == RECEIVE) begin
        if ((div_counter == divisor/2) | (div_counter == divisor))
            CLK <= ~CLK;
        div_counter <= (div_counter == divisor) ? 0 : div_counter + 1;
    end
end
```

Con esto, cada transacción arranca siempre en la misma fase (`div_counter=0`, `CLK=0`), sin importar cuántos ciclos de `clk_sys` transcurrieron desde el reset o desde la transacción anterior.

### Verificación recomendada tras el fix

Simulación dirigida variando artificialmente la duración de `WAIT_STRB` (ej. insertando distintos números de ciclos de espera antes de cada `rstrb`) y confirmando que el primer bit de `MOSI` en `SEND` siempre corresponde al MSB de `0x03`, independientemente de esa duración.

---

## Bug 6 — Instrucciones de carga (`lbu`/`lw`) fallan sistemáticamente al leer desde flash, independiente de la dirección y de la frecuencia de `clk_sys`

### Evidencia empírica

Se probaron múltiples firmwares en silicio real (SKY 25b, mux 238), variando frecuencia de `clk_sys` entre ~20MHz y 27MHz:

| Firmware | Mecanismo de acceso a datos | Resultado |
|---|---|---|
| `uart_no_pointer_test.s` | Ningún `lbu`/`lw` — todos los caracteres embebidos como inmediato (`li t4,'X'`) | ✅ Transmisión correcta y repetible (limpio a 22.5MHz) |
| `calculator_stream_base.S` | `la t3,command` + `lbu` en loop | ❌ Solo `0xFF` recibido |
| `uart_multi_copy_verify.s` | `li t3,<offset>` (absoluto, sin cálculo) + `lbu`, 4 direcciones distintas | ❌ Ninguna de las 4 direcciones pasó verificación, atascado indefinidamente |
| `uart_memdump.s` | `li t3,0x00` (dirección trivial, sin ningún cálculo) + `lbu` secuencial | ❌ `0xFF` constante desde el primer byte, **en todas las frecuencias probadas** |

El caso de `uart_memdump.s` es la evidencia decisiva: `li t3,0x00` es una carga de constante trivial, sin `auipc`, sin relocación, sin ningún mecanismo vulnerable a corrupción de dirección — y aun así, **cada `lbu` posterior, sin excepción, devuelve `0xFF`**, incluyendo la dirección `0x00`, que se sabe con certeza contiene código real y válido (el propio CPU se ejecuta correctamente desde ahí en todas las pruebas que no usan `lbu`).

### Diagnóstico

El patrón descarta las hipótesis previas (cálculo de dirección corrupto, corrimiento de fase transitorio dependiente de frecuencia — Bug 2) como causa de este caso específico, por dos razones:

1. **Independencia de la dirección**: `0x00` (constante trivial) falla igual que direcciones calculadas — el problema no está en *qué* dirección se usa, sino en la operación `lbu` en sí.
2. **Independencia de la frecuencia**: a diferencia del Bug 2 (donde 22.5MHz mostró comportamiento notablemente más estable), este fallo es 100% consistente en todo el rango de frecuencias probado — descarta que sea un problema de fase que varíe con `clk_sys`.

### Confirmación adicional (prueba dirigida `test_lbu_vs_fetch.s`)

Se probaron `lbu`, `lw` y `lh` en 5 posiciones distintas del programa (0, 2, 10 y 26 instrucciones de relleno antes de cada carga), todas apuntando a la dirección trivial `0x00`. **Las 5 lecturas, con los 3 tipos de instrucción, devolvieron `0xFF` sin excepción**, en múltiples repeticiones del ciclo completo. Esto descarta que exista alguna posición/fase donde la carga funcione — a diferencia del Bug 2 (fetch de instrucciones), que sí mostró sensibilidad a la frecuencia de `clk_sys` y a la posición en el programa, ninguna combinación probada libró a las instrucciones de carga del fallo. Confirma que el bug aplica a **toda la familia de instrucciones LOAD** (`lb`/`lbu`/`lh`/`lhu`/`lw`), no solo a `lbu`.

**Repetición a 22.5MHz** (frecuencia confirmada estable para fetch de instrucciones, ver Bug 2): los marcadores `A B C D E` (fetches de `li t4,'X'`) llegaron **perfectamente exactos** (`41 42 43 44 45`, sin ningún corrimiento), confirmando que el sistema opera en condiciones óptimas para el fetch. **Aun así, las 5 lecturas de datos siguieron devolviendo `0xFF` sin excepción.** Esto aísla definitivamente el Bug 6 como un mecanismo independiente del Bug 2: no es una manifestación adicional de fase transitoria (que en esta frecuencia ya no afecta al fetch), sino un fallo categórico y propio de las instrucciones de carga, presente incluso en el punto de operación donde el resto del sistema funciona sin errores.

La hipótesis de trabajo es que existe un desfase de ciclos **fijo** (determinado por las etapas internas de decodificación/ejecución de `femtorv32_quark` entre el fetch de la instrucción `lbu` y el disparo de su transacción de carga de dato) que cae sistemáticamente en una fase incorrecta relativa al período del divisor de `CLK` (`divisor=2` en `MappedSPIFlash`) — y como ambos son *cuentas de ciclos*, no tiempos absolutos, esa relación de fase **no cambia al variar `clk_sys`**, a diferencia del Bug 2 (donde la fase depende del historial de timing acumulado desde el reset, sí sensible a la frecuencia).

Pendiente confirmar con simulación dirigida (ver más abajo) si el mecanismo exacto es este, o si hay una causa adicional en cómo `femtorv32_quark` secuencia sus propias transacciones de `LOAD` frente al fetch normal.

### Impacto

- **Bloqueante para cualquier programa que necesite leer datos desde flash** (`.rodata`, tablas, strings) — el firmware queda forzado a usar solo inmediatos embebidos en código, lo cual es viable para casos simples pero inviable para datos grandes o generados en tiempo de ejecución.
- No confirmado aún si aplica igual a `lw`/`lh`, ni si aplica también a lecturas desde `MappedSPIRAM` (pendiente de prueba, ver más abajo) — de ser exclusivo de la flash, movería el mismo dato a través de la RAM SPI podría ser un workaround parcial (sujeto a los bugs ya documentados de `MappedSPIRAM`, Bug 3/4).

### Workaround confirmado

Evitar toda instrucción de carga (`lbu`/`lw`/`lh`) desde la flash. Cualquier dato necesario debe ir como inmediato directo en el código (`li`), replicado tantas veces como sea necesario en el programa — como en `uart_no_pointer_test.s`.

### Prueba dirigida para confirmar la hipótesis

Ver `test_lbu_vs_fetch.s` — mide de forma controlada si el problema es específico de `lbu`/`lw`, o si aplica también a otras variantes (`lb`, `lh`), y si depende de la posición del `lbu` dentro del programa (para descartar que sea, en cambio, una manifestación particular del Bug 2 con una ventana de "mala fase" inusualmente ancha).

---

## Resumen para inclusión en el libro

| # | Bug | Ubicación | Severidad | Corregible en silicio actual |
|---|---|---|---|---|
| 1 | Ciclo extra en salida de `RECEIVE` | `MappedSPIFlash.v` (y revisar `MappedSPIRAM.v`) | Baja (rendimiento, no corrección) | No aplica (no afecta funcionalidad) |
| 2 | `CLK` no sincronizado con `CS_N` tras reset | `MappedSPIFlash.v` (y revisar `MappedSPIRAM.v`) | Media-Alta (riesgo de ejecución incorrecta silenciosa) | Sí, con NOP sacrificable o delay de reset |
| 6 | `lb`/`lbu`/`lh`/`lhu`/`lw` fallan sistemáticamente leyendo desde flash, independiente de dirección, posición y frecuencia | `MappedSPIFlash.v` / interacción con `femtorv32_quark` | Alta (bloqueante para cualquier acceso a datos) | Sí, evitando instrucciones de carga (usar solo inmediatos) |

Los tres bugs son ejemplos didácticamente útiles del riesgo de romper la simetría de FSMs generadas por composición manual de bloques ASM — coherente con la metodología top-down (flowchart → ASM chart → RTL → prueba en hardware) del libro: el bug 1 es visible en el ASM chart si se dibuja con cuidado (falta de anticipación en la rama de salida), el bug 2 ilustra por qué un generador de reloj de periférico debe estar *gateado* por el propio estado de la FSM que lo consume, y el bug 6 muestra cómo un desfase de ciclos fijo entre dos tipos de transacción de bus (fetch vs. load) puede producir un fallo sistemático e independiente de la frecuencia, distinto en naturaleza a un problema de fase transitoria.
