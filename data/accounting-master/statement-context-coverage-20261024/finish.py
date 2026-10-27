"""One-time full-context control refresh after recorded replay."""
from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-statement-context-integration-20261024.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main():
    assert not (HERE/'control-refresh.json').exists()
    run=subprocess.run([sys.executable,'-B',str(HERE/'verify.py'),'--replay'],cwd=ROOT,text=True,capture_output=True,check=True)
    obs=json.loads(run.stdout);assert obs['passed']
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    note='\n'.join(['## Full statement contexts checked — 24 October 2026','',
        'The complete context reference passes 1,241 checks and replay; 124',
        'protected inputs remain unchanged. It preserves 256 observations and',
        '143 relations: 135 displayed differences, six derived subtotals and',
        'two unresolved dash-dependent calculations. Matched typed/text forms',
        'preserve economic instants separately from reporting periods.',
        'Result: '+REL+'/result.md.','','Next: '+NEXT+'.',
        'Integrate source relations and complete statement-context semantics,',
        'then re-audit general language architecture and the remaining phases.',
        'Version 3.57 remains 424 pages, not_ready until the successor passes.',
        'S1–S5 partial; S6 held; S7 deferred. No whole requirement closes.','',''])
    before={}
    for n in names:
        p=ROOT/n;before[n]=sha(p);dest=HERE/'control-before'/n
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        if n.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in n:rest='No command running. Preserve recorded packages and dirty work.\nNo commit/subagents/controller campaign/outreach/forecast experiment.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for n,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/n;d=json.loads(p.read_text());old={k:v for k,v in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=NEXT,latest_result=REL+'/result.md',updated='2026-10-24')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Full contexts:256 observations;143 relations;1241 checks/replay;124 protected files')
            a['next'][0]='Integrate statement contexts and relations into Version 3.58, then audit general architecture'
        dump(p,d);assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'replay-observation.json',obs)
    dump(HERE/'coverage-delta.json',{'whole_rows_closed':0,'remaining':'general source adapters,latent state,capability interoperability and independent/domain/human acceptance'})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'checks':obs['checks'],'controls':len(names),'next':NEXT}))
if __name__=='__main__':main()
