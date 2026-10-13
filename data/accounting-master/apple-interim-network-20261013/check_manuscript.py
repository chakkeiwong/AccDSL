"""Check the additive candidate against its protected source baseline."""
import collections
import hashlib
import json
import re
from pathlib import Path
import fitz

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads((UNIT / 'baseline.json').read_text())
candidate = json.loads((UNIT / 'candidate.json').read_text())
base, cand = ROOT / candidate['baseline'], ROOT / candidate['candidate']
checks = {}
for rel, digest in baseline['candidate_files'].items():
    checks['protected:' + rel] = sha(ROOT / rel) == digest
for rel in candidate['source_hashes']:
    text = (base / rel).read_text()
    if rel == 'accounting-product-proposal.tex':
        text = text.replace('Version 2.60', 'Version 2.61')
    if rel == 'chapters/13-reference-company.tex':
        text = text.replace('\\input{sections/apple-statement-network}', '\\input{sections/apple-statement-network}\n\\input{sections/apple-interim-network}')
    checks['additive:' + rel] = (cand / rel).read_text() == text
def features(folder):
    text = '\n'.join(p.read_text() for p in sorted(folder.rglob('*.tex')))
    cites = collections.Counter(k.strip() for match in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text) for k in match.split(','))
    displays = collections.Counter(re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}.*?\\end\{(?:equation|align|gather|multline)\*?\}', text, re.S))
    return cites, displays
old_cites, old_displays = features(base)
new_cites, new_displays = features(cand)
checks['prior_citations_preserved'] = not(old_cites - new_cites)
checks['prior_displays_preserved'] = not(old_displays - new_displays)
checks['bibliography_unchanged'] = sha(base / 'references.bib') == sha(cand / 'references.bib')
keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', (cand / 'references.bib').read_text()))
checks['citations_resolve'] = set(new_cites) <= keys
checks['clean_log'] = not re.search(r'Warning|Overfull|Underfull|undefined|^!', (cand / 'accounting-product-proposal.log').read_text(), re.M)
checks['build_success'] = json.loads((UNIT / 'build-run.json').read_text())['exit_code'] == 0
source_checks = json.loads((UNIT / 'source-arithmetic-checks.json').read_text())
checks['source_and_arithmetic_pass'] = not source_checks['failed']
renders = json.loads((UNIT / 'candidate-renders.json').read_text())
review = json.loads((UNIT / 'rendered-review.json').read_text())
pdf = cand / 'accounting-product-proposal.pdf'
checks['current_pdf_review'] = sha(pdf) == renders['pdf_sha256'] == review['pdf_sha256']
with fitz.open(pdf) as d:
    text = ' '.join(' '.join(p.get_text().split()) for p in d)
    checks['version_and_pages'] = 'Version 2.61' in text and len(d) == renders['pdf_pages'] == 212
    checks['new_section_rendered'] = all(s in text for s in ['following quarter must start', '134,729', '130,117', 'unaudited'])
checks['six_manuscript_pages_inspected'] = {p['pdf_page'] for p in review['pages'] if p['inspected']} == {1,2,17,18,19,20}
checks['five_source_pages_inspected'] = {p['table'] for p in review['source_pages'] if p['inspected']} == {12,13,14,15,16}
for p in renders['pages']:
    checks['render:' + str(p['pdf_page'])] = sha(ROOT / p['path']) == p['sha256']
for p in review['source_pages']:
    checks['source_render:' + str(p['table'])] = sha(ROOT / p['image']) == p['sha256']
for rel, digest in baseline['annual_dependencies'].items():
    checks['annual_dependency:' + rel] = sha(ROOT / rel) == digest
for rel, digest in baseline['frozen'].items():
    checks['frozen:' + rel] = sha(ROOT / rel) == digest
failed = [k for k,v in checks.items() if not v]
result = {'checks':checks, 'passed':sum(checks.values()), 'failed':failed, 'prior_displays':sum(old_displays.values()), 'current_displays':sum(new_displays.values()), 'prior_citations':sum(old_cites.values()), 'current_citations':sum(new_cites.values()), 'pdf_sha256':sha(pdf)}
(UNIT / 'manuscript-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k != 'checks'}))
raise SystemExit(bool(failed))
