"""Check the bounded manuscript delta and its protected baseline, not readiness."""
import hashlib
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'docs/design/proposal/manuscript'
NEW = ROOT / 'docs/design/proposal/manuscript-asbe-20261007'
start = time.monotonic()
checks = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name, passed, details=None):
    checks.append({'name': name, 'passed': bool(passed), 'details': details})


baseline = json.loads((OUT / 'baseline-manifest.json').read_text())
for path, expected in baseline['baseline_file_hashes'].items():
    check('baseline unchanged: ' + path, sha(ROOT / path) == expected)

allowed = {'accounting-product-proposal.tex', 'sections/standards-methods.tex',
           'references.bib'}
changed = [p for p in baseline['source_paths'] if sha(BASE / p) != sha(NEW / p)]
check('only intended three source inputs changed', set(changed) == allowed, changed)
check('all baseline source/specification inputs copied',
      all((NEW / p).is_file() for p in baseline['source_paths']))

tex_paths = [p for p in baseline['source_paths'] if p.endswith('.tex')]
old_text = '\n'.join((BASE / p).read_text() for p in tex_paths)
new_text = '\n'.join((NEW / p).read_text() for p in tex_paths)
labels = lambda text: re.findall(r'\\label\{([^}]+)\}', text)
old_labels, new_labels = Counter(labels(old_text)), Counter(labels(new_text))
check('all existing labels retained', not old_labels - new_labels)
check('no duplicate labels', all(n == 1 for n in new_labels.values()))
refs = set(re.findall(r'\\(?:eqref|ref|pageref|autoref)\{([^}]+)\}', new_text))
check('all TeX reference targets exist', refs <= set(new_labels), sorted(refs - set(new_labels)))


def cite_keys(text):
    groups = re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}', text)
    return {k.strip() for group in groups for k in group.split(',')}


old_cites, new_cites = cite_keys(old_text), cite_keys(new_text)
old_bib = set(re.findall(r'@\w+\s*\{\s*([^,]+)', (BASE / 'references.bib').read_text()))
new_bib_list = re.findall(r'@\w+\s*\{\s*([^,]+)', (NEW / 'references.bib').read_text())
new_bib = set(new_bib_list)
check('all original citation keys retained', old_cites <= new_cites)
check('all original bibliography keys retained', old_bib <= new_bib)
check('no duplicate bibliography keys', len(new_bib_list) == len(new_bib))
check('all citations resolve to bibliography entries', new_cites <= new_bib,
      sorted(new_cites - new_bib))
check('exactly three new primary-source entries',
      new_bib - old_bib == {'mofasbe18', 'moflease2018', 'mofinterpretation16'})

math_pattern = re.compile(
    r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}', re.S)
old_math = Counter(m.group(0) for m in math_pattern.finditer(old_text))
new_math = Counter(m.group(0) for m in math_pattern.finditer(new_text))
check('every pre-existing displayed equation retained exactly', not old_math - new_math,
      {'old': sum(old_math.values()), 'new': sum(new_math.values())})
check('one added balance-sheet display', sum((new_math - old_math).values()) == 1)
old_section = (BASE / 'sections/standards-methods.tex').read_text()
new_section = (NEW / 'sections/standards-methods.tex').read_text()
table_pattern = re.compile(r'\\begin\{longtable\}.*?\\end\{longtable\}', re.S)
check('matched-case table unchanged', table_pattern.findall(old_section) == table_pattern.findall(new_section))
stale = re.findall(r'Official ASBE 18 and Interpretation 16 pages still returned 502|'
                  r'issuance notice with entity-specific staged application remains inaccessible', new_text)
check('confirmed stale access statements removed from candidate', not stale)

manifest = json.loads((OUT / 'candidate-manifest-v1.json').read_text())
for group in ['artifacts', 'renders']:
    wrong = [p for p, expected in manifest[group].items() if sha(ROOT / p) != expected]
    check(group + ' match saved candidate manifest', not wrong, wrong)
log = (NEW / 'accounting-product-proposal.log').read_text()
warnings = [line for line in log.splitlines() if re.search(
    r'Warning:|Overfull|Underfull|Missing character|undefined|multiply defined', line)]
check('final LaTeX log has no warning/error candidates', not warnings, warnings)
doc = fitz.open(NEW / 'accounting-product-proposal.pdf')
check('all PDF pages have extractable text', all(p.get_text().strip() for p in doc), len(doc))

record = {'recorded_at': datetime.now(timezone.utc).isoformat(),
          'passed': all(row['passed'] for row in checks), 'checks': checks,
          'command': ['python3', str(Path(__file__).relative_to(ROOT))],
          'checker_sha256': sha(Path(__file__)), 'wall_seconds': time.monotonic() - start,
          'counts': {'checks': len(checks), 'baseline_files': len(baseline['baseline_file_hashes']),
                     'source_inputs': len(baseline['source_paths']), 'changed_inputs': len(changed),
                     'old_displayed_equations': sum(old_math.values()),
                     'new_displayed_equations': sum(new_math.values()),
                     'original_bibliography_entries': len(old_bib), 'new_bibliography_entries': len(new_bib),
                     'pages': len(doc)},
          'scope': 'Engineering preservation, source delta and rendering diagnostics only. '
                   'No accounting, whole-document readability, human acceptance or readiness certification.'}
(OUT / 'candidate-checks-v1.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'passed': record['passed'], 'counts': record['counts'],
                  'failures': [r for r in checks if not r['passed']]}))
raise SystemExit(0 if record['passed'] else 1)
