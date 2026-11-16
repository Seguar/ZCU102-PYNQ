#!/usr/bin/env python3
"""ZCU102 PS smoke gate; no overlay download or configuration changes.
Run in a fresh root bash shell (sudo bash), before any PYNQ import:
    source /etc/profile.d/xrt_setup.sh
    source /etc/profile.d/pynq_venv.sh
    python hardware_smoke.py
Requires XILINX_XRT, aarch64 ZCU102, Linux 6.12.40, Python 3.12.3,
PYNQ 4.0.0 and NumPy 1.26.4 plus the commit pins below.
Exit 0 only when every check passes. An unloaded overlay prevents default
memory allocation: expected PS-only prerequisite, still a failing allocation gate.
No checks execute on import. Output excludes addresses and unique identities.
"""
import json, os, platform, pathlib, subprocess, sys, glob
R={}
def check(name,fn):
    try: R[name]={'status':'pass','details':fn()}
    except Exception as e: R[name]={'status':'fail','error':type(e).__name__+': '+str(e)}
def require(ok,value):
    assert ok, str(value)
    return value
def read(p): return pathlib.Path(p).read_text().strip('\0\n ')
def identity():
    import pynq
    x={'model':read('/proc/device-tree/model'),'architecture':platform.machine(),'kernel':platform.release(),'python':platform.python_version(),'pynq':pynq.__version__}
    assert 'ZCU102' in x['model'] and x['architecture']=='aarch64',x
    assert x['kernel'].startswith('6.12.40-') and x['python']=='3.12.3' and x['pynq']=='4.0.0',x
    return x
def memory():
    m={k:int(v.split()[0]) for k,v in (s.split(':',1) for s in read('/proc/meminfo').splitlines()) if v.strip().split() and v.strip().split()[0].isdigit()}
    return require(3000000<m['MemTotal']<4300000, {k:m.get(k) for k in ['MemTotal','MemAvailable','CmaTotal','CmaFree','SwapTotal']})
def pins():
    from importlib.metadata import distribution
    out={}
    for name,pin in [('pynqmetadata','7ff39f7e699b854973e4f894fb6e5272534a42f7'),('pynqutils','fe88b2fd04b6789bd2c9d50c47b140e8453a6886')]:
        d=distribution(name); j=json.loads(d.read_text('direct_url.json')); actual=j['vcs_info']['commit_id']; assert actual==pin,(name,actual)
        out[name]={'version':d.version,'commit':actual}
    return out
def maths():
    import pynq, numpy as np
    assert np.__version__=='1.26.4',np.__version__
    a=np.arange(64,dtype=np.int64).reshape(8,8); b=a@a.T
    assert int(b.sum())==510720,int(b.sum())
    return {'numpy':np.__version__,'matrix_sum':int(b.sum())}
def allocation():
    import pynq,numpy as np
    out=[]
    for n in [1024,262144]:
        b=None
        try:
            b=pynq.allocate(shape=(n,),dtype=np.uint32)
            p=np.arange(n,dtype=np.uint32)^np.uint32(0xA5A55A5A)
            b[:]=p; b.sync_to_device(); b.sync_from_device(); assert np.array_equal(b,p)
            out.append({'uint32_count':n,'bytes':n*4,'pattern_sync_compare':'pass'})
        except Exception as e:
            out.append({'uint32_count':n,'bytes':n*4,'status':'fail','error':type(e).__name__+': '+str(e)})
        finally:
            if b is not None: b.freebuffer()
    return out
def zocl():
    p=pathlib.Path('/sys/module/zocl'); nodes=[pathlib.Path(s).name for s in glob.glob('/dev/dri/*')]
    return require(p.exists() and bool(nodes),{'module_loaded':p.exists(),'dri_nodes':nodes,'fpga_manager_states':[read(s) for s in glob.glob('/sys/class/fpga_manager/*/state')]})
def storage():
    root=json.loads(subprocess.check_output(['findmnt','-J','/'],text=True))['filesystems'][0]
    disk=json.loads(subprocess.check_output(['lsblk','-b','-J','-o','NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS'],text=True))
    return require(root['fstype']=='ext4',{'root_fstype':root['fstype'],'root_source':root['source'],'root_bytes':os.statvfs('/').f_blocks*os.statvfs('/').f_frsize,'block_devices':disk,'swap':[{'type':v[1],'size_kib':int(v[2]),'used_kib':int(v[3])} for v in (line.split() for line in read('/proc/swaps').splitlines()[1:])],'machine_id_nonempty':bool(read('/etc/machine-id')),'ssh_host_private_key_count':len(glob.glob('/etc/ssh/ssh_host_*_key'))})
def environment():
    return require(bool(os.environ.get('XILINX_XRT')), {'xrt_environment_present':bool(os.environ.get('XILINX_XRT'))})

def device_probe():
    from pynq.pl_server.device import Device
    devices=Device.devices
    return require(bool(devices), {'registered_device_count':len(devices),'registered_device_types':[type(d).__name__ for d in devices]})

def main():
    R.clear()
    for name,fn in [('environment',environment),('identity',identity),('memory',memory),('installed_pins',pins),('numpy_math',maths),('zocl_devices',zocl),('root_storage',storage),('device_probe',device_probe),('allocation',allocation)]:
        check(name,fn)
    if R['allocation']['status']=='pass' and any(v.get('status')=='fail' for v in R['allocation']['details']):
        R['allocation']['status']='fail'
    print(json.dumps(R,indent=2))
    return 1 if any(v['status']!='pass' for v in R.values()) else 0

if __name__=='__main__':
    sys.exit(main())
