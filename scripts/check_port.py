#!/usr/bin/env python3
"""Hardware-free checks for the production ZCU102 port contract."""
import json
from pathlib import Path
import subprocess

repo=Path(__file__).resolve().parents[1]
pynq=repo/'PYNQ'
assert subprocess.check_output(['git','-C',str(pynq),'rev-parse','HEAD'],text=True).strip()=='d90670c69f7b71ea1a5d23aaa3e0ec713ff5fa9f'
inputs=json.loads((repo/'docs/build-inputs.json').read_text())
assert inputs['part']=='xczu9eg-ffvb1156-2-e'
assert inputs['board_preset']=='xilinx.com:zcu102:part0:3.4'
assert inputs['ps_ddr_bytes']==4294967296 and inputs['boot_overlay'] is None
text=(repo/'ZCU102/edf.env').read_text()
for expected in ('EDF_MODE=custom','EDF_BOOT_MACHINE=zynqmp-zcu102-pynq','EDF_BOARD_DTS=zcu102-rev1.0','amd-edf-rel-v25.11.1','0x8 0x0 0x0 0x80000000'):
    assert expected in text,expected
spec=(repo/'ZCU102/ZCU102.spec').read_text()
assert 'aarch64' in spec and 'FPGA_MANAGER_ZCU102 := 1' in spec
assert all(name not in spec for name in ('xrfclk','xrfdc','xsdfec','tics'))
assert not list((repo/'ZCU102').rglob('*.bit'))
manifest=json.loads((repo/'ZCU102/selftest.json').read_text())
assert manifest['board']=='ZCU102' and manifest['defaults']['hardware'] is False
for test in manifest['tests']:
    language,name=test['id'].split('/')
    assert name!='rfsoc_stack'
    suffix={'python':'.py','bash':'.sh'}[language]
    assert (pynq/'sdbuild/packages/selftest/tests'/language/(name+suffix)).exists(),test['id']
print('PASS: PYNQ pin, ZCU102 identity, stock DDR policy, no boot overlay/RF packages, valid non-RF self-tests')
