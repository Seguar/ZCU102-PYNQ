# Validation

Checked 2026-11-16. Source contract and three offline identity-cleanup tests passed. Real Vivado 2025.2 recognizes the required production ZU9EG part and ZCU102 board preset 3.4; the PS-only XSA export completed successfully. Container hardware and SDT wrapper modes passed.

The official `zcu102-rev1.0` SDT compiled with the board CMA fragment and a test high-bank limit. It reports ZynqMP ZCU102 Rev1.0, serial0 at ff000000, the stock 2 GiB low plus 2 GiB high PS DDR ranges, 512 MiB CMA, and configured reference 33,330,000 Hz. This raw SDT also describes other memory/address windows; only the generated Linux CPU-domain DTB can establish the final Linux memory map. The test board marker and high-bank override used for this raw-source check do not substitute for final EDF artifact inspection.

SDTGen printed a reference-clock fallback warning; the actual compiled `pss_ref_clk` property was checked against the board preset. No instrument measurement is claimed. PYNQ's stock UltraScale clock helper uses a 33.333 MHz default; it is unchanged, so its calculated PL rates carry that small reference approximation. Precision clock/overlay use requires review and measurement.

Full EDF boot/kernel compilation, complete image assembly, exact-image inspection and physical board boot remain pending. No board, FPGA or SD-card changes have been performed. Publication must disclose its actual validation level.
