"""Verify preservation and rendering diagnostics; never infer reader acceptance."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import re
import difflib
import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT/'docs/design/proposal/manuscript-origin-matched-cessation-20261017'
NEXT = ROOT/'docs/design/proposal/manuscript-readability-20261017'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def expand(base,path='accounting-product-proposal.tex',seen=None):
    seen=[] if seen is None else seen
    seen.append(path)
    text=(base/path).read_text()
    return re.sub(r'\\(?:input|include)\{([^}]+)\}',
        lambda m:expand(base,m[1]+'.tex',seen),text)

def main():
    lock=json.loads((OUT/'source-lock.json').read_text())
    checks=[]
    def check(name,result):
        checks.append(dict(name=name,passed=bool(result)))
    delta=[]
    for row in lock['files']:
        rel=row['path']
        check('baseline/'+rel,sha(BASE/rel)==row['baseline_sha256'])
        if not row['changed']:
            check('unchanged/'+rel,(BASE/rel).read_bytes()==(NEXT/rel).read_bytes())
        a,b=(BASE/rel).read_text(),(NEXT/rel).read_text()
        if a!=b:
            delta.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='3.41/'+rel,tofile='3.42/'+rel))
    for row in lock['new_files']:
        rel=row['path']
        delta.extend(difflib.unified_diff([], (NEXT/rel).read_text().splitlines(True),fromfile='/dev/null',tofile='3.42/'+rel))
    (OUT/'final-body-delta.patch').write_text(''.join(delta))
    check('real-body-delta',len(delta)>0)
    grammar='spec/core-0.lark'
    check('grammar-dependency',(BASE/grammar).read_bytes()==(NEXT/grammar).read_bytes())
    seen=[]
    before=expand(BASE)
    after=expand(NEXT,seen=seen)
    check('no-duplicate-inputs',len(seen)==len(set(seen)))
    spec=importlib.util.spec_from_file_location('inventory',ROOT/'data/accounting-master/continuous-reading-20261017/reading_inventory.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    def equations(text):
        text=re.sub(r'(?<!\\)%[^\n]*','',text)
        text=re.sub(r'\\begin\{(lstlisting|verbatim|Verbatim)\}.*?\\end\{\1\}','',text,flags=re.S)
        answer=[];pos=0
        while match:=module.TOKEN.search(text,pos):
            pos=match.end()
            if match['heading']:
                _,pos=module.braces(text,pos)
            elif not match['input']:
                ending=r'\]' if match['bracket'] else '$$' if match['dollars'] else r'\end{'+match['math']+'}'
                end=text.find(ending,pos);assert end>=0
                answer.append(text[match.start():end+len(ending)].strip())
                pos=end+len(ending)
        return Counter(answer)
    ea,eb=equations(before),equations(after)
    check('all208-displays-preserved',ea==eb and sum(ea.values())==208)
    citations=r'\\cite[a-zA-Z]*\*?(?:\[[^]]*\])?\{[^}]+\}'
    ca,cb=Counter(re.findall(citations,before)),Counter(re.findall(citations,after))
    check('citation-occurrences-preserved',ca==cb)
    labels=re.findall(r'\\label\{([^}]+)\}',after)
    oldlabels=re.findall(r'\\label\{([^}]+)\}',before)
    refs=re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',after)
    check('all-original-labels-preserved',not set(oldlabels)-set(labels))
    check('no-duplicate-labels',len(labels)==len(set(labels)))
    check('no-missing-reference-targets',not set(refs)-set(labels))
    def paragraphs(text):
        text=re.sub(r'\\(?:subsubsection|subsection|section)\{',r'\\heading{',text)
        return Counter(' '.join(p.split()) for p in text.split('\n\n') if p.strip())
    pa,pb=paragraphs(before),paragraphs(after)
    removed=list((pa-pb).elements())
    added=list((pb-pa).elements())
    (OUT/'paragraph-delta.json').write_text(json.dumps(dict(removed=removed,added=added),indent=2,ensure_ascii=False)+'\n')
    markers=['Inventory and assets retain','Replacing a component removes',
             'Revaluation needs each','Employee benefits','Impairment and provisions',
             'An idle factory','Inspections, surrendered','Opening work carries',
             'Impairment across a group']
    positions=[after.index(m) for m in markers]
    check('prerequisite-order',positions==sorted(positions))
    warnings=[line for line in (NEXT/'accounting-product-proposal.log').read_text().splitlines()
              if any(term in line for term in ['Overfull','undefined','multiply defined','Missing character','Fatal error','LaTeX Error'])]
    check('no-material-build-warning',not warnings)
    pdf=NEXT/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
    bounds=[]
    for number,page in enumerate(doc,1):
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                        bounds.append(dict(page=number,text=span['text']))
    check('all-page-text-bounds',not bounds)
    result=dict(version='3.42',pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),pages=len(doc),
        checks=checks,failures=sum(not c['passed'] for c in checks),
        displayed_equations=sum(eb.values()),citation_occurrences=sum(cb.values()),
        paragraph_delta_to_review=len(removed),material_build_warnings=warnings,text_bounds=bounds,
        source_hashes=[dict(path=str(p.relative_to(NEXT)),sha256=sha(p)) for p in sorted(NEXT.rglob('*')) if p.suffix in ('.tex','.bib','.bnf','.ebnf','.lark')],
        bookmarks=doc.get_toc(),rendered_regression='pending',independent_reader='pending',human_acceptance='pending')
    (OUT/'candidate-checks.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:result[k] for k in ['version','pdf_sha256','pages','failures','displayed_equations','citation_occurrences','paragraph_delta_to_review','material_build_warnings']},ensure_ascii=False))
    print('Removed/changed paragraphs requiring disposition:')
    for i,p in enumerate(removed):print(i,p[:600])
    assert result['failures']==0

if __name__=='__main__':
    main()
