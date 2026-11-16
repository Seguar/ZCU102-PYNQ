#!/usr/bin/env python3
"""ZCU102 AXI BRAM/GPIO internal-loopback tests. No external PL pins."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

EXPECTED = {'bram_ctrl': (0xA0000000, 0x4000),
            'gpio_loop': (0xA0010000, 0x10000)}


def run(directory, program=False):
    import numpy as np
    import pynq

    root = Path(directory)
    assert platform.machine() == 'aarch64'
    assert 'ZCU102' in Path('/proc/device-tree/model').read_text()
    for field, expected in [('Result', 'success'), ('SubState', 'dead')]:
        actual = subprocess.check_output(
            ['systemctl', 'show', 'clear_pl_statefile', '-p', field, '--value'],
            text=True).strip()
        assert actual == expected, 'Wait for boot cleanup completion'
    assert int(subprocess.check_output(
        ['systemctl', 'show', 'clear_pl_statefile',
         '-p', 'ExecMainExitTimestampMonotonic', '--value'], text=True)) > 0
    assert subprocess.check_output(
        ['systemctl', 'is-active', 'jupyter'], text=True).strip() == 'active'
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
              for name in ('bram_gpio.bit', 'bram_gpio.hwh')}
    assert hashes == json.loads((root / 'SHA256.json').read_text())
    hwh = ET.parse(root / 'bram_gpio.hwh').getroot()
    info = hwh.find('SYSTEMINFO').attrib
    assert info['DEVICE'] == 'xczu9eg' and info['PACKAGE'] == 'ffvb1156'
    assert info['SPEEDGRADE'] == '-2'
    assert info['BOARD'] == 'xilinx.com:zcu102:part0:3.4'
    assert not list(hwh.find('EXTERNALPORTS'))
    assert not list(hwh.find('EXTERNALINTERFACES'))
    for name, (address, span) in EXPECTED.items():
        ranges = set()
        for region in hwh.iter('MEMRANGE'):
            if region.get('INSTANCE') == name:
                lo, hi = (int(region.get(k), 16)
                          for k in ('BASEVALUE', 'HIGHVALUE'))
                ranges.add((lo, hi - lo + 1))
        assert ranges == {(address, span)}, (name, ranges)
    gpio_module = hwh.find("./MODULES/MODULE[@INSTANCE='gpio_loop']")
    parameters = {p.get('NAME'): p.get('VALUE')
                  for p in gpio_module.findall('./PARAMETERS/PARAMETER')}
    assert parameters['C_ALL_OUTPUTS'] == '1'
    assert parameters['C_ALL_INPUTS_2'] == '1'
    overlay = pynq.Overlay(str(root / 'bram_gpio.bit'), download=False)
    runtime = {}
    for name, (address, span) in EXPECTED.items():
        item = overlay.ip_dict.get(name) or overlay.mem_dict.get(name)
        assert item is not None, name
        assert (item['phys_addr'], item['addr_range']) == (address, span), item
        runtime[name] = {'phys_addr': item['phys_addr'],
                         'addr_range': item['addr_range']}
    assert overlay.ip_dict['gpio_loop']['type'] == 'xilinx.com:ip:axi_gpio:2.0'
    if program:
        overlay.download()
    assert overlay.is_loaded(), 'Load this exact overlay before testing'
    result = {'status': 'PASS', 'pynq': pynq.__version__, 'hashes': hashes,
              'metadata': runtime,
              'fpga_state': Path('/sys/class/fpga_manager/fpga0/state').read_text().strip(),
              'programmed': program, 'startup_cleanup_complete': True,
              'fclk0_mhz_software_calculated': pynq.Clocks.fclk0_mhz,
              'external_pl_ports': 0}
    bram = pynq.MMIO(*EXPECTED['bram_ctrl'])
    gpio = pynq.MMIO(*EXPECTED['gpio_loop'])
    words = EXPECTED['bram_ctrl'][1] // 4
    saved_bram = [bram.read(i * 4) for i in range(words)]
    saved_gpio = gpio.read(0)
    saved_tri = gpio.read(4)
    # Fixed channel direction comes from HWH; the TRI register may retain its reset value.
    result['gpio_tri_register_initial'] = saved_tri
    restored_bram = restored_gpio = False
    try:
        rng = np.random.default_rng(102)
        address = np.arange(words, dtype=np.uint32)
        patterns = [np.zeros(words, dtype=np.uint32),
                    np.full(words, 0xFFFFFFFF, dtype=np.uint32),
                    address, ~address,
                    np.full(words, 0x55AA55AA, dtype=np.uint32),
                    np.full(words, 0xAA55AA55, dtype=np.uint32)]
        patterns.extend(rng.integers(0, 2**32, size=words, dtype=np.uint32)
                        for _ in range(2))
        for pattern in patterns:
            for i, value in enumerate(pattern):
                bram.write(i * 4, int(value))
            actual = [bram.read(i * 4) for i in range(words)]
            assert np.array_equal(np.asarray(actual, dtype=np.uint32), pattern)
        result['bram'] = {'bytes': words * 4, 'patterns': len(patterns),
                          'word_comparisons': words * len(patterns),
                          'access': '32-bit MMIO writes and actual readbacks'}
        gpio_patterns = [0, 0xFFFFFFFF, 0xAAAAAAAA, 0x55555555]
        gpio_patterns.extend(1 << i for i in range(32))
        gpio_patterns.extend((~(1 << i)) & 0xFFFFFFFF for i in range(32))
        gpio_patterns.extend(int(v) for v in rng.integers(0, 2**32, size=64, dtype=np.uint32))
        for value in gpio_patterns:
            gpio.write(0, value)
            assert gpio.read(0) == value
            assert gpio.read(8) == value, 'GPIO channel-2 hardware loopback mismatch'
        result['gpio'] = {'patterns': len(gpio_patterns), 'width': 32,
                          'output_register_readbacks': len(gpio_patterns),
                          'input_register_loopback_readbacks': len(gpio_patterns),
                          'physical_board_pins': False}
    finally:
        for i, value in enumerate(saved_bram):
            bram.write(i * 4, value)
        restored_bram = all(bram.read(i * 4) == value
                            for i, value in enumerate(saved_bram))
        gpio.write(0, saved_gpio)
        restored_gpio = (gpio.read(0) == saved_gpio and
                         gpio.read(8) == saved_gpio and gpio.read(4) == saved_tri)
        assert restored_bram and restored_gpio, 'State restoration failed'
    result['state_restored'] = {'bram': restored_bram, 'gpio': restored_gpio}
    result['allocations'] = []
    for count in (1024, 262144, 1048576):
        buffer = None
        try:
            buffer = pynq.allocate(shape=(count,), dtype=np.uint32)
            expected = np.arange(count, dtype=np.uint32) ^ np.uint32(0xA5A55A5A)
            buffer[:] = expected
            buffer.sync_to_device()
            buffer.sync_from_device()
            assert np.array_equal(buffer, expected)
            result['allocations'].append({'bytes': count * 4, 'sync_compare': 'PASS'})
        finally:
            if buffer is not None:
                buffer.freebuffer()
    result['buffers_freed'] = len(result['allocations'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory')
    parser.add_argument('--program', action='store_true')
    args = parser.parse_args()
    try:
        result = run(args.directory, args.program)
    except Exception as error:
        print(json.dumps({'status': 'FAIL', 'error': type(error).__name__ + ': ' + str(error)}, indent=2))
        sys.exit(1)
    print(json.dumps(result, indent=2))
