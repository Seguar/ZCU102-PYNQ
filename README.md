# ZCU102-PYNQ

Community **PYNQ 4.0.0** SD-image port for the production **ZCU102**, using **Vivado/Vitis 2025.2** and AMD EDF. Ubuntu 24.04 and Python 3.12 come from the official PYNQ root filesystem.

**Status: source preparation; image build and physical boot validation pending.** This repository is independent of the ZCU216 RFSoC port. It targets `xczu9eg-ffvb1156-2-e`, board preset `xilinx.com:zcu102:part0:3.4`, and the stock **4 GiB PS DDR4 SODIMM**. It uses the official `zcu102-rev1.0` device-tree description. AMD's matching Rev1.1 description inherits Rev1.0 and changes model/compatible identity; neither physical revision is verified here. RevA/RevB engineering samples and modified memory configurations are outside this target.

This is a **PS-only boot image port**. It provides Linux/PYNQ infrastructure and requires a user-supplied, compatible application overlay. It does not bundle a base/HDMI/FMC/DMA/PL-DDR design or claim those interfaces work. No RF converter libraries or CLK104 configuration are added by the board recipe.

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
- Non-RF self-test manifest; no automatic FPGA programming or peripheral output tests.

Default hostname is `pynq-zcu102`. Ethernet uses DHCP plus the standard PYNQ fallback `192.168.2.99`; avoid duplicate fallback addresses on the same link. Factory login is `xilinx` / `xilinx`; change factory passwords after first use. mDNS resolution is not promised.

## Sources

- [PYNQ v4.0.0](https://github.com/Xilinx/PYNQ/releases/tag/v4.0.0)
- [PYNQ external-board build system](https://github.com/Xilinx/PYNQ/blob/v4.0.0/sdbuild/BUILD_SYSTEM.md)
- [AMD ZCU102 guide, UG1182](https://docs.amd.com/api/khub/documents/rt6tROKcAceWoROXFPMY5w/content), especially PS memory and board peripherals
- [AMD system-device-tree sources](https://github.com/Xilinx/system-device-tree-xlnx)

Upstream software and firmware retain their own licenses and notices. This project distributes no AMD installers, account data or license keys.
