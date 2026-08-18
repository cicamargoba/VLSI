# *************************************************
# IMPORTANTE PARA PODER COMPILAR ESTE EJEMPLO:
# En el archivo:litex/litex/soc/software/common.mak
# cambiar de:
# ifeq ($(LTO), 1)
# COMMONFLAGS += -flto
# endif
# a:
# COMMONFLAGS += -flto
# *************************************************
#OBJECTS =  bin_to_bcd.o mult.o div.o wait.o putchar.o getchar.o calculator.o #hello.o 
#OBJECTS =  blink.o 
OBJECTS =  uart_full_demo.o
CROSS   = riscv32-unknown-elf
CC      = $(CROSS)-gcc
AS      = $(CROSS)-as
LD      = $(CROSS)-ld
OBJCOPY = $(CROSS)-objcopy
OBJDUMP = $(CROSS)-objdump
AFLAGS  = -march=rv32i -mabi=ilp32

all: firmware.hex

firmware.bin: firmware.elf
	$(OBJCOPY) -O verilog $< firmware_flash.hex
	$(OBJCOPY) -O ihex $< firmware_flash_intel.hex
	$(OBJCOPY) -O binary $< $@
	chmod -x $@
	python3 fix_shift.py firmware.bin firmware_shifted.bin --bits 1 --dir right --fill 0
	dd if=/dev/zero bs=1M count=4 2>/dev/null | tr '\000' '\377' > firmware_full.bin
	dd if=firmware_shifted.bin of=firmware_full.bin conv=notrunc bs=1 2>/dev/null
	sudo flashrom -p ch341a_spi -w firmware_full.bin
# sudo flashrom -p ch341a_spi -r test_read.bin

firmware.elf: $(OBJECTS) 
	$(LD) $(LDFLAGS) -T bram.ld  -m elf32lriscv -nostdlib -Map firmware.map -N -o $@ $(OBJECTS)
	chmod -x $@
	
firmware.hex: firmware.elf firmware.lst firmware.bin
	../firmware_words_src/firmware_words firmware.elf -ram 16384 -max_addr 16384  -out firmware.hex
	cp firmware.hex ../../
	cp firmware_flash.hex ../../

firmware.lst: firmware.elf
	$(OBJDUMP) -h -S $< > $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< 
%.o: %.S
	$(AS) $(AFLAGS) -c $< -o $@
clean:
	rm -rf  $(OBJECTS) *.elf *.bin .*~ *~ *.map *.d *.hex *.o *.lst
.PHONY: clean


#export PATH=$PATH:/home/carlos/Embedded/litex_work/learn-fpga/FemtoRV/FIRMWARE/TOOLCHAIN/riscv64-unknown-elf-gcc-8.3.0-2020.04.0-x86_64-linux-ubuntu14/bin/
