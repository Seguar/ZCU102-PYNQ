# ZCU102 BRAM and internal GPIO-loopback validation

A minimal fabric test following the AXI BRAM/GPIO architecture illustrated by [zPulse](https://github.com/bmatiasruben/zPulse/tree/f1ce1e3b0742e6168766a35c4bcaef2f7d793fc0). This is an independently generated test overlay, not a port or validation of the complete zPulse application. It does not configure the Si570, use transceivers, or expose external PL ports.

The design uses Vivado 2025.2, `xczu9eg-ffvb1156-2-e` and ZCU102 preset 3.4:

| Component | Address | Range | Test |
| --- | --- | --- | --- |
| `bram_ctrl` | `0xA0000000` | 16 KiB | Eight full-memory patterns through 32-bit MMIO |
| `gpio_loop` | `0xA0010000` | 64 KiB | 32-bit output wired internally to channel-2 input |

The GPIO test compares output and input **hardware registers**, rather than a driver's software shadow. Fixed channel directions are checked from the HWH; the TRI register retains its configured reset value and is preserved. It covers zero, ones, alternating bits, walking ones/zeros and deterministic random values. BRAM contents and GPIO state are restored and checked in `finally`. Physical LED, switch, connector and transceiver pins are outside this test.

## Build

Build in an empty directory on the licensed build host:

```sh
source /tools/Xilinx/2025.2/Vivado/settings64.sh
mkdir zcu102-bram-gpio-run
cd zcu102-bram-gpio-run
vivado -mode batch -source /path/to/ZCU102-PYNQ/validation/bram-gpio/build.tcl
```

The build writes matched `artifacts/bram_gpio.bit`, `.hwh` and `.xsa`. It requires completed implementation, DRC checks and nonnegative setup **and hold** slack. Inspect the full reports before programming. A new rebuild can produce different hashes; use a manifest belonging to that exact run.

## Run

Use only an idle, positively identified ZCU102. Extract the optional release bundle `ZCU102-BRAM-GPIO-validation.tar.xz` into an empty directory. It contains matching `bram_gpio.bit`, `bram_gpio.hwh`, `SHA256.json` and `test_overlay.py`. Verify the extracted bit/HWH hashes before use. These files are separate from the immutable SD image.

In a root Bash shell on the board:

```sh
source /etc/profile.d/xrt_setup.sh
source /etc/profile.d/pynq_venv.sh
python test_overlay.py /path/to/artifacts --program
```

The test checks boot cleanup completion, board/part/preset, hashes, absence of external PL ports, HWH ranges and matching PYNQ runtime ranges **before programming or MMIO**. It then tests all 4096 BRAM words with eight patterns, 132 GPIO patterns using actual output/input readback, and 4 KiB/1 MiB/4 MiB PYNQ allocations with synchronization and comparison. Buffers are freed. Errors return a nonzero process exit.

To repeat in an authenticated Jupyter kernel after loading the overlay:

```python
import runpy
module = runpy.run_path('/path/to/artifacts/test_overlay.py', run_name='validation_module')
results = module['run']('/path/to/artifacts', program=False)
results
```

Programming changes FPGA state and invalidates an existing application overlay. The test leaves this overlay loaded, with BRAM/GPIO restored, and does not add automatic loading at boot. The startup guard waits for the inherited `clear_pl_statefile` prerequisite by refusing an early run; retry once boot cleanup has completed.

FCLK0 is configured nominally at 100 MHz. PYNQ's reported rate is software-calculated, with the previously documented reference approximation; no external clock measurement is claimed. Internal GPIO loopback and CPU MMIO memory checks do not validate physical board I/O, a DMA engine, pulse generation, GT links, external timing or signal integrity.
