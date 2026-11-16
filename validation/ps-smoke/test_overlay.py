#!/usr/bin/env python3
"""Program only the matched PS-only ZCU102 smoke overlay, then test buffers."""
import hashlib,json,pathlib,platform,subprocess,sys,traceback,xml.etree.ElementTree as ET
import numpy as np
import pynq
root=pathlib.Path(sys.argv[1]); result={'status':'FAIL','buffers_freed':0}
try:
    assert platform.machine()=='aarch64'
    assert 'ZCU102' in pathlib.Path('/proc/device-tree/model').read_text()
    startup={}
    for key in ('Result','SubState','ExecMainExitTimestampMonotonic'):
        startup[key]=subprocess.check_output(['systemctl','show','clear_pl_statefile','-p',key,'--value'],text=True).strip()
    assert startup['Result']=='success' and startup['SubState']=='dead' and int(startup['ExecMainExitTimestampMonotonic'])>0, 'Wait for clear_pl_statefile startup completion'
    assert subprocess.check_output(['systemctl','is-active','jupyter'],text=True).strip()=='active'
    result['startup_cleanup_complete']=True
    hwh_root=ET.parse(root/'smoke.hwh').getroot()
    assert not list(hwh_root.find('EXTERNALPORTS')) and not list(hwh_root.find('EXTERNALINTERFACES'))
    assert all(m.get('IS_PL')=='FALSE' for m in hwh_root.findall('./MODULES/MODULE'))
    hwh=hwh_root.find('SYSTEMINFO')
    assert hwh.attrib['DEVICE']=='xczu9eg' and hwh.attrib['PACKAGE']=='ffvb1156'
    assert hwh.attrib['BOARD']=='xilinx.com:zcu102:part0:3.4'
    result['hashes']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('smoke.bit','smoke.hwh')}
    manifest=json.loads((root/'SHA256.json').read_text());assert result['hashes']==manifest
    ol=pynq.Overlay(str(root/'smoke.bit'),download=False)
    assert all(v['type'].startswith('xilinx.com:ip:zynq_ultra_ps_e:') for v in ol.ip_dict.values()),list(ol.ip_dict)
    result['ip_types']={k:v['type'] for k,v in ol.ip_dict.items()}
    result['memory']={k:{p:v.get(p) for p in ('type','base_address','size','idx')} for k,v in ol.mem_dict.items()}
    assert 'PSDDR' in ol.mem_dict and ol.mem_dict['PSDDR']['base_address']==0
    ol.download()
    assert ol.is_loaded()
    result['fpga_state']=pathlib.Path('/sys/class/fpga_manager/fpga0/state').read_text().strip()
    result['programming']='PASS'; result['allocation']=[]
    for n in (1024,262144,1048576):
        buf=None
        try:
            buf=pynq.allocate(shape=(n,),dtype=np.uint32)
            expected=np.arange(n,dtype=np.uint32)^np.uint32(0xA5A55A5A)
            buf[:]=expected;buf.sync_to_device();buf.sync_from_device()
            assert np.array_equal(buf,expected)
            result['allocation'].append({'words':n,'bytes':n*4,'sync_compare':'PASS'})
        finally:
            if buf is not None:buf.freebuffer();result['buffers_freed']+=1
    result['status']='PASS'
except Exception as e:
    result['error']=type(e).__name__+': '+str(e)
    result['traceback']=traceback.format_exc()
print(json.dumps(result,indent=2))
sys.exit(0 if result['status']=='PASS' else 1)
