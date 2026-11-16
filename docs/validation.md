# Validation

Checked 2026-11-16. Source contract and three offline identity-cleanup tests passed. Real Vivado 2025.2 recognizes the required production ZU9EG part and ZCU102 board preset 3.4; the PS-only XSA export completed successfully. Container hardware and SDT wrapper modes passed.

The official `zcu102-rev1.0` SDT compiled with the board CMA fragment and a test high-bank limit. It reports ZynqMP ZCU102 Rev1.0, serial0 at ff000000, the stock 2 GiB low plus 2 GiB high PS DDR ranges, 512 MiB CMA, and configured reference 33,330,000 Hz. This raw SDT also describes other memory/address windows; only the generated Linux CPU-domain DTB can establish the final Linux memory map. The test board marker and high-bank override used for this raw-source check do not substitute for final EDF artifact inspection.

SDTGen printed a reference-clock fallback warning; the actual compiled `pss_ref_clk` property was checked against the board preset. No instrument measurement is claimed. PYNQ's stock UltraScale clock helper uses a 33.333 MHz default; it is unchanged, so its calculated PL rates carry that small reference approximation. Precision clock/overlay use requires review and measurement.

All EDF bootbin/kernel/zocl/kernel-devsrc builds and complete image assembly passed. The exact assembled image passed partition bounds, FAT/ext4 integrity, boot-file comparisons, Linux DTB, root identity, module/zocl indexing, dependency commit and SSH service/socket ordering checks. PYNQ 4.0.0, metadata and utility imports passed under ARM user-mode QEMU, along with NumPy sum(arange(1024)) = 523776. Versions of 288 Python distributions and the installed Ubuntu packages were recorded.

The final Linux DTB passed its own strict checks after domain generation: production ZCU102 Rev1.0 identity, UART serial0 at ff000000, Ethernet PHY at c, 4095 MiB exposed from stock 4 GiB, configured reference 33,330,000 Hz, low-memory 512 MiB CMA and no enabled PL interrupt controller.

## Physical validation, 2026-11-16

The exact release image was subsequently flashed to a measured 16 GB SD card, flushed, and read back over all 8,266,973,184 image bytes with matching SHA256. After selecting SD boot with SW6, UART captured a physical ZCU102 boot through Linux and a usable shell. This supersedes the original offline-only status; the image bytes are unchanged.

Live checks on that installation passed board/architecture identity, Linux 6.12.40, Python 3.12.3, PYNQ 4.0.0, dependency commit pins, NumPy matrix math over SSH and authenticated Jupyter, root-filesystem expansion, swap and device discovery. The corrected SSH run loaded both the XRT and PYNQ environments before importing PYNQ. It discovered one `EmbeddedDevice`. The kernel exposes 512 MiB CMA and the expected stock 4 GiB memory configuration. Zero systemd units failed.

**Allocation has not passed.** Both 4 KiB and 1 MiB `pynq.allocate` attempts raised `RuntimeError: Overlay is not downloaded` in the correctly configured SSH environment and Jupyter. This is the upstream embedded driver's prerequisite for PS-memory metadata; no application overlay was loaded, and no metadata was fabricated. The initial SSH `No Devices Found` error came from an unsourced XRT environment and is retained as a test-setup finding. Kernel CMA/IRQ warnings are documented separately; their relationship to allocation is unproven.

The full runtime gate remains incomplete. A normal reboot/persistence retest was skipped because an existing console session was present. Application overlays, GPIO, DMA, FMC, video, PL DDR and instrument-measured clocks remain unverified. The live installation includes later hostname/LLMNR customization absent from the released image. The physical PCB revision was not independently established; the DT identifies Rev1.0.

See the [sanitized hardware report](hardware/2026-11-16/public-report.md), [machine-readable results](hardware/2026-11-16/public-results.json), and [evidence hashes](hardware/2026-11-16/evidence-sha256.json). To reproduce the on-board checks, copy [hardware_smoke.py](hardware/2026-11-16/hardware_smoke.py) to the board, open a root Bash shell, and run:

```sh
source /etc/profile.d/xrt_setup.sh
source /etc/profile.d/pynq_venv.sh
python hardware_smoke.py
```

The script does not program the FPGA or change configuration. It exits nonzero when any gate fails, including the current unloaded-overlay allocation prerequisite. Jupyter authentication/kernel execution and service/log inspection are separately recorded in the report. Read the [bring-up guide](bringup.md) before live tests.
