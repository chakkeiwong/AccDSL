from collections import Counter
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import re
import sys
import fitz
from prepare import ADDITIONS,expected

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def protected(text):
    return {'labels':Counter(re.findall(r'\\label\{([^}]+)\}',text)),
            'references':Counter(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}',text)),
            'citations':Counter(re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}',text)),
            'bracket_displays':Counter(re.findall(r'\\\[(.*?)\\\]',text,re.S)),
            'environment_displays':Counter(re.findall(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}(.*?)\\end\{\1\}',text,re.S))}

def verify():
    baseline=json.loads((HERE/'baseline.json').read_text());source=ROOT/baseline['source_root'];target=ROOT/baseline['candidate_root']
    issues=[];changed=[];counts=Counter()
    sentinel=r'\label{a} \ref{a} \citep{x} \[x+y\] \begin{equation}z\end{equation}'
    assert all(sum(v.values())==1 for v in protected(sentinel).values())
    for name,h in baseline['source_hashes'].items():
        a,b=source/name,target/name
        if sha(a)!=h:issues.append({'predecessor_changed':name})
        if not b.is_file():issues.append({'missing':name});continue
        if sha(b)!=h:changed.append(name)
        if b.read_text()!=expected(name,a.read_text()):issues.append({'unexpected_edit':name})
        if a.suffix=='.tex':
            before,after=protected(a.read_text()),protected(b.read_text())
            for kind,old in before.items():
                counts[kind]+=sum(old.values())
                if old-after[kind]:issues.append({'removed':kind,'file':name})
    allowed={'accounting-product-proposal.tex',*ADDITIONS}
    if set(changed)!=allowed:issues.append({'changed_set':sorted(set(changed)^allowed)})
    sources={p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    if sources!=set(baseline['source_hashes']):issues.append({'source_set':True})
    if sha(source/'accounting-product-proposal.pdf')!=baseline['pdf_sha256']:issues.append({'predecessor_pdf':True})
    for name,h in json.loads((HERE/'evidence-check.json').read_text())['protected_evidence'].items():
        if sha(ROOT/name)!=h:issues.append({'evidence_changed':name})
    for name,h in json.loads((HERE.parent/'declared-financing-clock-20261025'/'source-lock.json').read_text()).items():
        if sha(ROOT/name)!=h:issues.append({'transitive_evidence_changed':name})
    labels=Counter();refs=set()
    for p in target.rglob('*.tex'):
        tok=protected(p.read_text());labels.update(tok['labels']);refs.update(tok['references'])
    if any(n>1 for n in labels.values()):issues.append({'duplicate_labels':True})
    if refs-set(labels):issues.append({'missing_labels':sorted(refs-set(labels))})
    log=(target/'accounting-product-proposal.log').read_text(errors='replace')
    warnings=[line for line in log.splitlines() if re.search(r'^!|Undefined control sequence|undefined references|Citation .* undefined|Reference .* undefined|Overfull',line)]
    if warnings:issues.append({'build_warnings':warnings})
    build=json.loads((HERE/'build.json').read_text())
    if build['returncode']!=0:issues.append({'build_returncode':build['returncode']})
    pdf=target/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
    if 'Version 4.14' not in doc[0].get_text() or '25 October 2026' not in doc[0].get_text():issues.append({'cover':True})
    if sha(pdf)!=build['pdf_sha256']:issues.append({'pdf_hash':True})
    phrases=['Accrue interest before changing the principal it prices.', 'Keep financing, profit and direct equity distinct.', 'Compose bounded definitions without weakening each method’s checks.', 'Explain working-capital movements from the verified history.', 'Follow purchasing, sales and wages through one book.', 'Author the sequence while retaining its declared definitions.', 'Run the declared company through successive periods.', 'Close the recorded balances under explicit carry policies.', 'Report the declared accounts and explain their movements.', 'Carry the entire native book through the selected sale.', 'Bind a named method to the event that actually occurred.', 'Declare the company book before applying its methods.', 'A payment can change the decision that follows it.', 'Reuse a calculation without changing its meaning.', 'Resume the annual book from its last committed operation']
    locations={phrase:[i+1 for i,p in enumerate(doc) if i>20 and phrase in ' '.join(p.get_text().split())] for phrase in phrases}
    if any(not pages for pages in locations.values()):issues.append({'missing_passage':locations})
    return {'passed':not issues,'candidate_version':'4.14','pages':len(doc),'pdf_sha256':sha(pdf),
            'baseline_source_count':len(baseline['source_hashes']),'protected_occurrences':dict(counts),
            'changed_files':sorted(changed),'new_files':[],'passage_pages':locations,'issues':issues,
            'scope':'Source/build and bounded author review; full-document, independent/domain/human acceptance pending'}

if __name__=='__main__':
    result=verify()
    if sys.argv[1:]==['--record']:
        assert not (HERE/'verification.json').exists()
        (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));raise SystemExit(not result['passed'])
