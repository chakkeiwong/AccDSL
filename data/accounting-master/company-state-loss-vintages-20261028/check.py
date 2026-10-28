"""Exact original loss-vintage discrimination using unchanged native components."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import fixture as f
ROOT,H=f.ROOT,Path(__file__).resolve().parent
PLAN='docs/plans/company-state-loss-vintages-20261028.md'
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    out=ap.parse_args().output.resolve();out.mkdir(exist_ok=False);start=time.monotonic()
    checks=[];cases=[];applications=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def run(n,b,status='proposed'):
        old=f.m.book.digest(b);r=f.m.propose(b);cases.append(dict(id=n,request=b,result=r))
        ck(n+'/request preserved',f.m.book.digest(b),old);ck(n+'/status',r['status'],status)
        ck(n+'/repeat proposal',f.m.book.digest(f.m.propose(b)),f.m.book.digest(r))
        ck(n+'/admission flags',all(r[k] is False for k in f.m.FLAGS),True)
        if r['status']=='proposed':
            applied=f.m.apply(b,r);applications.append(dict(id=n,result=applied))
            ck(n+'/apply',applied['status'],'applied');ck(n+'/applied exact proposal',applied.get('after'),r['proposal']['after'])
        else:ck(n+'/no proposal', 'proposal' in r,False)
        return r
    def quantities(n,r,opening,generated,used,expired,closing,income,postloss,tax):
        if r['status']!='proposed':return
        p=r['proposal'];fmt=f.m.book.fmt
        ck(n+'/exact totals',p['totals'],dict(zip(['opening','generated','used','expired','closing'],[fmt(Q(x)) for x in [opening,generated,used,expired,closing]])))
        ck(n+'/income before',p['taxable_profit_before_losses'],fmt(Q(income)))
        ck(n+'/income after',p['taxable_profit_after_losses'],fmt(Q(postloss)))
        ck(n+'/conditional tax',p['conditional_gross_current_tax'],fmt(Q(tax)))
        ck(n+'/loss-ledger scope',p['continuity_scope'],'loss ledger only; native financial carry unestablished')
    b0=f.generate();r0=run('generate40',b0);quantities('generate40',r0,0,40,0,0,40,-40,0,0)
    if r0['status']!='proposed':raise RuntimeError('generation probe invalid')
    s40=r0['proposal']['after'];b1=f.step(s40,2027,'30/1',[('loss-2026','30/1')]);r1=run('income30_first',b1)
    quantities('income30_first',r1,40,0,30,0,10,30,0,0)
    s10=r1['proposal']['after'];b2=f.step(s10,2028,'30/1',[('loss-2026','10/1')]);r2=run('income30_second',b2)
    quantities('income30_second',r2,10,0,10,0,0,30,20,5)
    last=r2['proposal']['after'];lot=last['lots'][0]
    ck('same lot identity',[x['proposal']['after']['lots'][0]['id'] for x in [r0,r1,r2]],['loss-2026']*3)
    ck('final lot original used remaining expired',[lot[k] for k in ['original','used','remaining','expired']],['40/1','40/1','0/1','0/1'])
    ck('three distinct periods',[x['start'] for x in last['history']],['2026-01-01','2027-01-01','2028-01-01'])
    ck('three distinct steps',last['seen'],['loss-step-2026','loss-step-2027','loss-step-2028'])
    ck('origin retained',lot['origin_reference'],s40['lots'][0]['origin_reference'])
    for n,state,year,expected in [('additional_loss10',s40,2027,50),('loss10_after_use30',s10,2028,20)]:
        b=f.step(state,year,'-10/1',generation=f'loss-{year}',cap='0/1');r=run(n,b)
        opening=40 if year==2027 else 10;quantities(n,r,opening,10,0,0,expected,-10,0,0)
        if r['status']=='proposed':
            lots=r['proposal']['after']['lots'];ck(n+'/two vintages',[x['id'] for x in lots],['loss-2026',f'loss-{year}'])
            ck(n+'/old vintage remains',lots[0],state['lots'][0]);ck(n+'/new vintage amount',lots[1]['remaining'],'10/1')
    b=f.step(s40,2027,'1/3',[('loss-2026','1/3')]);r=run('fractional_use',b)
    quantities('fractional_use',r,40,0,Q(1,3),0,Q(119,3),Q(1,3),0,0)
    b=f.step(s40,2027,'0/1');r=run('zero_income',b);quantities('zero_income',r,40,0,0,0,40,0,0,0)
    bad=[]
    def add(n,b,status):bad.append((n,deepcopy(b),status))
    b=deepcopy(b2);b['uses'][0]['amount']='30/1';add('reuse_consumed30',b,'invalid')
    b=deepcopy(b1);b['uses']*=2;add('duplicate_lot_use',b,'invalid')
    b=deepcopy(b1);b['uses'][0]['amount']='31/1';add('use_exceeds_profit',b,'invalid')
    b=deepcopy(b1);b['utilization_cap']=f.ex.known('20/1');add('use_exceeds_cap',b,'invalid')
    b=deepcopy(b1);b['utilization_cap']=dict(status='unknown',reason='Unresolved tax authority');add('unknown_cap',b,'unresolved')
    for key in ['eligible','expiry']:
        b=deepcopy(b1);b['state']['lots'][0][key]=dict(status='unknown',reason='Unresolved eligibility') if key=='eligible' else dict(kind='unknown',reason='Unresolved expiry')
        f.rehash(b);add('unknown_'+key,b,'unresolved')
    b=deepcopy(b1);b['state']['opening_inventory']=dict(status='unknown',reason='No complete loss inventory');f.rehash(b);add('unknown_inventory',b,'unresolved')
    b=deepcopy(b1);b['state']['lots'][0]['eligible']=f.ex.known(False);f.rehash(b);add('ineligible_lot',b,'unsupported')
    b=deepcopy(b1);b['state']['jurisdiction']='different-jurisdiction';f.rehash(b);add('wrong_jurisdiction',b,'invalid')
    b=deepcopy(b2);b['step_id']='loss-step-2027';add('duplicate_step',b,'invalid')
    b=f.step(s10,2029,'30/1',[('loss-2026','10/1')]);add('missing_period',b,'invalid')
    b=deepcopy(b2);b['state']['lots'][0]['remaining']='40/1';f.rehash(b);add('reset_remaining_without_usage',b,'invalid')
    b=deepcopy(b2);b['state']['lots']=[];f.rehash(b);add('forgotten_loss_lot',b,'invalid')
    b=deepcopy(b2);b['state_sha256']='0'*64;add('forged_state_hash',b,'invalid')
    b=f.step(s40,2027,'-10/1',[('loss-2026','1/1')],generation='loss-2027');add('negative_profit_use',b,'invalid')
    b=f.step(s40,2027,'-10/1',generation='loss-2026');add('reused_generation_identity',b,'invalid')
    b=deepcopy(b1);b['state']['lots'][0]['expiry']=f.ex.dated('2027-12-31');f.rehash(b);add('use_on_exclusive_expiry',b,'invalid')
    for n,b,status in bad:run(n,b,status)
    b=deepcopy(b1);b['state']['lots'][0]['expiry']=f.ex.dated('2028-01-01');f.rehash(b)
    r=run('expiry_at_close_after_use',b);quantities('expiry_at_close_after_use',r,40,0,30,10,0,30,0,0)
    b=f.step(r['proposal']['after'],2028,'30/1');r=run('income_after_expiry',b);quantities('income_after_expiry',r,0,0,0,0,0,30,30,Q(15,2))
    altered=deepcopy(r2);altered['proposal']['after']['lots'][0]['remaining']='40/1'
    rejected=f.m.apply(b2,altered);applications.append(dict(id='altered_apply',result=rejected))
    ck('altered proposal refused',rejected['status'],'invalid')
    # Coherent but unauthenticated history is not protected by recomputing a digest.
    b=deepcopy(b2);s=b['state'];s['lots'][0].update(original='70/1',remaining='40/1')
    s['history'][-1].update(generated='30/1',closing='40/1');b['uses'][0]['amount']='30/1';f.rehash(b)
    r=run('coherent_invented_extra_loss',b)
    if r['status']=='proposed':
        ck('invented loss reduces conditional tax',r['proposal']['conditional_gross_current_tax'],'0/1')
        ck('independent prior-state binding rejects',f.m.book.digest(s)==f.m.book.digest(s10),False)
        ck('original vintage quantity oracle rejects',s['lots'][0]['original']=='40/1',False)
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    originals=[r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id']=='SIM-F042']
    ck('exact original target',originals[0]['discriminating_case'],'Loss40 then taxable income30,30 or negative10')
    for row in checks:
        if len(json.dumps(row))>1400:
            row['actual_sha256']=f.m.book.digest(row.pop('actual'));row['expected_sha256']=f.m.book.digest(row.pop('expected'))
    failed=[c for c in checks if not c['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),proposal_cases=len(cases),apply_cases=len(applications),failed=failed,original_rows=['SIM-F042'],actual_tax_admission=False,financial_book_carry=False,external_history_authentication=False)
    for name,value in [('verification',v),('checks',checks),('original-rows',originals)]:dump(out/(name+'.json'),value)
    with gzip.open(out/'loss-results.json.gz','wt') as fh:json.dump(dict(proposals=cases,applications=applications),fh)
    paths={Path(__file__),H/'fixture.py',ROOT/PLAN,fm}
    paths.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only exact rational loss/reconciliation execution; no GPU imports',random_seeds='N/A deterministic',data_version='Original loss40/30/30/negative10 and explicit conditional eligibility/rate/vintages',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}))
    for name in ['fixture.py','check.py']:(out/name).write_bytes((H/name).read_bytes())
    print(json.dumps(dict(status=v['status'],checks=len(checks),proposal_cases=len(cases),apply_cases=len(applications),failed=[c['name'] for c in failed])));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
