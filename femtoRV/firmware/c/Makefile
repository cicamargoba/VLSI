# Objects to build
OBJECTS = hello.o 

# Cross compiler prefix
CROSS   = riscv64-unknown-elf
CC      = $(CROSS)-gcc
AS      = $(CROSS)-as
OBJDUMP = $(CROSS)-objdump
OBJCOPY = $(CROSS)-objcopy

# Paths and libs
LIB_DIR = -Llibfemtorv
LIBS    = -lfemtorv -lgcc   # no -lc / -lm (baremetal)

# Flags
AFLAGS  = -march=rv32i -mabi=ilp32
CFLAGS  = -Ilibfemtorv/include -Ilibfemtoc/include \
          -fno-pic -march=rv32i -mabi=ilp32 \
          -fno-stack-protector -w

# Linker flags (forwarded to ld)
LDFLAGS = -nostdlib \
          -Wl,-T,linker.ld \
          -Wl,--no-relax \
          -Wl,--print-memory-usage

# Default target
all: firmware.hex

# Compile C
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Compile ASM
%.o: %.S
	$(AS) $(AFLAGS) -c $< -o $@

# Link ELF
firmware.elf: $(OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(OBJECTS) $(LIB_DIR) $(LIBS)
	chmod -x $@

# Dump assembly
firmware.lst: firmware.elf
	$(OBJDUMP) -h -S $< > $@

# Convert ELF → HEX (your tool)
firmware.hex: firmware.elf firmware.lst
	../firmware_words_src/firmware_words firmware.elf -ram 8192 -max_addr 8192 -out firmware.hex
	cp firmware.hex ../../rtl

# Optional binary (raw)
%.bin: %.elf
	$(OBJCOPY) -O binary $< $@
	chmod -x $@

# Cleanup
clean:
	rm -rf $(OBJECTS) *.elf *.bin *.map *.hex *.lst *~ .*~
.PHONY: clean
