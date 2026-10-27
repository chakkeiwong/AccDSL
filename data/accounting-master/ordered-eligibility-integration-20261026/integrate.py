"""Preserved Version 5.7 integration of ordered full-intent eligibility."""
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
SOURCE = ROOT / 'docs/design/proposal/manuscript-method-specialization-20261026'
TARGET = ROOT / 'docs/design/proposal/manuscript-ordered-eligibility-20261026'
BASE = 'b8b487bde8e661cb469b3cf7f71a1b2bc5ffc8f9e8644df713ce9a1eb3f46819'
BS = chr(92)

def sha(path):
    return sha256(path.read_bytes()).hexdigest()

def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

def expected(name, text):
    if name == 'accounting-product-proposal.tex':
        old='Version 5.6 (proposal candidate)'
        assert text.count(old)==1
        return text.replace(old,'Version 5.7 (proposal candidate)')
    if name == 'sections/authored-event-contract.tex':
        marker=BS+'input{sections/common-program-authoring}'
        assert text.count(marker)==1
        return text.replace(marker,BS+'input{sections/ordered-event-eligibility}'+chr(10)*2+marker)
    if name == 'sections/method-specialization.tex':
        first='Both constructors work with the native specializer disabled in their checks.'
        last='boundaries.'
        start=text.index(first);end=text.index(last,start)+len(last)
        revised='Both constructors work with the native specializer disabled in their checks.\nTheir construction interface leaves full-intent eligibility separate; the next\nsection supplies an explicit ordered alternative for the retained contracts.\nFixed chart context, role mapping and unit-cost choices remain declared scope.\nThe earlier complete program composition and invariant source continue to\nprovide their own boundaries.'
        return text[:start]+revised+text[end:]
    return text

def prepare():
    assert not TARGET.exists() and not (HERE / 'source-preservation.json').exists()
    assert sha(SOURCE / 'accounting-product-proposal.pdf') == BASE
    sources = {p.relative_to(SOURCE).as_posix(): sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert len(sources) == 217
    unit = HERE.parent / 'ordered-event-eligibility-20261026'
    checks = json.loads((unit / 'checks.json').read_text())
    assert checks['passed'] and checks['complete_events'] == 38 and checks['all_refusal_cases'] == 34 and checks['controls'] == 70
    evidence = {str((unit / name).relative_to(ROOT)): sha(unit / name) for name in ['result.md','checks.json','run-manifest.json','gate.py','verify.py','design.md','cases.json','controls.json','refusals.json','source-lock.json','repair-note.md']}
    for name in sources:
        p = TARGET / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(expected(name, (SOURCE / name).read_text()))
    (TARGET / 'sections/ordered-event-eligibility.tex').write_bytes((HERE / 'eligibility.tex').read_bytes())
    dump('source-preservation.json', dict(sources=sources, source_pdf_sha256=BASE, source=str(SOURCE.relative_to(ROOT)), target=str(TARGET.relative_to(ROOT)), evidence=evidence, added_source='sections/ordered-event-eligibility.tex', new_section_sha256=sha(HERE / 'eligibility.tex')))
    print(json.dumps({'protected_sources':len(sources), 'candidate':'5.7'}))

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
    assert 'Version 5.7' in doc[0].get_text()
    texts = [' '.join(page.get_text().split()) for page in doc]
    start = next(i+1 for i, text in enumerate(texts) if 'A customer can be unknown before a collection' in text)
    end = next(i+1 for i, text in enumerate(texts) if 'independent implementation acceptance remain open' in text)
    pages = sorted({1, *range(start-1,end+2)})
    for page in pages:
        doc[page-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(HERE / f'page-{page}.png')
        (HERE / f'page-{page}.txt').write_text(doc[page-1].get_text())
    bounds = [i+1 for i,page in enumerate(doc) if any(min(block[0],block[1]) < -1 or block[2] > page.rect.width+1 or block[3] > page.rect.height+1 for block in page.get_text('blocks'))]
    result = dict(passed_preservation=True, version='5.7', pages=len(doc), pdf=str(pdf.relative_to(ROOT)), pdf_sha256=sha(pdf), protected_source_files=len(preservation['sources']), changed_sources=[name for name,h in preservation['sources'].items() if sha(TARGET/name)!=h], simulation_sources_preserved=26, new_warnings=dict(new-old), inherited_warnings=dict(old), out_of_page_text_blocks=bounds, review_pages=pages, readiness='not_ready')
    dump('verification.json',result)
    print(json.dumps(result))
    assert not (new-old) and not bounds

if __name__ == '__main__':
    {'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
