# ZCU102 PS-only validation overlay

This optional overlay is separate from the SD image. It contains the processing-system preset and **no external PL ports or PL peripheral cores**. It tests the FPGA-manager/PYNQ metadata/XRT allocation path; it does not exercise GPIO, AXI DMA, FMC, video, PL DDR or RF hardware.

Target: `xczu9eg-ffvb1156-2-e`, ZCU102 board preset `xilinx.com:zcu102:part0:3.4`, Vivado 2025.2. The build uses the same PS configuration policy as the boot XSA, including disabled PS M_AXI_GP ports. It writes matched `smoke.bit`, `smoke.hwh` and `smoke.xsa` from one run. Inspect `drc.rpt` and `timing_summary.rpt`: this PS-only netlist has no timed fabric paths, so WNS/WHS are N/A.

Build in a fresh empty directory on the build host:

```sh
source /tools/Xilinx/2025.2/Vivado/settings64.sh
mkdir zcu102-smoke-run
cd zcu102-smoke-run
vivado -mode batch -source /path/to/ZCU102-PYNQ/validation/ps-smoke/build.tcl
```

The release supplies `smoke.bit.xz` and `smoke.hwh.xz` as optional test artifacts. Extract both next to `SHA256.json` (from this directory) and `test_overlay.py`. This manifest records the **decompressed** bit/HWH hashes. Verify the manifest against your chosen release/run; a fresh rebuild can produce a different bitstream hash.

Wait for boot services to finish before loading an overlay. Upstream `clear_pl_statefile.service` runs after Jupyter starts; loading metadata while this cleanup is still pending can leave a process with usable cached metadata but no state file for later kernels. The test script refuses to program until cleanup has completed successfully and Jupyter is active.

On the positively identified ZCU102, close your own buffers and kernels before reprogramming. In a root Bash shell, load the PYNQ environment and run:

```sh
source /etc/profile.d/xrt_setup.sh
source /etc/profile.d/pynq_venv.sh
python test_overlay.py /path/to/matched/artifacts
```

The script checks board identity, HWH part/preset, absence of external PL ports and PL cores, exact bit/HWH hashes, parsed IP types and PS-memory metadata **before** downloading. It then programs the FPGA through PYNQ, checks loaded state, and allocates 4 KiB, 1 MiB and 4 MiB buffers with known patterns and synchronization. Buffers are freed in `finally`. Success leaves the validation overlay loaded; it does not configure automatic loading at boot. It exits nonzero on failure.

This is intended for an idle validation board. Programming an overlay changes FPGA state; preserve any application work first. Do not use these files on another board, mix a bitstream with another HWH, or infer application peripheral support from allocation results.
