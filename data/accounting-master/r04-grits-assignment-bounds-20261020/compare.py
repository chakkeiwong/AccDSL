"""Read-only proof/witness and pinned-source verification."""
import ast
import copy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import struct

U=Path(__file__).resolve().parent
R=U.parents[2]

def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def local_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def independent_exact(a,b):
    # Enumerate row/column subsets directly; not the retained oracle DP.
    best=0
    for nr in range(3):
        for left_rows in itertools.combinations(range(2),nr):
            for right_rows in itertools.combinations(range(2),nr):
                for nc in range(3):
                    for left_cols in itertools.combinations(range(2),nc):
                        for right_cols in itertools.combinations(range(2),nc):
                            score=sum(a[i][k]==b[j][l] for i,j in zip(left_rows,right_rows)
                                      for k,l in zip(left_cols,right_cols))
                            best=max(best,score)
    return best

SUMMARY={'pairwise_bounds_invalidated':False,'reported_upper_is_fixed_assignment':True,
    'general_global_bound_guaranteed':False,'unique_binary_domain_counterexample_found':False,
    'tie_invariant_two_order_witness_found':True,'scipy_tie_rule_assumed':False,
    'float32_rounding_explains_integer_witness':False,'second_upper_assignment_has_mathematical_bound':True,
    'native_or_historical_execution':False}

def validate_summary(value):assert value==SUMMARY,'unsupported bound interpretation'

def check():
    count=0
    def need(ok,label):
        nonlocal count
        assert ok,label
        count+=1
    ledger=load(U/'source-ledger.json')
    for b in ledger['bindings']:need(sha(R/b['path'])==b['sha256'],'source binding')
    for a in ledger['anchors']:
        p=R/a['path'];need(sha(p)==a['sha256'],'anchor binding')
        need('\n'.join(p.read_text().splitlines()[a['first_line']-1:a['last_line']])==a['excerpt'],'anchor text')
    result=load(U/'search-result.json')
    # Replays are pure reads plus deterministic local arithmetic, not construction.
    need(local_module('bound_search',U/'search.py').compute()==result,'exact finite search replay')
    w=load(U/'tie-witness.json')
    need(local_module('bound_refinement',U/'refine.py').compute()==w,'tie refinement replay')
    need(w['found'] and w['matrices']['L']==w['swapped_matrices']['L'],'identical solver inputs')
    for i,a in enumerate(w['true_tables']):
        for j,b in enumerate(w['predicted_tables']):
            need(independent_exact(a,b)==w['matrices']['O'][i][j],'independent exact pair optimum')
    for name,mat in w['matrices'].items():
        for row in mat:
            for value in row:need(struct.unpack('!f',struct.pack('!f',value))[0]==value,'binary32 exact integer')
    for mat in (w['matrices'],w['swapped_matrices']):
        lower=[sum(mat['L'][i][p[i]] for i in range(2)) for p in itertools.permutations(range(2))]
        exact=[sum(mat['O'][i][p[i]] for i in range(2)) for p in itertools.permutations(range(2))]
        upper=[sum(mat['U'][i][p[i]] for i in range(2)) for p in itertools.permutations(range(2))]
        need(lower==[3,3],'lower tie')
        need(sorted(exact)==sorted(upper)==[3,4],'upper depends on assignment')
        need(max(lower)<=max(exact)<=max(upper),'separate upper optimization valid')
    need(w['assignment_scores']['U']==[4,3],'original order')
    need(result['first_unique_witness'] is None,'negative unique-witness result retained')
    need(result['summary']['collection_pairs']==18496 and result['summary']['unique_lower_assignment']==10636,'finite domain counts')
    need(result['summary']['at_least_one_lower_maximizer_with_insufficient_upper']==668,'tie-only examples')
    metric=R/'data/accounting-master/r04-pubtablesv2-20261019/sources/05-metric.py'
    tree=ast.parse(metric.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_hungarian_grits_matching')
    text=ast.unparse(fn)
    need('linear_sum_assignment(score_matrix, maximize=True)' in text,'assignment uses lower matrix')
    need('score_upper_bound_matrix[matched_true_indices, matched_pred_indices]' in text,'upper uses same matching')
    need(text.count('linear_sum_assignment(')==1,'no separate upper assignment here')
    validate_summary(load(U/'claim-support-ledger.json')['summary'])
    rejected=0
    for key in SUMMARY:
        bad=copy.deepcopy(SUMMARY);bad[key]=not bad[key]
        try:validate_summary(bad)
        except AssertionError:rejected+=1
    need(rejected==len(SUMMARY),'altered claim rejection')
    for name in ['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omission-risk']:
        need((U/(name+'-ledger.json')).is_file(),'source ledger')
    return {'assertions':count,'source_anchors':len(ledger['anchors']),'new_acquisitions':0,
        'exact_collection_pairs':18496,'unique_lower_assignments':10636,
        'unique_witness_found':False,'tie_conditional_cases':668,'tie_invariant_witness':True,
        'refinement_cases_examined':w['collections_examined_until_witness'],
        'altered_claim_controls_rejected':rejected,'upstream_executed':False,'whole_rows_closed':0}
