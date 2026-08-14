.section .text
.global _start
_start:
    lui   ra, 0x400
    addi  ra, ra, 16

loop:
    li    sp, 4
    li    gp, 0
    lui   t0, 15
    addi  t0, t0, 1060

    sw    sp, 0(ra)
delay1:
    mv    tp, t0
delay1_loop:
    addi  tp, tp, -1
    bnez  tp, delay1_loop

    sw    gp, 0(ra)
delay2:
    mv    tp, t0
delay2_loop:
    addi  tp, tp, -1
    bnez  tp, delay2_loop

    j     loop