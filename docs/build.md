# Build details

The port uses PYNQ v4.0.0 / 2025.2 EDF, without PetaLinux. The `.spec` and `edf.env` select aarch64, FPGA-manager mode and a custom machine generated from `hardware/ps.xsa`. The export script validates the exact production ZU9EG part and ZCU102 board preset before writing a PS-only XSA. No PL implementation, timing or bitstream claim is made.

The official SDT board description supplies the console, SD, Ethernet PHY, I2C and other PS peripherals. The board fragment only adds the PYNQ low-memory CMA pool; it does not copy RFSoC-specific nodes or legacy PL addresses. The high memory bank is capped at the stock remaining 2 GiB. The generated Linux CPU map may expose 4095 MiB because it omits a 1 MiB low-bank region; the board still has 4 GiB physical PS memory. The separate PL DDR component is not exposed as PS RAM or supported by this image port.

The wrapper supports `hardware`, `sdt`, `boot` and `image`. It exports board identity and FPGA-manager mode into Docker/EDF, generates hardware first and invalidates the boot stamp when the XSA changes. PYNQ's build container sources the host's mounted 2025.2 tools. `PYNQ_DOCKER_IMAGE` selects an existing compatible container image; `APPARMOR_PROFILE` can select a scoped build-container profile on hosts with restricted user namespaces. Do not disable host protection globally.

Use an isolated build checkout per board. Preserve download/shared-state caches, but keep each EDF source/build/custom-machine layer separate and permit only one writer to a cache at a time. Build inputs and actual package versions belong in the release evidence. The wrapper currently uses the default PYNQ cache location under its own checkout.

Upstream v4's boot extraction can skip the `system.dtb` symlink and select a regular U-Boot DTB. This wrapper explicitly selects the Linux symlink target, validates its board/memory/UART/CMA/PL policy and copies it to the boot output before assembling the card image.

The `pynq` board package delegates to upstream but renders exact Metadata/Utils Git revisions into the stage. Equal-version prebuilt wheels can otherwise mask those pins, so replacement is forced without replacing unrelated dependencies. The final release package checks actual installed `direct_url.json` commit IDs and repairs a mismatch before assembly. The public input manifest is retained at `/usr/local/share/zcu102-build-inputs.json`.

The release package clears inherited SSH host keys, user authentication/history, machine ID, random seed and leases from the offline root, and sets hostname `pynq-zcu102`. A oneshot service generates missing keys before SSH service and socket activation. It has no default dependency on `basic.target`, avoiding an ordering cycle with early socket units. This does not touch a running board.

Before publishing an image: check successful build exits, exact image partition bounds/filesystems, final Linux DTB, boot-file hashes, module indexing, identity state and installed dependency commits. Hash raw and compressed bytes and verify their equivalence. Hardware boot, Jupyter execution, allocation and application-overlay tests require the actual board; distinguish offline evidence from those gates. An intermediate image must remain an explicitly limited prerelease.

For image mode, the privileged wrapper registers the container's static AArch64 QEMU interpreter with binfmt flag `F`. This keeps the interpreter available across chroot/mount namespaces, without relying on an executable inside the target root. A conflicting or disabled existing PYNQ entry is rejected rather than silently overwritten. The registration is in the Linux build VM, not an FPGA board.

The configured PS reference is **33,330,000 Hz**, taken from preset 3.4 and the generated DT (UG1182 describes 33.33 MHz). It is not an instrument measurement. Upstream PYNQ's UltraScale helper retains its 33.333 MHz default, so calculated PL clock rates have that small reference approximation; this port does not claim precision clock accuracy or change library internals without hardware evidence.
