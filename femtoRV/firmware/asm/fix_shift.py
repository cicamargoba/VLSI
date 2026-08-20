#!/usr/bin/env python3
"""
Compensa un corrimiento de bit fijo y reproducible en el flujo de datos
leido desde la flash SPI, pre-desplazando el contenido del binario antes
de programarlo.

El corrimiento base (--bits/--dir/--fill) se aplica a TODO el archivo.
Si se especifica --loads-only <firmware.elf>, ademas se aplica un
corrimiento ADICIONAL (--extra-bits/--extra-dir/--extra-fill) solo sobre
las instrucciones LOAD (lb/lbu/lh/lhu/lw), por encima del corrimiento
base que ya recibieron junto con el resto del archivo.

Uso (comportamiento original, solo corrimiento base a todo el archivo):
    python3 fix_shift.py firmware.bin firmware_shifted.bin --bits 1 --dir left

Uso (corrimiento base a todo + corrimiento extra en los LOAD):
    python3 fix_shift.py firmware.bin firmware_shifted.bin --bits 1 --dir left \
        --loads-only firmware.elf --extra-bits 1 --extra-dir left
"""

import argparse
import re
import subprocess
import sys

LOAD_MNEMONICS = ("lb", "lbu", "lh", "lhu", "lw")


def bytes_to_bitstream(data: bytes) -> str:
    return ''.join(f'{b:08b}' for b in data)


def bitstream_to_bytes(bits: str) -> bytes:
    pad = (-len(bits)) % 8
    bits = bits + ('0' * pad)
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def shift_stream(data: bytes, n_bits: int, direction: str, fill_bit: str = '0') -> bytes:
    bits = bytes_to_bitstream(data)
    if direction == 'left':
        shifted = bits[n_bits:] + (fill_bit * n_bits)
    elif direction == 'right':
        shifted = (fill_bit * n_bits) + bits[:-n_bits]
    else:
        raise ValueError("direction debe ser 'left' o 'right'")
    return bitstream_to_bytes(shifted)


def find_load_offsets(elf_path, objdump="riscv32-unknown-elf-objdump"):
    for tool in (objdump, "riscv64-unknown-elf-objdump"):
        try:
            result = subprocess.run(
                [tool, "-d", elf_path],
                capture_output=True, text=True, check=True
            )
            break
        except FileNotFoundError:
            continue
    else:
        print("ERROR: no se encontro objdump de riscv32/riscv64 en el PATH",
              file=sys.stderr)
        sys.exit(1)

    offsets = []
    line_re = re.compile(r"^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]+)\s+(\S+)")
    for line in result.stdout.splitlines():
        m = line_re.match(line)
        if not m:
            continue
        addr_hex, word_hex, mnemonic = m.groups()
        if mnemonic in LOAD_MNEMONICS:
            offsets.append(int(addr_hex, 16))
    return offsets


def apply_extra_shift_on_loads(data: bytearray, extra_bits: int, extra_dir: str,
                                extra_fill: str, elf_path: str, objdump: str):
    """
    Aplica un corrimiento ADICIONAL, por encima del corrimiento base ya
    aplicado a todo el archivo, unicamente sobre los 4 bytes de cada
    instruccion LOAD localizada via objdump.
    """
    offsets = find_load_offsets(elf_path, objdump)
    for addr in offsets:
        if addr + 4 > len(data):
            print(f"  offset 0x{addr:04X}: fuera de rango, se omite")
            continue
        word = bytes(data[addr:addr + 4])
        extra_shifted = shift_stream(word, extra_bits, extra_dir, extra_fill)
        data[addr:addr + 4] = extra_shifted
        print(f"  LOAD offset 0x{addr:04X}: {word.hex(' ')} "
              f"-> (+corrimiento extra) -> {extra_shifted.hex(' ')}")
    print(f"Instrucciones LOAD con corrimiento adicional: {len(offsets)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input', help='firmware.bin original')
    ap.add_argument('output', help='archivo de salida pre-desplazado')
    ap.add_argument('--bits', type=int, default=1,
                     help='corrimiento BASE, aplicado a todo el archivo (default 1)')
    ap.add_argument('--dir', choices=['left', 'right'], default='left',
                     help='sentido del corrimiento base')
    ap.add_argument('--fill', choices=['0', '1'], default='0',
                     help='bit de relleno del corrimiento base (default 0)')

    ap.add_argument('--loads-only', metavar='FIRMWARE_ELF', default=None,
                     help='si se especifica, ademas del corrimiento base '
                          '(aplicado a TODO el archivo), se aplica un '
                          'corrimiento EXTRA solo sobre las instrucciones '
                          'LOAD localizadas en este .elf.')
    ap.add_argument('--extra-bits', type=int, default=1,
                     help='corrimiento ADICIONAL solo para LOAD (default 1)')
    ap.add_argument('--extra-dir', choices=['left', 'right'], default='left',
                     help='sentido del corrimiento adicional para LOAD')
    ap.add_argument('--extra-fill', choices=['0', '1'], default='0',
                     help='bit de relleno del corrimiento adicional')
    ap.add_argument('--objdump', default='riscv32-unknown-elf-objdump')
    args = ap.parse_args()

    with open(args.input, 'rb') as f:
        data = f.read()

    # 1) corrimiento BASE, siempre aplicado a TODO el archivo
    corrected = bytearray(shift_stream(data, args.bits, args.dir, args.fill))

    # 2) corrimiento EXTRA, solo sobre las instrucciones LOAD, por encima del base
    if args.loads_only:
        apply_extra_shift_on_loads(
            corrected, args.extra_bits, args.extra_dir, args.extra_fill,
            args.loads_only, args.objdump
        )

    with open(args.output, 'wb') as f:
        f.write(corrected)

    print(f"Entrada:  {len(data)} bytes")
    print(f"Salida:   {len(corrected)} bytes")
    print(f"Corrimiento base: {args.bits} bit(s) hacia la {args.dir}, relleno={args.fill}")
    if args.loads_only:
        print(f"Corrimiento extra en LOAD: {args.extra_bits} bit(s) hacia la "
              f"{args.extra_dir}, relleno={args.extra_fill}")
    print(f"Primeros 8 bytes original:  {data[:8].hex(' ')}")
    print(f"Primeros 8 bytes corregido: {bytes(corrected[:8]).hex(' ')}")


if __name__ == '__main__':
    main()
