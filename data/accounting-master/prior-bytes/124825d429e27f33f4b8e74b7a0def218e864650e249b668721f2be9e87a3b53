#!/usr/bin/env python3
"""Execute P04 obligations, regress P03, and retain supervisor inventory evidence."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import shlex
import sys
import time
import unittest
import z3
from check_accounting_p03 import capture_protection, finish_protection, digest, _inventory, _unique_object
ROOT=Path(__file__).resolve().parents[1]
HISTORICAL_INVENTORY='data/accounting-master/runs/20261002T221346-d54a6552/P04/phase-entry-inventory.json'
ORIGINAL_PLAN='data/accounting-master/runs/20261002T221346-d54a6552/P04/approved-plan.json'
SOURCES=['scripts/rational_solver_v1.py','scripts/reconstruction_v1.py','scripts/check_accounting_p04.py','tests/test_accounting_p04.py','docs/design/spec/reconstruction-profile-v1.md','docs/design/fixtures/p04-reconstruction-cases-v1.json']
OUTPUTS=['data/accounting-master/deliverables/P04/'+p for p in ('conformance.json','result.md','progress.md')]

def repository_path(root, relative):
    path=Path(relative)
    if (path.is_absolute() or '..' in path.parts or path.as_posix()!=relative
            or not (root/path).resolve().is_relative_to(root.resolve())):
        raise ValueError('provenance path must be repository-relative and remain inside the repository')
    return path


def approval_reference(root, relative):
    path=repository_path(root,relative)
    raw=(root/path).read_bytes()
    record=json.loads(raw,object_pairs_hook=_unique_object)
    if not isinstance(record,dict):
        raise ValueError('approval must be an object')
    for name,verdict in (('plan','PLAN'),('review','AGREE')):
        response=record.get(name)
        if not isinstance(response,dict) or response.get('verdict')!=verdict:
            raise ValueError('approval requires a PLAN and an AGREE review')
        if not isinstance(response.get('summary'),str):
            raise ValueError('malformed approval summary')
        for key in ('steps','assumptions','checks','evidence','issues','residuals','next_actions'):
            if not isinstance(response.get(key),list) or not all(isinstance(x,str) for x in response[key]):
                raise ValueError('malformed approval '+key)
    if record['review']['issues']:
        raise ValueError('no issue-free approved plan')
    plan_hash=hashlib.sha256(json.dumps(record['plan'],sort_keys=True,ensure_ascii=False,
                                      separators=(',',':'),allow_nan=False).encode()).hexdigest()
    if record.get('plan_hash')!=plan_hash:
        raise ValueError('approved plan hash mismatch')
    return {'path':relative,'sha256':hashlib.sha256(raw).hexdigest(),'plan_hash':plan_hash}


def prepare_provenance(root, execution_inventory, approved_plan):
    execution=repository_path(root,execution_inventory)
    plan=repository_path(root,approved_plan)
    if (plan.name!='approved-plan.json' or plan.parent.name!='P04'
            or plan.parent.parent.parent!=Path('data/accounting-master/runs')
            or execution.name!='pre-edit-files.json'
            or not re.fullmatch(r'execution-\d+',execution.parent.name)
            or execution.parent.parent!=plan.parent):
        raise ValueError('use a supervisor P04 approval and execution inventory from the same run')
    references={'approved_plan':approval_reference(root,approved_plan),
                'original_design':approval_reference(root,ORIGINAL_PLAN)}
    execution_baseline=_inventory(root,execution_inventory)
    protected=capture_protection(root,HISTORICAL_INVENTORY,execution_inventory,writable=SOURCES+OUTPUTS,
                                 required_paths=('docs/design/fixtures/borrowings.json','docs/design/fixtures/northstar.json','scripts/core0_ir_v1.py'))
    if protected['errors'] or protected['changed_since_execution_entry'] or protected['missing_before_check']:
        raise ValueError('protection failure before execution: '+str(protected['errors']+protected['changed_since_execution_entry']))
    for label,path in (('historical_inventory',HISTORICAL_INVENTORY),('execution_inventory',execution_inventory)):
        references[label]={'path':path,'sha256':protected['inventory_hashes'][path]}
    return protected,references,execution_baseline


def execute_checks():
    sys.path.insert(0,str(ROOT/'tests'))
    import test_accounting_p04 as p04
    import test_accounting_p03 as p03
    p04.OBSERVATIONS.clear();p03.OBSERVATIONS.clear()
    reports={}
    for name,module in [('P04',p04),('P03_regression',p03)]:
        stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromModule(module)
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        reports[name]={'methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
                       'skips':len(result.skipped),'passed':result.wasSuccessful() and result.testsRun>0 and not result.skipped,'output':stream.getvalue()}
    catalog=json.loads((ROOT/SOURCES[-1]).read_text())
    required=Counter(x['id'] for x in catalog['obligations']);observed=Counter(x['obligation'] for x in p04.OBSERVATIONS)
    status={'required':len(required),'observed':len(observed),'missing':sorted(required.keys()-observed.keys()),
            'uncatalogued':sorted(observed.keys()-required.keys()),
            'duplicate_ids':sorted(k for k in required.keys()|observed.keys() if required[k]>1 or observed[k]>1),
            'failed_observations':[x['obligation'] for x in p04.OBSERVATIONS if x.get('passed') is not True]}
    return reports,list(p04.OBSERVATIONS),status,catalog


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('--execution-inventory',required=True)
    parser.add_argument('--approved-plan',required=True)
    args=parser.parse_args(argv)
    if Path(args.output_dir).resolve()!=ROOT/'data/accounting-master/deliverables/P04':
        parser.error('use the declared P04 output directory')
    started=time.monotonic();utc=datetime.now(timezone.utc).isoformat()
    try:
        protected,references,execution_baseline=prepare_provenance(ROOT,args.execution_inventory,args.approved_plan)
    except (OSError,ValueError) as exc:
        parser.error(str(exc))
    os.environ['CUDA_VISIBLE_DEVICES']='-1'
    source_before={p:digest(ROOT/p) for p in SOURCES}
    source_before.update({r['path']:r['sha256'] for r in references.values()})
    reports,observations,status,catalog=execute_checks()
    finish_protection(ROOT,protected)
    source_after={p:digest(ROOT/p) for p in source_before}
    stable=all(h is not None and source_after[p]==h for p,h in source_before.items())
    passed=all(r['passed'] for r in reports.values()) and protected['passed'] and stable and status['required']>0 and not any(status[k] for k in ('missing','uncatalogued','duplicate_ids','failed_observations'))
    command='CUDA_VISIBLE_DEVICES=-1 '+shlex.join(['python3','-B','scripts/check_accounting_p04.py']+(sys.argv[1:] if argv is None else argv))
    payload={'schema_version':'accdsl.p04.conformance.v1','passed':bool(passed),'obligation_status':status,
        'tests':reports,'observations':observations,'protection':protected,'code_stable_during_check':stable,
        'provenance':references,
        'input_source_test_hashes':dict(protected['before'],**source_before),
        'manifest':{'git_commit':'unavailable: existing marker is not a usable repository','command':command,
            'working_directory':str(ROOT),'executable':sys.executable,'environment':{'python':platform.python_version(),'z3':z3.get_version_string()},
            'hardware':'CPU only; CUDA_VISIBLE_DEVICES=-1; no accelerator framework imported','random_seeds':'N/A: exact deterministic fixtures',
            'data_version':'p04-reconstruction-cases-v1 plus preserved borrowing/Northstar fixtures','started_utc':utc,
            'wall_seconds':round(time.monotonic()-started,6),'plan':args.approved_plan,'plan_sha256':references['approved_plan']['sha256'],
            'approved_plan_hash':references['approved_plan']['plan_hash'],
            'original_design_plan':ORIGINAL_PLAN,'original_design_plan_sha256':references['original_design']['sha256'],
            'historical_inventory':HISTORICAL_INVENTORY,'historical_inventory_sha256':references['historical_inventory']['sha256'],
            'execution_inventory':args.execution_inventory,'execution_inventory_sha256':references['execution_inventory']['sha256'],
            'phase_contribution_files':SOURCES+OUTPUTS,
            'changed_source_code_test_files':[p for p in SOURCES if source_before[p]!=execution_baseline.get(p)],
            'changed_files':[p for p in SOURCES+OUTPUTS if p in OUTPUTS[:2] or digest(ROOT/p)!=execution_baseline.get(p)],
            'outputs':OUTPUTS[:2],'result':OUTPUTS[1]},
        'requirement_coverage':{'MC08':'shared symbols, choices, views and joint queries','MC09':'declared posting templates and bounded coverage',
            'MC10':'six structural admission categories with provenance; external eligibility not independently certified',
            'MC11':'unhedged additive bullet-debt grouping with retained memory','MC12':'explicit finite joint weights and retained mass',
            'MC18':'strict bounds and unfinished cells','MC26':'exact rational linear and bounded integer numerical operations'},
        'unsupported':catalog['unsupported'],
        'acceptance':{'engineering':bool(passed),'accounting_validity':'not established','forecast_validity':'not established','human_acceptance':'pending','whole_gap_closure':False}}
    decision='PASS' if passed else 'FAIL'
    findings='''Declared templates construct account and economic-state roll-forwards. Independent Fraction enumeration checks three finite input variants; a selected Northstar receivables bridge replays original events to create observations before reconstruction. P03 integration preserves alpha=1/2, isolates endpoint conditions, retains overlapping views and rejects incompatible joint extrema. Parent coverage remains one continuous cell without genuine choices.

Exact debt interest ranges from 5 to 7. The rounded fixture has infimum 199/40, attained, and supremum 1407/200, unattained. Original strict feasibility precedes closure optimisation. Half-even negative ties, posting minor units, integer gaps, source conflicts, unsupported arithmetic, zero budgets and injected Unknown responses are checked. Incomplete search retains domains, predicates, ordinals and formulas; explored bounds cannot be global certificates.

Recovery repairs reject lossy rational-record coercion, malformed or unsupported domains, generated-name collisions, duplicate finite values and repeated contract identities. A bounded domain with 10^30 integer values stops after one completed cell and retains its exact unvisited cardinality. An independent integer predicate oracle checks disjoint coverage of overlapping guards. Changed principal and rate inputs, including reversed endpoint order, verify that P03 bounds come from generated inputs rather than fixed expected amounts.

The claimed target is the declared rational-linear family. The finite comparisons compute exactly the enumerated assignment sets; algebra supplies the continuous endpoint comparator. This establishes these tested invariants within the profile. It does not establish arbitrary-history completeness. Uncertainty admission checks validate records and declared permissions, not the truth of underlying evidence or professional accounting eligibility. Grouping covers unhedged additive bullet debt with no within-horizon maturity; year fractions are explicit assumptions. Probability atoms are declared disjoint economic hypotheses; their external interpretation is a modeling assumption.''' if passed else '''Verification failed. No numerical certification is issued by this run. Inspect the per-test failures, obligation coverage, code stability and protection comparisons in conformance.json before local repair. The intended comparators remain independent enumeration and exact endpoint algebra.'''
    text=f'''# P04 bounded reconstruction result

{decision}: {reports['P04']['methods']} P04 tests executed; observations cover {status['observed']}/{status['required']} catalogued obligations; {reports['P03_regression']['methods']} P03 regression tests executed. Full executed outcomes, formulas, cell assignments, witnesses, conflicts, source hashes and proof queries are in conformance.json.

The current recovery accepts explicit supervisor approval and execution-inventory paths, checks approval structure and plan-hash integrity, and retains the original design and historical inventory separately. Four checker obligations exercise malformed or unapproved inputs, rejection before writes, current manifest selection, unchanged protection exclusions and failure reporting in disposable trees. Their simulated test outcomes concern reporting behavior only; the reconstruction tests supply the numerical evidence below.

{findings}

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| {decision} for bounded engineering checks | Independent finite sets, integration and endpoint assertions | protection={protected['passed']}; tests={all(r['passed'] for r in reports.values())}; missing={status['missing']}; duplicates={status['duplicate_ids']} | shared solver defects, omitted templates, external admission truth | independent result review if PASS; local repair if FAIL | accounting validity, empirical forecast validity, human acceptance or closure of G1–G18 |

Engineering, numerical and interpretation ledgers remain separate: implementation and executed invariants are recorded above; exact results concern only declared constraints; full-company accounting and empirical forecasts remain unevaluated. No stochastic comparison or method ranking is made.

The strongest alternative explanation is a shared modeling error between construction and fixtures. Independent posting replay, perturbed inputs and analytic endpoint checks reduce that risk. An in-profile counterexample would overturn this result. The weakest evidence is breadth: these are small deterministic cases, not arbitrary accounting histories.

Actual command: `{command}`. Python {platform.python_version()}, Z3 {z3.get_version_string()}, CPU only with GPU devices intentionally hidden. Wall time: {payload['manifest']['wall_seconds']} seconds. Seeds: N/A, deterministic. Git provenance is unavailable; conformance.json contains content hashes and protection comparisons for {len(protected['before'])} files. Current approved plan: `{args.approved_plan}`. Original design: `{ORIGINAL_PLAN}`. Current execution inventory: `{args.execution_inventory}`; historical inventory: `{HISTORICAL_INVENTORY}`. Both references and their hashes are recorded separately. The manifest distinguishes all phase contributions from files changed during this execution.

Residuals: nonlinear inference, continuous probability inference, unbounded integer search, template discovery, general aggregation equivalence, accounting validity, forecast validity and human acceptance remain open. All MC01–MC35/G1–G18 retain wider obligations.
'''
    out=ROOT/args.output_dir;out.mkdir(parents=True,exist_ok=True)
    (out/'conformance.json').write_text(json.dumps(payload,indent=2)+'\n')
    (out/'result.md').write_text(text)
    print(json.dumps({'passed':bool(passed),'tests':{k:{x:v[x] for x in ('methods','failures','errors','skips')} for k,v in reports.items()},'obligations':status,'protected_inputs_passed':protected['passed']}))
    return 0 if passed else 1

if __name__=='__main__':
    raise SystemExit(main())
