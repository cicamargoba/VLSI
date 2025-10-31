.equ DPRAM_BASE, 0x450000  
.section .text
.globl start 
.globl blinker
.globl put_hello

calculator:
#   li   gp,UART_BASE
#   li   gp, DPRAM_BASE
   li   sp,0x10040
   li   sp,0x10040
loopM:
    
    li   t0, 22
	li   t1, 66

    li   a0, 64
	call putchar
	li   a0, 10
	call putchar

echo:
    li   a0, 10
	call putchar
	call getchar    # 
	call putchar    # echo

    j echo







putstring:
	addi sp,sp,-4 # save ra on the stack
	sw ra,0(sp)   # (need to do that for functions that call functions)
	mv t2,a0	
.L1:    lbu a0,0(t2)
	beqz a0,.L2
	call putchar
	addi t2,t2,1	
	j .L1
.L2:    lw ra,0(sp)  # restore ra
	addi sp,sp,4 # restore sp
	ret	

.section .data
command:
	.asciz "\r\nIN\n"
operator:
	.asciz "Op\n"
result:
	.asciz "R=\n"

#https://luplab.gitlab.io/rvcodecjs/