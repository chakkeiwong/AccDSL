"""Preserve source-access observations without treating responses as papers."""
from pathlib import Path
from hashlib import sha256
import json
import platform
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def run():
    start=time.monotonic();record='--record' in sys.argv
    if record:assert not (HERE/'source-lock.json').exists()
    text=(HERE/'official-developers.txt').read_text()
    assert 'register here' in text and 'reference implementation' in text
    assert b'%PDF' not in (HERE/'francis-author-pdf.response').read_bytes()[:8]
    assert '403' in (HERE/'francis-author-pdf.headers').read_text().splitlines()[0]
    names=['official-developers.html','official-developers.txt','francis-author-pdf.response','francis-author-pdf.headers','audit.md','result.md','verify.py']
    locks={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in names}
    for name in ['docs/plans/accounting-simulator-source-match-20261025.md','docs/design/research/actus-core-correspondence-20261023.md',
                 'docs/design/research/software/actus-interface-20261023/build.gradle.kts']:
        locks[name]=sha(ROOT/name)
    observations={'official_access_page':'registration_requested','exact_core_match_obtained':False,
                  'francis_route':'unverified_url_returned_403_html','technical_paper_obtained':False,'global_continuation_blocked':False}
    if record:
        dump(HERE/'source-lock.json',locks);dump(HERE/'observations.json',observations)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'Bounded curl acquisitions; python3 -B data/accounting-master/simulator-source-match-20261025/verify.py --record',
            'source_urls':['https://www.actusfrf.org/developers',
                'https://www.researchgate.net/profile/Jack-Francis-3/publication/315834569_A_Simultaneous_Equation_Model_of_the_Firm_for_Financial_Analysis_and_Planning/links/5bfc7d1492851cbcdd744ec9/A-Simultaneous-Equation-Model-of-the-Firm-for-Financial-Analysis-and-Planning.pdf'],
            'acquisition_date':'2026-10-25','environment':sys.version,'platform':platform.platform(),
            'cpu_gpu':'CPU text/byte checks; no GPU framework imported','seeds':'N/A: source acquisition',
            'wall_seconds':time.monotonic()-start,'wall_scope':'verification only; acquisition not timed in this manifest',
            'data_version':'Exact downloaded responses; not matched library/paper versions',
            'plan':'docs/plans/accounting-simulator-source-match-20261025.md','result':str((HERE/'result.md').relative_to(ROOT)),
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['source-lock.json','observations.json']}})
    else:
        assert locks==json.loads((HERE/'source-lock.json').read_text())
        assert observations==json.loads((HERE/'observations.json').read_text())
        for name,h in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items():assert sha(ROOT/name)==h
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay','locked_files':len(locks),**observations}))
if __name__=='__main__':run()
