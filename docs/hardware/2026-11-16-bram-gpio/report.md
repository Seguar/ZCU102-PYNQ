# ZCU102 BRAM/GPIO validation — 2026-11-16

**Passed in SSH and authenticated Jupyter, before and after a normal reboot.** This validates a minimal AXI BRAM/GPIO example inspired by zPulse, not its complete pulse-generator application.

## Test / how

Built an independent Vivado 2025.2 design for the production ZCU102 with 16 KiB AXI BRAM, SmartConnect and 32-bit AXI GPIO. GPIO output is wired internally to channel-2 input; there are no external PL ports. The matched bit/HWH/XSA came from one run. Setup slack was 6.022 ns, hold slack 0.010 ns, with zero failing timing endpoints and zero DRC violations.

Verified ZCU102 identity, artifact hashes, startup-cleanup completion, HWH address ranges and matching PYNQ runtime ranges before programming/MMIO. Used actual 32-bit MMIO writes/readbacks for eight full-BRAM patterns and actual GPIO output/input registers for 132 patterns. Patterns include zeros, ones, alternating bits, addresses, walking bits and deterministic random values. Each pass restores and verifies BRAM contents and GPIO state in `finally`, then fills/synchronizes/compares/frees 4 KiB, 1 MiB and 4 MiB PYNQ buffers.

Repeated the full test in separate SSH and authenticated Jupyter processes. Deleted only test-owned kernels. Requested one normal Linux reboot after confirming no active Jupyter work; verified a changed boot ID and remote reconnection, waited for startup cleanup, reloaded the same matched overlay, and repeated both full tests.

## Results

All four complete passes succeeded: **131,072 BRAM word comparisons**, **528 GPIO input loopback patterns** plus matching output-register comparisons, and **12 successful allocation/synchronization/comparison tests** with all buffers freed. Both owned Jupyter kernels were deleted. FPGA manager is `operating`; SSH, Jupyter and private remote access are active, with zero failed systemd units.

The initial test stopped before pattern writes because it incorrectly required TRI=0 for a fixed-output core. The HWH actually specifies fixed output/input channels and a TRI reset value of `0xffffffff`. The corrected test checks the fixed direction parameters and preserves TRI, while verifying actual hardware loopback. An unrelated apport error-reporting hook also failed to classify the PynqLinux OS ID during that uncaught assertion; settings were left untouched and the test CLI now handles its own errors as JSON. Initial failure evidence was retained privately.

## Conclusion

The current image supports this tested PS-to-PL AXI BRAM/GPIO path, PYNQ metadata/programming and synchronized allocation. Sources and optional matched artifacts are provided separately from the unchanged SD image. The validation overlay remains loaded, with tested BRAM/GPIO state restored; no automatic startup overlay was added. No other board or console was touched.

## Limits / next tests

This is **internal GPIO loopback**, not a physical LED, switch or connector test. The complete zPulse application, GT pulse outputs, phase alignment, Si570 reconfiguration, external timing, DMA engines, FMC, video and PL DDR remain untested. The FCLK0 report of 99.999 MHz is software-calculated, not measured. No cold power-cycle or prolonged stress/temperature sweep was performed. Previously documented kernel observations remain unresolved outside the paths exercised here.

See [machine-readable results](results.json), [evidence hashes](evidence-sha256.json), and [build/run instructions](../../../validation/bram-gpio/README.md). The current live system contains prior hostname/private-remote-access customizations absent from the published image.
