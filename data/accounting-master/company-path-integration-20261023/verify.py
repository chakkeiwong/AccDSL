"""Verify bounded successor preservation; --record is explicit and one-time."""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import re
import fitz

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def protected(text):
    return {'labels':Counter(re.findall(r'\\label\{([^}]+)\}',text)),
        'references':Counter(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}',text)),
        'citations':Counter(re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}',text)),
        'bracket_displays':Counter(re.findall(r'\\\[(.*?)\\\]',text,re.S)),
        'environment_displays':Counter(re.findall(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}(.*?)\\end\{\1\}',text,re.S))}


def verify():
    baseline=json.loads((HERE/'baseline.json').read_text())
    source,target=[ROOT/baseline[k] for k in ['source_root','candidate_root']]
    issues=[];changed=[];counts=Counter()
    sentinel=r'\label{a} \ref{a} \citep{x} \[x+y\] \begin{equation}z\end{equation}'
    if not all(sum(v.values())==1 for v in protected(sentinel).values()):raise AssertionError('broken protection matcher')
    for name,h in baseline['source_hashes'].items():
        a,b=source/name,target/name
        if sha(a)!=h:issues.append({'baseline_changed':name})
        if not b.exists():issues.append({'successor_missing':name});continue
        if sha(b)!=h:changed.append(name)
        if a.suffix=='.tex':
            before,after=protected(a.read_text()),protected(b.read_text())
            for kind,old in before.items():
                counts[kind]+=sum(old.values());removed=old-after[kind]
                if removed:issues.append({'file':name,'removed':kind,'count':sum(removed.values())})
    allowed={'accounting-product-proposal.tex','chapters/06-language.tex','chapters/07-execution.tex','sections/company-input-authoring.tex'}
    if set(changed)!=allowed:issues.append({'unexpected_source_changes':sorted(set(changed)^allowed)})
    current_sources={str(p.relative_to(target)) for p in target.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    added=current_sources-set(baseline['source_hashes'])
    if added!={'sections/company-operation-paths.tex'}:issues.append({'unexpected_new_files':sorted(added)})
    if sha(source/'accounting-product-proposal.pdf')!=baseline['pdf_sha256']:issues.append({'baseline_pdf_changed':True})
    labels=Counter()
    for p in target.rglob('*.tex'):labels.update(protected(p.read_text())['labels'])
    if any(v>1 for v in labels.values()):issues.append({'duplicate_labels':[k for k,v in labels.items() if v>1]})
    log=(target/'accounting-product-proposal.log').read_text(errors='replace')
    critical=[line for line in log.splitlines() if re.search(r'^!|Undefined control sequence|undefined references|Citation .* undefined|Reference .* undefined|Overfull',line)]
    if critical:issues.append({'build_warnings':critical})
    build=json.loads((HERE/'build.json').read_text())
    if build['returncode']!=0:issues.append({'build_exit':build['returncode']})
    pdf=target/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
    if 'Version 3.52' not in doc[0].get_text():issues.append({'wrong_title_version':True})
    if sha(pdf)!=build['pdf_sha256']:issues.append({'build_pdf_hash_mismatch':True})
    locators={}
    for phrase in ['Repeated operations and consecutive company years','When splitting operations','The next year starts','A revision must say','A coherent path still needs']:
        locators[phrase]=[i+1 for i,page in enumerate(doc) if phrase in page.get_text()]
        if not locators[phrase]:issues.append({'missing_reader_passage':phrase})
    return {'passed':not issues,'candidate_version':'3.52','pages':len(doc),
        'pdf_sha256':sha(pdf),'baseline_source_count':len(baseline['source_hashes']),
        'protected_occurrences':dict(counts),'changed_files':sorted(changed),
        'new_files':sorted(added),'passage_pages':locators,'issues':issues,
        'scope':'Bounded source/build preservation only; full successor reading and independent/domain/human acceptance remain pending.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');a=p.parse_args();r=verify()
    out=HERE/'verification.json'
    if a.record:
        if out.exists():raise RuntimeError('Existing verification evidence')
        out.write_text(json.dumps(r,indent=2)+'\n')
    elif out.exists() and r!=json.loads(out.read_text()):raise AssertionError('Verification evidence differs')
    print(json.dumps(r));return not r['passed']


if __name__=='__main__':raise SystemExit(main())
