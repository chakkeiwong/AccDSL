"""Check preservation and bind the rendered review to the actual candidate."""
import collections
import json
import re

import fitz

from build_candidate import BASE, CAND, ROOT, UNIT, expected_text, save, sha

if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')

candidate = json.loads((UNIT / 'candidate.json').read_text())
checks = {}
checks['source_and_dependency_evidence'] = not json.loads((UNIT / 'source-calculation-checks.json').read_text())['failed']
checks['prior_pdf_preserved'] = sha(BASE / 'accounting-product-proposal.pdf') == candidate['baseline_pdf_sha256']
for rel, digest in candidate['source_hashes'].items():
    checks['baseline:' + rel] = sha(BASE / rel) == digest
    checks['candidate:' + rel] = (CAND / rel).read_text() == expected_text(rel)

def features(folder):
    text = '\n'.join((folder / rel).read_text() for rel in candidate['source_hashes'] if rel.endswith('.tex'))
    citations = collections.Counter()
    for value in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text):
        citations.update(k.strip() for k in value.split(','))
    displays = collections.Counter(re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation|align|gather|multline)\*?\}.*?\\end\{(?:equation|align|gather|multline)\*?\}', text, re.S))
    return citations, displays

old_cites, old_displays = features(BASE)
new_cites, new_displays = features(CAND)
checks['all_prior_citations_preserved'] = not (old_cites - new_cites)
checks['all_prior_displays_preserved'] = not (old_displays - new_displays)
checks['bibliography_unchanged'] = sha(BASE / 'references.bib') == sha(CAND / 'references.bib')
keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', (CAND / 'references.bib').read_text()))
checks['citations_resolve'] = set(new_cites) <= keys
checks['clean_final_build'] = not re.search(r'Warning|Overfull|Underfull|undefined|^!', (CAND / 'accounting-product-proposal.log').read_text(), re.M)
checks['build_exit_zero'] = json.loads((UNIT / 'build-run.json').read_text())['exit_code'] == 0
pdf = CAND / 'accounting-product-proposal.pdf'
renders = json.loads((UNIT / 'candidate-renders.json').read_text())
review = json.loads((UNIT / 'rendered-review.json').read_text())
checks['current_pdf_reviewed'] = sha(pdf) == renders['pdf_sha256'] == review['pdf_sha256']
with fitz.open(pdf) as document:
    text = ' '.join(' '.join(page.get_text().split()) for page in document)
    checks['version_and_page_count'] = 'Version 2.56' in text and len(document) == renders['pdf_pages'] == 203
    checks['substantive_new_passage_present'] = all(s in text for s in ['Acquisition costs before the renewal contracts exist', 'counting the same loss of 5 twice', 'restores 15 of the earlier loss of 25'])
checks['seven_pages_inspected'] = {p['pdf_page'] for p in review['pages'] if p['inspected']} == {1, 5, 6, 144, 145, 146, 147}
for page in renders['pages']:
    checks['render:' + str(page['pdf_page'])] = sha(ROOT / page['path']) == page['sha256']
protected = json.loads((ROOT / 'data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json').read_text())
for rel, digest in protected['protected_hashes'].items():
    checks['frozen:' + rel] = sha(ROOT / rel) == digest
failures = [name for name, passed in checks.items() if not passed]
save('manuscript-checks.json', {'checks': checks, 'passed': sum(checks.values()), 'failed': failures,
                               'source_files': len(candidate['source_hashes']),
                               'prior_display_blocks': sum(old_displays.values()),
                               'prior_citation_occurrences': sum(old_cites.values()),
                               'current_citation_occurrences': sum(new_cites.values()),
                               'pdf_sha256': sha(pdf)})
print(json.dumps({'passed': sum(checks.values()), 'failed': failures, 'pdf_sha256': sha(pdf),
                  'source_files': len(candidate['source_hashes']), 'displays': sum(old_displays.values()),
                  'prior_citations': sum(old_cites.values()), 'current_citations': sum(new_cites.values())}))
raise SystemExit(bool(failures))
