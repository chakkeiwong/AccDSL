#!/usr/bin/env python3
"""Check document/library consistency; this is not a source-truth audit."""
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'docs/design'
RESEARCH = DESIGN / 'research'
started = time.monotonic()
errors = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    try:
        return json.loads(path.read_text())
    except (ValueError, OSError) as exc:
        errors.append(f'{path.relative_to(ROOT)}: {exc}')
        return None


def command(args):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        errors.append(f'{args[0]} failed: {result.stderr.strip()}')
    return result.stdout


catalog = read_json(RESEARCH / 'catalog.json') or []
ledgers = {}
for name in ['source-support', 'citation-venue', 'backward-snowball',
             'forward-snowball', 'claim-support', 'omissions', 'tools',
             'retrieval-attempts']:
    data = read_json(RESEARCH / f'{name}.json')
    ledgers[name] = len(data.get('records', data.get('attempts', []))) if isinstance(data, dict) else len(data or [])

paper_records = []
for row in catalog:
    if not row.get('local_path'):
        continue
    path = ROOT / row['local_path']
    if not path.exists():
        errors.append(f'Missing PDF: {row["local_path"]}')
        continue
    sha = digest(path)
    if sha != row.get('sha256'):
        errors.append(f'PDF hash differs from catalogue: {row["id"]}')
    with path.open('rb') as stream:
        if not stream.read(8).startswith(b'%PDF-'):
            errors.append(f'Non-PDF content: {row["local_path"]}')
    if not (ROOT / row['text_path']).is_file():
        errors.append(f'Missing source text: {row["id"]}')
    info = command(['pdfinfo', str(path)])
    pages_match = re.search(r'^Pages:\s+(\d+)', info, re.M)
    pages = int(pages_match[1]) if pages_match else None
    if pages != row.get('pages'):
        errors.append(f'PDF page count differs from catalogue: {row["id"]}')
    paper_records.append({'id': row['id'], 'path': row['local_path'],
                          'sha256': sha, 'pages': pages})
expected = {ROOT / r['path'] for r in paper_records}
actual = set((ROOT / 'docs/papers').glob('*.pdf'))
if expected != actual:
    errors.append('Paper directory and catalogue PDF paths differ')
ids = [r['id'] for r in catalog]
if len(ids) != len(set(ids)):
    errors.append('Duplicate catalogue identifiers')

root_tex = DESIGN / 'accounting-product-design.tex'
source = root_tex.read_text()
inputs = [DESIGN / (p + '.tex') for p in re.findall(r'\\input\{([^}]+)\}', source)]
expanded = re.sub(r'\\input\{([^}]+)\}', lambda m: (DESIGN / (m[1] + '.tex')).read_text(), source)
(DESIGN / 'review/expanded-source.tex').write_text(expanded)
labels = re.findall(r'\\label\{([^}]+)\}', expanded)
references = re.findall(r'\\(?:eqref|ref|pageref)\{([^}]+)\}', expanded)
if len(labels) != len(set(labels)):
    errors.append('Duplicate TeX labels')
missing_refs = sorted(set(references) - set(labels))
if missing_refs:
    errors.append(f'Missing reference targets: {missing_refs}')
bib = DESIGN / 'references.bib'
bib_keys = re.findall(r'@\w+\{([^,]+),', bib.read_text())
if len(bib_keys) != len(set(bib_keys)):
    errors.append('Duplicate bibliography keys')
cited = set()
for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', expanded):
    cited.update(x.strip() for x in group.split(','))
if cited - set(bib_keys):
    errors.append(f'Missing bibliography entries: {sorted(cited - set(bib_keys))}')

log_path = DESIGN / 'accounting-product-design.log'
log = log_path.read_text()
problem_patterns = [r'^! .+', r'^Overfull .+', r'^Missing character:.+',
                    r'^LaTeX Warning: (?:Citation|Reference).+',
                    r'^Package natbib Warning: Citation.+',
                    r'There were undefined (?:references|citations)']
for pattern in problem_patterns:
    errors.extend(re.findall(pattern, log, re.M))
underfull = re.findall(r'^Underfull .+', log, re.M)
pdf = DESIGN / 'accounting-product-design.pdf'
info = command(['pdfinfo', str(pdf)])
match = re.search(r'^Pages:\s+(\d+)', info, re.M)
pdf_pages = int(match[1]) if match else None
build_inputs = [root_tex, bib, *inputs]
if any(p.stat().st_mtime > pdf.stat().st_mtime for p in build_inputs):
    errors.append('A TeX/bibliography input is newer than the PDF')

examples = read_json(DESIGN / 'review/example-checks.json') or {}
example_checks = examples.get('checks', [])
if not example_checks or not all(c.get('passed') is True for c in example_checks):
    errors.append('Example arithmetic result is missing or reports a failure')

files = [*build_inputs, pdf, ROOT / 'docs/papers/README.md', DESIGN / 'README.md',
         *sorted(RESEARCH.glob('*.json')), DESIGN / 'review/example-checks.json',
         ROOT / 'scripts/check_design_examples.py',
         ROOT / 'scripts/build_design_research.py', Path(__file__).resolve()]
result = {
    'verified_at_utc': datetime.now(timezone.utc).isoformat(),
    'command': 'python3 scripts/verify_design_document.py',
    'question': 'Are the compiled design, local paper library and research references internally consistent?',
    'criterion': 'No missing/hash-mismatched PDFs, unresolved references/citations, stale build inputs, or serious TeX diagnostics',
    'status': 'passed' if not errors else 'failed',
    'errors': errors,
    'document_pages': pdf_pages,
    'chapters_and_appendices': len(inputs),
    'archived_papers': len(paper_records),
    'blocked_catalogue_candidates': [r['id'] for r in catalog if not r.get('local_path')],
    'cited_keys': sorted(cited),
    'bibliography_entries': len(bib_keys),
    'research_record_counts': ledgers,
    'existing_exact_arithmetic_checks': len(example_checks),
    'arithmetic_scope': 'Previously executed manuscript illustrations; no DSL/runtime test',
    'layout_diagnostics': {'overfull_boxes': 0 if not re.search(r'^Overfull ', log, re.M) else 'see errors',
                           'underfull_boxes': len(underfull),
                           'interpretation': 'Underfull spacing requires visual disposition, not automatic failure'},
    'papers': paper_records,
    'sha256': {str(p.relative_to(ROOT)): digest(p) for p in files},
    'environment': {'python': sys.version.splitlines()[0],
                    'xelatex': command(['xelatex', '--version']).splitlines()[0],
                    'processor': 'ordinary CPU document utilities; no ML/GPU framework used',
                    'seeds': 'N/A: deterministic document checks',
                    'git_commit': 'unavailable: workspace Git marker is not a usable repository'},
    'plan': 'docs/plans/accounting-product-design.md',
    'review': 'docs/design/review/author-review.md',
    'wall_seconds': round(time.monotonic() - started, 3),
    'does_not_establish': ['source claims independently verified', 'human comprehension',
                           'accounting-standard compliance', 'implemented product',
                           'forecast validity or superiority'],
}
out = DESIGN / 'review/verification.json'
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'pages': pdf_pages,
                  'papers': len(paper_records), 'errors': errors,
                  'report': str(out.relative_to(ROOT))}))
raise SystemExit(bool(errors))
