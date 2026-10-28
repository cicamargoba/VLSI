/* hello.c -- C sobre femto_UN respetando las reglas de silicio
  *   - sin variables globales (no hay .data/.bss) y SIN pila útil: todo el estado vive en registros
 *   - la SPI RAM sólo con ram_store/ram_load (palabras de 31 bits, máscara del bit 31, DEF-S2)
 *   - sin M (no hay mul/div): se usan sumas y restas
 *   - constantes (cadenas) en la flash, leídas con lbu (la flash sí admite todos los anchos)
 */
#include <stdint.h>
#define UART_DATA (*(volatile uint32_t *)0x400008)
#define UART_CTRL (*(volatile uint32_t *)0x400010)
#define LED_BIT   0x4

static void putc_(char c) {
    while (UART_CTRL & 0x200) ;      /* tx_busy */
    UART_DATA = (uint32_t)c;
    UART_CTRL = 0x8;                  /* tx_wr = 1 */
    UART_CTRL = 0x0;                  /* hay que bajarlo: es un nivel, no un pulso */
}
static void puts_(const char *s) { while (*s) putc_(*s++); }
static void puthex(uint32_t v, int n) {
    for (int i = n - 1; i >= 0; i--) {
        uint32_t d = (v >> (4 * i)) & 15;
        putc_(d < 10 ? '0' + d : 'A' + d - 10);
    }
}
/* SIN recursión: GCC guardaría registros en la pila (SPI RAM) y al restaurarlos el bit 31 llega aleatorio (DEF-S2). */
static uint32_t fib(uint32_t n) { uint32_t a = 0, b = 1; while (n--) { uint32_t t = a + b; a = b; b = t; } return a; }

/* Acceso EXPLÍCITO a la SPI RAM: sólo lw/sw, valores de 31 bits y máscara del bit 31 tras cada lectura. */
#define RAM ((volatile uint32_t *)0x10000)
static inline void     ram_store(uint32_t i, uint32_t v) { RAM[i] = v & 0x7FFFFFFF; }
static inline uint32_t ram_load(uint32_t i)               { return RAM[i] & 0x7FFFFFFF; }

int main(void) {
    puts_("C on femto_UN\n");
    puts_("fib(10)=");  puthex(fib(10), 2); putc_('\n');
    for (uint32_t i = 0; i < 10; i++) ram_store(i, i * i);          /* tabla de cuadrados en la SPI RAM */
    uint32_t sum = 0; for (uint32_t i = 0; i < 10; i++) sum += ram_load(i);
    puts_("ram31sum="); puthex(sum, 4); putc_('\n');                /* 285 = 0x011D */
    uint32_t primes = 0;                                   /* primos < 50 por división repetida */
    for (uint32_t n = 2; n < 50; n++) {
        uint32_t is_p = 1;
        for (uint32_t d = 2; d * d <= n; d++) {            /* d*d con M ausente -> __mulsi3 */
            uint32_t m = n; while (m >= d) m -= d;
            if (m == 0) { is_p = 0; break; }
        }
        primes += is_p;
    }
    puts_("primes<50="); puthex(primes, 2); putc_('\n');
    UART_CTRL = LED_BIT;                                   /* enciende el LED */
    for (;;) ;
}
