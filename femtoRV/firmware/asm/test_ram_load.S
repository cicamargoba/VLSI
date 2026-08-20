.section .text
.global _start
_start:
    lui   t1, 0x400
    addi  t1, t1, 8          # t1 = 0x00400008  (UART TX data)
    lui   t2, 0x400
    addi  t2, t2, 16         # t2 = 0x00400010  (UART TX ctrl/status)
    lui   t0, 0x10             # t0 = 0x00010000 (base RAM SPI)

    # ---- escribe 4 palabras (16 bytes) conocidas a la RAM ----
    li    t3, 0x6C6C6548        # "Hell" en little-endian
    sw    t3, 0(t0)
    li    t3, 0x6F57206F        # "o Wo"
    sw    t3, 4(t0)
    li    t3, 0x00646C72        # "rld\0"
    sw    t3, 8(t0)

restart:
    li    t3, 0x00               # offset dentro de la RAM

send_loop:
    add   t4, t0, t3
    lbu   t4, 0(t4)             # lectura desde RAM, no flash
    beqz  t4, restart

wait_tx:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx

    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    addi  t3, t3, 1
    j     send_loop
