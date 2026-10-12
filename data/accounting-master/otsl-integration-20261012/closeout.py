"""Close the checked 2.46 integration once and refresh four live controls."""
import datetime
import json
import platform
import sys
from build_candidate import ROOT, OUT, BASE, CAND, sha, save

assert not (OUT / 'completion.json').exists()
b = json.loads((OUT / 'baseline.json').read_text())
c = json.loads((OUT / 'integration-checks.json').read_text())
assert c['passed'] == 127 and not c['failed'] and c['pages'] == 183
pdf = CAND / 'accounting-product-proposal.pdf'
assert sha(pdf) == c['pdf_sha256']
assert (OUT / 'result.md').exists()
old = '''Integrate the checked OTSL syntax/geometry distinction and specific later-code
verification boundary in a separate Version 2.46. Preserve Version 2.45 and
all old content, then rotate to another concrete workstream. Plan:
`docs/plans/accounting-otsl-integration-20261012.md`.'''
new = '''Seek the exact Apple 5 November 2018 indenture, incorporated as annual
Exhibit 4.19 from S-3 accession 0001193125-18-317844, through a new public
contract-index source. Distinguish mirror identity from official-byte
equivalence; do not retry the failed SEC or EDGAR Online routes. Preserve
Version 2.46 and the frozen forty-target frontier. Plan:
`docs/plans/accounting-apple-2018-indenture-source-20261012.md`.'''
summary = '''Version 2.46 explains token syntax versus rectangular merged-cell geometry
on PDF 150, using the checked two-by-two counterexample and the specific
later-decoder source defect. All 127 integration checks pass; all 48 displays,
92 earlier references and prior prose remain, with one reference added.
Eight final pages were inspected and the build is clean. The source inquiry
passed 50 checks. Published-version equivalence, actual prediction effects,
runtime compatibility and independent/human acceptance remain open.
Full readiness stays not_ready. E01/E05/E07/E08/E14 remain open.
Result: `data/accounting-master/otsl-integration-20261012/result.md`.
'''
heading = '## Current Version 2.46 token syntax and cell geometry\n\n'

def replace_once(s, before, after):
    assert s.count(before) == 1, (before, s.count(before))
    return s.replace(before, after, 1)

prepared = []
for r in b['pointer_snapshots']:
    p = ROOT / r['live']
    assert sha(p) == r['sha256'] == sha(ROOT / r['snapshot'])
    s = p.read_text()
    if p.name == 'accounting-master-checkpoint.md':
        s = replace_once(s, '## Current candidate\n\n',
            '## Current candidate\n\n**Version 2.46, 183 pages**\nPDF: '
            + str(pdf.relative_to(ROOT)) + '\nSHA256: ' + sha(pdf) + '\n\n'
            + summary + '\n## Preserved Version 2.45 TableFormer explanation\n\n')
    elif p.name == 'next-plan.md':
        s = replace_once(s, '**182-page Version 2.45**', '**183-page Version 2.46**')
        s = replace_once(s, str((BASE / 'accounting-product-proposal.pdf').relative_to(ROOT)), str(pdf.relative_to(ROOT)))
        s = replace_once(s, b['pdf_sha256'], sha(pdf))
        s = replace_once(s, 'Result: data/accounting-master/tableformer-integration-20261012/result.md',
                         'Result: data/accounting-master/otsl-integration-20261012/result.md')
        s = replace_once(s, '## Completed boundary\n\n', '## Completed boundary\n\n'
                         + summary + '\n## Preserved Version 2.45 TableFormer explanation\n\n')
    elif p.name == 'accounting-continuation-requirements-20261007.md':
        s = replace_once(s, '## Current Version 2.45 TableFormer explanation',
            heading + 'E08/C06, E14/C07, P18; MC23/25/29–35, G8/G9/G10/G18.\n'
            + summary + '\n## Preserved Version 2.45 TableFormer explanation')
    else:
        s = replace_once(s, 'Version 2.45 adds the TableFormer text/structure/score distinction and adapter evidence.',
            'Version 2.46 adds the token-syntax/cell-geometry distinction and decoder source finding.\n'
            'Version 2.45 preserves the TableFormer text/structure/score distinction and adapter evidence.')
        s = replace_once(s, '**182-page Version 2.45**', '**183-page Version 2.46**')
        s = replace_once(s, b['pdf_sha256'], sha(pdf))
        s = replace_once(s, 'Current through Version 2.45 and the TableFormer inquiry', 'Current through Version 2.46 and the OTSL inquiry')
        s = replace_once(s, 'Current; Version 2.45 integrated; OTSL inquiry complete; next unit integrates geometry validation',
                         'Current; Version 2.46 integrated; next unit seeks the exact Apple 2018 indenture through a new source')
        s = replace_once(s, 'Current through Version 2.45 and the latest bounded source inquiries',
                         'Current through Version 2.46 and the latest bounded source inquiries')
        s = replace_once(s, 'or Version 2.45 outputs', 'or Version 2.46 outputs')
        s = replace_once(s, 'Bounded integration delivered through Version 2.45', 'Bounded integration delivered through Version 2.46')
        s = replace_once(s, 'The current baseline is Version 2.44;', 'The current baseline is Version 2.46;')
        s = replace_once(s, '## Current Version 2.44 score-rounding explanation', '## Preserved Version 2.44 score-rounding explanation')
        s = replace_once(s, '## Current Version 2.45 TableFormer explanation',
                         heading + summary + '\n## Preserved Version 2.45 TableFormer explanation')
        s = replace_once(s, 'latest Caiani access evidence and six forward metadata dispositions',
            'Caiani access evidence and six forward metadata dispositions; complete 2022 TableFormer main/supplement inspection (60 checks), exact OTSL arXiv v1 inspection (50 checks), and Version 2.45/2.46 method/score/geometry explanations')
        s = replace_once(s, 'TableFormer 4.0.2 source/consumer audit and 32 checks;',
            'TableFormer 4.0.2 source/consumer audit and 32 checks; later matching, geometry and constant-counter findings with explicit runtime limits;')
        s = replace_once(s, 'Extend the existing reference frontier from the 40 outstanding targets, recording newly discovered substantive dependencies.',
            'Seek the exact 5 November 2018 Apple indenture through a new public source, preserving mirror/official identity limits. Extend the existing reference frontier from the 40 outstanding targets, recording newly discovered substantive dependencies.')
        s = replace_once(s, 'the frontier review selects independent TableFormer literature/consumer work next.',
            'TableFormer/OTSL preparation and Version 2.45/2.46 integration are complete; the next rotation seeks the exact Apple 2018 debt contract.')
        s = replace_once(s, 'integrate the syntax/geometry distinction and match remaining manuscript claims to technically inspected sources.',
            'Version 2.46 integrates the syntax/geometry distinction. Match remaining manuscript claims to technically inspected sources.')
        s = replace_once(s, '1. Follow the direct next plan: integrate the checked OTSL syntax/geometry\n   distinction in Version 2.46, then rotate to another concrete workstream.',
            '1. Follow the direct next plan: seek the exact Apple 2018 indenture through\n   a new public source after the completed Version 2.46 integration.')
    if p.name != 'accounting-continuation-requirements-20261007.md':
        s = replace_once(s, old, new)
    s = replace_once(s, 'reported experiments. Add explicit geometry validation in Version 2.46.',
                     'reported experiments. Version 2.46 now explains the extra geometry requirement.')
    s = replace_once(s, 'reference 9 identifies the exact 2023 tokenization follow-up, still unread.',
                     'reference 9 identifies the exact 2023 tokenization follow-up, now inspected\nin the separate OTSL inquiry.')
    s = replace_once(s, 'performance, the exact tokenization follow-up and independent/human acceptance\nremain open.',
        'performance and independent/human acceptance remain open. The exact\ntokenization follow-up is now inspected and integrated in Version 2.46.')
    prepared.append((p, r, s))

