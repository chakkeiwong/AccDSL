"""Record complete author diagnosis once; never alter a completed review."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[3]
assert not (U / 'completion.json').exists()
subprocess.run([sys.executable, '-B', str(U / 'initialize.py'), 'validate'], check=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
d = json.loads((U / 'structure-ledger.json').read_text())
s = json.loads((U / 'synthesis-ledger.json').read_text())
assert len(d['ordered_segments']) == 74 and d['diagnosis_status'] == 'author_diagnosis_complete'
assert len(s['chapter_regressions']) == 17 and len(s['cumulative_prefixes']) == 8
for row in s['chapter_regressions'] + s['cumulative_prefixes']:
    assert sha(R / row['synthesis']['path']) == row['synthesis']['sha256']
assert sha(R / s['document_synthesis']['path']) == s['document_synthesis']['sha256']
controls = [R / p for p in ('docs/plans/accounting-master-current.md',
    'docs/plans/accounting-master-checkpoint.md', 'docs/plans/accounting-mission-requirements.md',
    'data/accounting-master/next-plan.md')]
snapshot = U / 'controls-before-diagnosis-complete'
snapshot.mkdir()
replacement = '''The exact Version 3.45 author diagnosis is complete: all 401 physical pages
and 676 nodes are recorded in 74 ordered segments, with 17 chapter/appendix
syntheses and eight cumulative prefixes. Three confirmed defects remain:
RR-001 tax project-history wording, RR-002 lease filename aside, and RR-003
initial-library/query scope. Independent and human acceptance remain pending.

Next: execute the audited protected Version 3.46 repair under
docs/plans/accounting-readability-repair-20261021.md. Preserve all mathematics,
citations, source qualifications and completed 3.45 evidence. Then continue
exact-candidate review and the named Wang1995, Merz/Wüthrich2014 and England2019
original-source/edition inquiries. No reading credit transfers to 3.46.
Allocation, current authority and actual entity preferences remain separate
dependencies. The E3 target and six scientific choices remain unselected; all
192 vintage admissions remain false. These block only dependent empirical work.

'''
for p in controls:
    text = p.read_text()
    start = text.index('Next: resume the whole-document chain at physical page ')
    end = text.index('The plan was skeptically re-audited at recovery.', start)
    revised = text[:start] + replacement + text[end:]
    revised = revised.replace('Whole-document regression' + chr(10) + 'remains pending; no local or inherited page credit applies.',
        'The completed whole-document author diagnosis is recorded below;' + chr(10) + 'independent acceptance remains pending.')
    shutil.copy2(p, snapshot / p.name)
    p.write_text(revised)
files = [p for p in U.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
result = {'status':'author_diagnosis_complete_repairs_required',
    'candidate_pdf':s['candidate_pdf'], 'pdf_sha256':s['pdf_sha256'],
    'pages':401, 'nodes':676, 'segments':74, 'chapter_syntheses':17, 'prefix_syntheses':8,
    'defects':[x['id'] for x in d['defects']],
    'independent_reader':'pending', 'human_acceptance':'pending',
    'whole_rows_closed':0, 'readiness':'not_ready',
    'bindings':{str(p.relative_to(R)):sha(p) for p in sorted(files)},
    'live_controls_at_completion':{str(p.relative_to(R)):sha(p) for p in controls}}
with (U / 'completion.json').open('x') as f:
    json.dump(result, f, indent=2); f.write(chr(10))
print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','live_controls_at_completion')}))
