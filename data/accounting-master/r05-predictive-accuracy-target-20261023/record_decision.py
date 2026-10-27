"""Record the research-purpose target and exact documentary fixtures once."""
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
from reference import check

U=Path(__file__).resolve().parent; R=U.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bound=lambda p:{'path':str(p.relative_to(R)),'sha256':sha(p)}
load=lambda p:json.loads(p.read_text())


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (U/'decision.json').exists() and not (U/'reference-results.json').exists()
    predecessor=R/'data/accounting-master/r05-source-timing-feasibility-20261023'
    timing=load(predecessor/'matrix.json')
    purpose=load(predecessor/'research-purpose-answer.json')
    assert timing['counts']['byte_admissions']==0
    result=check()
    decision={
      'schema':'accdsl.documentary.e3_predictive_accuracy_target.v1',
      'authority':'User answer in this session, 23 October 2026 Asia/Hong_Kong',
      'recorded_utc':datetime.now(timezone.utc).isoformat(),
      'purpose':purpose,
      'selected_target':{'outcome':'operating_cash flow','interval':'next_complete_fiscal_year',
        'population':'same nine named companies at future origins','issuer_weights':{f'i{k}':'1/9' for k in range(1,10)},
        'score':'asset-scaled CRPS with common positive as-of assets',
        'effect':'candidate_minus_locked_comparator','direction':'negative is better',
        'research_boundary':'Delta < 0; equality at zero is the directional comparison boundary'},
      'promotion':{'directional':'uncertainty bound below zero plus all validity vetoes',
        'material_improvement':'requires a separately justified negative margin; not selected',
        'economic_value':'not selected and not inferred'},
      'unresolved':['future-origin joint law Q','within-issuer origin weights b(i,t)',
        'fiscal grouping across asynchronous intervals','refit/window/cadence','fallback/service policy',
        'financial scope and target mapping','inference procedure/dependence theory',
        'confidence/multiplicity/replication','sample and resource budget'],
      'frozen_e3_preserved':True,'historical_vintage_admissions':0,
      'empirical_execution':False,'runtime_admitted':False,
      'predecessor_timing_matrix':bound(predecessor/'matrix.json'),
      'inference_source_transfer':False}
    with (U/'decision.json').open('x') as f: json.dump(decision,f,ensure_ascii=False,indent=2);f.write('\n')
    with (U/'reference-results.json').open('x') as f: json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))


if __name__=='__main__': main()
