"""Prepare a distinct successor; preserve both the old candidate and live work."""
from pathlib import Path
import importlib.util, json, hashlib

H = Path(__file__).resolve().parent
R = H.parents[2]
OLD = H.parent / 'control-authority-integration-20261027'
assert not (H / 'source-preservation.json').exists()
assert json.loads((OLD / 'verification.json').read_text())['status'] == 'PASS'
live = json.loads((R / 'scripts/accounting_master_catalog.json').read_text())['active_execution_note']
assert live['current_candidate'].startswith('5.25;'), live['current_candidate']
source = (R / live['current_pdf']).parent
spec = importlib.util.spec_from_file_location('prior_integration', OLD / 'integrate.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
for name in ['simulation/conversion-book.tex', 'simulation/control-price.tex', 'chapters/14-financing-groups.tex', 'references.bib']:
    prior.transform(name, (source / name).read_text(), '5.25', '5.26')
assert 'aasb9scope2026' not in (source / 'references.bib').read_text()
code = (OLD / 'integrate.py').read_text()
code = code.replace("'control-boundary-repair-20261026','control-history-contract-20261026']", "'control-boundary-repair-20261026','control-history-contract-20261026','source-policy-integration-20261027']")
code = code.replace('accounting-control-authority-integration-20261026.md', 'accounting-control-authority-rebase-20261027.md')
(H / 'integrate.py').write_text(code)
body = (OLD / 'funding-control-authority.tex').read_text()
for old, new in [('paragraphs31', 'paragraphs 31'), ('paragraphs15', 'paragraphs 15'), ('and28', 'and 28'), ('paragraphs4', 'paragraphs 4'), ('15--16,22', '15--16, 22')]:
    body = body.replace(old, new)
(H / 'funding-control-authority.tex').write_text(body)
(H / 'authority.bib').write_bytes((OLD / 'authority.bib').read_bytes())
(H / 'reader-plan.md').write_text((OLD / 'reader-plan.md').read_text() + '\nRebase: the live 5.25 source-policy edition is the protected comparator. All new source-policy sections survive. The original 922-check candidate is retained but not advanced.\n')
spec = importlib.util.spec_from_file_location('rebased_integration', H / 'integrate.py')
rebased = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rebased)
rebased.prepare()
record = dict(status='PASS', reason='Live 5.25 superseded the original 5.24 baseline', prior_verification_sha256=hashlib.sha256((OLD/'verification.json').read_bytes()).hexdigest(), prior_candidate_preserved=True, citation_spacing_repaired=True)
(H/'rebase.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record))
