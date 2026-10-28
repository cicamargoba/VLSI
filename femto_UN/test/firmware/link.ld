/* Mapa de memoria del chip: código y constantes en la SPI flash, pila en la SPI RAM */
ENTRY(_start)
MEMORY {
    FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 64K     /* 0x0000..0xFFFF (la RAM oculta 0x10000+) */
}
SECTIONS {
    .text : { KEEP(*(.init)) *(.text*) *(.rodata*) *(.srodata*) } > FLASH
    /DISCARD/ : { *(.data*) *(.bss*) *(.sdata*) *(.sbss*) *(.comment) *(.riscv.attributes) }
}
