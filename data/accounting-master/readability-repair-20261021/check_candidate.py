"""Read-only preservation and build checks for the prose repair."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'docs/design/proposal/manuscript-reserve-risk-20261020'
C = R / 'docs/design/proposal/manuscript-readability-20261021'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())

def check(source_only=False):
    protection = load(U / 'protection.json')
    for name,digest in protection['protected'].items():
        assert sha(R / name) == digest,name
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip() == protection['head']
    assert sha(R / '.git/index') == protection['index_sha256']
    current = subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'],cwd=R,text=True)
    rows = [x for x in current.split(chr(0)) if x]
    assert all(x[:2]==' M' for x in rows)
    assert {x[3:] for x in rows} == set(protection['tracked_dirty'])
    for name,digest in protection['tracked_dirty'].items():
        if name not in protection['controls']:
            assert sha(R/name) == digest,name
    lock = load(U/'source-lock.json')
    changed = []
    for row in lock['files']:
        name=row['path']
        assert sha(B/name)==row['baseline_sha256'] and sha(C/name)==row['candidate_sha256'],name
        restored=(C/name).read_text()
        for change in reversed(lock['replacements']):
            if change['path']==name:
                assert restored.count(change['new'])==1,change['id']
                restored=restored.replace(change['new'],change['old'],1)
        assert restored==(B/name).read_text(),name
        if row['changed']: changed.append(name)
    assert changed==['accounting-product-proposal.tex','chapters/12-research.tex','sections/corporate-methods.tex','sections/corporate-residuals.tex']
    assert {str(p.relative_to(C)) for p in C.rglob('*') if p.suffix in ('.tex','.bib','.lark')}=={r['path'] for r in lock['files']}
    spec=importlib.util.spec_from_file_location('prior_check',R/'data/accounting-master/reserve-risk-integration-20261020/check_candidate.py')
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    old,new=prior.expand(B),prior.expand(C)
    bs=chr(92)
    token_spec=importlib.util.spec_from_file_location('inventory',R/'data/accounting-master/continuous-reading-20261017/reading_inventory.py')
    inv=importlib.util.module_from_spec(token_spec);token_spec.loader.exec_module(inv)
    def displays(text):
        found=[];pos=0
        while (m:=inv.TOKEN.search(text,pos)) is not None:
            pos=m.end()
            if m['heading']: _,pos=inv.braces(text,pos)
            elif not m['input']:
                ending=bs+']' if m['bracket'] else '$$' if m['dollars'] else bs+'end{'+m['math']+'}'
                end=text.find(ending,pos);assert end>=0
                found.append(text[m.start():end+len(ending)].strip());pos=end+len(ending)
        return Counter(found)
    before,after=displays(old),displays(new)
    assert before==after
    citation_pattern = re.escape(bs) + 'cite[a-zA-Z]*[*]?(?:' + re.escape('[') + '[^]]*' + re.escape(']') + ')?' + re.escape('{') + '[^}]+' + re.escape('}')
    cb,ca=Counter(re.findall(citation_pattern,old)),Counter(re.findall(citation_pattern,new))
    assert cb==ca and sum(cb.values())==727
    labels=re.findall(re.escape(bs)+'label'+re.escape('{')+'([^}]+)'+re.escape('}'),new)
    refs=re.findall(re.escape(bs)+'(?:ref|eqref|pageref)'+re.escape('{')+'([^}]+)'+re.escape('}'),new)
    assert len(labels)==len(set(labels)) and not(set(refs)-set(labels))
    result={'status':'source preservation passed','version':'3.46','sources':len(lock['files']),
        'changed_sources':changed,'displays_preserved':sum(before.values()),'citations_preserved':sum(cb.values()),
        'protected_files':len(protection['protected']),'tracked_dirty_preserved':len(rows),'whole_rows_closed':0}
    if source_only:return result
    import fitz
    warnings=[line for line in (C/'accounting-product-proposal.log').read_text().splitlines() if any(x in line for x in ('Overfull','undefined','multiply defined','Missing character','Fatal error','LaTeX Error'))]
    assert not warnings,warnings
    bib=(C/'accounting-product-proposal.blg').read_text()
    assert 'Warning--' not in bib and 'I found no' not in bib
    pdf=fitz.open(C/'accounting-product-proposal.pdf');bad=[]
    for number,page in enumerate(pdf,1):
        for block in page.get_text('dict')['blocks']:
            if block['type']!=0:continue
            for line in block['lines']:
                x0,y0,x1,y1=line['bbox']
                if min(x0,y0)<-1 or x1>page.rect.width+1 or y1>page.rect.height+1:bad.append(number)
    assert not bad,bad
    result.update(status='source and build preservation passed',pages=len(pdf),pdf_sha256=sha(C/'accounting-product-proposal.pdf'),bad_build_warnings=warnings,out_of_page_text=bad)
    return result

if __name__=='__main__':
    print(json.dumps(check('--source-only' in sys.argv)))
