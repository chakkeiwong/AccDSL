"""Exact rational versus binary32 storage model; no NumPy or acquired code."""
from collections import Counter
from fractions import Fraction
import ast
import copy
import hashlib
from itertools import combinations
import json
from pathlib import Path
import struct

U=Path(__file__).resolve().parent
R=U.parents[2]
METRIC=R/'data/accounting-master/r04-pubtablesv2-20261019/sources/05-metric.py'

def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f32(value):return struct.unpack('!f',struct.pack('!f',float(value)))[0]
def bits(value):return struct.unpack('!I',struct.pack('!f',float(value)))[0]
def from_bits(value):return struct.unpack('!f',struct.pack('!I',value))[0]

def record(q):
    intermediate=float(q)
    value=f32(intermediate)
    exact=Fraction(value)
    err=exact-q
    b=bits(value)
    lower=Fraction(from_bits(b-1)) if err>0 else exact
    upper=Fraction(from_bits(b+1)) if err<0 else exact
    assert lower<=q<=upper
    # Check the nearest property for this finite-domain value using exact rationals.
    if b>0:assert abs(exact-q)<=abs(Fraction(from_bits(b-1))-q)
    assert abs(exact-q)<=abs(Fraction(from_bits(b+1))-q)
    return {'exact':str(q),'binary64_hex':intermediate.hex(),
        'binary64_signed_error':str(Fraction(intermediate)-q),
        'binary32_bits':f'{b:08x}','binary32_value':repr(value),
        'binary32_exact':str(exact),'signed_error':str(err),
        'direction':'up' if err>0 else 'down' if err<0 else 'exact',
        'illustrative_outward_lower':str(lower),'illustrative_outward_upper':str(upper)}

def lcs(a,b):
    # Independent exhaustive string subsequences, not a library call.
    def subs(s):return {tuple(s[i] for i in c) for k in range(len(s)+1) for c in combinations(range(len(s)),k)}
    return max(map(len,subs(a)&subs(b)))

def compute():
    pairs=[('up_two_thirds','a','ab',Fraction(2,3)),
        ('down_seven_tenths','abcdefgXXX','abcdefgYYY',Fraction(7,10)),
        ('exact_half','a','abc',Fraction(1,2)),('exact_one','a','a',Fraction(1)),
        ('exact_zero','a','b',Fraction(0))]
    examples=[]
    for name,a,b,expected in pairs:
        length=lcs(a,b);q=Fraction(2*length,len(a)+len(b));assert q==expected
        examples.append({'id':name,'a':a,'b':b,'lcs':length,'one_cell_grid':True,**record(q)})
    counts=Counter();unique={}
    for m in range(1,25):
        for n in range(1,25):
            for k in range(min(m,n)+1):
                q=Fraction(2*k,m+n)
                if q not in unique:unique[q]=record(q)
                counts[unique[q]['direction']]+=1
    distinct=Counter(r['direction'] for r in unique.values())
    q=Fraction(7,10);delta=Fraction(1,2**30)
    assert q<q+delta and f32(q)==f32(q+delta)
    return {'model':'Exact rational -> Python binary64 -> struct IEEE binary32; no NumPy execution.',
        'examples':examples,'rational_domain':{'m_range':[1,24],'n_range':[1,24],'k_range':'0..min(m,n)',
            'triples':sum(counts.values()),'triple_directions':dict(counts),
            'unique_rationals':len(unique),'unique_directions':dict(distinct),
            'meaning':'Combinatorial representation census, not frequency or probability in a dataset.'},
        'abstract_order_collapse':{'q':str(q),'larger':str(q+delta),'difference':str(delta),
            'common_binary32':repr(f32(q)),'grid_realization_claimed':False},
        'sum_order_or_native_runtime_checked':False}

SUMMARY={'nearest_binary32_preserves_all_lower_directions':False,
    'nearest_binary32_preserves_all_upper_directions':False,
    'one_cell_realizable_witnesses':True,'native_numpy_conversion_executed':False,
    'historical_score_impact_established':False,'all_gaps_fixed_by_one_ulp_padding':False,
    'outward_conversion_from_exact_rational_is_local_enclosure':True,
    'second_upper_assignment_alone_certifies_numeric_bound':False}

def validate_summary(value):assert value==SUMMARY,'unsupported rounding conclusion'

def check():
    count=0
    def need(ok,label):
        nonlocal count
        assert ok,label
        count+=1
    ledger=load(U/'source-ledger.json')
    for b in ledger['bindings']:need(sha(R/b['path'])==b['sha256'],'source identity')
    for a in ledger['anchors']:
        p=R/a['path'];need(sha(p)==a['sha256'],'anchor identity')
        need('\n'.join(p.read_text().splitlines()[a['first_line']-1:a['last_line']])==a['excerpt'],'anchor text')
    result=compute();need(load(U/'witnesses.json')==result,'deterministic exact replay')
    examples={x['id']:x for x in result['examples']}
    need(examples['up_two_thirds']['direction']=='up','lower rises above exact')
    need(examples['down_seven_tenths']['direction']=='down','upper drops below exact')
    need(examples['up_two_thirds']['binary32_bits']=='3f2aaaab','two-thirds bits')
    need(examples['down_seven_tenths']['binary32_bits']=='3f333333','seven-tenths bits')
    for r in result['examples']:
        need(Fraction(r['illustrative_outward_lower'])<=Fraction(r['exact'])<=Fraction(r['illustrative_outward_upper']),'local enclosure')
    need(result['rational_domain']['triples']==5476,'declared finite domain')
    need(all(result['rational_domain']['triple_directions'][k]>0 for k in ['up','down','exact']),'all rounding directions present')
    fn=next(n for n in ast.parse(METRIC.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='_hungarian_grits_matching')
    text=ast.unparse(fn)
    need('score_matrix = np.empty((num_true_grids, num_pred_grids), dtype=np.float32)' in text,'lower dtype')
    need('score_upper_bound_matrix = np.empty((num_true_grids, num_pred_grids), dtype=np.float32)' in text,'upper dtype')
    need('float(true_positive_scores_per_grid.sum())' in text,'float conversion after sum')
    need('float(true_positive_scores_upper_bound.sum())' in text,'upper float conversion after sum')
    need('nextafter' not in text,'no directed storage in selected function')
    validate_summary(load(U/'claim-support-ledger.json')['summary'])
    rejected=0
    for key in SUMMARY:
        bad=copy.deepcopy(SUMMARY);bad[key]=not bad[key]
        try:validate_summary(bad)
        except AssertionError:rejected+=1
    need(rejected==len(SUMMARY),'altered summaries')
    for name in ['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omission-risk']:
        need((U/(name+'-ledger.json')).is_file(),'additive ledger')
    return {'assertions':count,'source_anchors':len(ledger['anchors']),'new_acquisitions':0,
        'realizable_one_cell_examples':len(result['examples']),
        'rational_triples':result['rational_domain']['triples'],
        'unique_rationals':result['rational_domain']['unique_rationals'],
        'altered_controls_rejected':rejected,'upstream_executed':False,'whole_rows_closed':0}
