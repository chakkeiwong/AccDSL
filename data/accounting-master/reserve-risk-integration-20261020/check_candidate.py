"""Read-only comparison of additive manuscript sources and build artifacts."""
from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

import fitz

U=Path(__file__).resolve().parent
R=U.parents[2]
BASE=R/'docs/design/proposal/manuscript-early-conversion-20261018'
NEXT=R/'docs/design/proposal/manuscript-reserve-risk-20261020'


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def expand(base,path='accounting-product-proposal.tex',seen=None):
    if seen is None:seen=[]
    assert path not in seen,path
    seen.append(path)
    return re.sub(r'\\(?:input|include)\{([^}]+)\}',lambda m:expand(base,m[1]+'.tex',seen),(base/path).read_text())


def check():
    protection=load(U/'protection.json')
    for name,h in protection['protected'].items():assert sha(R/name)==h,name
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==protection['head']
    assert sha(R/'.git/index')==protection['index_sha256']
    assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R,text=True).strip()==''
    for name,h in protection['tracked_dirty'].items():
        if name not in protection['controls']:assert sha(R/name)==h,name
    status=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'],cwd=R,text=True)
    rows=[x for x in status.split('\0') if x]
    assert all(x[:2]==' M' for x in rows)
    assert {x[3:] for x in rows}==set(protection['tracked_dirty'])
    lock=load(U/'source-lock.json')
    changed=[]
    for item in lock['files']:
        assert sha(BASE/item['path'])==item['baseline_sha256']
        assert sha(NEXT/item['path'])==item['candidate_sha256']
        if item['changed']:changed.append(item['path'])
    assert changed==['accounting-product-proposal.tex','sections/insurance-methods.tex']
    added=lock['added'];assert sha(NEXT/added['path'])==added['sha256']
    actual={str(p.relative_to(NEXT)) for p in NEXT.rglob('*') if p.suffix in ('.tex','.bib','.lark')}
    assert actual=={r['path'] for r in lock['files']}|{added['path']}
    old=expand(BASE);new=expand(NEXT);addition=(NEXT/added['path']).read_text()
    assert new.count(addition)==1
    restored=new.replace(addition+'\n','',1).replace('Version 3.45 (proposal candidate) \\quad 20 October 2026','Version 3.44 (proposal candidate) \\quad 18 October 2026')
    assert restored==old,'expanded baseline body must be exactly preserved'
    spec=importlib.util.spec_from_file_location('inventory',R/'data/accounting-master/continuous-reading-20261017/reading_inventory.py')
    inv=importlib.util.module_from_spec(spec);spec.loader.exec_module(inv)
    def equations(source):
        source=re.sub(r'(?<!\\)%[^\n]*','',source)
        source=re.sub(r'\\begin\{(lstlisting|verbatim|Verbatim)\}.*?\\end\{\1\}','',source,flags=re.S)
        found=[];pos=0
        while (m:=inv.TOKEN.search(source,pos)) is not None:
            pos=m.end()
            if m['heading']:_,pos=inv.braces(source,pos)
            elif not m['input']:
                ending=r'\]' if m['bracket'] else '$$' if m['dollars'] else r'\end{'+m['math']+'}'
                end=source.find(ending,pos);assert end>=0
                found.append(source[m.start():end+len(ending)].strip());pos=end+len(ending)
        return Counter(found)
    before,after=equations(old),equations(new)
    assert sum(before.values())==208 and not (before-after)
    cp=r'\\cite[a-zA-Z]*\*?(?:\[[^]]*\])?\{[^}]+\}'
    cb,ca=Counter(re.findall(cp,old)),Counter(re.findall(cp,new))
    assert sum(cb.values())==718 and not (cb-ca)
    labels=re.findall(r'\\label\{([^}]+)\}',new)
    refs=re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',new)
    assert len(labels)==len(set(labels)) and not(set(refs)-set(labels))
    warnings=[l for l in (NEXT/'accounting-product-proposal.log').read_text().splitlines() if any(t in l for t in ['Overfull','undefined','multiply defined','Missing character','Fatal error','LaTeX Error'])]
    assert not warnings,warnings
    bib=(NEXT/'accounting-product-proposal.blg').read_text();assert 'Warning--' not in bib and 'I found no' not in bib
    pdf=fitz.open(NEXT/'accounting-product-proposal.pdf')
    baseline_pdf=fitz.open(BASE/'accounting-product-proposal.pdf')
    assert len(baseline_pdf)==396
    bad=[]
    for n,page in enumerate(pdf):
        rect=page.rect
        for block in page.get_text('dict')['blocks']:
            if block['type']!=0:continue
            for line in block['lines']:
                x0,y0,x1,y1=line['bbox']
                if min(x0,y0)<-1 or x1>rect.width+1 or y1>rect.height+1:bad.append(n+1)
    assert not bad,bad
    toc=pdf.get_toc();new_entry=next(x for x in toc if 'A payment distribution still leaves compensation' in x[1]);exit_entry=next(x for x in toc if 'A zero payment and a failed draw' in x[1])
    src=subprocess.run([sys.executable,'-B',str(R/'data/accounting-master/r04-reserve-risk-20261020/verify.py')],capture_output=True,text=True,check=True)
    assert json.loads(src.stdout)['status']=='read-only replay passed'
    return {'status':'additive source and build checks passed','candidate_version':'3.45','pages':len(pdf),
        'pdf_sha256':sha(NEXT/'accounting-product-proposal.pdf'),'baseline_sources':len(lock['files']),
        'changed_existing_sources':changed,'added_source':added['path'],'baseline_displays_preserved':sum(before.values()),
        'candidate_displays':sum(after.values()),'baseline_citations_preserved':sum(cb.values()),
        'added_citations':sum((ca-cb).values()),'bad_build_warnings':warnings,'out_of_page_text':bad,
        'new_unit_start':new_entry[2],'following_unit_start':exit_entry[2],
        'whole_document_regression':'pending','independent_reader':'pending','whole_rows_closed':0}


if __name__=='__main__':
    print(json.dumps(check()))
