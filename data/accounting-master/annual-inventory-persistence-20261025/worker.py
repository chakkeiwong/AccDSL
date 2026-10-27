"""Bounded fresh-process reopen and explicit process-exit fault probes."""
from pathlib import Path
import json,os,sys
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import annual_inventory_store_v1 as m

def main():
    path,action=sys.argv[1:3]
    def fault(point):
        if point==action:os._exit(73)
    body=json.loads(Path(sys.argv[3]).read_text()) if len(sys.argv)>3 else None
    with m.Store(path,body,fault=fault) as store:
        if action=='inspect':result=store.inspect()
        else:result=store.advance(1,expected_cursor=store.cursor)
        print(json.dumps({'cursor':result['cursor'],'result_sha256':result['result_sha256'],'status':result['result']['status']}))
if __name__=='__main__':main()
