"""Classify existing owners without executing, merging or replacing them."""
from pathlib import Path
from hashlib import sha256
import argparse
import ast
from copy import deepcopy
from datetime import datetime, timezone
import json
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();checks=[];lock={}
    def check(name,actual,expected=True):
        checks.append(dict(name=name,passed=actual==expected,actual=actual,expected=expected))
    def protect(path):
        p=ROOT/path;lock[path]=sha256(p.read_bytes()).hexdigest();return p
    def signatures(path):
        tree=ast.parse(protect(path).read_text());found={}
        for node in tree.body:
            if isinstance(node,ast.FunctionDef):found[node.name]=ast.unparse(node.args)
            elif isinstance(node,ast.ClassDef):
                for f in node.body:
                    if isinstance(f,ast.FunctionDef):found[node.name+'.'+f.name]=ast.unparse(f.args)
        return found
    baseline='data/accounting-master/compatibility-current-20261028/registry.json'
    prior=json.loads(protect(baseline).read_text())
    roles={
        'method':'method_compiler','authored_program':'program_compiler_and_runner',
        'inline_invariant_program':'program_compiler_and_runner','selected_company':'selected_lifecycle_program',
        'complete_claims':'selected_population_program','nested_contract':'state_definition_and_assessment',
        'term_event':'selected_event_executor','term_program':'selected_sequence_executor',
        'selected_reading':'source_constraint_constructor','temporal':'temporal_constraint_solver',
        'retained_history':'source_history_attachment','typed_history':'typed_history_attachment',
        'selected_history':'selected_source_history_attachment','opening':'conditional_opening_mapper',
        'transition':'financial_transition_owner','continuation':'opening_transition_report_composer',
        'report':'report_query_owner','carry':'closing_memory_owner'}
    check('review covers exact indexed identifiers',sorted(roles),sorted(x['id'] for x in prior['interfaces']))
    rows=[]
    for row in prior['interfaces']:
        actual=signatures(row['implementation'])
        for name,args in row['signatures'].items():
            check(row['profile']+' signature '+name,actual.get(name),args)
        rows.append(dict(profile=row['profile'],role=roles[row['id']],native_interface=deepcopy(row),
            state_contract='Exact native inputs/context and effect owner in preserved interface record',
            population_contract='Supplied domain only; no inferred actual-company completeness',
            actor_information='Use native context/clock contract; no additional actor admission',
            evidence_class='reused inspected native interface plus current identity/signature verification'))
    sector=[
      ('InsurancePAADatedBook/1','conditional_interim_program','insurance-paa-dated-book-20261027/bridge.py',{'propose':'body'},'insurance-paa-dated-book-20261027/contract.md','Distinct issued/held groups, fixed calendar and finite synthetic cases; no annual carry'),
      ('BankComponents/1','documentary_lending_commitment_book','extended-method-exchanges-20261015/bank/verify_exchanges.py',{'Auditor.dispatch':'self, rqref, w'},'extended-method-exchanges-20261015/bank/semantic-contract.md','Finite dated loan commitment, supplied draw/default premises and expiry; not general contract lifecycle'),
      ('BankComponents/2','documentary_transfer_classification_book','extended-method-exchanges-20261015/bank-v2/verify_exchanges.py',{'Auditor.dispatch':'self, rqref, w'},'extended-method-exchanges-20261015/bank-v2/semantic-contract.md','Separate transfer/options/classification memory; foreign profile refused'),
      ('BankAssessment/1','conditional_prudential_and_loss_queries','extended-method-exchanges-20261015/bank-assessment/verify_exchanges.py',{'Auditor.request':'self, rq, sub, w','Auditor.response':'self, ex'},'extended-method-exchanges-20261015/bank-assessment/semantic-contract.md','Evidence-view/cutoff checks and per-metric unknowns; queries do not post or grant distribution authority'),
      ('BankAssessmentExactTime/1','exact_clock_identity_successor','exact-bank-profile-adoption-20261026/successor.py',{'Auditor.profile_contract':'self','Auditor.request':'self, rq, sub, w','Auditor.response':'self, exchange'},'exact-bank-profile-adoption-20261026/semantic-contract.md','Exact clock envelope; unchanged underlying financial checker, new receipts where identity changes')]
    for profile,role,implementation,sigs,authority,limit in sector:
        implementation='data/accounting-master/'+implementation;authority='data/accounting-master/'+authority
        actual=signatures(implementation);protect(authority)
        for name,args in sigs.items():check(profile+' signature '+name,actual.get(name),args)
        rows.append(dict(profile=profile,role=role,implementation=implementation,signatures=sigs,authority=authority,
            state_contract=limit,population_contract='Exact retained finite native case population',
            actor_information='Native declared views only; no actual-source or authenticated receipt admission',
            evidence_class='reused sector annex and direct contract/source inspection'))
    additions=[
      ('CompanyOperationPathDraft/1','annual_operation_path','company-operation-path-20261023/composition.py'),
      ('CompanyPopulationAdmissionInspection/1','guarded_population_inspector','company-state-population-admission-20261028/admission.py'),
      ('CompanyStateInspectionRequest/1','typed_audit_history_query','company-state-typed-request-20261028/request.py'),
      ('CompanyPolicyEffectRequest/1','explicit_policy_effect_inspector','company-state-policy-effects-20261028/effects.py')]
    for profile,role,impl in additions:
        impl='data/accounting-master/'+impl;actual=signatures(impl)
        names={'CompanyOperationPathDraft/1':['execute','report_view','verify_chain']}.get(profile,['inspect'])
        for name in names:check(profile+' entry exists '+name,name in actual)
        rows.append(dict(profile=profile,role=role,implementation=impl,signatures={n:actual.get(n) for n in names},
            authority='docs/design/research/company-state-program-20261028/native-construction-contract-v1.md',
            state_contract='Full exact native path and guarded executed populations; financial effects owned by CompanyOperationPathDraft/1',
            population_contract='Supplied claims/assets and executed prefix; incomplete/unknown remain explicit',
            actor_information='Only audit_only archival_exogenous_stress; other actor requests unsupported',
            evidence_class='current inspected modules and retained deterministic results'))
    for file in ['data/accounting-master/compatibility-current-20261028/source-lock.json',
                 'data/accounting-master/sector-compatibility-current-20261028/attempt-02/source-lock.json']:
        original=json.loads(protect(file).read_text())
        for path,expected in original.items():
            actual=sha256((ROOT/path).read_bytes()).hexdigest();check('retained identity '+path,actual,expected);lock[path]=actual
    for path in [
        'docs/plans/company-state-owner-semantics-20261028.md',
        'docs/design/research/company-state-program-20261028/common-state-owners.md',
        'docs/design/research/company-state-program-20261028/native-construction-contract-v1.md',
        'data/accounting-master/sector-compatibility-current-20261028/compatibility.md',
        'data/accounting-master/term-structural-admission-20261026/audit.md',
        'data/accounting-master/selected-term-program-20261027/contract.md',
        'data/accounting-master/company-state-owner-semantics-20261028/review.py']:protect(path)
    check('scoped owner count',len(rows),27);check('unique profiles',len({x['profile'] for x in rows}),27)
    check('existing edge count retained',len(prior['edges']),16)
    registry=dict(profile='CompanyStateOwnerMeaningReview/1',date='2026-10-28',
        interfaces=rows,existing_edges=deepcopy(prior['edges']),
        common_categories=['economic_resources_obligations','accounting_memory','parameters','actions_external_inputs','retained_history','information_beliefs'],
        mapping_obligations=['profile_versions','context','population_scope','economic_identity','memory_owner','time_information','units_scales','exclusive_effect_owner','historical_queries','native_refusals','complete_expected_outputs'],
        source_admission=False,actor_information_admission=False,shared_state_composition=False,
        common_dispatcher_implemented=False,whole_company_complete=False)
    failed=[x for x in checks if not x['passed']]
    verification=dict(status='fail' if failed else 'pass',checks=len(checks),failed=failed,profiles=len(rows),retained_edges=len(prior['edges']),scope='identity/signature and meaning review; no new financial replay or composition')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=sys.version,cpu_gpu='CPU-only static inspection; no accelerator imports',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,utc=datetime.now(timezone.utc).isoformat(),plan_file='docs/plans/company-state-owner-semantics-20261028.md',result_file='data/accounting-master/company-state-owner-semantics-20261028/result.md',source_hashes=lock)
    for name,value in [('registry',registry),('verification',verification),('checks',checks),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+chr(10))
    (out/'review.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(verification));return bool(failed)

if __name__=='__main__':raise SystemExit(main())
