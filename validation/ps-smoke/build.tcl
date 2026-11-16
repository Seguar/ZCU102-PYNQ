# ZCU102 validation-only PS overlay, no external PL I/O.
if {[version -short] ne "2025.2"} {error "Requires Vivado 2025.2"}
set part xczu9eg-ffvb1156-2-e
create_project zcu102_smoke ./project -part $part
set_property board_part xilinx.com:zcu102:part0:3.4 [current_project]
create_bd_design smoke
create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e:3.5 ps
apply_bd_automation -rule xilinx.com:bd_rule:zynq_ultra_ps_e -config {apply_board_preset "1"} [get_bd_cells ps]
set_property -dict [list CONFIG.PSU__USE__M_AXI_GP0 {0} CONFIG.PSU__USE__M_AXI_GP1 {0} CONFIG.PSU__USE__M_AXI_GP2 {0}] [get_bd_cells ps]
validate_bd_design
save_bd_design
generate_target all [get_files */smoke.bd]
make_wrapper -files [get_files */smoke.bd] -top
add_files -norecurse ./project/zcu102_smoke.gen/sources_1/bd/smoke/hdl/smoke_wrapper.v
set_property top smoke_wrapper [current_fileset]
update_compile_order -fileset sources_1
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} {error "Implementation did not finish"}
open_run impl_1
report_timing_summary -delay_type min_max -file timing_summary.rpt
report_drc -file drc.rpt
set bad [get_drc_violations -quiet -filter {SEVERITY == Error}]
if {[llength $bad] != 0} {error "DRC errors: $bad"}
set setup [get_timing_paths -quiet -delay_type max -max_paths 1]
set hold [get_timing_paths -quiet -delay_type min -max_paths 1]
foreach p [concat $setup $hold] {if {[get_property SLACK $p] < 0} {error "Timing failed"}}
file mkdir artifacts
file copy ./project/zcu102_smoke.runs/impl_1/smoke_wrapper.bit artifacts/smoke.bit
file copy ./project/zcu102_smoke.gen/sources_1/bd/smoke/hw_handoff/smoke.hwh artifacts/smoke.hwh
write_hw_platform -fixed -include_bit -force -file artifacts/smoke.xsa
puts "ZCU102_SMOKE_OVERLAY_BUILD_PASS"
exit
