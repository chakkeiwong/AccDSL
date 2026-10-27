"""Add one checked passage; preserve the predecessor and all other sources."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import re
import subprocess
import sys
import time
import fitz

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
SOURCE = ROOT / 'docs/design/proposal/manuscript-collection-clock-20261025'
TARGET = ROOT / 'docs/design/proposal/manuscript-receivable-lifecycle-20261025'
BASE_PDF = 'fe3abf909215f1f28e7651d863fee25c76d4e55dc7b2e9f597716d66880ebc56'
SECTION = 'sections/company-family-language.tex'
ANCHOR = r'\paragraph{A payment can change the decision that follows it.}'


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2) + '\n')
def tokens(text):
    return {
        'labels': Counter(re.findall(r'\\label\{([^}]+)\}', text)),
        'references': Counter(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}', text)),
        'citations': Counter(re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)),
        'bracket_displays': Counter(re.findall(r'\\\[(.*?)\\\]', text, re.S)),
        'environment_displays': Counter(re.findall(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}(.*?)\\end\{\1\}', text, re.S))}


def expected(name, original):
    if name == 'accounting-product-proposal.tex':
        assert original.count('Version 4.16 (proposal candidate)') == 1
        return original.replace('Version 4.16 (proposal candidate)', 'Version 4.17 (proposal candidate)')
    if name == SECTION:
        assert original.count(ANCHOR) == 1
        return original.replace(ANCHOR, (HERE / 'collection-addition.tex').read_text() + '\n' + ANCHOR)
    return original


def verify():
    base = json.loads((HERE / 'integration-baseline.json').read_text())
    assert sha(SOURCE / 'accounting-product-proposal.pdf') == BASE_PDF
    counts = Counter(); changed = []; labels = Counter(); refs = Counter()
    sentinel = r'\label{a} \ref{a} \citep{x} \[x+y\] \begin{equation}z\end{equation}'
    assert all(sum(v.values()) == 1 for v in tokens(sentinel).values())
    for name, old in base['source_hashes'].items():
        assert sha(SOURCE / name) == old, 'predecessor_changed:' + name
        a = (SOURCE / name).read_text(); b = (TARGET / name).read_text()
        assert b == expected(name, a), 'unexpected_delta:' + name
        if a != b: changed.append(name)
        before, after = tokens(a), tokens(b)
        for key in before:
            assert not before[key] - after[key], 'removed_content:' + name + ':' + key
            counts[key] += sum(before[key].values())
        labels.update(after['labels']); refs.update(after['references'])
    assert set(changed) == {'accounting-product-proposal.tex', SECTION}
    assert all(v == 1 for v in labels.values()) and not (set(refs) - set(labels))
    actual = {p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in ['.tex', '.bib', '.lark']}
    assert actual == set(base['source_hashes'])
    for name, old in base['evidence_hashes'].items(): assert sha(ROOT / name) == old, name
    for name, old in json.loads((HERE / 'source-lock.json').read_text()).items(): assert sha(ROOT / name) == old, name
    log = (TARGET / 'accounting-product-proposal.log').read_text(errors='replace')
    warnings = [s for s in log.splitlines() if re.search(r'^!|Undefined control sequence|undefined references|Citation .* undefined|Reference .* undefined|Overfull', s)]
    assert not warnings, warnings[:8]
    build = json.loads((HERE / 'build.json').read_text()); assert build['returncode'] == 0
    pdf = TARGET / 'accounting-product-proposal.pdf'; doc = fitz.open(pdf)
    assert 'Version 4.17' in doc[0].get_text() and sha(pdf) == build['pdf_sha256']
    phrases = ['A credit sale must create the claim that can later be collected.',
               'An invoice created after an earlier assessment therefore remains visibly',
               'The versioned DeclaredReceivableText/1 adapter uses the existing',
               'A payment can change the decision that follows it.']
    locations = {phrase: [i + 1 for i, p in enumerate(doc) if phrase in ' '.join(p.get_text().split())] for phrase in phrases}
    assert all(locations.values()), locations
    return {'passed': True, 'candidate_version': '4.17', 'pages': len(doc), 'pdf_sha256': sha(pdf),
            'protected_sources': len(base['source_hashes']), 'protected_occurrences': dict(counts),
            'changed_files': changed, 'passage_pages': locations, 'pdf': pdf.relative_to(ROOT).as_posix(),
            'scope': 'Exact additive sources and build checks; rendered review separate; no full acceptance'}


def main():
    mode = sys.argv[1]; assert mode in ['prepare', 'build', 'verify']
    if mode == 'prepare':
        assert not TARGET.exists() and not (HERE / 'integration-baseline.json').exists()
        checks = json.loads((HERE / 'checks.json').read_text()); assert checks['passed']
        assert sha(SOURCE / 'accounting-product-proposal.pdf') == BASE_PDF
        sources = {p.relative_to(SOURCE).as_posix(): sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex', '.bib', '.lark']}
        assert len(sources) == 174
        evidence = {p.relative_to(ROOT).as_posix(): sha(p) for p in HERE.iterdir() if p.is_file() and p.name not in ['progress.md']}
        dump(HERE / 'integration-baseline.json', {'source_root': SOURCE.relative_to(ROOT).as_posix(),
             'target_root': TARGET.relative_to(ROOT).as_posix(), 'pdf_sha256': BASE_PDF, 'source_hashes': sources, 'evidence_hashes': evidence})
        for name in sources:
            target = TARGET / name; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(expected(name, (SOURCE / name).read_text()))
        print(json.dumps({'prepared': True, 'sources': len(sources)}))
    elif mode == 'build':
        assert not (HERE / 'build.json').exists()
        command = ['latexmk', '-lualatex', '-silent', '-g', '-interaction=nonstopmode', '-halt-on-error', 'accounting-product-proposal.tex']
        cache = '/tmp/accdsl-receivable-lifecycle-20261025-tex-cache'; Path(cache).mkdir(parents=True, exist_ok=True)
        env = {'TEXMFVAR': cache, 'TEXMFCACHE': cache, 'CUDA_VISIBLE_DEVICES': '-1'}
        start = time.monotonic(); started = datetime.now(timezone.utc).isoformat()
        with (HERE / 'build.log').open('w') as stream:
            run = subprocess.run(command, cwd=TARGET, env={**os.environ, **env}, stdout=stream, stderr=subprocess.STDOUT, timeout=240)
        pdf = TARGET / 'accounting-product-proposal.pdf'
        dump(HERE / 'build.json', {'command': command, 'cwd': str(TARGET), 'environment': env, 'started_utc': started,
             'wall_seconds': time.monotonic() - start, 'returncode': run.returncode, 'pdf_sha256': sha(pdf) if pdf.exists() else None})
        print(json.dumps({'returncode': run.returncode})); raise SystemExit(run.returncode)
    else:
        result = verify(); assert not (HERE / 'integration-verification.json').exists()
        dump(HERE / 'integration-verification.json', result); print(json.dumps(result))
        doc = fitz.open(ROOT / result['pdf']); pages = {1}
        relevant = [p for v in result['passage_pages'].values() for p in v]
        pages.update(range(min(relevant) - 1, max(relevant) + 2))
        for page in sorted(pages): doc[page - 1].get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(HERE / ('page-' + str(page) + '.png'))


if __name__ == '__main__': main()
