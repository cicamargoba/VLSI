.section .text
.global _start
_start:
    lui   t1, 0x400
    addi  t1, t1, 8          # t1 = 0x00400008  (UART TX data)
    lui   t2, 0x400
    addi  t2, t2, 16         # t2 = 0x00400010  (UART TX ctrl/status)

    la    t3, packet_data
    la    t4, packet_data_end

send_loop:
    beq   t3, t4, halt

wait_tx:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_tx

    lbu   t5, 0(t3)
    sw    t5, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    addi  t3, t3, 1
    j     send_loop

halt:
    j     halt

.section .rodata
packet_data:
    .byte 0xAA,0x55,0x04,0x00,0x00,0x10,0x01,0x11,0x55,0xAA
    .byte 0xAA,0x55,0x21,0x00,0x00,0x40,0x01,0x50,0x00,0x00,0x00,0x18
    .ascii "Hello World from femtoUN"
    .byte 0x77,0x55,0xAA
packet_data_end:

