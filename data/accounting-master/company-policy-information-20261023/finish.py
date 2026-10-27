"""One-time additive result/control refresh; no predecessor evidence rewrite."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REL = HERE.relative_to(ROOT).as_posix()
NEXT = 'docs/plans/accounting-language-scope-review-20261023.md'

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert not (HERE / 'control-refresh.json').exists(), 'one-time refresh already recorded'
    checks = json.loads((HERE / 'checks.json').read_text())
    assert checks['passed'] and len(checks['checks']) == 93
    manifest = json.loads((HERE / 'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        assert sha(ROOT / name) == expected, name
    coverage = json.loads((ROOT / 'data/accounting-master/company-authoring-integration-20261023/coverage-delta.json').read_text())
    coverage['scope'] = 'Additive policy-information evidence; outside protected Version 3.53; no whole-row closure'
    coverage['increment_evidence'] = ['PolicyInformationDraft/1: 93 recorded checks and read-only replay; 276 protected files unchanged']
    changed = {'MC05','MC10','MC13','MC14','MC15','MC16','MC18','MC24','MC25','MC28','MC34','G13','G14','G18'}
    for row in coverage['rows']:
        row['previous_increment'] = row['new_evidence']
        row['new_evidence'] = ('Exact policy/method timing and full canonical replay; synthetic dependencies and partial results remain explicit.' if row['id'] in changed else 'No new evidence attributed; prior scope retained.')
        row['assessment'] = 'bounded_increment_full_requirement_open' if row['id'] in changed else 'unchanged_scope_not_reaudited'
    write_json(HERE / 'coverage-delta.json', coverage)
    write_json(HERE / 'replay-observation.json', {'command':'CUDA_VISIBLE_DEVICES=-1 python3 '+REL+'/verify.py','exit_code':0,'checks':93,'passed':True,'protected_files':276,'wall_seconds':83.118,'origin':'Observed completion of tool session 37717; no second recording'})
    names = ['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
    before = {}
    for name in names:
        path = ROOT / name
        before[name] = sha(path)
        dest = HERE / 'control-before' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
    section = ('## 23 October 2026 — policy-information extension checked\n\n'
        'The recorded run and read-only replay pass 93 checks; all 276 protected\n'
        'files are unchanged. Exact policy and materializer availability is separate\n'
        'from parent information and historical execution. Eligible inputs may still\n'
        'produce partial accounting; no child clock or real forecast admission is\n'
        'invented. Result: `'+REL+'/result.md`.\n\n'
        'Next: execute `'+NEXT+'`. Review all 53 obligations,\n'
        '6 interactions and 46 operations against actual company authoring, then\n'
        'continue the next consequential design repair. Version 3.53 remains\n'
        '413 pages, not_ready and unchanged; this increment awaits integration.\n'
        'S1–S5 remain partial, S6 held, S7 deferred. No whole requirement closes.\n'
        'Earlier entries below are historical checkpoints.\n\n')
    for name in names:
        path = ROOT / name
        if name.endswith('.md') and 'simulator-session' not in name:
            title, rest = path.read_text().split('\n', 1)
            path.write_text(title+'\n\n'+section+rest.lstrip('\n'))
    session = '# Simulator-first continuation checkpoint\n\n'+section
    session += ('Protected manuscript: `docs/design/proposal/manuscript-company-authoring-20261023/accounting-product-proposal.pdf`\n'
        'SHA256: `5bf364ae6c78bddcf833331d408c447ddd5f540aba1e47d4d28bc7e648c09893`.\n'
        'No running diagnostic remains. Do not repeat one-time recording, manuscript\n'
        'build/copy or historical controller operations. Preserve all dirty work.\n'
        'Full prior session memo is in this increment’s `control-before` directory.\n'
        'No commit or subagent is requested. No global continuation veto fired.\n')
    (ROOT / 'data/accounting-master/simulator-session-20261023.md').write_text(session)
    path = ROOT / 'data/accounting-master/next-plan.json'
    data = json.loads(path.read_text()); prior = {k:v for k,v in data.items() if k != 'active_execution'}
    active = data['active_execution']
    active['active_work_plan'] = NEXT
    active['latest_result'] = REL + '/result.md'
    active['latest_results'].append(REL+'/result.md')
    active['completed_increments'].append('PolicyInformationDraft/1:93 checks and read-only replay; exact policy/materializer timing and partial-result semantics; synthetic only')
    active['next'][0] = 'Whole-language review of all 53 obligations, 6 interactions and 46 operations, then highest-dependency ready design repair'
    write_json(path, data)
    assert {k:v for k,v in json.loads(path.read_text()).items() if k != 'active_execution'} == prior
    path = ROOT / 'scripts/accounting_master_catalog.json'
    data = json.loads(path.read_text()); prior = {k:v for k,v in data.items() if k != 'active_execution_note'}
    data['active_execution_note']['active_work_plan'] = NEXT
    data['active_execution_note']['latest_result'] = REL + '/result.md'
    write_json(path,data)
    assert {k:v for k,v in json.loads(path.read_text()).items() if k != 'active_execution_note'} == prior
    write_json(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True,'whole_rows_closed':0})
    print(json.dumps({'updated_controls':len(names),'checks':93,'next_plan':NEXT,'legacy_fields_unchanged':True}))

if __name__ == '__main__':
    main()
