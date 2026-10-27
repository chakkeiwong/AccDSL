"""Advance the verified 5.2 candidate once; preserve all replaced control bytes."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import importlib.util
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def digest(p):
    return sha256(p.read_bytes()).hexdigest()

def dump(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

v = json.loads((HERE / 'verification.json').read_text())
assert v['version'] == '5.2' and v['pages'] == 716
assert v['passed_preservation'] and not v['new_warnings'] and not v['out_of_page_text_blocks']
assert digest(ROOT / v['pdf']) == v['pdf_sha256']
assert (HERE / 'review.md').exists() and (HERE / 'result.md').exists()
spec = importlib.util.spec_from_file_location('integration', HERE / 'integrate.py')
integration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integration)
preservation = json.loads((HERE / 'source-preservation.json').read_text())
for name, h in preservation['sources'].items():
    assert digest(integration.SOURCE / name) == h
    assert (integration.TARGET / name).read_text() == integration.expected(name, (integration.SOURCE / name).read_text())
for name, h in preservation['evidence'].items():
    assert digest(ROOT / name) == h
assert digest(integration.TARGET / preservation['added_source']) == preservation['new_section_sha256']

plan = 'docs/plans/accounting-insurance-identity-adoption-20261026.md'
result = str((HERE / 'result.md').relative_to(ROOT))
remaining = str((HERE / 'remaining-work.md').relative_to(ROOT))
assert (ROOT / plan).exists()
concise = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-current-program-20261025.md', 'data/accounting-master/next-plan.md']
historical = ['docs/plans/accounting-master-checkpoint.md', 'docs/plans/accounting-master-program.md', 'docs/plans/accounting-product-design-checkpoint.md', 'docs/plans/accounting-mission-requirements.md', 'data/accounting-master/simulator-session-20261023.md']
controls = concise + historical + ['data/accounting-master/next-plan.json', 'scripts/accounting_master_catalog.json']
navigation = ['MISSION_CONTROL.md', 'docs/README.md', 'docs/design/README.md', 'data/accounting-master/recovery-current-20261026.md']
before = {n: (ROOT / n).read_bytes() for n in controls + navigation}
backup = HERE / 'control-before'
assert not backup.exists() and not (HERE / 'control-refresh.json').exists()

note = f'''## Current governing candidate — Version 5.2 — 26 October 2026

Version 5.2 is the 716-page governing design candidate, not_ready. Explicit
finite invariant source now reproduces both company programs and all 22 command
results, with 16 state counterexamples and 14 compile refusals. All 212 predecessor
sources are preserved under the recorded prose delta; 26 simulation chapters
remain unchanged. No new warnings. Cover/pages 267–268 and 681–684 inspected.
All 53 obligations, six interactions and 46 operations remain; no whole
requirement closes. S1–S5 partial, S6 held and E3 deferred.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.

'''
proposed = {}
for n in concise:
    tail = before[n].decode().split('Mission:', 1)[1]
    lines = []
    for line in ('Mission:' + tail).splitlines():
        if line.startswith('Current question:'):
            line = 'Current question: can versioned insurer request identity preserve complete financial publications and recovery?'
        elif line.startswith('Next action:'):
            line = 'Next action: audit native financial ownership and execute ' + plan + '.'
        elif line.startswith('Current residuals:'):
            line = 'Current residuals: ' + remaining + '.'
        elif line.startswith('| S3 Language |'):
            line = '| S3 Language | Wider rule algorithms, dynamic specialization and broader measurements/fiscal policies | Partial |'
        lines.append(line)
    proposed[n] = '# Current AccDSL master program\n\n' + note + '\n'.join(lines) + '\n'
for n in historical:
    first, rest = before[n].decode().split('\n', 1)
    rest = rest.replace('## Current governing candidate — Version 5.1', '## Prior governing candidate — Version 5.1', 1)
    proposed[n] = first + '\n\n' + note + rest.lstrip('\n')
updates = {'active_work_plan': plan, 'latest_result': result, 'current_candidate': '5.2;716 pages;not_ready',
           'current_pdf': v['pdf'], 'current_pdf_sha256': v['pdf_sha256'], 'remaining_work': remaining}
n = 'data/accounting-master/next-plan.json'
d = json.loads(before[n])
d['active_execution'].update(updates)
d['active_execution']['next'] = ['Audit native insurer ownership, effects and exact replay', 'Check an explicit versioned request-identity successor against full native publications', 'Integrate checked result, refresh remaining scope; S6 held and E3 deferred']
d['active_execution']['completed_increments'].append('Version5.2:716 pages;explicit finite invariant source;22 commands,16 counterexamples,14 compile refusals;212 predecessor sources protected')
d['active_execution']['latest_results'].extend(['data/accounting-master/invariant-source-authoring-20261026/result.md', result])
proposed[n] = json.dumps(d, indent=2) + '\n'
n = 'scripts/accounting_master_catalog.json'
d = json.loads(before[n])
d['active_execution_note'].update(updates)
proposed[n] = json.dumps(d, indent=2) + '\n'
n = 'MISSION_CONTROL.md'
t = before[n].decode()
assert 'Version 5.1 is the current 715-page' in t
t = t.replace('Version 5.1 is the current 715-page', 'Version 5.2 is the current 716-page', 1)
old = 'The [current integration result](data/accounting-master/bank-time-manuscript-integration-20261026/result.md) records exact bank profile adoption, preserved simulation content and repaired navigation. The [active plan](docs/plans/accounting-invariant-source-authoring-20261026.md) continues explicit invariant authoring.'
assert old in t
proposed[n] = t.replace(old, f'The [current integration result]({result}) records explicit finite invariant authoring and preserved simulation content. The [active plan]({plan}) audits insurer request identity with complete financial publication and recovery.')
n = 'docs/README.md'
proposed[n] = before[n].decode().replace('**Version 5.1, 715 pages**', '**Version 5.2, 716 pages**', 1).replace('bank-time-manuscript-integration-20261026/result.md', 'invariant-source-integration-20261026/result.md', 1)
n = 'docs/design/README.md'
proposed[n] = before[n].decode().replace('Version 5.1,', 'Version 5.2,', 1)
n = 'data/accounting-master/recovery-current-20261026.md'
proposed[n] = '# Current recovery pointer\n\n' + note + 'Next: native insurer identity adoption audit. Invariant source implementation and manuscript integration are complete.\nTen controls agree. Main stable links select 5.2; standalone links retain the unchanged verified 5.1 reading edition.\nDo not rerun completed writers. No background process running.\n'
prior = (HERE.parent / 'bank-time-manuscript-integration-20261026/remaining-work.md').read_text()
prior = prior.split('## Next dependency', 1)[0].replace('Version 5.1, 715 pages', 'Version 5.2, 716 pages')
prior = prior.replace('General rule/invariant authoring, broader algorithms and authoring usability', 'Wider rule algorithms, dynamic specialization and authoring usability')
prior += f'''## Next dependency

Explicit invariant source now removes the complete typed invariant from caller
imports and preserves all 22 saved command results, unknowns and refusal prefixes.
Bank exact-time adoption and its prior manuscript integration remain complete.
Execute {plan}.
The insurer request-pair repair is still metadata-only; inspect native financial
ownership before adopting it. Its financial publications differ from bank queries.
Retain ambiguous-history refusals and the complete-history migration assumption.

The 26 simulation chapters retain 67 failure mechanisms and 169 teaching checks;
these do not establish runtime or predictive acceptance. General authoring,
actual-source histories, sector/group compatibility, fiscal and measurement rules,
source gaps and independent whole-document acceptance remain. S6 held; E3 deferred.
'''
scope = ROOT / 'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts = {k: len(x) for k, x in json.loads(scope.read_text())['groups'].items()}
assert counts == {'obligations': 53, 'interactions': 6, 'operations': 46}
standalone = ROOT / 'docs/AccDSL-simulation-foundations.pdf'
prior_refresh = json.loads((HERE.parent / 'bank-time-manuscript-integration-20261026/control-refresh.json').read_text())
assert digest(standalone) == prior_refresh['standalone_pdf_sha256']
for n, data in before.items():
    p = backup / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
(HERE / 'remaining-work.md').write_text(prior)
for n, t in proposed.items():
    assert (ROOT / n).read_bytes() == before[n], 'concurrent_control_change:' + n
    (ROOT / n).write_text(t)
links = []
for suffix in ['pdf', 'tex']:
    p = ROOT / ('docs/AccDSL-latest.' + suffix)
    destination = integration.TARGET / ('accounting-product-proposal.' + suffix)
    assert p.is_symlink() and destination.exists()
    old = os.readlink(p)
    relative = os.path.relpath(destination, p.parent)
    temp = p.with_name(p.name + '.next')
    assert not temp.exists() and not temp.is_symlink()
    os.symlink(relative, temp)
    os.replace(temp, p)
    assert p.resolve() == destination
    links.append({'path': str(p.relative_to(ROOT)), 'before_target': old, 'after_target': relative, 'sha256': digest(p)})
for n in controls:
    assert plan in (ROOT / n).read_text() and v['pdf_sha256'] in (ROOT / n).read_text()
dump(HERE / 'control-refresh.json', {'next_plan': plan, 'updated_files': {n: {'before': sha256(b).hexdigest(), 'after': digest(ROOT / n)} for n, b in before.items()}, 'links': links, 'ten_controls_agree': True, 'original_scope': counts, 'whole_requirements_closed': 0, 'standalone_unchanged': True, 'standalone_pdf_sha256': digest(standalone)})
dump(HERE / 'run-manifest.json', {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'commands': ['integrate.py prepare', 'integrate.py build', 'integrate.py verify', 'advance.py'], 'environment': sys.version, 'cpu_gpu': 'CPU; GPU intentionally hidden', 'random_seeds': 'N/A deterministic', 'wall_seconds': json.loads((HERE / 'build.json').read_text())['wall_seconds'], 'wall_time_scope': 'Main manuscript build only', 'data_version': digest(scope), 'plan_file': 'docs/plans/accounting-invariant-source-integration-20261026.md', 'result_file': result, 'artifact_paths': ['source-preservation.json', 'verification.json', 'review.md', 'control-refresh.json', 'remaining-work.md'], 'timestamp_utc': datetime.now(timezone.utc).isoformat()})
print(json.dumps({'candidate': updates['current_candidate'], 'controls': len(controls), 'main_links': len(links), 'standalone_unchanged': True, 'next_plan': plan}))
