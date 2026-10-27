"""Bounded manuscript preservation, build checks and render-location recording."""
from collections import Counter
from pathlib import Path
import hashlib,json,re,sys
import fitz
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def protected(text):
    return {'labels':Counter(re.findall(r'\\label\{([^}]+)\}',text)),
            'references':Counter(re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}',text)),
            'citations':Counter(re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}',text)),
            'bracket_displays':Counter(re.findall(r'\\\[(.*?)\\\]',text,re.S)),
            'environment_displays':Counter(re.findall(r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}(.*?)\\end\{\1\}',text,re.S))}
def verify():
    baseline=json.loads((HERE/'baseline.json').read_text()); source=ROOT/baseline['source_root']; target=ROOT/baseline['candidate_root']
    issues=[]; changed=[]; counts=Counter()
    sentinel=r'\label{a} \ref{a} \citep{x} \[x+y\] \begin{equation}z\end{equation}'
    assert all(sum(v.values())==1 for v in protected(sentinel).values()),'broken preservation matcher'
    for name,h in baseline['source_hashes'].items():
        a,b=source/name,target/name
        if sha(a)!=h: issues.append({'baseline_changed':name})
        if not b.exists(): issues.append({'successor_missing':name}); continue
        if sha(b)!=h: changed.append(name)
        if a.suffix=='.tex':
            before,after=protected(a.read_text()),protected(b.read_text())
            for kind,old in before.items():
                counts[kind]+=sum(old.values())
                if old-after[kind]: issues.append({'removed':kind,'file':name})
    allowed={'accounting-product-proposal.tex','chapters/06-language.tex','chapters/17-portable-reference.tex','sections/method-requirement-language.tex'}
    if set(changed)!=allowed: issues.append({'unexpected_changes':sorted(set(changed)^allowed)})
    sources={str(p.relative_to(target)) for p in target.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    added=sources-set(baseline['source_hashes'])
    if added!={'sections/requirement-successors.tex'}: issues.append({'unexpected_new':sorted(added)})
    if sha(source/'accounting-product-proposal.pdf')!=baseline['pdf_sha256']: issues.append({'baseline_pdf_changed':True})
    labels=Counter(); references=set(); citations=set()
    for p in target.rglob('*.tex'):
        tokens=protected(p.read_text()); labels.update(tokens['labels']); references.update(tokens['references'])
    if any(n>1 for n in labels.values()): issues.append({'duplicate_labels':[k for k,n in labels.items() if n>1]})
    if references-set(labels): issues.append({'missing_labels':sorted(references-set(labels))})
    log=(target/'accounting-product-proposal.log').read_text(errors='replace')
    warnings=[line for line in log.splitlines() if re.search(r'^!|Undefined control sequence|undefined references|Citation .* undefined|Reference .* undefined|Overfull',line)]
    if warnings: issues.append({'build_warnings':warnings})
    build=json.loads((HERE/'build.json').read_text())
    if build['returncode']!=0: issues.append({'build_exit':build['returncode']})
    pdf=target/'accounting-product-proposal.pdf'; document=fitz.open(pdf)
    if 'Version 3.60' not in document[0].get_text(): issues.append({'title_version':True})
    if '24 October 2026' not in document[0].get_text(): issues.append({'title_date':True})
    if sha(pdf)!=build['pdf_sha256']: issues.append({'build_pdf_mismatch':True})
    phrases=['Binding a return obligation to its applicable equations', 'Select the record before checking its amounts', 'Multiply quantities without erasing their units', 'An inactive equation does not settle an unknown fact', 'Keep versions explicit through authoring and exchange']
    locations={text:[i+1 for i,p in enumerate(document) if text in p.get_text()] for text in phrases}
    for phrase,pages in locations.items():
        if not pages: issues.append({'missing_passage':phrase})
    return {'passed':not issues,'candidate_version':'3.60','pages':len(document),'pdf_sha256':sha(pdf),'baseline_source_count':len(baseline['source_hashes']),'protected_occurrences':dict(counts),'changed_files':sorted(changed),'new_files':sorted(added),'passage_pages':locations,'issues':issues,'scope':'Source/build and bounded reading only; full manuscript and independent/domain/human acceptance pending'}
def main():
    result=verify()
    if '--record' in sys.argv:
        assert not (HERE/'verification.json').exists()
        (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    elif (HERE/'verification.json').exists(): assert result==json.loads((HERE/'verification.json').read_text())
    print(json.dumps(result)); return not result['passed']
if __name__=='__main__': raise SystemExit(main())
