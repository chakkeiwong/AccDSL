"""One-shot documentary closeout; never executes the historical controller."""
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

manifest = OUT / 'run-manifest.json'
assert not manifest.exists(), 'Closeout already recorded; inspect rather than rerun'
checks = json.loads((OUT / 'checks.json').read_text())
assert checks['passed'] and checks['count'] == 78
index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
assert index == (ROOT / 'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
pdf = ROOT / 'docs/design/proposal/manuscript-corporate-residuals-20261015/accounting-product-proposal.pdf'
assert sha(pdf) == '2f827b851470e38a3242bb70a0a106a8ff8c3e9140c1cfa66a71effbc4d97f59'
paths = [
    'docs/plans/accounting-master-current.md',
    'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-continuation-requirements-20261007.md',
    'docs/plans/accounting-p17-completion-20261014.md',
    'docs/plans/accounting-p18-completion-20261014.md',
    'data/accounting-master/next-plan.md',
]
old = 'Next: execute R04 under docs/plans/accounting-consequential-literature-20261015.md; then ready R05 future validation protocols and R06 reuse locks, while resolving the named R03 design residuals before R07/R08. Runtime execution remains held.'
new = 'Next: execute R05 future validation protocols, then R06 selected reuse/terms/exchanges, while resolving the named R03 design residuals before R07/R08. R04 scoped reconciliation is delivered; broad scholarly coverage remains open. Runtime execution remains held.'
section = '''## Literature reconciliation and next work — 15 October 2026

R04's scoped reconciliation is delivered: 44 inherited consequential claims reviewed, 20 source-specific claim records appended, and 78 integrity/disposition checks passed. All six ledgers preserve historical rows and dates; four blocked originals remain blocked. Result: data/accounting-master/consequential-literature-20261015/result.md. Version 3.00 and its PDF are unchanged. Broad literature/proof coverage, named R03 design residuals, validation, dependency decisions and final assessment remain open; full readiness stays not_ready.

Next: R05 under docs/plans/accounting-future-validation-20261015.md. Prepare target-specific future protocols only; no experiment, runtime, installation or review campaign is authorised by this closeout. Continue R06 and the named R03 repairs before R07/R08.

'''
before = OUT / 'controls-before-r05'
before.mkdir()
records = []
for rel in paths:
    p = ROOT / rel
    text = p.read_text()
    assert old in text, rel
    (before / p.name).write_bytes(p.read_bytes())
    original = sha(p)
    text = text.replace(old, new)
    pos = text.index('\n## ')
    text = text[:pos+1] + section + text[pos+1:]
    p.write_text(text)
    records.append({'path': rel, 'before_sha256': original, 'after_sha256': sha(p), 'obsolete_next_pointer_absent': old not in text})
record = {
    'date': '2026-10-15', 'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'git_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'commands': ['python3 data/accounting-master/consequential-literature-20261015/inventory.py', 'python3 data/accounting-master/consequential-literature-20261015/reconcile.py', 'python3 data/accounting-master/consequential-literature-20261015/verify.py', 'python3 data/accounting-master/consequential-literature-20261015/closeout.py'],
    'command_provenance': 'Earlier completed commands recovered from execution artifacts; only closeout is executed by this script.',
    'environment': 'System python3; documentary JSON/text and hash checks only',
    'cpu_gpu_status': 'CPU file processing; no numerical framework or GPU detection/initialisation',
    'data_version': 'Version 3.00 plus the six-ledger baseline and append-only reconciliation',
    'seeds': 'N/A: deterministic documentary audit',
    'wall_time': 'Not captured for the interrupted/recovered multi-turn reconciliation; no runtime claim',
    'plan': 'docs/plans/accounting-consequential-literature-20261015.md',
    'result': str((OUT/'result.md').relative_to(ROOT)),
    'artifact_paths': [str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))] + [str((OUT/'claim-review.md').relative_to(ROOT))],
    'candidate_pdf': str(pdf.relative_to(ROOT)), 'candidate_sha256': sha(pdf),
    'checks': {'passed': True, 'count': 78, 'meaning': checks['interpretation']},
    'controls': records, 'index_sha256': hashlib.sha256(index).hexdigest(),
    'readiness': 'not_ready', 'next': 'R05 future protocols; R06 and named R03 repairs remain ready',
}
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT) == index
manifest.write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps({'closed': 'R04 scoped reconciliation', 'checks':78,'controls_updated':len(records),'candidate_preserved':True,'index_preserved':True,'next':'R05'}))
