.section .text
.global _start
_start:
    li    t3, 0x00

loop:
    lbu   t4, 0(t3)
    j     loop