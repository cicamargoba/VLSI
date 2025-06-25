prep -design femto -tag myrun -config config.json -init_design_config -overwrite
run_sythesis
run_floorplan
run_placement
run_cts
run_routing
write_powered_verilog 
set_netlist $::env(routing_logs)/$::env(femto).powered.v
run_magic
run_magic_spice_export
run_magic_drc
run_lvs
