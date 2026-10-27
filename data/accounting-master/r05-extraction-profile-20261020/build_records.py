"""One-time profile and fictional record construction, no experiment."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode=True
os.environ['CUDA_VISIBLE_DEVICES']='-1'
U=Path(__file__).resolve().parent
R=U.parents[2]

def bind(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(name,value):
    with (U/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    assert not (U/'source-ledger.json').exists(),'one-time construction'
    spec=importlib.util.spec_from_file_location('local_profile_checks',U/'compare.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    root=R/'data/accounting-master'
    mapping=[
        ('table_context','r04-pubtabnet-20261019/result.md','Use independent context/value labels beyond cell score.','Actual financial transfer and labels'),
        ('dataset_identity','r04-pubtablesv2-metadata-20261019/result.md','Bind exact split and source membership; retain failures.','Archive IDs,overlap and experiment revision'),
        ('matching_objective','r04-pubtablesv2-20261019/result.md','Declare raw-cell versus normalized table matching and macro/micro aggregation.','Historical benchmark metric/failure/merging protocol'),
        ('pair_heuristic','r04-grits-theory-20261020/result.md','Retain feasible lower and relaxation upper with exact scope.','Historical selected algorithm and tightness'),
        ('geometry','r04-grits-geometry-20261020/result.md','Distinguish enclosure from set union and pin source recipe.','Installed native correspondence'),
        ('text_binding','r04-pybind-strings-20261020/result.md','Validate scalar text/bytes/surrogates before equality shortcut.','Actual pylcs binary build and dependency version'),
        ('input_contract','r04-grits-input-contract-20261020/result.md','Check missingness,occupancy,frame,numeric intermediates and sample commit.','Workload budgets and deployed adapter'),
        ('global_bounds','r04-grits-assignment-bounds-20261020/result.md','Label fixed assignment upper or optimize a justified global upper.','Certified solver implementation'),
        ('numeric_bounds','r04-grits-float-bounds-20261020/result.md','Label estimates unless directed full-program enclosure is established.','Native arithmetic and tolerance/precision protocol'),
        ('prediction_boundary','r05-target-overlap-20261018/specification.md','Keep E3 target/inference separate from E1 diagnostic scores.','Population,weights,margin,confidence,sample size and inference'),
    ]
    rows=[{'id':i,'evidence':str((root/p).relative_to(R)),'action':a,'retained_unknown':g} for i,p,a,g in mapping]
    write('finding-crosswalk.json',rows)
    paths=[root/p for _,p,_,_ in mapping]+[
        root/'future-validation-20261015/protocol-ledger.md',root/'r05-target-overlap-20261018/target-sheets.json',
        root/'r05-vintage-admission-20261018/reconciliation.json',root/'protocol-delta-refresh-20261018/protocol-supplement.md',
        R/'docs/design/proposal/manuscript-early-conversion-20261018/sections/future-validation.tex',
        R/'docs/design/proposal/manuscript-early-conversion-20261018/chapters/03-literature.tex']
    anchors=[]
    for name,p,first,last in [
        ('e1_protocol',paths[-2],15,23),('e3_protocol',paths[-2],33,59),
        ('table_limit',paths[-1],199,239),
        ('evidence_roles',root/'future-validation-20261015/protocol-ledger.md',7,20),
        ('r05_target_choices',root/'r05-target-overlap-20261018/specification.md',1,47)]:
        anchors.append({'id':name,**bind(p),'first_line':first,'last_line':last,
            'excerpt':'\n'.join(p.read_text().splitlines()[first-1:last])})
    write('source-ledger.json',{'date':'2026-10-20','new_acquisitions':0,'bindings':[bind(p) for p in paths],
        'anchors':anchors,'scope':'Additive protocol reconciliation; prior source ledgers remain frozen.'})
    targets=json.loads((root/'r05-target-overlap-20261018/target-sheets.json').read_text())
    write('profile.json',{'status':'proposed_not_admitted','selected_e3_design':None,
        'unselected':{k:None for k in m.UNSELECTED},'e3_target_alternatives':[x['id'] for x in targets['sheets']],
        'e1_table_metric_role':'explanatory_diagnostic','e1_primary_criteria':['independent_context_value','source_coverage','unresolved_coverage'],
        'e1_hard_veto':'materially_wrong_admitted_fact_or_fabricated_locator_or_silent_loss_in_reviewed_conformance',
        'e3_primary_target':'operating_cash_flow','e3_primary_score':'CRPS_complete_probability_law_finite_first_moment',
        'e3_baseline_policy':'locked_same_information_economics_target_and_tuning',
        'selected_byte_vintage_admissions':0,'runtime_execution':False,'empirical_execution':False,
        'numeric_failures_receive_zero':False,'new_metric_default_selected':False,'whole_rows_closed':0,
        'record_groups':['identity','population_denominator','labels','transforms','metric_semantics','bounds_numeric_meaning','failures','decision_roles'],
        'user_target_question':'pending; no selection inferred from elapsed time'})
    packages=[
        {'package_id':'fictional-A','required':10,'resolved':10,'correct_context_value':9,'wrong_admitted':1,'unresolved':0,'status':'scored','diagnostic_score':'1'},
        {'package_id':'fictional-B','required':10,'resolved':8,'correct_context_value':8,'wrong_admitted':0,'unresolved':2,'status':'scored','diagnostic_score':'4/5'},
        {'package_id':'fictional-C','required':10,'resolved':0,'correct_context_value':0,'wrong_admitted':0,'unresolved':10,'status':'parse_failure','diagnostic_score':None},
        {'package_id':'fictional-D','required':10,'resolved':0,'correct_context_value':0,'wrong_admitted':0,'unresolved':10,'status':'unsupported_format','diagnostic_score':None}]
    write('fictional-packages.json',packages);write('fictional-results.json',m.summarize(packages))
    write('remaining-decisions.json',{'scientific_direction':['Choose E3 finite-panel,repeated-origin or future-issuer question'],
        'internal_preparation':['specific byte-vintage source routes','independent source/context label records','exact evaluator/build identities','task-defined population and strata proposals','source-backed numerical and inference conditions'],
        'requires_direction_then_design':['substantive weights','decision margin','confidence and multiplicity','sample-size/resource justification','matched inference procedure'],
        'held_actions':['runtime/controller','installation','empirical campaign','commit','outreach','publication','fees'],
        'other_independent_work':'R03 exact EPS,hedge allocation,CGU authority and insurance termination interpretation remain recorded open obligations.'})
    print(json.dumps({'constructed':True,'bindings':len(paths),'findings':len(rows),'fictional_result':m.summarize(packages)}))

if __name__=='__main__':main()
