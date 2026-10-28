"""Original SIM-F006 native discriminator and independent gross-history oracle."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import fixture as f
ROOT, HERE = f.ROOT, Path(__file__).resolve().parent
PLAN = 'docs/plans/company-state-gross-equity-history-20261028.md'
CHAPTER = 'docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation/15-ownership-case.tex'

def dump(path, value):
    path.write_text(json.dumps(value, indent=2)+chr(10))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();checks=[];runs=[];oracles=[]
    def check(name,actual,expected):
        checks.append(dict(name=name,passed=actual==expected,actual=actual,expected=expected))
    def execute(name,body):
        before=deepcopy(body);r=f.program.run(body)
        check(name+'/input immutable',body==before,True)
        check(name+'/entire native replay',f.program.verify(body,r),True)
        runs.append(dict(id=name,input=body,result=r));return r
    originals=json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())
    row=next(x['original_row'] for x in originals['rows'] if x['original_row']['id']=='SIM-F006')
    check('original exact target',row['discriminating_case'],'Issue thirty shares and repurchase ten versus issue twenty')
    check('original price passage retained','issue of thirty shares at 4 and repurchase of ten at 6' in (ROOT/CHAPTER).read_text(),True)
    old_apply=f.native.Engine.apply
    f.native.Engine.apply=lambda *a,**k: (_ for _ in ()).throw(AssertionError('undeclared native fallback forbidden'))
    families={};valid={}
    try:
        for owner in ['alpha','beta']:
            for history in ['issue_only','issue_and_retire']:
                name=owner+'/'+history;body,m=f.make(history,owner);r=execute(name,body)
                valid[name]=(body,r,m)
                check(name+'/complete',r['status'],'complete_provisional')
                if r['status']!='complete_provisional':continue
                transactions=[(20,3)] if history=='issue_only' else [(30,4),(-10,6)]
                before=deepcopy(body['opening']);gross=[];expected_states=[]
                for i,(shares,price) in enumerate(transactions):
                    cmd=body['commands'][i];t=r['trace'][i]['result']['transition'];amount=Q(shares)*price
                    check(name+f'/{i}/preceding state',t['before_sha256'],f.program.digest(before))
                    balances=deepcopy(before['balances'])
                    balances[m['cash']]=f.fmt(Q(balances[m['cash']])+amount)
                    balances[m['capital']]=f.fmt(Q(balances[m['capital']])-amount)
                    memory=deepcopy(before['memory']);memory['terms']['new_shares']=f.fmt(Q(memory['terms']['new_shares'])+shares)
                    memory['terms']['stage']=f.fmt(4+i)
                    journal={account:'0/1' for account in balances}
                    journal.update({m['cash']:f.fmt(amount),m['capital']:f.fmt(-amount)})
                    check(name+f'/{i}/all balances',t['after']['balances'],balances)
                    check(name+f'/{i}/all memory',t['after']['memory'],memory)
                    check(name+f'/{i}/all journal accounts',t['journal'],journal)
                    check(name+f'/{i}/conservation',str(sum(Q(v) for v in t['journal'].values())),'0')
                    check(name+f'/{i}/dated event',t['after']['date'],cmd['event']['date'])
                    check(name+f'/{i}/event identity',t['after']['seen'],before['seen']+[cmd['event']['id']])
                    flow=[{k:x[k] for k in ['event_id','date','activity','origin','amount']} for x in t['flows']]
                    expected_flow=[dict(event_id=cmd['event']['id'],date=cmd['event']['date'],activity='financing',origin=cmd['method_key'],amount=f.fmt(amount))]
                    check(name+f'/{i}/gross flow',flow,expected_flow)
                    check(name+f'/{i}/old shares preserved',memory['terms']['old_shares'],'100/1')
                    expected_states.append(dict(balances=balances,memory=memory,journal=journal,flows=expected_flow))
                    gross.append(amount);before=t['after']
                report=r['trace'][-1]['result']
                receipts=sum((x for x in gross if x>0),Q());payments=-sum((x for x in gross if x<0),Q())
                check(name+'/reported',report['status'],'reported')
                check(name+'/BS',report['balance_sheet'],dict(total_assets='70/1',total_liabilities='0/1',equity_including_profit='70/1'))
                check(name+'/income',report['income'],dict(income='0/1',expenses='0/1',profit='0/1'))
                expected_totals=dict(asset='70/1',liability='0/1',equity='70/1',income='0/1',expense='0/1')
                check(name+'/all closing totals',report['closing_totals'],expected_totals)
                expected_activities={k:dict(receipts='0/1',payments='0/1',net='0/1') for k in ['operating','investing']}
                expected_activities['financing']=dict(receipts=f.fmt(receipts),payments=f.fmt(payments),net='60/1')
                check(name+'/all cash activities',report['cash_flows']['activities'],expected_activities)
                check(name+'/cash bridge',[report['cash_flows'][k] for k in ['opening_cash','closing_cash','net_movement']],['10/1','70/1','60/1'])
                check(name+'/equity bridge',[report['equity'][k] for k in ['opening','direct_movements','profit','closing']],['10/1','60/1','0/1','70/1'])
                check(name+'/all reconciliations',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                check(name+'/gross equity movements',report['equity']['movements'],body['commands'][-1]['equity_movements'])
                check(name+'/gross cash retained',[x['amount'] for x in report['cash_flows']['gross_origins']],[f.fmt(x) for x in gross])
                check(name+'/unresolved note retained',report['notes'],body['commands'][-1]['notes'])
                check(name+'/no admission',[r[k] for k in ['source_admission','accounting_admission','posting_authorized']],[False]*3)
                check(name+'/closing share count',str(Q(before['memory']['terms']['old_shares'])+Q(before['memory']['terms']['new_shares'])),'120')
                oracles.append(dict(id=name,expected_states=expected_states,expected_activities=expected_activities))
                families[history]=dict(gross_issue_cash=f.fmt(receipts),retirement_cash=f.fmt(payments),net_cash='60/1',net_shares='20/1',probability=None)
            a,b=[valid[owner+'/'+h][1] for h in ['issue_only','issue_and_retire']]
            check(owner+'/same closing balances',a['current']['balances'],b['current']['balances'])
            check(owner+'/different histories',a['trace']==b['trace'],False)
            check(owner+'/net price not all transaction prices',Q(60)/20 in [Q(4),Q(6)],False)
        baseline,m=f.make('issue_and_retire')
        def mutate_input(b,key,value):b['commands'][1]['event']['inputs'][key]['value']=value
        trials=[]
        for name,key,value in [('too_many_shares','shares','31/1'),('cash_shortfall','price','20/1'),('zero_price','price','0/1'),('negative_shares','shares','-1/1')]:
            b=deepcopy(baseline);mutate_input(b,key,f.program.engine.known(value));trials.append((name,b,'stopped_provisional','invalid'))
        b=deepcopy(baseline);mutate_input(b,'price',dict(status='unknown',reason='Unknown purchase price'));trials.append(('unknown_price',b,'stopped_provisional','unresolved'))
        b=deepcopy(baseline);del b['commands'][1]['event']['inputs']['price'];trials.append(('missing_price',b,'invalid',None))
        b=deepcopy(baseline);b['commands'][1]['event']['inputs']['shares']['type']=deepcopy(b['commands'][1]['event']['inputs']['price']['type']);trials.append(('wrong_units',b,'invalid',None))
        b=deepcopy(baseline);b['commands'][1]['event']['id']='equity_issue';trials.append(('duplicate_identity',b,'stopped_provisional','invalid'))
        b=deepcopy(baseline);b['commands'][1]['event']['date']='2027-01-04';trials.append(('backdated_retirement',b,'stopped_provisional','invalid'))
        b=deepcopy(baseline);b['commands']=[b['commands'][1],b['commands'][0],b['commands'][2]];trials.append(('retirement_before_issue',b,'stopped_provisional','invalid'))
        for name,b,status,stop in trials:
            r=execute('control/'+name,b);check(name+'/refusal',r['status'],status)
            if r['status']=='stopped_provisional':
                check(name+'/reason status',r['stop']['status'],stop)
                before=b['opening'] if not r['trace'] else r['trace'][-1]['result']['transition']['after']
                check(name+'/atomic whole state',r['current'],before)
                check(name+'/no final report',len(r['reports']),0)
        b=deepcopy(baseline);e=b['registry']['entries']['equity_retire']
        e['method']['memory']['definition']['operations']=[x for x in e['method']['memory']['definition']['operations'] if x['id']!='write.new_shares']
        e['method_sha256']=f.program.digest(e['method']);r=execute('mutation/missing_share_retirement',b)
        check('mutation/native permits self-consistent authored method',r['status'],'complete_provisional')
        check('mutation/share oracle detects missing decrement',r['current']['memory']['terms']['new_shares'],'30/1')
        check('mutation/balanced statements do not catch share omission',r['reports'][-1]['result']['reconciliations'] if isinstance(r['reports'][-1],dict) and 'result' in r['reports'][-1] else r['trace'][-1]['result']['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
    finally:f.native.Engine.apply=old_apply
    selections=[]
    def select(name,note,cutoff,ids,status,applied):
        actual=f.select_histories(families,note,cutoff);expected=dict(status=status,ids=ids,applied=applied)
        check('note/'+name,actual,expected);selections.append(dict(id=name,note=note,cutoff=cutoff,result=actual))
    both=['issue_only','issue_and_retire']
    select('absent',None,219,both,'conditional_family',False)
    for label,values,ids in [('simple',('60','0'),['issue_only']),('gross',('120','60'),['issue_and_retire']),('contradiction',('100','40'),[])]:
        note=dict(gross_issue_cash=values[0],retirement_cash=values[1],available_at=220)
        select(label+'/earlier',note,219,both,'conditional_family',False)
        select(label+'/available',note,220,ids,'conditional_family' if ids else 'conflict',True)
    select('unknown_timing',dict(gross_issue_cash='120',retirement_cash='60',available_at=None),220,both,'unresolved_availability',False)
    select('unknown_amount',dict(gross_issue_cash='120',retirement_cash=None,available_at=220),220,both,'unresolved_amount',False)
    select('float_amount',dict(gross_issue_cash=120.0,retirement_cash='60',available_at=220),220,[],'invalid',False)
    select('wrong_fields',dict(net_cash='60',available_at=220),220,[],'invalid',False)
    check('no history probability',[x['probability'] for x in families.values()],[None,None])
    paths=[Path(__file__),HERE/'fixture.py',ROOT/PLAN,ROOT/CHAPTER,ROOT/'data/accounting-master/unified-program-20261028/failure-map.json']
    paths += [Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT)]
    hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
    failed=[x for x in checks if not x['passed']]
    v=dict(status='fail' if failed else 'pass',checks=len(checks),native_runs=len(runs),note_cases=len(selections),failed=failed,original_row='SIM-F006',original_status_changed=False,general_repurchase_admission=False)
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only exact rational execution; no accelerator imports',random_seeds='N/A deterministic fixtures',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,data_version='Original SIM-F006 plus explicit new synthetic retirement method',plan_file=PLAN,result_file=str((HERE/'result.md').relative_to(ROOT)),source_hashes=hashes)
    for name,obj in [('verification',v),('checks',checks),('runs',runs),('oracles',oracles),('finite-family',families),('note-results',selections),('run-manifest',manifest),('original-row',row)]:dump(out/(name+'.json'),obj)
    for name in ['check.py','fixture.py']:(out/name).write_bytes((HERE/name).read_bytes())
    print(json.dumps(v));return bool(failed)

if __name__=='__main__':raise SystemExit(main())

