#!/usr/bin/env python3
"""Independent replay, comparator and bounded execution evidence for P05."""
from __future__ import annotations
from collections import defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shlex
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
SOURCES=['scripts/company_execution_v1.py','scripts/check_accounting_p05.py','tests/test_accounting_p05.py','docs/design/fixtures/p05-economic-inputs-v1.json']
OUTPUTS=['data/accounting-master/deliverables/P05/'+n for n in ('execution.json','result.md','progress.md')]
SUITES=('test_accounting_p05','test_accounting_p02','test_accounting_p03','test_accounting_p04')
REQUIRED_CHECKS={*(f'replay:{p}' for p in ('2024H1','2024H2','2024FY','2025_fixed','2025_floating')),
                 'protected_reference','adapter_execution:0','adapter_execution:1','apple_journal_replay',
                 'branch:fixed','branch:floating','branch:payroll60','rejected_branch_retention',
                 'protected_files','approval_integrity',*SUITES}
OBLIGATIONS={
    'economic_inputs':['all_statement_bridges_and_reference_movements','input_perturbation_changes_delivery_profit_and_tax','runtime_never_reads_expected_fixture'],
    'independent_checks':['checker_detects_posting_and_classification_and_bridge_mutations','checker_rejects_identity_cash_endpoints_and_asset_corruption','checker_requires_named_obligations'],
    'event_identity':['duplicate_and_conflicting_ids','dependency_cycle_and_canonical_schedule'],
    'atomic_failures':['invalid_context_dates_and_amounts','insufficient_inventory_excess_settlement_and_unknown_fields','injected_internal_failure_atomic','balanced_hook_and_provenance_corruption_are_atomic'],
    'distinct_outcomes':['unknown_operation_and_intervention','funding_default_preserves_unpaid_liability_and_last_state','failed_forecast_prevents_complete_top_level_status'],
    'financing':['equity_and_par_debt_lifecycles','full_par_redemption_keeps_financing_bridge'],
    'information_access':['role_date_guard_for_both_consumers','forecast_behaviour_rejects_realized_future_and_accepts_stress','forecast_does_not_grant_measurement_permission','forecast_provenance_is_rechecked_at_measurement','forecast_rejects_future_initial_state','information_requires_typed_roles_and_kind','revision_views_and_unknown_availability'],
    'joint_branches':['branch_isolation_order_mass_and_conditioning','p03_p04_joint_adapter','branch_payroll_provenance_matches_consumed_input','invalid_branch_retains_mass_and_other_branches'],
    'real_case':['apple_conditional_and_source_distinctions','period_boundary_and_real_case_default'],
    'replay':['deterministic_replay_and_asset_schedule'],
}
REQUIREMENT_EVIDENCE={
    'MC13':{'obligations':['economic_inputs','event_identity','atomic_failures'], 'scope':'Economic events and atomic state/journal updates in DemoCorporate/1'},
    'MC14':{'obligations':['information_access','joint_branches'], 'scope':'Explicit stress and finite conditioning; intervention unsupported'},
    'MC15':{'obligations':['economic_inputs','financing'], 'scope':'Northstar operations, half-year closing and declared simple tax'},
    'MC16':{'obligations':['independent_checks','replay'], 'scope':'Common-journal statements, debt and plant schedules'},
    'MC17':{'obligations':['financing','distinct_outcomes'], 'scope':'Cash equity and par debt only; general instrument lifecycles unresolved'},
    'MC18':{'obligations':['joint_branches','distinct_outcomes'], 'scope':'Joint allocations and retained complete/default/unsupported mass'},
    'MC28':{'obligations':['economic_inputs','real_case'], 'scope':'Synthetic Northstar and conditional Apple stress; real-company semantic completeness unresolved'},
}


def coverage(checks):
    ids=[c.get('id',c.get('module')) for c in checks]
    missing=sorted(REQUIRED_CHECKS-set(ids))
    duplicate=sorted({i for i in ids if ids.count(i)>1})
    return {'id':'required_check_coverage','passed':not missing and not duplicate,
            'missing':missing,'duplicates':duplicate,'required':sorted(REQUIRED_CHECKS)}


