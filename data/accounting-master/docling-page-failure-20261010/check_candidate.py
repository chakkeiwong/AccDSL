"""Document preservation and source-binding checks; no product execution."""
from datetime import datetime, timezone
from pathlib import Path
import difflib
import hashlib
import json
import os
import re
import subprocess
import time
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-service-access-20261010'
NEW = ROOT / 'docs/design/proposal/manuscript-page-failure-20261010'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def main():
    started, timer = datetime.now(timezone.utc).isoformat(), time.monotonic()
    checks, inputs = [], {}
    def ck(n, ok): checks.append(dict(id=n, passed=bool(ok)))
    def verify(mapping, name):
        bad = [p for p, h in mapping.items() if not (ROOT / p).is_file() or sha(ROOT / p) != h]
        ck(name, not bad)
        if not bad: inputs.update(mapping)

    base = read(OUT / 'baseline.json'); prior_path = ROOT / base['prior_manifest']
    ck('preceding manifest unchanged', sha(prior_path) == base['prior_manifest_sha256'])
    reloc = {r['historical_path']: r['preserved_path'] for r in base['pointer_relocations']}
    prior = read(prior_path)
    verify({reloc.get(p, p): h for p, h in prior['artifact_hashes'].items()}, '1062 preceding artifact references preserved')
    ck('preceding reference population', len(prior['artifact_hashes']) == 1062)
    protection = read(OUT / 'integration-baseline.json')
    verify(protection['protected_hashes'], 'all 56 baseline manuscript files preserved')
    verify(protection['baseline_images'], 'baseline render pixels preserved')
    ck('diagnosis precedes candidate and stays unchanged', sha(OUT / 'ordered-reading.md') == protection['diagnosis_sha256'])
    probe = read(OUT / 'checks.json'); verify(probe['inputs'], 'probe source and result bindings current')
    ck('35 exact-method checks passing', probe['passed'] == 35 and probe['failed'] == 0
       and probe['checker_sha256'] == sha(OUT / 'probe.py'))
    anchors = read(OUT / 'source-anchors.json'); anchor_ok = True
    for a in anchors['anchors']:
        p = ROOT / a['path']; quote = '\n'.join(p.read_text().splitlines()[a['first_line']-1:a['last_line']]) + '\n'
        anchor_ok &= sha(p) == a['sha256'] and hashlib.sha256(quote.encode()).hexdigest() == a['quote_sha256']
    ck('all exact method and caller anchors resolve', anchor_ok)
    old = {p.relative_to(OLD): p for p in OLD.rglob('*') if p.suffix in {'.tex', '.bib', '.lark'}}
    new = {p.relative_to(NEW): p for p in NEW.rglob('*') if p.suffix in {'.tex', '.bib', '.lark'}}
    ck('all 48 inherited source files retained', old.keys() == new.keys() and len(old) == 48)
    changed, delta = [], []
    for n, p in sorted(new.items()):
        a, b = old[n].read_text(), p.read_text(); inputs[rel(p)] = sha(p)
        if a != b:
            changed.append(str(n)); delta += list(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=rel(old[n]), tofile=rel(p)))
    ck('only three declared files changed', set(changed) == {'accounting-product-proposal.tex', 'sections/adapter-methods.tex', 'references.bib'})
    ck('version-only title increment', (NEW / 'accounting-product-proposal.tex').read_text().replace(
        'Version 2.25','Version 2.24') == (OLD / 'accounting-product-proposal.tex').read_text())
    section = (NEW / 'sections/adapter-methods.tex').read_text()
    start = section.index('A returned layout conversion can also conceal missing pages.')
    end = section.index('The retained Apple annual filing', start)
    ck('all prior adapter prose retained exactly', section[:start] + section[end:] == (OLD / 'sections/adapter-methods.tex').read_text())
    all_old = '\n'.join(p.read_text() for _,p in sorted(old.items()) if p.suffix=='.tex')
    all_new = '\n'.join(p.read_text() for _,p in sorted(new.items()) if p.suffix=='.tex')
    displays = lambda s: re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}', s, re.S)
    ck('all 48 displays byte-identical', len(displays(all_old))==48 and displays(all_old)==displays(all_new))
    bib = (NEW / 'references.bib').read_text(); new_entry = re.search(r'@misc\{doclingpinned2026,.*?\n\}\n\n',bib,re.S)
    keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib)
    ck('all 66 old bibliography entries unchanged, one added', new_entry is not None
       and bib[:new_entry.start()]+bib[new_entry.end():] == (OLD / 'references.bib').read_text() and len(keys)==67)
    cites = lambda s:{k.strip() for q in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in q.split(',')}
    ck('citations retained and resolved', cites(all_old)<=cites(all_new)<=set(keys))
    labels = re.findall(r'\\label\{([^}]+)\}',all_new); refs = re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',all_new)
    ck('unique labels and resolved references', len(labels)==len(set(labels)) and set(refs)<=set(labels))
    ck('clean final LuaLaTeX log', not any(t in (NEW/'accounting-product-proposal.log').read_text() for t in ['Warning','Overfull','Underfull','! ']))
    ck('clean bibliography log', not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
    render = read(OUT/'render-manifest.json');pdf=ROOT/render['pdf']['path']
    ck('PDF hash binds 168-page candidate', sha(pdf)==render['pdf']['sha256'] and len(fitz.open(pdf))==render['pdf']['pages']==168)
    verify({r['path']:r['sha256'] for r in render['images']},'all 13 final render images current')
    ck('author review binds final candidate with independent pending', render['pdf']['sha256'] in (OUT/'author-review.md').read_text()
       and 'independent_reader_pending' in (OUT/'author-review.md').read_text())
    cmd=['git','diff','--check','--',rel(OUT),rel(NEW),'docs/plans/accounting-docling-page-failure-20261010.md']
    ck('scoped diff check', subprocess.run(cmd,cwd=ROOT,capture_output=True).returncode==0)
    (OUT/'manuscript-delta.diff').write_text(''.join(delta))
    report=dict(checker_sha256=sha(Path(__file__)),checks=checks,inputs=inputs,
        passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),
        pdf=render['pdf'],changed_sources=changed,started_at=started,wall_seconds=time.monotonic()-timer,
        command='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 '+rel(Path(__file__)))
    (OUT/'candidate-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['passed','failed','wall_seconds']}))
    assert not report['failed'], [c['id'] for c in checks if not c['passed']]


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'completion.json').exists()
    main()
