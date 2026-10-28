.include "femtorv32.inc"

.text
.global _start
.type _start, @function

_start:
.option push
.option norelax
     li   gp,IO_BASE
     li   sp,IO_HW_CONFIG_RAM + 0x1000
     call main
     tail exit


