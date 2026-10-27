"""Inspect retained nested shapes; no new financial validator is promoted."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(HERE.parent/'authored-state-invariants-20261026'))
import guards
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def pointer(parts):return '/'+ '/'.join(x.replace('~','~0').replace('/','~1') for x in parts)

def main():
    start=time.monotonic();assertions=[];summaries=[];projections=[];controls=[]
    def ensure(ok,label):assertions.append(dict(check=label,passed=bool(ok)));assert ok,label
    paths=['scripts/receivable_term_history_v1.py','scripts/receivable_term_text_v1.py',
           'scripts/method_collections_v1.py','scripts/method_collection_totals_v1.py',
           'data/accounting-master/authored-state-invariants-20261026/guards.py',
           'data/accounting-master/receivable-term-history-20261025/evidence.json',
           'data/accounting-master/receivable-term-history-20261025/source-lock.json',
           'data/accounting-master/invariant-unicode-repair-20261026/checks.json']
    lock={n:sha(ROOT/n) for n in paths};dump('source-lock.json',lock)
    evidence=read(ROOT/paths[5])['cases']
    for chart,case in evidence.items():
        states=[('migration',case['migration']['state'])]
        states += [(f'event-{i}',r['result']['after']) for i,r in enumerate(case['steps'])]
        states += [('carry',case['carry']['after'])]
        for label,state in states:
            rows=[]
            for claim_id,claim in state['book']['memory']['claims'].items():
                for kind in ('terms','assessments'):
                    for child_id,row in claim[kind].items():
                        path=pointer(['claims',claim_id,kind,child_id])
                        found,actual=guards.base.binding.located(state['book']['memory'],path)
                        ensure(found and actual==row,chart+':'+label+':exact_path')
                        for key,value in row.items():
                            leaf=path+'/'+key
                            ensure(leaf in state['book']['memory_types'],chart+':'+label+':typed_leaf')
                            guards.core.scalar(value,state['book']['memory_types'][leaf]['kind'])
                        rows.append(dict(claim_id=claim_id,kind=kind,child_id=child_id,path=path,
                                         parent_issued=claim['issued'],value=deepcopy(row)))
            projections.append(dict(chart=chart,state=label,state_sha256=guards.core.digest(state),rows=rows))
            summaries.append(dict(chart=chart,state=label,claims=len(state['book']['memory']['claims']),
                                  terms=sum(r['kind']=='terms' for r in rows),assessments=sum(r['kind']=='assessments' for r in rows)))
        final=case['final']['book']['memory']['claims']['invoice/a~1']
        ensure(final['assessments']['imported']['term_id']=='initial' and final['assessments']['imported']['overdue']=='20/1',chart+':old_basis')
        ensure(final['terms'][final['current_term']]['due']=='2027-05-31',chart+':current_due')
        imported=final['assessments']['imported']
        naive=imported['remaining'] if imported['as_of']>final['due'] else '0/1'
        ensure(naive!=imported['overdue'],chart+':current_due_is_wrong_for_old_assessment')
        controls.append(dict(case=chart+':historical_due_discriminator',historical_overdue=imported['overdue'],
                             incorrectly_using_current_due=naive))
    # Two distinct claims may reuse the same local term ID.
    left=deepcopy(evidence['alpha']['final']['book']['memory']['claims']['invoice/a~1'])
    right=deepcopy(left);right['terms']['initial']['due']='2027-02-10'
    owners={'invoice/a~1':left,'invoice/~other':right}
    local=[k for row in owners.values() for k in row['terms']]
    qualified=[pointer([owner,k]) for owner,row in owners.items() for k in row['terms']]
    ensure(len(set(local))<len(local) and len(set(qualified))==len(qualified),'claim_qualified_keys_prevent_false_match')
    controls.append(dict(case='claim_qualified_keys',local_keys=local,qualified_keys=qualified))
    # Insertion order, effective-date order and lexical key order are distinct.
    terms=left['terms'];reverse=dict(reversed(list(terms.items())))
    chronology=sorted(reverse,key=lambda k:reverse[k]['effective'])
    ensure(list(reverse)!=chronology and sorted(reverse)!=chronology,'explicit_order_required')
    controls.append(dict(case='order_discriminator',insertion=list(reverse),lexical=sorted(reverse),effective=chronology))
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    dump('projections.json',projections);dump('states.json',summaries);dump('controls.json',controls);dump('assertions.json',assertions)
    checks=dict(passed=True,retained_states=len(summaries),charts=2,controls=len(controls),assertions=len(assertions),
                protected_files=len(lock),diagnostic_only=True,new_financial_validator=False)
    dump('checks.json',checks)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/nested-term-invariant-audit-20261026/probe.py',
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',
      wall_seconds=time.monotonic()-start,data_version=sha(HERE/'source-lock.json'),
      plan_file='docs/plans/accounting-nested-term-invariant-audit-20261026.md',
      result_file='data/accounting-master/nested-term-invariant-audit-20261026/result.md',
      artifacts=['states.json','projections.json','controls.json','checks.json','assertions.json','obligations.md'],
      timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(checks))

if __name__=='__main__':main()
