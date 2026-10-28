 .section .text
.global _start
_start:
    nop                     
    lui   t1, 0x400
    addi  t1, t1, 8            # t1 = 0x00400008 (UART TX data)
    lui   t2, 0x400
    addi  t2, t2, 16           # t2 = 0x00400010 (UART TX ctrl/status)
    lui   t0, 0x10             # t0 = 0x00010000 (Base RAM SPI)

    # ---- Escribe 3 palabras (12 bytes) a la RAM SPI ----
    li    t3, 0x6C6C6548        # "Hell" en little-endian
    sw    t3, 0(t0)
    li    t3, 0x6F57206F        # "o Wo"
    sw    t3, 4(t0)
    li    t3, 0x00646C72        # "rld\0"
    sw    t3, 8(t0)

restart:
    li    s0, 0                 # Offset de palabra dentro de la RAM (0, 4, 8)

word_loop:
    add   t4, t0, s0
    lw    s1, 0(t4)             # Lectura de palabra completa (32 bits) desde RAM SPI
    li    s2, 4                 # Contador: 4 bytes por palabra

byte_loop:
    andi  t4, s1, 0xFF          # Extrae el byte menos significativo
    beqz  t4, restart           # Si es '\0', reinicia el ciclo ("Hello World")

wait_tx:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200         # Bit 9: tx_busy
    bnez  t5, wait_tx

    sw    t4, 0(t1)             # Escribe dato en UART DATA
    li    t6, 0x08
    sw    t6, 0(t2)             # Pulso tx_wr = 1
    li    t6, 0x00
    sw    t6, 0(t2)             # tx_wr = 0

    srli  s1, s1, 8             # Desplaza al siguiente byte de la palabra
    addi  s2, s2, -1
    bnez  s2, byte_loop

    addi  s0, s0, 4             # Avanza a la siguiente palabra
    j     word_loop