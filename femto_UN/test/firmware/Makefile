# Compilar firmware para femto_UN:   make   ->  hello.bin  (imagen para la flash, dirección 0)
CROSS ?= riscv64-unknown-elf-
CFLAGS = -march=rv32i -mabi=ilp32 -O2 -ffreestanding -fno-builtin -fno-stack-protector -fomit-frame-pointer -Wall
LDFLAGS = -nostdlib -T link.ld -Wl,--gc-sections
hello.bin: hello.elf ; $(CROSS)objcopy -O binary $< $@
hello.elf: crt0.S hello.c link.ld ; $(CROSS)gcc $(CFLAGS) $(LDFLAGS) crt0.S hello.c -o $@ -lgcc
dis: hello.elf ; $(CROSS)objdump -d $<
clean: ; rm -f *.elf *.bin
