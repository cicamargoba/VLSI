.section .text
.global _start
_start:
    lui   t1, 0x400
    addi  t1, t1, 8
    lui   t2, 0x400
    addi  t2, t2, 16

restart:
    li    t4, 'H'
wait_tx0:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx0
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'e'
wait_tx1:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx1
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'l'
wait_tx2:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx2
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'l'
wait_tx3:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx3
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'o'
wait_tx4:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx4
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, ' '
wait_tx5:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx5
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'W'
wait_tx6:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx6
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'o'
wait_tx7:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx7
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'r'
wait_tx8:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx8
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'l'
wait_tx9:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx9
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'd'
wait_tx10:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx10
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, ' '
wait_tx11:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx11
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'f'
wait_tx12:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx12
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'r'
wait_tx13:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx13
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'o'
wait_tx14:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx14
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'm'
wait_tx15:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx15
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, ' '
wait_tx16:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx16
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'f'
wait_tx17:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx17
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'e'
wait_tx18:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx18
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'm'
wait_tx19:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx19
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 't'
wait_tx20:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx20
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'o'
wait_tx21:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx21
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, ' '
wait_tx22:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx22
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'U'
wait_tx23:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx23
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'N'
wait_tx24:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx24
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 0x0A
wait_tx25:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx25
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 0x0D
wait_tx26:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx26
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    j     restart