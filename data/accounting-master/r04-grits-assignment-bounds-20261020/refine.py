"""Separate bounded tie-invariant witness search; no SciPy or acquired execution."""
import importlib.util
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
U=Path(__file__).resolve().parent
R=U.parents[2]

def compute():
    path=R/'data/accounting-master/r04-grits-theory-20261020/compare.py'
    spec=importlib.util.spec_from_file_location('retained_grid_math',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    grids=[[list(x[:2]),list(x[2:])] for x in itertools.product('ab',repeat=4)]
    pair={(i,j):m.grid_scores(a,b) for i,a in enumerate(grids) for j,b in enumerate(grids)}
    seen=0
    for left in itertools.combinations_with_replacement(range(16),2):
        for right in itertools.combinations_with_replacement(range(16),2):
            seen+=1
            matrices={k:[[pair[left[i],right[j]][key] for j in range(2)] for i in range(2)]
                for k,key in [('L','current_lower_raw'),('O','exact_raw'),('U','current_upper_raw')]}
            if any(row[0]!=row[1] for row in matrices['L']):continue
            scores={k:[v[0][0]+v[1][1],v[0][1]+v[1][0]] for k,v in matrices.items()}
            if min(scores['U'])>=max(scores['O']):continue
            return {'found':True,'collections_examined_until_witness':seen,
                'true_tables':[grids[x] for x in left],'predicted_tables':[grids[x] for x in right],
                'matrices':matrices,'assignment_scores':scores,
                'swapped_matrices':{k:[list(reversed(row)) for row in v] for k,v in matrices.items()},
                'pair_details':[[pair[left[i],right[j]] for j in range(2)] for i in range(2)],
                'claim':'For any deterministic selection based only on L, at least one of the two prediction orders has selected U below global exact O.',
                'actual_scipy_tie_behavior':'not executed or assumed'}
    return {'found':False,'collections_examined_until_witness':seen}

if __name__=='__main__':
    assert not (U/'tie-witness.json').exists(),'one-time refinement'
    result=compute()
    with (U/'tie-witness.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))
