# ZCU102 image validation continuation — 2026-11-16

**Result: scoped PS-only runtime gate passed, with the limits below.** This supersedes the earlier allocation-incomplete and reboot-untested status. Earlier reports remain unchanged.

## Test

Verify normal reboot persistence and exercise PYNQ FPGA-manager programming, real HWH metadata, XRT buffer allocation and authenticated Jupyter execution on the previously flashed exact release image. A separate PS-only validation overlay supplies the metadata prerequisite absent from the bare image.

## How

Confirmed the console was an idle automatic login and Jupyter had no user kernels/sessions. Requested two normal Linux reboots; confirmed changed boot IDs and reconnection over the board's private remote connection. No physical reset was needed. Built a matched bit/HWH/XSA from Vivado 2025.2 and the production ZCU102 preset. Reviewed DRC (zero violations) and setup/hold reports (no timed fabric paths, WNS/WHS N/A). The design has no external PL ports or PL peripheral cores.

The loader verifies ZCU102 identity, part/preset, hashes and parsed PS-only metadata before programming. Both SSH and fresh authenticated Jupyter kernels filled 4 KiB, 1 MiB and 4 MiB uint32 buffers with known patterns, synchronized them both ways, compared and freed them. Two complete SSH/Jupyter passes were accepted across a reboot: 12 successful comparisons and 12 corresponding frees. A final rerun of the original core smoke script also exited zero. Test-owned kernels were deleted.

## Results

Linux 6.12.40, Python 3.12.3, PYNQ 4.0.0, pinned metadata/utilities, NumPy, memory/storage and device discovery passed. FPGA manager reported `operating`; both matched-overlay programming runs and cross-process allocation passed. SSH, Jupyter, hostname and the private remote service returned after both reboots; zero failed systemd units were present at the end. Physical PS RAM remains the stock 4 GiB configuration; the XRT PSDDR topology entry is 256 MiB and is not a physical capacity measurement.

A reload initiated while startup cleanup was pending passed in the SSH process but a later kernel reported `Overlay is not downloaded`. The inherited `clear_pl_statefile` unit runs after Jupyter startup. Once cleanup had completed, a reload restored allocation in fresh processes. The validation loader now refuses to start before cleanup completes; no installed unit was modified. This boot-startup caveat remains documented. An initial XML identity guard failure stopped before programming and was corrected. A slow raw transfer was interrupted before programming; the extracted compressed transfer passed exact hashes.

## Conclusion

The unchanged release image supports the tested PS-only runtime and the optional matched validation overlay. Allocation without an overlay remains unsupported. This is not a GPIO, DMA-engine or application-platform certification. The live system also contains previously installed hostname/name-advertisement and private remote-access customizations absent from the release image.

## Limits and next tests

The validation overlay remains loaded and is not configured to load automatically. Application GPIO, DMA, FMC, video, PL DDR, RF and measured clock accuracy remain untested. No physical PCB revision readout, new cold-power-cycle test or exhaustive memory stress test was performed. Existing kernel IRQ/CMA, AES/SHA, regulatory database and Ethernet PTP clock warnings are retained observations; these successful tests do not establish their cause or correctness of those untested paths. Use the loader only after boot cleanup completes and preserve application work before programming.

See [results.json](results.json), [artifact hashes](evidence-sha256.json), and the [reproducible overlay/test source](../../../validation/ps-smoke/README.md). The image bytes and original release tag remain unchanged.
