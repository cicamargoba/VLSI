/* crt0.S -- arranque para el silicio femto_UN (commit f15fccd)
 *
 * Reglas de silicio aplicadas aquí:
 *  R1  La instrucción de la dirección 0 NUNCA se ejecuta (la 1ª lectura tras reset se pierde, DEF-R1):
 *      se coloca un NOP sacrificial.
 *  R2  Los registros arrancan con basura: se ponen todos a 0 antes de usarlos.
 *  R3  La pila va en la SPI RAM (0x10000..0x1FFFF), sólo con accesos de palabra (lw/sw).
 */
    .section .init, "ax"
    .globl _start
_start:
    nop                         /* R1: dirección 0, se pierde */
    li   x1,  0                 /* R2 */
    li   x3,  0
    li   x4,  0
    li   x5,  0
    li   x6,  0
    li   x7,  0
    li   x8,  0
    li   x9,  0
    li   x10, 0
    li   x11, 0
    li   x12, 0
    li   x13, 0
    li   x14, 0
    li   x15, 0
    li   x16, 0
    li   x17, 0
    li   x18, 0
    li   x19, 0
    li   x20, 0
    li   x21, 0
    li   x22, 0
    li   x23, 0
    li   x24, 0
    li   x25, 0
    li   x26, 0
    li   x27, 0
    li   x28, 0
    li   x29, 0
    li   x30, 0
    li   x31, 0
    lui  sp, 0x20               /* R3: sp = 0x20000 (fin de la SPI RAM) */
    addi sp, sp, -16
    call main
1:  j    1b
