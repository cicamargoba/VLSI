.equ DPRAM_BASE, 0x450000  
.section .text
.globl start 
.globl blinker
.globl put_hello

calculator:
#   li   gp,UART_BASE
#   li   gp, DPRAM_BASE
   li   sp,0x10040

loopM:
    
    li   t0, 22
	li   t1, 66

	la   a0, command
	call putstring

	# Receive first decimal number	
	call getchar    # 
	call putchar    # echo
	addi a0, a0, -0x30
	mv   a2, a0     # first digit operand

	# Receive operator	
	call getchar    # 
	call putchar    # echo	
    mv   a3, a0     # a3 = operator
	
	# Receive second decimal number	
	call getchar    # 
	call putchar    # echo
	addi a0, a0, -0x30
	mv   t0, a0
	

	la   a0, result
	call putstring
	


	mv   a1,t0
	mv   a0,a2
		
	li   t0, '*'
	bne  t0, a3, divide
#	call mult
	call mult_hw
	j    print_res
divide:
	call div
#	call div_hw

print_res:		
	call bin_to_bcd
	j    loopM
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
	.asciz "In\n"
operator:
	.asciz "Op\n"
result:
	.asciz "R=\n"

#https://luplab.gitlab.io/rvcodecjs/