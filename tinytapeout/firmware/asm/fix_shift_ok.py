#!/usr/bin/env python3
"""
Compensa un corrimiento de bit fijo y reproducible en el flujo de datos
leido desde la flash SPI, pre-desplazando el contenido del binario antes
de programarlo.

Uso:
    python3 fix_shift.py firmware.bin firmware_shifted.bin --bits 1 --dir left
    python3 fix_shift.py firmware.bin firmware_shifted.bin --bits 1 --dir right
"""

import argparse

def bytes_to_bitstream(data: bytes) -> str:
    return ''.join(f'{b:08b}' for b in data)

def bitstream_to_bytes(bits: str) -> bytes:
    # rellena a múltiplo de 8 con ceros al final si hace falta
    pad = (-len(bits)) % 8
    bits = bits + ('0' * pad)
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def shift_stream(data: bytes, n_bits: int, direction: str, fill_bit: str = '0') -> bytes:
    bits = bytes_to_bitstream(data)
    if direction == 'left':
        # descarta n_bits del inicio, rellena al final
        shifted = bits[n_bits:] + (fill_bit * n_bits)
    elif direction == 'right':
        # inserta n_bits al inicio, descarta n_bits del final
        shifted = (fill_bit * n_bits) + bits[:-n_bits]
    else:
        raise ValueError("direction debe ser 'left' o 'right'")
    return bitstream_to_bytes(shifted)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', help='firmware.bin original')
    ap.add_argument('output', help='archivo de salida pre-desplazado')
    ap.add_argument('--bits', type=int, default=1, help='cantidad de bits a corregir (default 1)')
    ap.add_argument('--dir', choices=['left', 'right'], default='left',
                     help='sentido del corrimiento observado en el analizador')
    ap.add_argument('--fill', choices=['0', '1'], default='0',
                     help='bit de relleno insertado (default 0)')
    args = ap.parse_args()

    with open(args.input, 'rb') as f:
        data = f.read()

    corrected = shift_stream(data, args.bits, args.dir, args.fill)

    with open(args.output, 'wb') as f:
        f.write(corrected)

    print(f"Entrada:  {len(data)} bytes")
    print(f"Salida:   {len(corrected)} bytes")
    print(f"Corrimiento aplicado: {args.bits} bit(s) hacia la {args.dir}, relleno={args.fill}")
    print(f"Primeros 8 bytes original:  {data[:8].hex(' ')}")
    print(f"Primeros 8 bytes corregido: {corrected[:8].hex(' ')}")

if __name__ == '__main__':
    main()