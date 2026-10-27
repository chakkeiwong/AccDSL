"""Preserved Version 5.11 integration of complete supplied claim openings."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json
import os
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'docs/design/proposal/manuscript-selected-source-20261026'
TARGET = ROOT / 'docs/design/proposal/manuscript-complete-claims-20261026'
BASE = '75e96cd056682fa198c6015b41d32731fea077f40e3965593b3015c498a30f9a'
BS = chr(92)

def sha(path):
    return sha256(path.read_bytes()).hexdigest()

def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        old = 'Version 5.10 (proposal candidate)'
        assert text.count(old) == 1
        return text.replace(old, 'Version 5.11 (proposal candidate)')
    if name == 'chapters/06-language.tex':
        old = 'the wider financial language or establish accounting applicability.'
        assert text.count(old) == 1
        new = old + '\nSection~' + BS + 'ref{sec:complete-claims-opening} extends the opening contract\n'
        new += 'to live carried claims under an explicit supplied-population declaration\n'
        new += 'and the independently selected full invariant. The source states that\n'
        new += 'premise without inferring completeness from a successful continuation.'
        return text.replace(old, new)
    if name == 'sections/common-program-authoring.tex':
        marker = BS + 'input{sections/selected-company-source}'
        assert text.count(marker) == 1
        return text.replace(marker, marker + '\n\n' + BS + 'input{sections/complete-claims-opening}')
    if name == 'sections/selected-company-source.tex':
        old = 'declared opening and execution path together.'
        assert text.count(old) == 1
        new = old + ' The opening template in\nthis profile still requires an empty claim map. Section~'
        new += BS + 'ref{sec:complete-claims-opening}\nextends that boundary for explicitly complete supplied carried claims.'
        return text.replace(old, new)
    return text

def prepare():
    assert not TARGET.exists() and not (HERE / 'source-preservation.json').exists()
    assert sha(SOURCE / 'accounting-product-proposal.pdf') == BASE
    sources = {p.relative_to(SOURCE).as_posix(): sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert len(sources) == 221
    units = {
        'nonempty-opening-audit-20261026': (5, 76),
        'complete-claims-opening-20261026': (38, 326),
        'complete-claims-source-20261026': (32, 787)}
    evidence = {}
    for unit_name, (controls, assertions) in units.items():
        unit = HERE.parent / unit_name
        checks = json.loads((unit / 'checks.json').read_text())
        assert checks['passed'] and checks.get('controls', checks.get('invalid_state_controls')) == controls and checks['assertions'] == assertions
        for path in unit.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                evidence[str(path.relative_to(ROOT))] = sha(path)
    for name in sources:
        p = TARGET / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(expected(name, (SOURCE / name).read_text()))
    (TARGET / 'sections/complete-claims-opening.tex').write_bytes((HERE / 'source.tex').read_bytes())
    dump('source-preservation.json', dict(sources=sources, source_pdf_sha256=BASE, source=str(SOURCE.relative_to(ROOT)), target=str(TARGET.relative_to(ROOT)), evidence=evidence, added_source='sections/complete-claims-opening.tex', new_section_sha256=sha(HERE / 'source.tex')))
    print(json.dumps({'protected_sources':len(sources), 'candidate':'5.11'}))

def build():
    assert not (HERE / 'build.json').exists()
    start = time.monotonic()
    env = {'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
    command = ['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
    with (HERE / 'build.log').open('w') as log:
        result = subprocess.run(command, cwd=TARGET, env={**os.environ,**env}, stdout=log, stderr=subprocess.STDOUT, timeout=300)
    pdf = TARGET / 'accounting-product-proposal.pdf'
    dump('build.json', dict(command=command, cwd=str(TARGET), environment=env, returncode=result.returncode, wall_seconds=time.monotonic()-start, pdf_sha256=sha(pdf) if pdf.exists() else None))
    print(json.dumps({'returncode': result.returncode}), flush=True)
    raise SystemExit(result.returncode)

def verify():
    import fitz
    preservation = json.loads((HERE / 'source-preservation.json').read_text())
    assert sha(SOURCE / 'accounting-product-proposal.pdf') == BASE
    for name, h in preservation['sources'].items():
        assert sha(SOURCE / name) == h
        assert (TARGET / name).read_text() == expected(name, (SOURCE / name).read_text()), name
    for name, h in preservation['evidence'].items():
        assert sha(ROOT / name) == h, name
    assert sha(TARGET / preservation['added_source']) == preservation['new_section_sha256']
    actual = {p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert actual == set(preservation['sources']) | {preservation['added_source']}
    reachable = set()
    def visit(name):
        assert name not in reachable
        reachable.add(name)
        for child in re.findall(re.escape(BS) + r'(?:input|include)\{([^}]+)}', (TARGET / name).read_text()):
            visit(child if child.endswith('.tex') else child + '.tex')
    visit('accounting-product-proposal.tex')
    text = '\n'.join((TARGET / name).read_text() for name in reachable)
    labels = Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',text))
    refs = set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref)\{([^}]+)}',text))
    assert all(x == 1 for x in labels.values()) and refs <= set(labels)
    def warnings(path):
        return Counter(line for line in path.read_text(errors='replace').splitlines() if any(x in line for x in ['Warning','Overfull','Underfull','undefined','Missing character:','LaTeX Error']) or line.startswith('!'))
    old = warnings(SOURCE / 'accounting-product-proposal.log')
    new = warnings(TARGET / 'accounting-product-proposal.log')
    pdf = TARGET / 'accounting-product-proposal.pdf'
    b = json.loads((HERE / 'build.json').read_text())
    assert b['returncode'] == 0 and sha(pdf) == b['pdf_sha256']
    doc = fitz.open(pdf)
    assert 'Version 5.11' in doc[0].get_text()
    texts = [' '.join(page.get_text().split()) for page in doc]
    start = next(i+1 for i, text in enumerate(texts) if 'A new reporting period need not begin with an empty receivables register.' in text)
    end = next(i+1 for i, text in enumerate(texts) if 'The checked successor therefore admits these complete supplied carried books' in text)
    language = next(i+1 for i, text in enumerate(texts) if 'The current design has several checked, bounded language profiles.' in text)
    pages = sorted({1, language, language+1, *range(start-1,end+2)})
    for page in pages:
        doc[page-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(HERE / f'page-{page}.png')
        (HERE / f'page-{page}.txt').write_text(doc[page-1].get_text())
    bounds = [i+1 for i,page in enumerate(doc) if any(min(block[0],block[1]) < -1 or block[2] > page.rect.width+1 or block[3] > page.rect.height+1 for block in page.get_text('blocks'))]
    result = dict(passed_preservation=True, version='5.11', pages=len(doc), pdf=str(pdf.relative_to(ROOT)), pdf_sha256=sha(pdf), protected_source_files=len(preservation['sources']), changed_sources=[name for name,h in preservation['sources'].items() if sha(TARGET/name)!=h], simulation_sources_preserved=26, new_warnings=dict(new-old), inherited_warnings=dict(old), out_of_page_text_blocks=bounds, review_pages=pages, readiness='not_ready')
    dump('verification.json',result)
    print(json.dumps(result))
    assert not (new-old) and not bounds

if __name__ == '__main__':
    {'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
