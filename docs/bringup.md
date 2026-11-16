# ZCU102 first boot

1. Download the release image and `SHA256SUMS`, extract it, and verify the raw checksum. Flash the whole SD card, flush writes, and verify a readback of exactly 8,266,973,184 bytes. Use a measured-capacity 16 GB or larger card.
2. With board power off, insert the card and select SD boot with **SW6: 1 ON, 2 OFF, 3 OFF, 4 OFF**. Follow the switch's printed ON marking, rather than guessing from board orientation. See [AMD's SD boot instructions](https://docs.amd.com/r/en-US/xapp1344-key-revocation-lab/Run-Boot-Image).
3. Connect the dedicated USB UART. Select the CP2108 **interface 0** at **115200 baud, 8 data bits, no parity, 1 stop bit, no flow control**. COM numbers depend on the host; do not assume a fixed number. The adapter exposes four interfaces; the system-controller console is separate from Linux.
4. Start capture before applying power. Expect the ZCU102/zu9eg bootloader, Linux, a mounted root filesystem and a login prompt. UART silence alone does not prove a bad image: check power, boot switches, SD seating and the selected UART interface.
5. Connect Ethernet to a DHCP-enabled LAN and obtain the board's numeric address from the console. Open `http://<board-address>:9090`. Verify the device-tree model and architecture before using credentials when other PYNQ boards share the network.

Factory login is `xilinx` / `xilinx`. Change factory passwords after first use. Avoid the fallback `192.168.2.99` when another PYNQ board uses that address.

## Hostnames

The released image defaults to `pynq-zcu102`. Changing the Linux hostname does not by itself enable LAN name resolution. Use the numeric DHCP address first. A bare name such as `pynq-zu` can resolve through LLMNR when the board advertises it and the client/network supports it; `pynq-zu.local` requires mDNS separately.

The hardware used for validation was subsequently renamed and configured for LLMNR. Those installation-specific changes are not part of the published image. No lab addresses or laptop hosts entries are needed to build the port.

## Scope of runtime tests

This image supplies a PS-only baseline. NumPy and authenticated notebook execution can be checked without programming the FPGA. PYNQ buffer allocation through the embedded XRT device requires a loaded compatible overlay and its PS-memory metadata. The upstream driver raises `RuntimeError: Overlay is not downloaded` when that state is absent. A reserved CMA pool or loaded `zocl` module alone does not establish successful `pynq.allocate` operation.

Do not load a bitstream from another board to satisfy this test. Validate a user-supplied ZCU102 overlay's part, metadata addresses and clocks before programming it or accessing MMIO. GPIO, DMA, FMC, video and PL DDR need their own hardware tests.
