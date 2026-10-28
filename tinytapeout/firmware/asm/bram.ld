MEMORY
{
   BRAM (RWX) : ORIGIN = 0x0000, LENGTH = 0x4000  /* 16kB */
}

SECTIONS
{
    everything :
    {
        . = ALIGN(4);
        *(.text)
        *(.rodata)
        *(.rodata.*)
    } >BRAM

    /DISCARD/ :
    {
        *(.riscv.attributes)
        *(.comment)
        *(.symtab)
        *(.strtab)
        *(.shstrtab)
        *(.eh_frame)
    }
}
