# Validation

Checked 2026-11-16. Source contract and three offline identity-cleanup tests passed. Real Vivado 2025.2 recognizes the required production ZU9EG part and ZCU102 board preset 3.4; the PS-only XSA export completed successfully. Container hardware and SDT wrapper modes passed.

The official `zcu102-rev1.0` SDT compiled with the board CMA fragment and a test high-bank limit. It reports ZynqMP ZCU102 Rev1.0, serial0 at ff000000, the stock 2 GiB low plus 2 GiB high PS DDR ranges, 512 MiB CMA, and configured reference 33,330,000 Hz. This raw SDT also describes other memory/address windows; only the generated Linux CPU-domain DTB can establish the final Linux memory map. The test board marker and high-bank override used for this raw-source check do not substitute for final EDF artifact inspection.

SDTGen printed a reference-clock fallback warning; the actual compiled `pss_ref_clk` property was checked against the board preset. No instrument measurement is claimed. PYNQ's stock UltraScale clock helper uses a 33.333 MHz default; it is unchanged, so its calculated PL rates carry that small reference approximation. Precision clock/overlay use requires review and measurement.

All EDF bootbin/kernel/zocl/kernel-devsrc builds and complete image assembly passed. The exact assembled image passed partition bounds, FAT/ext4 integrity, boot-file comparisons, Linux DTB, root identity, module/zocl indexing, dependency commit and SSH service/socket ordering checks. PYNQ 4.0.0, metadata and utility imports passed under ARM user-mode QEMU, along with NumPy sum(arange(1024)) = 523776. Versions of 288 Python distributions and the installed Ubuntu packages were recorded.

The final Linux DTB passed its own strict checks after domain generation: production ZCU102 Rev1.0 identity, UART serial0 at ff000000, Ethernet PHY at c, 4095 MiB exposed from stock 4 GiB, configured reference 33,330,000 Hz, low-memory 512 MiB CMA and no enabled PL interrupt controller.

Fresh physical boot, on-board Jupyter/allocation, application overlays, GPIO, DMA, FMC, video and PL DDR remain **unverified**. See the experimental release for the image and exact hashes. No board, FPGA or SD-card changes have been performed.
