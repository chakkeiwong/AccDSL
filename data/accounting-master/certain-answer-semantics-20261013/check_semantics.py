"""Exact finite teaching example and protected source checks; no engine implementation."""
import hashlib,json,subprocess
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
b=json.loads((U/'baseline.json').read_text());checks={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for group in ['candidate_files','frozen','dependencies']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
histories=[frozenset({('A',100)}),frozenset({('B',100)})]
intersection=set.intersection(*(set(h) for h in histories))
union=set.union(*(set(h) for h in histories))
totals=[sum(a for _,a in h) for h in histories]
queries={
 'some_payable':lambda h:bool(h),
 'A_is_owed_100':lambda h:('A',100) in h,
 'B_is_owed_100':lambda h:('B',100) in h,
 'total_is_100':lambda h:sum(a for _,a in h)==100,
 'no_payable':lambda h:not h,
 'A_and_B_are_both_owed_100':lambda h:('A',100) in h and ('B',100) in h,
}
def classify(hs,q):
    if not hs:return {'status':'Infeasible','per_history':[]}
    values=[q(h) for h in hs]
    return {'status':'entailed' if all(values) else 'refuted' if not any(values) else 'undetermined_mixed','per_history':values}
answers={k:classify(histories,q) for k,q in queries.items()}
expected=['entailed','undetermined_mixed','undetermined_mixed','entailed','refuted','refuted']
for (k,v),e in zip(answers.items(),expected):checks['query:'+k]=v['status']==e
checks['intersection_empty']=intersection==set()
checks['union_total_is_wrong_for_every_history']=sum(a for _,a in union)==200 and 200 not in totals
checks['intersection_total_is_wrong_for_every_history']=sum(a for _,a in intersection)==0 and 0 not in totals
checks['family_totals_agree']=totals==[100,100]
checks['existential_not_tuple_membership']=answers['some_payable']['status']=='entailed' and not intersection
checks['open_search_witness_not_proof']=classify(histories[:1],queries['A_is_owed_100'])['status']=='entailed' and answers['A_is_owed_100']['status']=='undetermined_mixed'
scope_extension=histories+[frozenset()]
checks['scope_change_invalidates_existence']=classify(scope_extension,queries['some_payable'])['status']=='undetermined_mixed'
checks['scope_change_invalidates_total']=classify(scope_extension,queries['total_is_100'])['status']=='undetermined_mixed'
checks['empty_family_not_vacuous_truth']=all(classify([],q)['status']=='Infeasible' for q in queries.values())
for k,q in queries.items():
    positive=[i for i,h in enumerate(histories) if q(h)]
    negative=[i for i,h in enumerate(histories) if not q(h)]
    checks['partition:'+k]=set(positive).isdisjoint(negative) and sorted(positive+negative)==[0,1]
    checks['entailed_iff_no_counterexample:'+k]=(not negative)==(answers[k]['status']=='entailed')
    checks['refuted_iff_no_witness:'+k]=(not positive)==(answers[k]['status']=='refuted')
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=R)
checks['unrelated_index_preserved']=index==(U/'unrelated-index-before.txt').read_bytes()
checks['100_unrelated_entries']=len(index.splitlines())==100
out={'scope':'Constructed exhaustive two-history diagnostic; not issuer evidence or runtime conformance',
 'histories':[sorted(h) for h in histories],'certain_tuples':sorted(intersection),'possible_tuples':sorted(union),'totals':totals,'answers':answers,
 'extended_scope_existence':classify(scope_extension,queries['some_payable']),
 'checks':checks,'passed':sum(checks.values()),'failed':[k for k,v in checks.items() if not v]}
(U/'source-arithmetic-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['scope','answers','passed','failed']}))
raise SystemExit(bool(out['failed']))
