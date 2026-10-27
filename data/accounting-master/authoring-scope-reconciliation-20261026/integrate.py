"""Isolated documentation successor; never mutate the protected candidate."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import os
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'docs/design/proposal/manuscript-fiscal-timeline-20261025'
TARGET = ROOT / 'docs/design/proposal/manuscript-authoring-scope-20261026'
BASE_SHA = '2c9e72249cbc28aadcb6ded520165b6ee86bcbff88adc634afc05740ee9ac8f9'
SECTION = 'sections/portable-values.tex'
OLD = '''Typed constructors must express every included declaration in the portable IR
without opaque Python functions. The initially matched text frontend covers the
bounded debt and constraint fragment. Whole-company textual authoring remains
a subsequent frontend obligation; the whole-company typed model is part of the
initial domain. Thus domain scope and authoring syntax are separate decisions.
'''
NEW = r'''Typed constructors must express every included declaration in the portable IR
without opaque Python functions. For this original portable profile, the first
matched text frontend covers the bounded debt and constraint fragment; its
whole-company typed model has a wider domain than that frontend. Later bounded
profiles add text authoring for repeated multi-year operations
(Section~\ref{sec:company-path-authoring}), a mixed return-and-lease book
(Section~\ref{sec:shared-book-authoring}) and method requirements
(Section~\ref{sec:method-requirement-language}). Each retains its own grammar,
typed records and execution limits. Together they provide several checked
authoring routes, while a common language covering all company methods remains
unfinished. Domain scope and authoring syntax are therefore separate decisions.
'''


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        assert text.count('Version 4.39 (proposal candidate)') == 1
        return text.replace('Version 4.39 (proposal candidate)', 'Version 4.40 (proposal candidate)').replace('25 October 2026', '26 October 2026')
    if name == SECTION:
        assert text.count(OLD) == 1
        return text.replace(OLD, NEW)
    return text


def tokens(text):
    return {
        'labels': Counter(re.findall(r'\\label\{([^}]+)\}', text)),
        'references': Counter(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}', text)),
        'citations': Counter(re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)),
        'bracket_displays': Counter(re.findall(r'\\\[(.*?)\\\]', text, re.S)),
        'environment_displays': Counter(re.findall(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}(.*?)\\end\{\1\}', text, re.S)),
    }


def verify():
    import fitz
    baseline = json.loads((HERE / 'baseline.json').read_text())
    assert sha(SOURCE / 'accounting-product-proposal.pdf') == BASE_SHA
    assert sha(Path(__file__)) == baseline['writer_sha256']
    counts = Counter()
    labels, refs = Counter(), Counter()
    changed = []
    for name, digest in baseline['sources'].items():
        assert sha(SOURCE / name) == digest, 'baseline changed: ' + name
        before, after = (SOURCE / name).read_text(), (TARGET / name).read_text()
        assert after == expected(name, before), 'unexpected delta: ' + name
        if before != after:
            changed.append(name)
        old, new = tokens(before), tokens(after)
        for key in old:
            assert not old[key] - new[key], (name, key)
            counts[key] += sum(old[key].values())
        labels.update(new['labels'])
        refs.update(new['references'])
    assert set(changed) == {'accounting-product-proposal.tex', SECTION}
    assert all(v == 1 for v in labels.values())
    assert not (set(refs) - set(labels))
    actual = {p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}}
    assert actual == set(baseline['sources'])
    build = json.loads((HERE / 'build.json').read_text())
    assert build['returncode'] == 0
    pdf = TARGET / 'accounting-product-proposal.pdf'
    assert sha(pdf) == build['pdf_sha256']
    doc = fitz.open(pdf)
    assert 'Version 4.40' in doc[0].get_text()
    logs = [(SOURCE / 'accounting-product-proposal.log').read_text(errors='replace'),
            (TARGET / 'accounting-product-proposal.log').read_text(errors='replace')]
    def warnings(text):
        return Counter(line for line in text.splitlines()
                       if any(s in line for s in ['Warning', 'Overfull', 'Underfull', 'Undefined', 'undefined', 'Missing character:', 'LaTeX Error']) or line.startswith('!'))
    old, new = map(warnings, logs)
    assert not new - old, dict(new - old)
    phrase = 'For this original portable profile'
    locations = [i + 1 for i, page in enumerate(doc) if phrase in ' '.join(page.get_text().split())]
    assert len(locations) == 1, locations
    pages = sorted({1, locations[0] - 1, locations[0], locations[0] + 1})
    return {'passed': True, 'version': '4.40', 'pages': len(doc), 'pdf': str(pdf.relative_to(ROOT)),
            'pdf_sha256': sha(pdf), 'protected_source_files': len(baseline['sources']),
            'protected_occurrences': dict(counts), 'changed_files': changed,
            'warnings': dict(new), 'new_warnings': [], 'review_pages': pages,
            'acceptance': 'not_ready', 'scope': 'Authoring-boundary clarification only'}


def main():
    mode = sys.argv[1]
    if mode == 'prepare':
        assert not TARGET.exists() and not (HERE / 'baseline.json').exists()
        assert sha(SOURCE / 'accounting-product-proposal.pdf') == BASE_SHA
        sources = {p.relative_to(SOURCE).as_posix(): sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}}
        assert len(sources) == 174
        for name in sources:
            target = TARGET / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(expected(name, (SOURCE / name).read_text()))
        dump(HERE / 'baseline.json', {'sources': sources, 'pdf_sha256': BASE_SHA, 'writer_sha256': sha(Path(__file__))})
        print(json.dumps({'prepared': True, 'sources': len(sources)}))
    elif mode == 'build':
        assert not (HERE / 'build.json').exists()
        cache = '/tmp/accdsl-authoring-scope-20261026-tex-cache'
        Path(cache).mkdir(parents=True, exist_ok=True)
        env = {'TEXMFVAR': cache, 'TEXMFCACHE': cache, 'CUDA_VISIBLE_DEVICES': '-1'}
        command = ['latexmk', '-lualatex', '-silent', '-g', '-interaction=nonstopmode', '-halt-on-error', 'accounting-product-proposal.tex']
        start = time.monotonic()
        with (HERE / 'build.log').open('w') as stream:
            result = subprocess.run(command, cwd=TARGET, env={**os.environ, **env}, stdout=stream, stderr=subprocess.STDOUT, timeout=240)
        pdf = TARGET / 'accounting-product-proposal.pdf'
        dump(HERE / 'build.json', {'command': command, 'cwd': str(TARGET), 'environment': env, 'wall_seconds': time.monotonic() - start,
                                  'returncode': result.returncode, 'pdf_sha256': sha(pdf) if pdf.exists() else None})
        print(json.dumps({'returncode': result.returncode}))
        raise SystemExit(result.returncode)
    elif mode == 'verify':
        import fitz
        result = verify()
        dump(HERE / 'verification.json', result)
        doc = fitz.open(ROOT / result['pdf'])
        for page in result['review_pages']:
            doc[page - 1].get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(HERE / ('page-' + str(page) + '.png'))
        print(json.dumps(result))
    else:
        raise SystemExit('Unknown mode')


if __name__ == '__main__':
    main()
