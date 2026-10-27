"""Bounded staged source retrieval; no installation or acquired code execution."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess

os.environ['CUDA_VISIBLE_DEVICES']='-1'
UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
S=UNIT/'sources'


def repository():
    info=json.loads((S/'01-package.body').read_text())['info']
    urls=[info.get('home_page','')]+list((info.get('project_urls') or {}).values())
    repos={m.group(1).rstrip('/') for url in urls if url and (m:=re.fullmatch(r'https://github.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/?',url))}
    assert len(repos)==1, 'exact unambiguous metadata source required'
    return repos.pop()


def commit():
    matches=set(re.findall(r'"currentOid":"([0-9a-f]{40})"',(S/'02-repository.body').read_text()))
    assert len(matches)==1,'exact repository head required'
    return matches.pop()


def fetch(stem,url):
    assert not list(S.glob(stem+'.*')),'one-time request'
    assert len(list(S.glob('*.receipt.json')))<6,'six-request bound'
    body,header=S/(stem+'.body'),S/(stem+'.headers')
    command=['curl','--silent','--show-error','--location','--connect-timeout','10','--max-time','35',
        '--max-filesize','2097152','--proto','=https','--proto-redir','=https',
        '--dump-header',str(header.relative_to(ROOT)),'--output',str(body.relative_to(ROOT)),
        '--write-out','%{json}\n',url]
    started=datetime.now(timezone.utc).isoformat()
    result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    receipt=json.loads(result.stdout)
    with (S/(stem+'.receipt.json')).open('x') as handle:
        json.dump(receipt,handle,indent=2);handle.write('\n')
    with (S/(stem+'.invocation.json')).open('x') as handle:
        json.dump({'argv':command,'started_utc':started,'returncode':result.returncode,'stderr':result.stderr},handle,indent=2);handle.write('\n')
    print(json.dumps({'source':stem,'status':receipt['http_code'],'exitcode':result.returncode,
                      'bytes':receipt['size_download'],'seconds':receipt['time_total']}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('identity','repository','tree','selected'))
    stage=parser.parse_args().stage
    assert (UNIT/'protection.json').is_file(),'prepare first'
    if stage=='identity':fetch('01-package','https://pypi.org/pypi/pylcs/json')
    elif stage=='repository':fetch('02-repository','https://github.com/'+repository())
    elif stage=='tree':fetch('03-tree','https://api.github.com/repos/'+repository()+'/git/trees/'+commit()+'?recursive=1')
    else:
        tree=json.loads((S/'03-tree.body').read_text())
        selected=json.loads((UNIT/'source-selection.json').read_text())
        assert len(selected)<=3 and not tree['truncated'],'bounded source selection'
        for i,name in enumerate(selected,4):
            entry=next(r for r in tree['tree'] if r['path']==name)
            assert entry['type']=='blob' and entry['size']<2097152
            assert Path(name).suffix in ('.py','.cpp','.h','.hpp','.cc','.md','.txt','.toml')
            assert '..' not in Path(name).parts
            fetch(f'{i:02d}-source','https://raw.githubusercontent.com/'+repository()+'/'+commit()+'/'+name)


if __name__=='__main__':main()
