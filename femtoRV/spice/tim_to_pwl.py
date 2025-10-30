#!/usr/bin/env python3
"""
GTKWave TIM to ngspice PWL converter with SQUARE WAVE output
This version ensures digital signals have sharp edges, not triangular ramps
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
        # Extract signal name
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
            # Use 1% of time scale or 1ps, whichever is smaller
            epsilon = 2e-9
            
            # Only add pre-transition point if voltage is changing
            if new_voltage != current_voltage:
                # Point just before transition (maintains current level)
                pwl_points.append(f"{time_sec - epsilon} {current_voltage}")
                
                # Actual transition point
                pwl_points.append(f"{time_sec} {new_voltage}")
                
                current_voltage = new_voltage
        
        # Create safe node name for SPICE
        safe_name = re.sub(r'[^\w]', '_', signal_name)
        
        pwl_statement = f"V_{safe_name} {safe_name} 0 PWL({' '.join(pwl_points)})"
        
        signals.append({
            'original_name': signal_name,
            'safe_name': safe_name,
            'pwl': pwl_statement,
            'edges': len(edges),
            'start_state': start_state
        })
        
        print(f"Processed: {signal_name} ({len(edges)} edges, start: {start_state})")
    
    # Write output file
    with open(output_filename, 'w') as f:
        f.write(f"* VDD Level: {vdd}V\n")
        f.write(f"* Signals: {len(signals)}\n\n")
        f.write(f".lib /usr/local/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt \n")
        f.write(f".tran 1000ns 600us\n")
        f.write(f".print tran format=raw file=Mult4_cir.raw  v(*)\n")
        f.write(f"* Fuentes de alimentación\n")
        f.write(f"Vvdd VPWR 0 DC 3.3\n")
        f.write(f"Vgnd VGND 0 DC 0\n")

        # Write PWL statements
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
        f.write(".include \"./" + spice_filename + "\"\n")
        f.write(".end\n")
    
    print(f"\nSquare wave PWL conversion complete!")
    print(f"Output: {output_filename}")
    print(f"Spice:  {spice_filename}")
    
    return signals

def demo_square_wave():
    """Demonstrate the square wave PWL generation"""
    
    # Create a test TIM file with clock signal
    test_content = '''Time_Scale:        1.000000E-12
Digital_Signal
     Position:          1
     Height:            24
     Space_Above:       24
     Name:              clk
     Start_State:       0
     Number_Edges:      8
     Rise_Time:         0.2
     Fall_Time:         0.2
          Edge:               10000.0 1
          Edge:               20000.0 0
          Edge:               30000.0 1
          Edge:               40000.0 0
          Edge:               50000.0 1
          Edge:               60000.0 0
          Edge:               70000.0 1
          Edge:               80000.0 0
Digital_Signal
     Position:          2
     Height:            24
     Space_Above:       24
     Name:              spi_cs_n
     Start_State:       X
     Number_Edges:      4
     Rise_Time:         0.2
     Fall_Time:         0.2
          Edge:               15000.0 1
          Edge:               25000.0 0
          Edge:               55000.0 1
          Edge:               65000.0 0
'''
    
    with open('demo_square.tim', 'w') as f:
        f.write(test_content)
    
    signals = convert_tim_to_square_pwl('demo_square.tim', 'demo_square.cir')
    
    print("\n" + "="*50)
    print("DEMO: Generated square wave PWL statements:")
    print("="*50)
    
    for signal in signals:
        print(f"\n{signal['original_name']}:")
        print(signal['pwl'])

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        convert_tim_to_square_pwl(sys.argv[1])
    else:
        print("Usage: python square_pwl_converter.py <tim_file>")
        print("\nRunning demo...")
        demo_square_wave()