rows = []
for p, r, s in prepared:
    p.write_text(s)
    q = OUT / 'pointers-after' / r['live']
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_bytes(p.read_bytes())
    rows.append({'live': r['live'], 'snapshot': str(q.relative_to(ROOT)), 'sha256': sha(q)})
save('controls-after.json', rows)
plans = ['docs/plans/accounting-otsl-integration-20261012.md',
         'docs/plans/accounting-apple-2018-indenture-source-20261012.md']
deps = [BASE / 'accounting-product-proposal.pdf',
        ROOT / 'data/accounting-master/otsl-paper-20261012/run-manifest.json',
        ROOT / 'data/accounting-master/otsl-paper-20261012/completion.json']
paths = [p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [p for p in CAND.rglob('*') if p.is_file()] + [ROOT / p for p in plans]
now = datetime.datetime.now(datetime.timezone.utc)
m = {'git_commit': b['git_commit'], 'started_utc': b['started_utc'], 'closed_utc': now.isoformat(),
     'plans': plans, 'result': str((OUT / 'result.md').relative_to(ROOT)),
     'commands': [['python3', str((OUT / n).relative_to(ROOT))] for n in
                  ['build_candidate.py', 'render_review.py', 'verify_integration.py', 'closeout.py']],
     'build_commands': 'build-run.json', 'surface_commands': 'surface-runs.json',
     'reviewed_pdf_pages': [1, 149, 150, 151, 152, 179, 180, 183],
     'environment': {'python': sys.executable, 'version': platform.python_version(), 'tex': 'LuaLaTeX/BibTeX through latexmk'},
     'cpu_gpu': 'CPU document processing; CUDA_VISIBLE_DEVICES=-1 for build; no framework/device use',
     'data_version': 'Protected 2.45 source/PDF and closed OTSL arXiv v1/consumer inquiry',
     'seeds': 'N/A: deterministic integration',
     'wall_seconds': {'elapsed_including_review': (now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
                      'build': json.loads((OUT / 'build-run.json').read_text())['wall_seconds'], 'checks': c['wall_seconds']},
     'input_hashes': {str(p.relative_to(ROOT)): sha(p) for p in deps},
     'artifact_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))},
     'pdf_sha256': sha(pdf), 'pages': c['pages'], 'readiness': 'not_ready',
     'runtime': 'held', 'next_plan': plans[-1]}
save('run-manifest.json', m)
for p, h in (m['input_hashes'] | m['artifact_hashes']).items():
    assert sha(ROOT / p) == h
save('completion.json', {'status': 'bounded integration complete; independent_reader_pending',
    'integration_checks': c['passed'], 'failed': 0, 'manifest_sha256': sha(OUT / 'run-manifest.json'),
    'bound_artifacts': len(m['artifact_hashes']), 'readiness': 'not_ready',
    'pdf_sha256': sha(pdf), 'pages': c['pages'], 'next_plan': plans[-1]})
print(json.dumps({'checks': c['passed'], 'artifacts': len(m['artifact_hashes']), 'controls': len(rows), 'pdf_sha256': sha(pdf)}))
