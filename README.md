# ZCU102-PYNQ

Community **PYNQ 4.0.0** SD-image port for the production **ZCU102**, using **Vivado/Vitis 2025.2** and AMD EDF. Ubuntu 24.04 and Python 3.12 come from the official PYNQ root filesystem.

**Status: experimental PS-only image; physical boot, two normal reboots, matched test-overlay programming, allocation/synchronization and authenticated Jupyter checks passed.** It targets `xczu9eg-ffvb1156-2-e`, board preset `xilinx.com:zcu102:part0:3.4`, and the stock **4 GiB PS DDR4 SODIMM**. It uses the official `zcu102-rev1.0` device-tree description. AMD's matching Rev1.1 description inherits Rev1.0 and changes model/compatible identity; the physical PCB revision of the tested unit was not independently established. RevA/RevB engineering samples and modified memory configurations are outside this target.

This is a **PS-only boot image port**. It provides Linux/PYNQ infrastructure and requires a user-supplied, compatible application overlay. It does not bundle a base/HDMI/FMC/DMA/PL-DDR design or claim those interfaces work.

## Image download

Download the image and `SHA256SUMS` from the [experimental PYNQ 4 release](https://github.com/Seguar/ZCU102-PYNQ/releases/tag/v4.0.0-zcu102.1-rc1). Use a **16 GB or larger SD card**; the raw image is 8,266,973,184 bytes. The exact image passed offline filesystem, boot-artifact, device-tree, identity and module checks. ARM QEMU imports/math passed. The exact bytes were flashed, fully read back with a matching SHA256, and booted on a physical ZCU102. On-board identity, imports, dependency pins, memory/storage, NumPy and authenticated Jupyter checks passed. A separate matched PS-only overlay passed programming and 4 KiB/1 MiB/4 MiB allocation/synchronization tests over SSH and Jupyter across a normal reboot. Boot-service persistence passed across two reboots. A separate AXI BRAM/internal-GPIO example also passed SSH/Jupyter tests across a normal reboot: [results and limits](docs/hardware/2026-11-16-bram-gpio/report.md). Physical application interfaces remain untested. See the [latest hardware results](docs/hardware/2026-11-16-continuation/report.md) and [optional test overlay](validation/ps-smoke/README.md), including the startup-cleanup caveat. The release supplies provenance, package inventory, kernel configuration and resolved EDF layer revisions.

## Build

Use an x86-64 Linux build host with Docker, AMD **2025.2** tools supporting ZU9EG, a suitable license, and at least 100 GB free storage. Tools and licenses are obtained separately.

```sh
git clone --recurse-submodules https://github.com/Seguar/ZCU102-PYNQ.git
cd ZCU102-PYNQ
./scripts/prepare.sh
export XILINX_TOOLS=/tools/Xilinx/2025.2
export XILINXD_LICENSE_FILE="$HOME/.Xilinx"
./scripts/build.sh hardware
./scripts/build.sh sdt
```

Stage the official PYNQ 4.0.0 AArch64 rootfs and SDIST in `PYNQ/sdbuild/prebuilt` as `pynq_rootfs.aarch64.tar.gz` and `pynq_sdist.tar.gz`; record their checksums. Then:

```sh
./scripts/build.sh boot
./scripts/build.sh image
```

Output: `PYNQ/sdbuild/output/ZCU102-4.0.0.img`. See [build details](docs/build.md), [inputs](docs/build-inputs.json) and [validation](docs/validation.md). Use a measured-capacity SD card large enough for the raw image; 16 GB or larger is the intended release target.

## Port policy

- PYNQ pinned to v4.0.0 commit `d90670c69f7b71ea1a5d23aaa3e0ec713ff5fa9f`.
- Fresh PS-only XSA from the actual ZCU102 preset; custom EDF machine `zynqmp-zcu102-pynq`.
- Stock 2 GiB low + 2 GiB high PS DDR limit and a 512 MiB CMA pool constrained to low memory.
- FPGA-manager/polling policy; no enabled, unconfigured PL interrupt controller.
- Explicit selection and validation of the final Linux DTB before image assembly.
- Metadata/utility Git dependencies pinned, with installed `direct_url.json` commit verification.
- Offline identity cleanup and per-device SSH host-key generation ordered before both SSH service and socket.
- PS-only self-test manifest; no automatic FPGA programming or peripheral output tests.

Default hostname is `pynq-zcu102`. Ethernet uses DHCP plus the standard PYNQ fallback `192.168.2.99`; avoid duplicate fallback addresses on the same link. Factory login is `xilinx` / `xilinx`; change factory passwords after first use. mDNS resolution is not promised. See [first-boot instructions](docs/bringup.md) for SD boot switches, UART selection, LAN naming and allocation prerequisites.

## Sources

- [PYNQ v4.0.0](https://github.com/Xilinx/PYNQ/releases/tag/v4.0.0)
- [PYNQ external-board build system](https://github.com/Xilinx/PYNQ/blob/v4.0.0/sdbuild/BUILD_SYSTEM.md)
- [AMD ZCU102 guide, UG1182](https://docs.amd.com/api/khub/documents/rt6tROKcAceWoROXFPMY5w/content), especially PS memory and board peripherals
- [AMD system-device-tree sources](https://github.com/Xilinx/system-device-tree-xlnx)

Upstream software and firmware retain their own licenses and notices. This project distributes no AMD installers, account data or license keys.
