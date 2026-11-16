# ZCU102 AXI BRAM and internal GPIO-loopback validation; no external PL ports.
if {[version -short] ne "2025.2"} {error "Requires Vivado 2025.2"}
create_project zcu102_bram_gpio ./project -part xczu9eg-ffvb1156-2-e
set_property board_part xilinx.com:zcu102:part0:3.4 [current_project]
create_bd_design bram_gpio
create_bd_cell -type ip -vlnv xilinx.com:ip:zynq_ultra_ps_e:3.5 ps
apply_bd_automation -rule xilinx.com:bd_rule:zynq_ultra_ps_e -config {apply_board_preset "1"} [get_bd_cells ps]
set_property -dict [list CONFIG.PSU__USE__M_AXI_GP0 {1} CONFIG.PSU__USE__M_AXI_GP1 {0} CONFIG.PSU__USE__M_AXI_GP2 {0} CONFIG.PSU__CRL_APB__PL0_REF_CTRL__FREQMHZ {100}] [get_bd_cells ps]
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect:1.0 axi
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {2}] [get_bd_cells axi]
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_bram_ctrl:4.1 bram_ctrl
set_property -dict [list CONFIG.DATA_WIDTH {32} CONFIG.SINGLE_PORT_BRAM {1}] [get_bd_cells bram_ctrl]
create_bd_cell -type ip -vlnv xilinx.com:ip:blk_mem_gen:8.4 ram
set_property -dict [list CONFIG.Memory_Type {Single_Port_RAM} CONFIG.Write_Width_A {32} CONFIG.Write_Depth_A {4096} CONFIG.Enable_A {Use_ENA_Pin} CONFIG.Use_Byte_Write_Enable {true} CONFIG.Byte_Size {8}] [get_bd_cells ram]
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 gpio_loop
set_property -dict [list CONFIG.C_GPIO_WIDTH {32} CONFIG.C_ALL_OUTPUTS {1} CONFIG.C_IS_DUAL {1} CONFIG.C_GPIO2_WIDTH {32} CONFIG.C_ALL_INPUTS_2 {1} CONFIG.C_INTERRUPT_PRESENT {0}] [get_bd_cells gpio_loop]
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 rst
set_property CONFIG.C_EXT_RESET_HIGH {0} [get_bd_cells rst]
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:1.1 locked
set_property -dict [list CONFIG.CONST_WIDTH {1} CONFIG.CONST_VAL {1}] [get_bd_cells locked]
connect_bd_intf_net [get_bd_intf_pins ps/M_AXI_HPM0_FPD] [get_bd_intf_pins axi/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins axi/M00_AXI] [get_bd_intf_pins bram_ctrl/S_AXI]
connect_bd_intf_net [get_bd_intf_pins axi/M01_AXI] [get_bd_intf_pins gpio_loop/S_AXI]
connect_bd_intf_net [get_bd_intf_pins bram_ctrl/BRAM_PORTA] [get_bd_intf_pins ram/BRAM_PORTA]
connect_bd_net [get_bd_pins gpio_loop/gpio_io_o] [get_bd_pins gpio_loop/gpio2_io_i]
connect_bd_net [get_bd_pins ps/pl_clk0] [get_bd_pins ps/maxihpm0_fpd_aclk] [get_bd_pins axi/aclk] [get_bd_pins bram_ctrl/s_axi_aclk] [get_bd_pins gpio_loop/s_axi_aclk] [get_bd_pins rst/slowest_sync_clk]
connect_bd_net [get_bd_pins ps/pl_resetn0] [get_bd_pins rst/ext_reset_in]
connect_bd_net [get_bd_pins locked/dout] [get_bd_pins rst/dcm_locked]
connect_bd_net [get_bd_pins rst/peripheral_aresetn] [get_bd_pins axi/aresetn] [get_bd_pins bram_ctrl/s_axi_aresetn] [get_bd_pins gpio_loop/s_axi_aresetn]
create_bd_addr_seg -range 16K -offset 0xA0000000 [get_bd_addr_spaces ps/Data] [get_bd_addr_segs bram_ctrl/S_AXI/Mem0] SEG_BRAM
create_bd_addr_seg -range 64K -offset 0xA0010000 [get_bd_addr_spaces ps/Data] [get_bd_addr_segs gpio_loop/S_AXI/Reg] SEG_GPIO
validate_bd_design
save_bd_design
generate_target all [get_files */bram_gpio.bd]
make_wrapper -files [get_files */bram_gpio.bd] -top
add_files -norecurse ./project/zcu102_bram_gpio.gen/sources_1/bd/bram_gpio/hdl/bram_gpio_wrapper.v
set_property top bram_gpio_wrapper [current_fileset]
update_compile_order -fileset sources_1
launch_runs impl_1 -to_step write_bitstream -jobs 8
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} {error "Implementation did not finish"}
open_run impl_1
report_timing_summary -delay_type min_max -file timing_summary.rpt
report_drc -file drc.rpt
if {[llength [get_drc_violations -quiet -filter {SEVERITY == Error}]]} {error "DRC errors"}
foreach delay {max min} {
    set paths [get_timing_paths -quiet -delay_type $delay -max_paths 1]
    if {![llength $paths]} {error "Expected timed fabric paths for $delay"}
    if {[get_property SLACK [lindex $paths 0]] < 0} {error "$delay timing failed"}
}
file mkdir artifacts
file copy ./project/zcu102_bram_gpio.runs/impl_1/bram_gpio_wrapper.bit artifacts/bram_gpio.bit
file copy ./project/zcu102_bram_gpio.gen/sources_1/bd/bram_gpio/hw_handoff/bram_gpio.hwh artifacts/bram_gpio.hwh
write_hw_platform -fixed -include_bit -force -file artifacts/bram_gpio.xsa
puts "ZCU102_BRAM_GPIO_BUILD_PASS"
exit
