.equ DPRAM_BASE, 0x450000  
.section .text
.globl start 
.globl blinker
.globl put_hello

calculator:
   li   sp,0x10030
   li   sp,0x10030    

    
    li   t0, 300 #12C
	sw   t0,0(sp)
	sw   t0,4(sp)
	sw   t0,8(sp)
	sw   t0,12(sp)

	li   t1, 600 #258
    sw   t1,0(sp) 
    lw   a0,0(sp)

	li   t1, 700 #2BC
    sw   t1,0(sp) 
    lw   a0,0(sp)


	li   t1, 500 #1F4
    sw   t1,0(sp) 
    lw   a0,0(sp)
loopM:
	la   a0, command
	call putstring

	# Receive first digit decimal number	
	call getchar    # 
	call putchar    # echo
	addi a2, a0, -0x30   #a2 first op
	
	# Receive operator	
	call getchar    # 
	call putchar    # echo	
    mv   a3, a0     # a3 = operator
	
	# Receive second  digit decimal number	
	call getchar    # 
	call putchar    # echo
	addi t0, a0, -0x30  #t0 Second op

	mv   a1,t0
	mv   a0,a2

	call mult
	
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
.L2:    
    lw ra,0(sp)  # restore ra
	addi sp,sp,4 # restore sp
	ret	

.section .data
command:
	.asciz "IN\n"
operator:
	.asciz "Op\n"
result:
	.asciz "R=\n"

#https://luplab.gitlab.io/rvcodecjs/