def verify(record):
    """Independent account replay and statement bridges; no runtime helpers."""
    if record['status']!='Complete':raise ValueError('complete record required')
    b=defaultdict(Q,{k:Q(v) for k,v in record['opening'].items()});o=deepcopy(b)
    totals=defaultdict(Q); flows=defaultdict(Q); movements=defaultdict(Q); dividends=Q(0);issues=Q(0)
    classes={'collect':'operating','supplier_pay':'operating','payroll_pay':'operating','interest_pay':'operating','tax_pay':'operating',
             'plant_pay':'investing','dividend_pay':'financing','equity_issue':'financing','debt_issue':'financing','debt_redeem':'financing'}
    closed=set();ids=set()
    inputs={e['id']:e for e in record.get('inputs',[])}
    if 'inputs' in record:
        assert len(inputs)==len(record['inputs']),'duplicate input identity'
        assert set(inputs)=={j['event_id'] for j in record['journals']},'input/journal coverage'
    for j in record['journals']:
        assert j['event_id'] not in ids,'duplicate committed journal';ids.add(j['event_id'])
        assert j['period'] not in closed,'posting after close'
        assert j['cash_class']==classes.get(j['op']),'cash classification'
        if 'inputs' in record:
            e=inputs[j['event_id']]
            token=hashlib.sha256(json.dumps(e,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
            assert j['input_sha256']==token,'economic input identity'
            assert all(j[k]==e[k] for k in ('op','date','period','provenance')),'journal input provenance'
        assert sum(Q(x['signed_amount']) for x in j['postings'])==0,'unbalanced batch'
        for line in j['postings']:
            a=line['account'];v=Q(line['signed_amount']);b[a]+=v
            if j['op']!='close':totals[a]+=v
            movements[(j['op'],a)]+=v
            if a=='cash':
                assert j['cash_class'] or not v,'cash without classification'
                flows[j['cash_class']]+=v
        assert sum(b.values())==0,'account bridge not balanced'
        if j['op']=='close':
            assert all(b[a]==0 for a in ('revenue','cost_of_sales','payroll','depreciation','interest','tax')),'unclosed income'
            closed.add(j['period'])
    s=record['statements']; bs=s['balance_sheet'];inc=s['income'];cf=s['cash_flow'];eq=s['equity'];debt=s['debt'];plant=s['plant']
    assert {k:Q(v) for k,v in bs['accounts'].items()}==dict(b),'account bridge'
    profit=-sum(totals[a] for a in ('revenue','cost_of_sales','payroll','depreciation','interest','tax'))
    for a in ('revenue','cost_of_sales','payroll','depreciation','interest','tax'):
        assert Q(inc[a])==(-totals[a] if a=='revenue' else totals[a]),'income classification'
    assert Q(inc['profit'])==profit and Q(inc['oci'])==0 and Q(inc['comprehensive_income'])==profit,'income/OCI'
    assets=sum(b[a] for a in ('cash','receivables','inventory','plant_cost','accum_depreciation','tax_prepaid'))
    liabilities=-sum(b[a] for a in ('payables','debt','interest_payable','tax_payable','payroll_payable','plant_payable','dividend_payable'))
    equity=-b['capital']-b['retained']
    assert Q(bs['assets'])==assets and Q(bs['liabilities'])==liabilities and Q(bs['equity'])==equity and assets==liabilities+equity,'balance sheet'
    for k in ('operating','investing','financing'):assert Q(cf['direct'][k])==flows[k],'direct cash bridge'
    assert Q(cf['opening'])==o['cash'] and Q(cf['closing'])==b['cash'],'cash endpoints'
    assert sum(flows.values())==b['cash']-o['cash']==Q(cf['closing'])-Q(cf['opening']),'cash total'
    indirect=profit+totals['depreciation']-sum(b[a]-o[a] for a in ('receivables','inventory','tax_prepaid','payables','interest_payable','tax_payable','payroll_payable'))
    assert indirect==flows['operating']==Q(cf['indirect_operating']),'indirect cash'
    dividends=movements['dividend_declare','retained'];issues=-movements['equity_issue','capital']
    assert Q(eq['opening'])==-o['capital']-o['retained'] and Q(eq['profit'])==profit and Q(eq['oci'])==0,'equity inputs'
    assert Q(eq['issues'])==issues and Q(eq['dividends'])==dividends and Q(eq['closing'])==equity,'equity movements'
    assert equity==-o['capital']-o['retained']+profit+issues-dividends,'equity roll-forward'
    assert Q(debt['opening'])==-o['debt'] and Q(debt['closing'])==-b['debt'],'debt endpoints'
    assert Q(debt['issued'])==-movements['debt_issue','debt'] and Q(debt['redeemed'])==movements['debt_redeem','debt'],'debt movements'
    assert Q(debt['closing'])==Q(debt['opening'])+Q(debt['issued'])-Q(debt['redeemed']),'debt bridge'
    assert Q(plant['opening_cost'])==o['plant_cost'] and Q(plant['closing_cost'])==b['plant_cost'],'plant endpoints'
    assert Q(plant['additions'])==totals['plant_cost'] and Q(plant['closing_cost'])==Q(plant['opening_cost'])+Q(plant['additions']),'plant bridge'
    assert Q(plant['depreciation'])==totals['depreciation'] and Q(plant['opening_accumulated'])==-o['accum_depreciation'],'depreciation'
    assert Q(plant['closing_accumulated'])==-b['accum_depreciation']==Q(plant['opening_accumulated'])+Q(plant['depreciation']),'accumulated depreciation'
    flat={'cash':b['cash'],'receivables':b['receivables'],'inventory':b['inventory'],'tax_prepaid':b['tax_prepaid'],
          'plant_net':b['plant_cost']+b['accum_depreciation'],'assets':assets,'payables':-b['payables'],'debt':-b['debt'],
          'equity':equity,'revenue':-totals['revenue'],'profit':profit,'interest':totals['interest'],'tax':totals['tax'],
          'operating_cash':flows['operating'],'investing_cash':flows['investing'],'financing_cash':flows['financing'],'cash_change':b['cash']-o['cash']}
    assert {k:Q(v) for k,v in s['flat'].items()}==flat,'flat statement mapping'
    if 'closing' in record:
        closing=record['closing']
        assert {k:Q(v) for k,v in closing['balances'].items()}==dict(b),'committed state differs'
        assert sum(Q(a['cost']) for a in closing['assets'])==b['plant_cost'],'asset cost schedule'
        assert sum(Q(a['accumulated']) for a in closing['assets'])==-b['accum_depreciation'],'asset depreciation schedule'
        for j in record['journals']:
            assert closing['applied'][j['event_id']]['input_sha256']==j['input_sha256'],'committed identity'
    return {'passed':True,'batches':len(ids),'all_account_bridges':True,'statements':['balance_sheet','income_OCI','direct_cash','indirect_cash','equity','debt','plant']}


def compare_reference(periods, reference):
    for name,expected in reference['expected'].items():
        for k,v in expected.items():assert Q(periods[name]['statements']['flat'][k])==Q(v),(name,k)
    for name in ('2024H1','2024H2'):
        expected=defaultdict(Q);actual=defaultdict(Q)
        for e in reference['historical_events']:
            if e['period']==name:
                for p in e['postings']:expected[p['account']]+=Q(p['signed_amount'])
        for e in periods[name]['journals']:
            if e['op']!='close':
                for p in e['postings']:actual[p['account']]+=Q(p['signed_amount'])
        assert {k:v for k,v in expected.items() if v}=={k:v for k,v in actual.items() if v},'reference account movements'
    return {'passed':True,'periods':list(reference['expected']),'historical_movement_comparisons':2}


def suite(name):
    sys.path.insert(0,str(ROOT/'tests'));stream=io.StringIO()
    mod=__import__(name);tests=unittest.defaultTestLoader.loadTestsFromModule(mod)
    def test_ids(node):
        if isinstance(node,unittest.TestSuite):
            return [i for child in node for i in test_ids(child)]
        return [node.id()]
    ids=test_ids(tests)
    required={f'test_accounting_p05.P05Tests.test_{m}' for methods in OBLIGATIONS.values() for m in methods} if name=='test_accounting_p05' else set()
    missing=sorted(required-set(ids))
    r=unittest.TextTestRunner(stream=stream,verbosity=2).run(tests)
    return {'module':name,'methods':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skips':len(r.skipped),
            'test_ids':ids,'missing_required_tests':missing,
            'passed':r.wasSuccessful() and r.testsRun>0 and not r.skipped and not missing,'output':stream.getvalue()}


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',required=True);parser.add_argument('--approved-plan',required=True);parser.add_argument('--execution-inventory',required=True)
    args=parser.parse_args(argv);started=time.monotonic()
    from check_accounting_p04 import approval_reference,repository_path
    from check_accounting_p03 import capture_protection,finish_protection,digest,_inventory
    approval=approval_reference(ROOT,args.approved_plan)
    inv=repository_path(ROOT,args.execution_inventory);plan=repository_path(ROOT,args.approved_plan);out=repository_path(ROOT,args.output_dir)
    if plan.name!='approved-plan.json' or plan.parent.name!='P05' or inv.name!='pre-edit-files.json' or inv.parent.parent!=plan.parent:
        raise ValueError('matching supervisor P05 approval/execution inventory required')
    if out!=Path('data/accounting-master/deliverables/P05'):raise ValueError('only declared P05 output directory is writable')
    baseline=_inventory(ROOT,args.execution_inventory)
    historical=str(plan.parent/'phase-entry-inventory.json')
    phase_baseline=_inventory(ROOT,historical)
    protection=capture_protection(ROOT,historical,args.execution_inventory,writable=SOURCES+OUTPUTS)
    from company_execution_v1 import run_northstar,apple_conditional,branch_family,p03_family,serial
    checks=[];runs={};error=None
    try:
        raw=run_northstar();engine=raw.pop('historical_engine');runs['northstar']=raw
        for name,p in raw['periods'].items():checks.append({'id':'replay:'+name,**verify(p)})
        checks.append({'id':'protected_reference',**compare_reference(raw['periods'],json.loads((ROOT/'docs/design/fixtures/northstar.json').read_text()))})
        spec=json.loads((ROOT/'docs/design/fixtures/p05-economic-inputs-v1.json').read_text())
        atoms=[{'id':name,'weight':'1/4','hypothesis':{'fixed_fraction':alpha,'payroll':pay,'operation':op}}
               for name,alpha,pay,op in [('fixed','1','50','supported'),('floating','0','50','supported'),('default','0','1000','supported'),('unsupported','1','50','convertible')]]
        runs['joint_stress']=branch_family(engine,spec,atoms)
        runs['conditioning']=branch_family(engine,spec,atoms,'conditioning',{'fixed':'1','floating':'1/2','default':'1/2','unsupported':'0'})
        # P03 bindings are explicit synthetic inputs, not expected IR or runtime values.
        sys.path.insert(0,str(ROOT/'tests'));from test_accounting_p03 import BASE,bindings
        from core0_frontends_v1 import compile_source
        compiled=compile_source(BASE,bindings());runs['p03_p04_adapter']=p03_family(compiled.ir,bindings())
        from company_execution_v1 import execute_period,forecast_period
        for endpoint in runs['p03_p04_adapter']['endpoints']:
            branch=engine.fork()
            endpoint['company_execution']=execute_period(branch,spec,forecast_period(branch,spec,endpoint['fixed_fraction']))
            checks.append({'id':'adapter_execution:'+endpoint['fixed_fraction'],**verify(endpoint['company_execution'])})
        runs['apple']=apple_conditional()
        checks.append({'id':'apple_journal_replay',**verify({**runs['apple'],'status':'Complete'})})
        for a in runs['joint_stress']['atoms']:
            if a['status']=='Complete':checks.append({'id':'branch:'+a['id'],**verify(a['execution'])})
        validation_atoms=[{'id':ident,'weight':'1/3','hypothesis':{'fixed_fraction':alpha,'payroll':pay,'operation':'supported'}}
                          for ident,alpha,pay in [('invalid_fraction','2','50'),('invalid_payroll','1','NaN'),('payroll60','1','60')]]
        runs['branch_validation']=branch_family(engine,spec,validation_atoms)
        validation=runs['branch_validation']
        assert validation['summary']['mass']=={'Rejected':'2/3','Complete':'1/3'},'failed branch mass lost'
        assert validation['summary']['mean'] is None and not validation['summary']['normalised_over_successful_only'],'success-only summary'
        for a in validation['atoms']:
            if a['status']=='Rejected':
                assert a['execution']['last_committed_state']==engine.snapshot(),'rejected branch changed state'
                assert a['execution']['journals']==[] and a['outcome'] is None,'rejected branch fabricated output'
            else:
                checks.append({'id':'branch:'+a['id'],**verify(a['execution'])})
                for e in a['execution']['inputs']:
                    assert e['provenance'][1]['information_inputs']['payroll']['value']=='60','branch payroll provenance'
                assert a['execution']['statements']['income']['payroll']=='60','branch payroll consumption'
        checks.append({'id':'rejected_branch_retention','passed':True,'mass':validation['summary']['mass'],
                       'unconditional_mean_available':False,'preserved_last_committed_states':True})
        checks.extend(suite(n) for n in SUITES)
    except Exception as exc:
        error=type(exc).__name__+': '+str(exc);checks.append({'id':'execution_exception','passed':False,'error':error})
    finish_protection(ROOT,protection)
    checks.append({'id':'protected_files','passed':protection['passed']})
    checks.append({'id':'approval_integrity','passed':digest(ROOT/args.approved_plan)==approval['sha256']})
    checks.append(coverage(checks))
    passed=all(c['passed'] for c in checks) and error is None
    changed=[p for p in SOURCES if baseline.get(p)!=digest(ROOT/p)]
    phase_changed=[p for p in SOURCES if phase_baseline.get(p)!=digest(ROOT/p)]
    payload={'schema_version':'accdsl.p05.execution.v1','passed':passed,'requirements':['MC13','MC14','MC15','MC16','MC17','MC18','MC28'],
             'checks':checks,'obligations':OBLIGATIONS,'requirement_evidence':REQUIREMENT_EVIDENCE,'runs':serial(runs),'protection':protection,'manifest':{
             'created_at':datetime.now(timezone.utc).isoformat(),'git_commit':None,'git_reason':'existing marker is not a usable repository',
             'command':'CUDA_VISIBLE_DEVICES=-1 '+shlex.join(['python3','-B','scripts/check_accounting_p05.py']+(argv or sys.argv[1:])),
             'environment':{'python':platform.python_version(),'executable':sys.executable,'CUDA_VISIBLE_DEVICES':os.environ.get('CUDA_VISIBLE_DEVICES'),'GPU':'intentionally hidden; no GPU framework used'},
             'seeds':'N/A: deterministic exact arithmetic','wall_seconds':round(time.monotonic()-started,3),'plan':approval,
             'execution_inventory':args.execution_inventory,'execution_inventory_sha256':digest(ROOT/args.execution_inventory),
             'data_version':'p05-economic-inputs-v1 and protected P02/P03/P04 sources','changed_files':changed,'phase_changed_files':phase_changed,
             'hashes':{p:digest(ROOT/p) for p in SOURCES},'input_hashes':{p:digest(ROOT/p) for p in ['docs/design/fixtures/northstar.json','docs/design/chapters/13-reference-company.tex','data/accounting-master/deliverables/P02/case.json','docs/design/fixtures/borrowing.acc','tests/test_accounting_p03.py','scripts/core0_frontends_v1.py','scripts/core0_ir_v1.py','scripts/reconstruction_v1.py','scripts/rational_solver_v1.py','scripts/check_accounting_p03.py','scripts/check_accounting_p04.py']},'outputs':OUTPUTS[:2]},
             'acceptance':{'engineering':'passed' if passed else 'failed','accounting_validity':'not established','forecast_validity':'not evaluated','human_acceptance':'pending'},
             'nonclaims':['No general corporate or GAAP compliance','No empirical forecast accuracy or superiority','No inferred Apple floating exposure','No G1–G18 or whole-program closure']}
    outdir=ROOT/out;outdir.mkdir(parents=True,exist_ok=True)
    (outdir/'execution.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    methods=sum(c.get('methods',0) for c in checks)
    text=f'''# P05 bounded company execution

Engineering result: **{'PASS' if passed else 'FAIL'}**. Actual economic inputs generate Northstar journals and all statements. The protected posting fixture is read only by the independent comparator. {methods} unittest methods ran across P05 and P02–P04; exact outcomes and complete check output are in execution.json. Failure, skip, absent check or integrity mismatch blocks acceptance.

Recovery repaired two reproduced failures: a balanced commit-hook rewrite previously changed journals without changing staged state, and forecast construction previously granted measurement permission to a behaviour-only driver. Commit hooks now receive a checked copy; original driver permissions, dates and provenance survive construction and are rechecked on execution. Required checks and unittest obligations are named explicitly. Independent verification additionally checks input hashes, cash-flow endpoints and asset schedules. Incomplete forecast branches prevent a complete top-level status.

The second repair corrected branch-specific payroll provenance: a payroll-60 hypothesis previously executed with payroll-50 information recorded in its journals. Branch hypotheses now enter the shared behaviour and measurement checks before event construction. Invalid fixed fractions or malformed payroll amounts return Rejected branches with their original probability mass and last committed state; valid neighbours still execute. Invalid joint weights or coordinates reject the family before execution. The branch_validation record preserves two rejected thirds and one complete third, with no unconditional mean or success-only renormalisation. Endpoint regression tests check the actual guarded call path, order invariance and explicit conditioning.

Northstar's H1, H2, FY and fixed/floating forecast paths reproduce the independent reference. Every batch, account bridge, closing entry, balance sheet, income/zero OCI, direct/indirect cash flow, equity, debt and plant schedule is independently replayed. Aggregate ordering, cost-5 goods, 20% simple tax, half-year accrual, end-period capex and zero OCI are synthetic conventions with source provenance in the input fixture; they are not general defaults. Atomic rejection, duplicate identity, conflicting identity, economic funding default, unsupported operations and internal failure have distinct outcomes. A failed payment preserves the accrued obligation and last committed state.

Behaviour and measurement read through role/date checks. Future economic realizations, future publication/ingestion and unknown availability are rejected. Explicit prospective stresses are marked as assumptions. Original/corrected disclosures remain separate and incompatible revision groups cannot be subtracted. The synthetic reference starts from specified economic history; it does not establish that corrected disclosures were available at the forecast origin. An as-known historical reconstruction from those disclosures remains outside this bounded demonstration.

The P03/P04 adapter retains the joint fixed-plus-floating principal constraint and continuous parent family. Its mapping is structural; Acme's synthetic evidence dates do not prove Northstar facts. Endpoint company executions do not exhaust the continuous family. The illustrative finite joint law preserves complete, default and unsupported branches without success-only renormalisation; conditioning changes weights only under explicit likelihoods. These probabilities are assumptions, not estimates.

Apple's marginal +200bp, 13/52-year calculation uses an explicitly assumed USD 14.575bn effective floating exposure: additional interest and immediate cash/equity reduction are USD 72.875m, with no tax. This assumed exposure numerically matches a reported notional for illustration but is not identified by it. P02 observation IDs, contexts, scales, precision, source spans and pins are retained; principal, carrying amount and notional remain different measurements. Computational balancing capital is not reported Apple equity. Retained-byte historical availability, actual hedge allocation, debt movements and asset histories remain unresolved. The calculation is not a full Apple forecast.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Bounded engineering {'candidate passes' if passed else 'requires repair'} | Economic execution and independent bridges | {'All recorded checks pass' if passed else 'See failed checks in execution.json'} | General operations and timing omitted | Independent result review | Accounting/forecast validity |
| Conditional real-case illustration | Shared interest/settlement/closing engine | Source and measurement distinctions retained | Effective floating exposure unknown | Resolve source-specific allocation evidence | Actual exposure or forecast accuracy |

| Evidence ledger | Status |
|---|---|
| Engineering correctness | {'Passed declared bounded checks' if passed else 'Failed; do not accept'} |
| Accounting validity | Not established professionally; journal balance alone is insufficient |
| Empirical forecast validity | Not evaluated; no stochastic ranking |
| Human acceptance | Pending; no paid review requested |

Pre-run audit/evidence/defaults are preserved in progress.md. Strongest alternative explanation: shared economic assumptions may be incomplete despite independent arithmetic. A disagreement with checked contract/source semantics would overturn any wider accounting interpretation. Weakest evidence: illustrative chronology and conditional real exposure. Broader MC01–MC35/G1–G18 obligations remain open.

The requirement mapping in execution.json links MC13 to economic inputs and atomic event identity; MC14 to information access and scenario meaning; MC15 to bounded corporate operations; MC16 to all statement bridges; MC17 to cash-equity/par-debt lifecycles; MC18 to retained joint branches and distinct failures; and MC28 to Northstar plus the conditional Apple case. These mappings identify bounded evidence rather than whole-requirement closure.

Actual command and environment, elapsed time, source/code/test hashes, approval and inventory references, and protected-file comparisons are recorded in execution.json. Git provenance remains unavailable. Changed source/code/test files this repair: {', '.join(changed)}. Full P05 contributions: {', '.join(phase_changed)}. Only declared P05 files were authored. No benchmark, statistical superiority, production-readiness or human-acceptance claim is made.
'''
    (outdir/'result.md').write_text(text)
    print(json.dumps({'passed':passed,'checks':len(checks),'tests':methods,'error':error,'output':str(out/'execution.json')}))
    return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
