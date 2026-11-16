# SPDX-License-Identifier: BSD-3-Clause
# PS-only boot hardware, not an RF/MTS overlay.
if {[version -short] ne "2025.2"} {error "Use Vivado 2025.2 for this port"}
set here [file dirname [file normalize [info script]]]
cd $here
set part xczu9eg-ffvb1156-2-e
set board xilinx.com:zcu102:part0:3.4
if {[llength [get_parts -quiet $part]] != 1} {error "Required Zynq UltraScale+ device support missing"}
if {[llength [get_board_parts -quiet $board]] != 1} {error "Required ZCU102 board preset missing"}
create_project -force zcu102_boot ./build -part $part
set_property board_part $board [current_project]
create_bd_design ps
create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e:3.5 ps
apply_bd_automation -rule xilinx.com:bd_rule:zynq_ultra_ps_e -config {apply_board_preset "1"} [get_bd_cells ps]
set_property -dict [list CONFIG.PSU__USE__M_AXI_GP0 {0} CONFIG.PSU__USE__M_AXI_GP1 {0} CONFIG.PSU__USE__M_AXI_GP2 {0}] [get_bd_cells ps]
validate_bd_design
save_bd_design
generate_target all [get_files */ps.bd]
write_hw_platform -fixed -force -file ps.xsa
puts "ZCU102_PS_EXPORT_PASS"
exit
