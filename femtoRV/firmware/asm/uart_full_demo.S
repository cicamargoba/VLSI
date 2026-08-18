.section .text
.global _start
_start:
    lui   t1, 0x400
    addi  t1, t1, 8          # t1 = 0x00400008  (UART registro de datos)
    lui   t2, 0x400
    addi  t2, t2, 16         # t2 = 0x00400010  (UART registro de control/estado)

# ---------------------------------------------------------------
# 1) Envio del string, caracteres como inmediatos (sin lbu/lw a flash)
# ---------------------------------------------------------------
    li    t4, 'H'
wait_txs0:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs0
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'e'
wait_txs1:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs1
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'l'
wait_txs2:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs2
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'l'
wait_txs3:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs3
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'o'
wait_txs4:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs4
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, ' '
wait_txs5:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs5
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'W'
wait_txs6:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs6
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'o'
wait_txs7:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs7
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'r'
wait_txs8:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs8
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'l'
wait_txs9:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs9
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'd'
wait_txs10:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs10
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, ' '
wait_txs11:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs11
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'f'
wait_txs12:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs12
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'r'
wait_txs13:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs13
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'o'
wait_txs14:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs14
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'm'
wait_txs15:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs15
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, ' '
wait_txs16:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs16
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'f'
wait_txs17:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs17
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'e'
wait_txs18:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs18
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'm'
wait_txs19:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs19
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 't'
wait_txs20:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs20
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'o'
wait_txs21:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs21
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, ' '
wait_txs22:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs22
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'U'
wait_txs23:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs23
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 'N'
wait_txs24:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs24
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 0x0A
wait_txs25:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs25
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    li    t4, 0x0D
wait_txs26:
    lw    t5, 0(t2)
    andi  t5, t5, 0x200
    bnez  t5, wait_txs26
    sw    t4, 0(t1)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

# ---------------------------------------------------------------
# 2) Blink del LED, 2 veces
# ---------------------------------------------------------------
    li    t0, 2
blink_loop:
    li    t6, 0x04
    sw    t6, 0(t2)
    li    t5, 33750
blink_delay1:
    addi  t5, t5, -1
    bnez  t5, blink_delay1

    li    t6, 0x00
    sw    t6, 0(t2)
    li    t5, 33750
blink_delay2:
    addi  t5, t5, -1
    bnez  t5, blink_delay2

    addi  t0, t0, -1
    bnez  t0, blink_loop

# ---------------------------------------------------------------
# 3) Loop de eco: recibe por UART y retransmite
# ---------------------------------------------------------------
echo_loop:
wait_rx:
    lw    t3, 0(t2)
    andi  t3, t3, 0x100        # bit8 = rx_avail
    beqz  t3, wait_rx

    lw    t4, 0(t1)             # lee el byte recibido
    andi  t4, t4, 0xFF

    li    t6, 0x01               # bit0 = rx_ack
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

wait_txe:
    lw    t3, 0(t2)
    andi  t3, t3, 0x200         # bit9 = tx_busy
    bnez  t3, wait_txe

    sw    t4, 0(t1)              # retransmite el mismo byte (eco)
    li    t6, 0x08
    sw    t6, 0(t2)
    li    t6, 0x00
    sw    t6, 0(t2)

    j     echo_loop
