#!/usr/bin/env python3
"""
GTKWave TIM to ngspice PWL converter with SQUARE WAVE output
This version preserves signal names with brackets [ ] and other characters
"""

import re

def convert_tim_to_square_pwl(tim_filename, output_filename=None, vdd=3.3):
    """Convert GTKWave TIM file to ngspice PWL format with square waves"""
    
    if output_filename is None:
        output_filename = tim_filename.replace('.tim', '.cir')
        spice_filename  = tim_filename.replace('.tim', '.spice')
    
    with open(tim_filename, 'r') as f:
        content = f.read()
    
    # Extract time scale
    time_scale_match = re.search(r'Time_Scale:\s*([\d.E+-]+)', content)
    time_scale = float(time_scale_match.group(1)) if time_scale_match else 1e-12
    
    print(f"Time scale: {time_scale} seconds")
    
    # Find all Digital_Signal blocks
    signal_pattern = r'Digital_Signal\s*\n(.*?)(?=Digital_Signal|Digital_Bus|$)'
    signal_blocks = re.findall(signal_pattern, content, re.DOTALL)
    
    signals = []
    
    for block in signal_blocks:
        # Extract signal name (preserve all characters including [ ] )
        name_match = re.search(r'Name:\s*([\w\[\]:_.-]+)', block)
        if not name_match:
            continue
        signal_name = name_match.group(1)
        
        # Extract start state
        start_match = re.search(r'Start_State:\s*([01X])', block)
        start_state = start_match.group(1) if start_match else '0'
        
        # Extract all edges
        edge_matches = re.findall(r'Edge:\s*([\d.]+)\s+([01])', block)
        edges = [(float(time), int(value)) for time, value in edge_matches]
        
        # Generate SQUARE WAVE PWL
        pwl_points = []
        
        # Initial state at time 0
        if start_state == '1':
            current_voltage = vdd
        elif start_state == '0':
            current_voltage = 0
        else:  # X state
            current_voltage = 0
        
        pwl_points.append(f"0 {current_voltage}")
        
        # Add edges with sharp transitions
        for time, value in edges:
            time_sec = time * time_scale
            new_voltage = vdd if value == 1 else 0
            
            # Calculate epsilon (small time before transition)
            epsilon = 100e-9
            
            # Only add pre-transition point if voltage is changing
            if new_voltage != current_voltage:
                # Point just before transition (maintains current level)
                pwl_points.append(f"{time_sec - epsilon} {current_voltage}")
                
                # Actual transition point
                pwl_points.append(f"{time_sec} {new_voltage}")
                
                current_voltage = new_voltage
        
        # Preserve original signal name (keep [ ] and other characters)
        # Only replace characters that are truly problematic in SPICE
        safe_name = signal_name.replace(':', '_').replace('.', '_').replace('-', '_')
        # Keep brackets [ ] and underscores _ as they are valid in SPICE node names
        
        pwl_statement = f"V_{safe_name} {safe_name} 0 PWL({' '.join(pwl_points)})"
        
        signals.append({
            'original_name': signal_name,
            'safe_name': safe_name,
            'pwl': pwl_statement,
            'edges': len(edges),
            'start_state': start_state
        })
        
        print(f"Processed: {signal_name} → {safe_name} ({len(edges)} edges, start: {start_state})")
    
    # Write output file
    with open(output_filename, 'w') as f:
        f.write(f"* GTKWave TIM to ngspice PWL converter\n")
        f.write(f"* Source: {tim_filename}\n")
        f.write(f"* Time Scale: {time_scale} seconds\n")
        f.write(f"* VDD Level: {vdd}V\n")
        f.write(f"* Signals: {len(signals)}\n\n")
        f.write(f".lib /usr/local/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt \n")
        f.write(f".tran 10000ns 600us\n")
        f.write(f".print tran format=raw file=Mult4_cir.raw  v(*)\n")
        f.write(f"* Fuentes de alimentación\n")
        f.write(f"Vvdd VPWR 0 DC 3.3\n")
        f.write(f"Vgnd VGND 0 DC 0\n\n")

        # Write PWL statements with preserved signal names
        for signal in signals:
            f.write(f"* {signal['original_name']} - {signal['edges']} transitions\n")
            f.write(f"{signal['pwl']}\n\n")
        
        # Calculate simulation time
        max_time = 0
        for block in signal_blocks:
            edge_matches = re.findall(r'Edge:\s*([\d.]+)\s+([01])', block)
            if edge_matches:
                block_max = max(float(time) for time, _ in edge_matches) * time_scale
                max_time = max(max_time, block_max)
        
        sim_time = max_time * 1.1
        timestep = time_scale * 10  # 10x time scale for good resolution
        
        f.write(f"* Include circuit netlist\n")
        f.write(".include \"./" + spice_filename + "\"\n")
        f.write(".end\n")
    
    print(f"\nSquare wave PWL conversion complete!")
    print(f"Output: {output_filename}")
    print(f"Spice:  {spice_filename}")
    print(f"\nSignal name preservation:")
    for signal in signals:
        if signal['original_name'] != signal['safe_name']:
            print(f"  {signal['original_name']} → {signal['safe_name']}")
        else:
            print(f"  {signal['original_name']} (unchanged)")
    
    return signals

def test_signal_names():
    """Test signal name preservation"""
    test_names = [
        "clk",
        "data[7:0]", 
        "addr[15:0]",
        "spi_cs_n",
        "uart_tx.out",
        "mem-enable"
    ]
    
    print("Testing signal name preservation:")
    for name in test_names:
        safe_name = name.replace(':', '_').replace('.', '_').replace('-', '_')
        print(f"  {name} → {safe_name}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        convert_tim_to_square_pwl(sys.argv[1])
    else:
        print("Usage: python tim_converter.py <tim_file>")
        print("\nTesting signal name preservation...")
        test_signal_names()