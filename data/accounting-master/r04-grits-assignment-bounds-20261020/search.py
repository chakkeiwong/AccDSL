"""Bounded exact local-oracle search; never executes acquired library code."""
from collections import Counter
import importlib.util
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
U=Path(__file__).resolve().parent
R=U.parents[2]
ORACLE=R/'data/accounting-master/r04-grits-theory-20261020/compare.py'

def compute():
    spec=importlib.util.spec_from_file_location('retained_local_math_oracle',ORACLE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    grids=[[list(x[:2]),list(x[2:])] for x in itertools.product('ab',repeat=4)]
    pair={}
    for i,a in enumerate(grids):
        for j,b in enumerate(grids):
            v=module.grid_scores(a,b)
            pair[i,j]={'L':v['current_lower_raw'],'O':v['exact_raw'],'U':v['current_upper_raw'],
                'rows':v['rows'],'columns':v['columns'],'shortcut':v['current_shortcut']}
    collections=list(itertools.combinations_with_replacement(range(16),2))
    summary=Counter();first=None
    for left in collections:
        for right in collections:
            matrices={k:[[pair[left[i],right[j]][k] for j in range(2)] for i in range(2)] for k in ('L','O','U')}
            scores={k:[v[0][0]+v[1][1],v[0][1]+v[1][0]] for k,v in matrices.items()}
            bestL=max(scores['L']);bestO=max(scores['O']);bestU=max(scores['U'])
            assert bestL<=bestO<=bestU
            summary['collection_pairs']+=1
            unique=scores['L'][0]!=scores['L'][1]
            summary['unique_lower_assignment']+=int(unique)
            possible=[i for i,x in enumerate(scores['L']) if x==bestL]
            violations=[i for i in possible if scores['U'][i]<bestO]
            summary['at_least_one_lower_maximizer_with_insufficient_upper']+=int(bool(violations))
            summary['all_lower_maximizers_with_insufficient_upper']+=int(len(violations)==len(possible))
            if unique and violations:
                summary['unique_assignment_insufficient_upper']+=1
                if first is None:
                    chosen=possible[0]
                    first={'left_ids':list(left),'right_ids':list(right),
                        'true_tables':[grids[x] for x in left],'predicted_tables':[grids[x] for x in right],
                        'matrices':matrices,'assignment_scores':scores,'chosen_assignment':chosen,
                        'assignments':[[[0,0],[1,1]],[[0,1],[1,0]]],
                        'selected_lower':scores['L'][chosen],'selected_upper':scores['U'][chosen],
                        'selected_exact':scores['O'][chosen],'global_exact':bestO,'global_upper':bestU,
                        'pair_details':[[pair[left[i],right[j]] for j in range(2)] for i in range(2)]}
    return {'domain':'All two-element multisets of the 16 binary 2x2 grids, on both sides.',
        'grid_count':16,'collection_count_per_side':len(collections),'pair_cache_count':len(pair),
        'summary':dict(summary),'first_unique_witness':first,
        'generic_example':{'L':[[1,0],[0,1]],'O':[[1,2],[2,1]],'U':[[1,2],[2,1]],
            'unique_lower_assignment':'diagonal','reported_selected_upper':2,'global_exact':4},
        'upstream_executed':False,'empirical_rate_claim':False}

if __name__=='__main__':
    assert not (U/'search-result.json').exists(),'one-time construction'
    result=compute()
    with (U/'search-result.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'summary':result['summary'],'witness':result['first_unique_witness']},ensure_ascii=True))
