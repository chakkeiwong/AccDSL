"""One-time control refresh after corrected recording and observed replay."""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
PLAN = 'docs/plans/accounting-company-module-boundary-20261023.md'


def digest(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2)+'\n')


def main():
    assert not (HERE/'control-refresh.json').exists()
    result = json.loads((HERE/'checks.json').read_text())
    assert result['passed'] and len(result['checks']) == 62
    manifest = json.loads((HERE/'manifest.json').read_text())
    for group in ['data_version', 'implementation', 'outputs']:
        for name, h in manifest[group].items(): assert digest(ROOT/name) == h, name
    names = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md', 'docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md', 'data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md', 'data/accounting-master/next-plan.json',
        'scripts/accounting_master_catalog.json']
    note = ('## Portable company authoring checked after session recovery\n\n'
        'The corrected record and read-only replay pass 62 checks; 558 protected\n'
        'files remain unchanged. The typed closure has 168 records and 67 blobs.\n'
        'Original bytes, legacy draft identity and portable content/import identity\n'
        'remain separate. All six scenarios and both partial outcomes replay;\n'
        'rehashed false cash passes binding but fails trusted execution.\n'
        'Result: '+REL+'/result.md.\n\n'
        'Next: '+PLAN+'.\n'
        'Reuse the retained return-state migration to define the shared-book module\n'
        'boundary, then address native company state/authoring gaps. Existing\n'
        'corporate and sector methods remain distinct; no owner renaming or\n'
        'unearned generality. Version 3.54 stays 415 pages, not_ready, unchanged.\n'
        'S1–S5 partial; S6 held; S7 deferred; no whole requirement closes.\n'
        'Earlier entries are historical checkpoints.\n\n')
    before = {}
    for name in names:
        path = ROOT/name; before[name] = digest(path)
        dest = HERE/'control-before'/name; dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
        if name.endswith('.md'):
            title, rest = path.read_text().split('\n', 1)
            if 'simulator-session' in name:
                rest = ('PDF: docs/design/proposal/manuscript-company-language-20261023/accounting-product-proposal.pdf\n'
                    'SHA256: 8ca29eb2f2f2fbce11c2b02245e599e75493545f964782e1c450bf6690b84f6e.\n'
                    'No active diagnostic; preserve one-time recordings and dirty work.\n'
                    'No commit/subagents/controller campaign/outreach/forecast experiment.\n'
                    'Portable reference is not yet integrated into the manuscript.\n'
                    'Next read CompanyComposition migration_design.py and attempt-03 inputs.\n')
            path.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    path = ROOT/'data/accounting-master/next-plan.json'; data = json.loads(path.read_text())
    legacy = {k:v for k,v in data.items() if k != 'active_execution'}
    active = data['active_execution']; active.update(active_work_plan=PLAN, latest_result=REL+'/result.md')
    active['latest_results'].append(active['latest_result'])
    active['completed_increments'].append('Portable authoring:62 checks/replay;168 records,67 blobs,558 preserved files;exact legacy/content/import identities and trusted replay')
    active['next'][0] = 'Define and verify richer-method shared-book boundaries before native company state extensions'
    dump(path, data)
    assert legacy == {k:v for k,v in json.loads(path.read_text()).items() if k != 'active_execution'}
    path = ROOT/'scripts/accounting_master_catalog.json'; data = json.loads(path.read_text())
    legacy = {k:v for k,v in data.items() if k != 'active_execution_note'}
    data['active_execution_note'].update(active_work_plan=PLAN, latest_result=REL+'/result.md')
    dump(path, data)
    assert legacy == {k:v for k,v in json.loads(path.read_text()).items() if k != 'active_execution_note'}
    dump(HERE/'replay-observation.json', {'passed': True, 'checks': 62, 'protected_files': 558,
        'wall_seconds': 20.539550312998472, 'tool_session': 38460, 'read_only_replay': True})
    dump(HERE/'coverage-delta.json', {'advanced': ['MC02','MC04','MC05','MC08','MC10','MC13','MC18','MC24','MC25','MC28','MC34'],
        'evidence': REL+'/checks.json', 'whole_rows_closed': 0,
        'remaining': ['full normalized type IR', 'native richer modules', 'real source admission', 'physical durability', 'independent/domain/human acceptance']})
    dump(HERE/'control-refresh.json', {'before': before, 'after': {n:digest(ROOT/n) for n in names},
        'legacy_json_fields_unchanged': True, 'whole_rows_closed': 0})
    print(json.dumps({'controls': len(names), 'next': PLAN, 'legacy_fields_unchanged': True}))


if __name__ == '__main__': main()
