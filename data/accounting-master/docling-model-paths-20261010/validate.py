"""Check documentary identity, declared scope and manuscript preservation."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import os
import re
import time
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-page-failure-20261010'
NEW = ROOT / 'docs/design/proposal/manuscript-model-paths-20261010'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def main():
    tick = time.monotonic(); checks = []; inputs = {}
    def ck(name, ok): checks.append(dict(id=name, passed=bool(ok)))
    def verify(mapping, label):
        ck(label, all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in mapping.items()))
        inputs.update(mapping)
    base = read(OUT/'baseline.json'); prior = ROOT/base['prior_manifest']; manifest = read(prior)
    ck('prior manifest identity', sha(prior)==base['prior_manifest_sha256']==read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc = {x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    verify({reloc.get(p,p):h for p,h in manifest['artifact_hashes'].items()}, '1279 inherited references')
    tree = read(OUT/'sources/tree.json'); ck('complete tree at intended pin', tree['sha']=='eda5b5fc86d10b2b79a900ff3e69fc159d5f6014' and not tree['truncated'])
    blobs = {x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'}
    acquisitions = read(OUT/'acquisitions.json'); success = [x for x in acquisitions if x['exit_code']==0]
    ck('bounded distinct acquisitions and one preserved timeout', len(acquisitions)==25 and len(success)==24 and len({x['url'] for x in acquisitions})==25 and [x['exit_code'] for x in acquisitions if x['exit_code']]!=[] and all(x['exit_code']==28 and x['bytes']==0 for x in acquisitions if x['exit_code']))
    sources = [(x['upstream_path'],ROOT/x['path']) for x in success]
    sources.append(('docling/models/inference_engines/common/__init__.py',OUT/'sources/docling__models__inference_engines__common____init__.py'))
    for name,p in sources:
        raw=p.read_bytes(); ck('source Git blob '+name, hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[name]);inputs[rel(p)]=sha(p)
    for x in read(OUT/'retained-sources.json'):
        p=ROOT/x['path'];ck('retained '+x['upstream_path'],sha(p)==x['sha256']);inputs[rel(p)]=sha(p)
    anchors=read(OUT/'source-anchors.json');ck('25 distinct source anchors',len(anchors)==len({a['id'] for a in anchors})==25)
    for a in anchors:
        p=ROOT/a['path'];excerpt=''.join(p.read_text().splitlines(keepends=True)[a['start_line']-1:a['end_line']]);ck('anchor '+a['id'],sha(p)==a['sha256'] and hashlib.sha256(excerpt.encode()).hexdigest()==a['excerpt_sha256']);inputs[rel(p)]=sha(p)
    fields=read(OUT/'default-expressions.json');ck('91 unevaluated fields',len(fields)==91 and all(x['status']=='upstream expression; not evaluated or adopted' for x in fields))
    for p,h in {x['path']:x['sha256'] for x in fields}.items():ck('default source '+p,sha(ROOT/p)==h);inputs[p]=h
    configs=read(OUT/'configuration-records.json');ck('two explicitly non-executable hypotheses',len(configs['arms'])==2 and 'non-executable' in configs['status'] and configs['common']['layout_options']['revision'] is None)
    ck('explicit OCR distinction',configs['arms'][0]['do_ocr'] is False and configs['arms'][1]['ocr_options']['download_enabled'] is False and configs['arms'][1]['ocr_options']['lang']==['en'])
    deps=read(OUT/'dependency-proposals.json');ck('declarations not locks',deps['project']=='docling-slim' and deps['base_count']==9 and all(x['exact_lock'] is None for x in deps['proposals'].values()) and [len(x['declared_requirements']) for x in deps['proposals'].values()]==[20,22])
    protection=read(OUT/'integration-baseline.json');verify(protection['protected_hashes'],'frozen manuscript tree unchanged');verify(protection['baseline_images'],'baseline render preserved')
    ck('diagnosis preserved',sha(OUT/'ordered-reading.md')==protection['diagnosis_sha256'])
    old={p.relative_to(OLD):p for p in OLD.rglob('*') if p.suffix in {'.tex','.bib','.lark'}}
    new={p.relative_to(NEW):p for p in NEW.rglob('*') if p.suffix in {'.tex','.bib','.lark'}}
    ck('48 source names preserved',len(old)==48 and old.keys()==new.keys());changed=[];delta=[]
    for n,p in sorted(new.items()):
        a,b=old[n].read_text(),p.read_text();inputs[rel(p)]=sha(p)
        if a!=b:changed.append(str(n));delta.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=rel(old[n]),tofile=rel(p)))
    ck('two intended source edits',set(changed)=={'accounting-product-proposal.tex','sections/adapter-methods.tex'})
    ck('version increment only on title', (NEW/'accounting-product-proposal.tex').read_text().replace('Version 2.26','Version 2.25')==(OLD/'accounting-product-proposal.tex').read_text())
    section=(NEW/'sections/adapter-methods.tex').read_text();start=section.index('A requested processing stage may also remain unperformed.');end=section.index('The retained Apple annual filing',start)
    ck('prior section preserved verbatim',section[:start]+section[end:]==(OLD/'sections/adapter-methods.tex').read_text())
    oldtext='\n'.join(p.read_text() for n,p in sorted(old.items()) if p.suffix=='.tex');newtext='\n'.join(p.read_text() for n,p in sorted(new.items()) if p.suffix=='.tex')
    displays=lambda s:re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}',s,re.S)
    ck('48 displays unchanged',len(displays(oldtext))==48 and displays(oldtext)==displays(newtext))
    bib=(NEW/'references.bib').read_text();keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib);ck('67 bibliography entries unchanged',len(keys)==67 and bib==(OLD/'references.bib').read_text())
    cites=lambda s:{k.strip() for group in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in group.split(',')}
    ck('citations preserved/resolved',cites(oldtext)<=cites(newtext)<=set(keys))
    labels=re.findall(r'\\label\{([^}]+)\}',newtext);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',newtext);ck('labels and references',len(labels)==len(set(labels)) and set(refs)<=set(labels))
    ck('clean final TeX log',not any(t in (NEW/'accounting-product-proposal.log').read_text() for t in ['Warning','Overfull','Underfull','! ']))
    ck('clean bibliography log',not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
    render=read(OUT/'render-manifest.json');pdf=ROOT/render['pdf']['path'];ck('168-page candidate identity',sha(pdf)==render['pdf']['sha256'] and len(fitz.open(pdf))==render['pdf']['pages']==168)
    verify({x['path']:x['sha256'] for x in render['images']},'13 rendered pages current')
    ck('author review bound and independent pending',render['pdf']['sha256'] in (OUT/'author-review.md').read_text() and 'independent_reader_pending' in (OUT/'author-review.md').read_text())
    (OUT/'manuscript-delta.diff').write_text(''.join(delta))
    inputs.update({rel(p):sha(p) for p in OUT.glob('*.json') if p.name not in {'checks.json','run-manifest.json','completion.json'}})
    report=dict(passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,pdf=render['pdf'],changed_sources=changed)
    (OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['passed','failed','wall_seconds']}));assert not report['failed'],[x['id'] for x in checks if not x['passed']]


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    main()
