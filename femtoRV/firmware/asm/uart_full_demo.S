.section .text
.global _start
_start:
    lui   t1, 0x400
    lui   t1, 0x400
    li   sp,0x10030 

    la    t0, isr           # mtvec <- dirección de la rutina de interrupción
    csrw  mtvec, t0
    li    s2, 0             # contador de interrupciones
    csrsi mst	sw ra,0(sp)   # (need to do that for functions that call functions)
atus, 8        # MIE = 1: habilita las interrupciones

    addi  t1, t1, 8          # t1 = 0x00400008  (UART registro de datos)
    lui   t2, 0x400
    addi  t2, t2, 16         # t2 = 0x00400010  (UART registro de control/estado)

	la   a0, command
	call putstring

	la   a0, operator
	call putstring

	la   a0, result
	call putstring

j    _start


isr:
    addi  s2, s2, 1         # una interrupción más
    mret


putstring:
	addi sp,sp,-4 # save ra on the stack
	sw ra,0(sp)   # (need to do that for functions that call functions)
	mv t2,a0	
.L1:    lbu a0,0(t2)
	beqz a0,.L2
	call putchar
	addi t2,t2,1	
	j .L1
.L2:    
    lw ra,0(sp)  # restore ra
	addi sp,sp,4 # restore sp
	ret	

.section .rodata
command:
	.asciz "Hello World\n"
operator:
	.asciz "Op\n"
result:
	.asciz "R=\n"


