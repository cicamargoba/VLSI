import sys
import re

def convert_ngspice_to_xyce(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    out_lines = []
    in_control = False

    for line in lines:
        stripped = line.strip()

        # Skip ngspice control blocks
        if stripped.lower().startswith('.control'):
            in_control = True
            continue
        if stripped.lower().startswith('.endc'):
            in_control = False
            continue
        if in_control:
            # Example: convert `plot clk done` -> .print tran v(clk) v(done)
            if stripped.lower().startswith('plot'):
                tokens = stripped.split()[1:]
                signals = " ".join(f"v({sig})" for sig in tokens)
                out_lines.append(f".print tran {signals}\n")
            continue

        # Skip ngspice-only options
        if re.search(r'\.options.*post', stripped.lower()):
            continue

        # Otherwise keep line
        out_lines.append(line)

    with open(output_file, 'w') as f:
        f.writelines(out_lines)

    print(f"Converted netlist written to {output_file}")

# Usage: python convert.py input.cir output.cir
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert.py input.cir output.cir")
    else:
        convert_ngspice_to_xyce(sys.argv[1], sys.argv[2])
