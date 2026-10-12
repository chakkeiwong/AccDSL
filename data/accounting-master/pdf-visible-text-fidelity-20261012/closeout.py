"""Freeze final evidence after review; later work changes only live controls."""
import json
import subprocess
import time
from pathlib import Path
from prepare import OUT, ROOT, PDF, BASE, sha, save
from build_candidate import CAND

start=time.monotonic()
assert not (OUT/'completion.json').exists()
checks=json.loads((OUT/'checks.json').read_text())
assert checks['passed']==136 and not checks['failed']
assert sha(CAND/'accounting-product-proposal.pdf')==checks['candidate_pdf_sha256']
review=(OUT/'author-review.md').read_text()
assert checks['candidate_pdf_sha256'] in review
assert all(x in review for x in ['Reader comprehension','Mathematical integrity','Source fidelity','Typography and rendering'])
for x in json.loads((OUT/'controls-after.json').read_text()):
    assert sha(ROOT/x['live'])==x['sha256']==sha(ROOT/x['snapshot'])
    assert '2.38' in (ROOT/x['live']).read_text()
for x in json.loads((OUT/'final-renders.json').read_text()):
    assert sha(ROOT/x['pdf'])==x['pdf_sha256'] and sha(ROOT/x['path'])==x['sha256']
# Superseded temporary surface runs precede the typography repair; the named
# root/adapter before/after reports and comparison are the final diagnostics.
for name in ['surface-before.json','surface-before.md','surface-before-stdout.log',
             'surface-after.json','surface-after.md','surface-after-stdout.log']:
    p=OUT/name
    if p.exists():
        dest=OUT/'intermediate'/name
        dest.parent.mkdir(exist_ok=True)
        p.rename(dest)
plan=ROOT/'docs/plans/accounting-pdf-visible-text-fidelity-20261012.md'
nextplan=ROOT/'docs/plans/accounting-jpmorgan-funds-transfer-20261012.md'
inputs=[PDF,BASE/'accounting-product-proposal.pdf',
        ROOT/'data/financial-report-benchmark/annotation-record.schema.json',plan]
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [p for p in CAND.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark','.pdf','.log','.blg'}]
paths += [nextplan]
build=json.loads((OUT/'build-run.json').read_text())
diagnostic=json.loads((OUT/'diagnostic-run.json').read_text())
render=json.loads((OUT/'render-run.json').read_text())
manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'date':'2026-10-12','plan':str(plan.relative_to(ROOT)),'result':str((OUT/'result.md').relative_to(ROOT)),
    'commands':[diagnostic['command'],['python3',str(OUT.relative_to(ROOT))+'/exchange.py'],
        ['python3',str(OUT.relative_to(ROOT))+'/build_candidate.py'],build['command'],render['command'],
        ['python3',str(OUT.relative_to(ROOT))+'/verify.py'],['python3',str(OUT.relative_to(ROOT))+'/update_controls.py'],
        ['python3',str(Path(__file__).relative_to(ROOT))]],
    'environment':{'python':diagnostic['python'],'pymupdf':diagnostic['pymupdf'],'mupdf':diagnostic['mupdf'],
        'poppler':diagnostic['poppler_version'],'build':build['environment_overrides']},
    'cpu_gpu':'CPU-only document preparation; CUDA_VISIBLE_DEVICES=-1; no GPU import or device use.',
    'data_version':'Exact selected PDF and frozen Version 2.37 bound below',
    'seeds':'N/A: deterministic document preparation',
    'wall_time_seconds':{'diagnostic':diagnostic['wall_seconds'],'final_build':build['wall_seconds'],
        'render_and_surface':render['wall_seconds'],'verification':checks['wall_seconds'],
        'closeout':time.monotonic()-start},
    'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in inputs},
    'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)},
    'intermediate_scope':'intermediate/surface-after describes the pre-typography PDF; final diagnostics are surface-root-after and surface-adapter-after.',
    'review':'Author only; independent/human/domain/legal acceptance pending.',
    'readiness':'not_ready','runtime':'held'}
save('run-manifest.json',manifest)
for rel,digest in manifest['input_hashes'].items(): assert sha(ROOT/rel)==digest
for rel,digest in manifest['artifact_hashes'].items(): assert sha(ROOT/rel)==digest
save('completion.json',{'status':'bounded documentary and manuscript unit complete','checks':136,'failed':0,
    'bound_inputs':len(inputs),'bound_artifacts':len(manifest['artifact_hashes']),
    'manifest_sha256':sha(OUT/'run-manifest.json'),'pdf_sha256':checks['candidate_pdf_sha256'],
    'pages':175,'readiness':'not_ready','next_plan':str(nextplan.relative_to(ROOT))})
print(json.dumps({'checks':136,'bound_artifacts':len(manifest['artifact_hashes']),'pages':175,'readiness':'not_ready'}))
