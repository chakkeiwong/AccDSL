"""Build an additive Version 4.20 manuscript successor."""
from collections import Counter
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
SOURCE = ROOT / 'docs/design/proposal/manuscript-conditional-continuation-20261025'
TARGET = ROOT / 'docs/design/proposal/manuscript-sector-reference-binding-20261025'
BASE_PDF_SHA256 = '8173fa80a7c21d754bd0a5e909cac2e3bb107c81c151cff2b4c0b2de4612b7ac'
SECTION = 'sections/company-family-language.tex'
ANCHOR = r'\input{sections/company-module-language}'

def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
def tokens(text):
    return {'labels': Counter(re.findall(r'\\label\{([^}]+)\}', text)),
            'references': Counter(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}', text)),
            'citations': Counter(re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text)),
            'bracket_displays': Counter(re.findall(r'\\\[(.*?)\\\]', text, re.S)),
            'environment_displays': Counter(re.findall(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}(.*?)\\end\{\1\}', text, re.S))}

def expected(name, original):
    if name == 'accounting-product-proposal.tex':
        assert original.count('Version 4.19 (proposal candidate)') == 1
        return original.replace('Version 4.19 (proposal candidate)', 'Version 4.20 (proposal candidate)')
    if name == SECTION:
        assert original.count(ANCHOR) == 1
        addition = (HERE / 'collection-addition.tex').read_text()
        return original.replace(ANCHOR, addition + '\n\n' + ANCHOR)
    return original

def verify():
    baseline = json.loads((HERE / 'integration-baseline.json').read_text())
    assert sha(SOURCE / 'accounting-product-proposal.pdf') == BASE_PDF_SHA256
    counts = Counter(); changed = []; labels = Counter(); refs = Counter()
    for name, old_sha in baseline['source_hashes'].items():
        source = SOURCE / name; target = TARGET / name
        assert sha(source) == old_sha, 'predecessor_changed:' + name
        before, after = source.read_text(), target.read_text()
        assert after == expected(name, before), 'unexpected_delta:' + name
        if before != after: changed.append(name)
        b, a = tokens(before), tokens(after)
        for key in b:
            assert not b[key] - a[key], 'removed_content:' + name + ':' + key
            counts[key] += sum(b[key].values())
        labels.update(a['labels']); refs.update(a['references'])
    assert set(changed) == {'accounting-product-proposal.tex', SECTION}
    assert all(v == 1 for v in labels.values()) and not (set(refs) - set(labels))
    actual = {p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    assert actual == set(baseline['source_hashes'])
    for name, expected_sha in json.loads((HERE / 'source-lock.json').read_text()).items():
        assert sha(ROOT / name) == expected_sha, 'evidence_changed:' + name
    build = json.loads((HERE / 'build.json').read_text()); assert build['returncode'] == 0
    pdf = TARGET / 'accounting-product-proposal.pdf'; doc = fitz.open(pdf)
    assert 'Version 4.20' in doc[0].get_text() and sha(pdf) == build['pdf_sha256']
    phrases = ['Resolve a sector assessment without turning it into a common ledger.',
               'The retained bank case illustrates why the context travels with the state.',
               'The common boundary contributes a safe route']
    locations = {phrase: [i + 1 for i, page in enumerate(doc) if phrase in ' '.join(page.get_text().split())] for phrase in phrases}
    assert all(locations.values()), locations
    return {'passed': True, 'candidate_version': '4.20', 'pages': len(doc), 'pdf_sha256': sha(pdf),
            'protected_sources': len(baseline['source_hashes']), 'protected_occurrences': dict(counts),
            'changed_files': changed, 'passage_pages': locations,
            'pdf': pdf.relative_to(ROOT).as_posix(), 'scope': 'Additive sector-reference passage; no whole acceptance'}

def main():
    mode = sys.argv[1]; assert mode in ['prepare','build','verify']
    if mode == 'prepare':
        assert not TARGET.exists() and not (HERE / 'integration-baseline.json').exists()
        source_hashes = {p.relative_to(SOURCE).as_posix(): sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
        assert len(source_hashes) == 174 and sha(SOURCE / 'accounting-product-proposal.pdf') == BASE_PDF_SHA256
        evidence_hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in HERE.iterdir() if p.is_file() and p.name not in ['progress.md']}
        dump(HERE / 'integration-baseline.json', {'source_root': SOURCE.relative_to(ROOT).as_posix(), 'target_root': TARGET.relative_to(ROOT).as_posix(), 'pdf_sha256': BASE_PDF_SHA256, 'source_hashes': source_hashes, 'evidence_hashes': evidence_hashes})
        for name in source_hashes:
            target = TARGET / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(expected(name, (SOURCE / name).read_text()))
        print(json.dumps({'prepared': True, 'sources': len(source_hashes)})); return
    if mode == 'build':
        assert not (HERE / 'build.json').exists()
        command = ['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
        cache = '/tmp/accdsl-sector-reference-binding-20261025-tex-cache'; Path(cache).mkdir(parents=True, exist_ok=True)
        env = {'TEXMFVAR': cache, 'TEXMFCACHE': cache, 'CUDA_VISIBLE_DEVICES': '-1'}; start = time.monotonic()
        with (HERE / 'build.log').open('w') as stream: run = subprocess.run(command, cwd=TARGET, env={**os.environ, **env}, stdout=stream, stderr=subprocess.STDOUT, timeout=240)
        pdf = TARGET / 'accounting-product-proposal.pdf'; dump(HERE / 'build.json', {'command': command, 'cwd': str(TARGET), 'environment': env, 'wall_seconds': time.monotonic()-start, 'returncode': run.returncode, 'pdf_sha256': sha(pdf) if pdf.exists() else None}); print(json.dumps({'returncode':run.returncode})); raise SystemExit(run.returncode)
    result = verify(); dump(HERE / 'integration-verification.json', result); print(json.dumps(result))
    doc = fitz.open(ROOT / result['pdf']); pages = {1}; relevant = [p for v in result['passage_pages'].values() for p in v]; pages.update(range(min(relevant)-1, max(relevant)+2))
    for page in sorted(pages): doc[page-1].get_pixmap(matrix=fitz.Matrix(1.35,1.35)).save(HERE / ('page-'+str(page)+'.png'))

if __name__ == '__main__': main()
