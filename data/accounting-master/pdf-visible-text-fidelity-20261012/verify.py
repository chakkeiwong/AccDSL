"""Check source bindings, exact manuscript preservation and final build evidence."""
import json
import re
import time
import fitz
import jsonschema
from prepare import OUT, ROOT, BASE, PDF, EXPECTED, sha, save
from build_candidate import CAND, ANCHOR, BIB

def main():
    start = time.monotonic()
    assert not (OUT/'completion.json').exists(), 'Closed evidence is immutable'
    baseline = json.loads((OUT/'baseline.json').read_text())
    checks=[]
    def ck(name,value):
        checks.append({'name':name,'passed':bool(value)})
    ck('original selected PDF unchanged',sha(PDF)==EXPECTED)
    source=fitz.open(PDF)
    ck('450-page selected annual, physical cover page',len(source)==450)
    raw=(OUT/'pymupdf-page1.txt').read_text()
    ck('reproduced unmodified raw extraction',raw==source[0].get_text('text',sort=False))
    ck('both years survive both fresh extractors',all(y in (OUT/p).read_text() for y in ['2023','2024'] for p in ['pymupdf-page1.txt','poppler-page1.txt']))
    retained=ROOT/baseline['retained_extraction']
    ck('retained extraction unchanged',sha(retained)==baseline['retained_extraction_sha256'])
    ck('bounded retained extraction exact',retained.read_text().split('\f')[0]==(OUT/'retained-poppler-page1.txt').read_text())
    paint=json.loads((OUT/'paint-evidence.json').read_text())
    ck('trace binding',paint['pdf_sha256']==EXPECTED and paint['pdf_page']==1)
    old=next(s for s in paint['trace'] if s['seqno']==8 and 'Accounts 2024' in s['text'])
    later=next(s for s in paint['trace'] if s['seqno']==50)
    rectangle=paint['drawings'][0]
    k=old['text'].index('Accounts 2024')
    glyphs=old['chars'][k:k+len('Accounts 2024')]
    rect=fitz.Rect(rectangle['rect'])
    ck('opaque later fill covers earlier title glyph bounds',rectangle['seqno']==49 and rectangle['type']=='f' and rectangle['fill_opacity']==1 and all(rect.contains(fitz.Rect(c[3])) for c in glyphs))
    ck('2023 text painted after rectangle',later['text']=='Accounts 2023' and later['seqno']>rectangle['seqno']>old['seqno'] and later['opacity']==1)
    annotation=json.loads((OUT/'annotation.json').read_text())
    schema=ROOT/'data/financial-report-benchmark/annotation-record.schema.json'
    errors=list(jsonschema.Draft202012Validator(json.loads(schema.read_text())).iter_errors(annotation))
    ck('existing annotation schema valid',not errors)
    ck('annotation retains raw output and its hash',annotation['literal']==raw and annotation['source']['extracted_text_sha256']==sha(OUT/'pymupdf-page1.txt'))
    ck('source identity bound in annotation',annotation['original_sha256']==EXPECTED)
    ck('author review not independent adjudication',annotation['review_status']=='internally_checked' and all(r['status']!='adjudicated' for r in annotation['readings']))
    ck('hidden year rejected as visible report year',annotation['readings'][2]['value_exact']=='2024' and annotation['readings'][2]['status']=='rejected_with_reason')
    ck('visible year stays proposed',annotation['readings'][1]['value_exact']=='2023' and annotation['readings'][1]['status']=='proposed')
    ck('baseline PDF preserved',sha(BASE/'accounting-product-proposal.pdf')==baseline['baseline_pdf_sha256'])
    files=baseline['source_hashes']
    ck('author source inventory preserved',set(files)=={str(p.relative_to(CAND)) for p in CAND.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}})
    insertion=(OUT/'insertion.tex').read_text()
    for rel,digest in files.items():
        ck('protected baseline '+rel,sha(BASE/rel)==digest)
        oldtext=(BASE/rel).read_text()
        expected=oldtext
        if rel=='accounting-product-proposal.tex':
            expected=expected.replace('Version 2.37 (proposal candidate)','Version 2.38 (proposal candidate)')
        elif rel=='references.bib': expected+=BIB
        elif rel=='sections/adapter-methods.tex': expected=expected.replace(ANCHOR,insertion+'\n'+ANCHOR)
        ck('exact preserved or declared edit '+rel,(CAND/rel).read_text()==expected)
    before='\n'.join((BASE/p).read_text() for p in sorted(files) if p.endswith('.tex'))
    after='\n'.join((CAND/p).read_text() for p in sorted(files) if p.endswith('.tex'))
    pattern=re.compile(r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}',re.S)
    displays=lambda t:[m.group() for m in pattern.finditer(t)]
    ck('48 unchanged displays',displays(before)==displays(after) and len(displays(after))==48)
    labels=re.findall(r'\\label\{([^{}]+)\}',after)
    refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}',after)
    ck('unique labels and resolved references',len(labels)==len(set(labels)) and set(refs)<=set(labels))
    bib=(CAND/'references.bib').read_text()
    keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib)
    citations={k.strip() for g in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}',after) for k in g.split(',')}
    ck('75 previous entries plus one cover source',len(keys)==len(set(keys))==76 and bib==(BASE/'references.bib').read_text()+BIB)
    ck('all citations resolve',citations<=set(keys))
    ck('insertion source hash',sha(OUT/'insertion.tex')==json.loads((OUT/'candidate.json').read_text())['insertion_sha256'])
    pdf=CAND/'accounting-product-proposal.pdf'
    doc=fitz.open(pdf)
    text=' '.join(' '.join(p.get_text().split()) for p in doc)
    ck('new visible-text example in PDF',all(x in text for x in ['A PDF can preserve characters','opaque dark rectangle','unchanged raw extraction','raw-text search still finds 2024','explicit Supersede','unresolved availability condition']))
    log=(CAND/'accounting-product-proposal.log').read_text(errors='replace')
    warnings=[line for line in log.splitlines() if re.search(r'^! |Overfull|Underfull|LaTeX Warning|Package .* Warning',line)]
    ck('clean final TeX log',not warnings)
    blg=(CAND/'accounting-product-proposal.blg').read_text(errors='replace')
    ck('clean bibliography log','Warning--' not in blg and "I didn't find" not in blg)
    for item in baseline['pointer_snapshots']:
        ck('preserved pointer '+item['live'],sha(ROOT/item['snapshot'])==item['sha256'])
    renders=json.loads((OUT/'initial-renders.json').read_text())+json.loads((OUT/'final-renders.json').read_text())
    for item in renders:
        ck('render binding '+item['path'],sha(ROOT/item['pdf'])==item['pdf_sha256'] and sha(ROOT/item['path'])==item['sha256'])
    failed=[x['name'] for x in checks if not x['passed']]
    result={'checks':checks,'passed':len(checks)-len(failed),'failed':failed,'pages':len(doc),
        'candidate_pdf':str(pdf.relative_to(ROOT)),'candidate_pdf_sha256':sha(pdf),'warnings':warnings,
        'wall_seconds':time.monotonic()-start,'scope':'Documentary and preservation checks; not semantic completeness, independent acceptance or adapter runtime validation.'}
    save('checks.json',result)
    print(json.dumps({k:result[k] for k in ['passed','failed','pages','candidate_pdf_sha256','warnings']}))
    raise SystemExit(bool(failed))

if __name__=='__main__': main()
