"""Read-only checks of proposed records and exact fictional denominators."""
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]

def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def summarize(rows):
    assert len({r['package_id'] for r in rows})==len(rows),'duplicate package'
    for r in rows:
        assert r['required']==r['resolved']+r['unresolved'],'coverage accounting'
        assert r['resolved']==r['correct_context_value']+r['wrong_admitted'],'resolved accounting'
        assert r['status'] in ['scored','parse_failure','unsupported_format']
        assert (r['diagnostic_score'] is not None)==(r['status']=='scored'),'no fabricated failure scores'
        if r['diagnostic_score'] is not None:assert 0<=Fraction(r['diagnostic_score'])<=1
    totals={k:sum(r[k] for r in rows) for k in ['required','resolved','unresolved','correct_context_value','wrong_admitted']}
    scores=[Fraction(r['diagnostic_score']) for r in rows if r['diagnostic_score'] is not None]
    return {**totals,'eligible_packages':len(rows),'diagnostic_scored_packages':len(scores),
        'conditional_diagnostic_mean':str(sum(scores)/len(scores)),
        'full_required_context_value_fraction':str(Fraction(totals['correct_context_value'],totals['required'])),
        'resolved_only_context_value_fraction':str(Fraction(totals['correct_context_value'],totals['resolved'])),
        'reviewed_conformance_veto':totals['wrong_admitted']>0,
        'population_accuracy_inference':False,'empirical_evidence':False}

UNSELECTED=['deployment_population','weights','improvement_margin','confidence_level','inference_procedure','sample_size']

def validate_profile(p):
    assert p['status']=='proposed_not_admitted'
    assert p['selected_e3_design'] is None
    assert all(p['unselected'][k] is None for k in UNSELECTED)
    assert p['e1_table_metric_role']=='explanatory_diagnostic'
    assert p['e3_primary_target']=='operating_cash_flow'
    assert p['e3_primary_score']=='CRPS_complete_probability_law_finite_first_moment'
    assert p['e3_baseline_policy']=='locked_same_information_economics_target_and_tuning'
    assert p['selected_byte_vintage_admissions']==0
    assert p['runtime_execution'] is False and p['empirical_execution'] is False
    assert p['numeric_failures_receive_zero'] is False
    assert p['new_metric_default_selected'] is False
    assert p['whole_rows_closed']==0

def check():
    count=0
    def need(ok,label):
        nonlocal count
        assert ok,label
        count+=1
    ledger=load(U/'source-ledger.json')
    for b in ledger['bindings']:need(sha(R/b['path'])==b['sha256'],'input identity')
    for a in ledger['anchors']:
        p=R/a['path'];need(sha(p)==a['sha256'],'anchor identity')
        need('\n'.join(p.read_text().splitlines()[a['first_line']-1:a['last_line']])==a['excerpt'],'anchor content')
    profile=load(U/'profile.json');validate_profile(profile)
    targets=load(R/'data/accounting-master/r05-target-overlap-20261018/target-sheets.json')
    need(targets['selected_design'] is None,'original design unselected')
    for k in UNSELECTED:need(targets['unselected'][k] is None,'original scientific choice unset')
    need(profile['e3_target_alternatives']==[x['id'] for x in targets['sheets']],'target alternatives preserved')
    vintage=load(R/'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json')
    need(len(vintage['rows'])==192,'complete report panel')
    need(all(x['selected_byte_available_at'] is None for x in vintage['rows']),'all byte vintages unknown')
    rows=load(U/'fictional-packages.json');result=summarize(rows)
    need(result==load(U/'fictional-results.json'),'exact result replay')
    for k,v in {'required':40,'resolved':18,'correct_context_value':17,'wrong_admitted':1,'unresolved':22,'eligible_packages':4,'diagnostic_scored_packages':2}.items():
        need(result[k]==v,k)
    need(result['conditional_diagnostic_mean']=='9/10','conditional diagnostic')
    need(result['full_required_context_value_fraction']=='17/40','full denominator')
    need(result['resolved_only_context_value_fraction']=='17/18','conditional accuracy')
    need(result['reviewed_conformance_veto'] is True,'wrong admitted unit veto')
    crosswalk=load(U/'finding-crosswalk.json')
    need(len(crosswalk)==10 and len({x['id'] for x in crosswalk})==10,'ten distinct source obligations')
    for row in crosswalk:
        need((R/row['evidence']).is_file() and bool(row['action']) and bool(row['retained_unknown']),'actionable source obligation')
    rejection_count=0
    for field,value in [('selected_e3_design','repeated_origins'),('e1_table_metric_role','promotion_criterion'),
        ('e3_primary_target','table_similarity'),('selected_byte_vintage_admissions',192),
        ('empirical_execution',True),('numeric_failures_receive_zero',True),('new_metric_default_selected',True),
        ('whole_rows_closed',1)]:
        bad=copy.deepcopy(profile);bad[field]=value
        try:validate_profile(bad)
        except AssertionError:rejection_count+=1
    for k in UNSELECTED:
        bad=copy.deepcopy(profile);bad['unselected'][k]='invented'
        try:validate_profile(bad)
        except AssertionError:rejection_count+=1
    for edit in ['zero_failed_score','drop_unresolved','duplicate']:
        bad=copy.deepcopy(rows)
        if edit=='zero_failed_score':bad[2]['diagnostic_score']='0'
        elif edit=='drop_unresolved':bad[2]['unresolved']=0
        else:bad.append(copy.deepcopy(bad[0]))
        try:summarize(bad)
        except AssertionError:rejection_count+=1
    need(rejection_count==17,'invalid profile/record controls')
    return {'assertions':count,'source_anchors':len(ledger['anchors']),'bound_inputs':len(ledger['bindings']),
        'source_findings_reconciled':10,'fictional_packages':4,'eligible_source_units':40,
        'original_target_alternatives':3,'unselected_scientific_fields':6,
        'historical_byte_vintage_admissions':0,'rejected_controls':rejection_count,
        'empirical_execution':False,'whole_rows_closed':0}
