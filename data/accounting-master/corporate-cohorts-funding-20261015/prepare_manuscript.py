from pathlib import Path
import hashlib,json,shutil,re
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-group-restatement-20261015'
NEW=ROOT/'docs/design/proposal/manuscript-corporate-cohorts-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not NEW.exists()
assert json.loads((OUT/'cases.json').read_text())['passed']
assert sha(OLD/'accounting-product-proposal.pdf')=='c4eba8f000c9489a3cbdf798b05cd7997626923a59be21cbdf81b95cf6616d61'
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline':str(OLD.relative_to(ROOT)),'pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.09')==1;p.write_text(s.replace('Version 3.09','Version 3.10'))
method=ROOT/'docs/design/proposal/methods/corporate-cohorts-funding-20261015.tex'
(NEW/'sections/corporate-cohorts-funding.tex').write_text(method.read_text())
p=NEW/'sections/corporate-methods.tex';s=p.read_text();anchor=r'\input{sections/corporate-events}';assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+'\n\n'+r'\input{sections/corporate-cohorts-funding}'))
entry=r"""
@misc{ifric2012cashclassification,
  author = {{IFRS Foundation staff}},
  title = {{Examples illustrating the classification of cash flows}},
  year = {2012},
  howpublished = {IFRS Interpretations Committee meeting, July 2012, Agenda paper 3},
  url = {https://www.ifrs.org/content/dam/ifrs/meetings/2012/july/interpretations-committee/031207ap03ias7examplesillustratingclassificationcashflows.pdf},
  note = {Appendix A, A35--A43 inspected. Staff analysis, not an authoritative Interpretation.}
}
"""
p=NEW/'references.bib';s=p.read_text();assert 'ifric2012cashclassification' not in s;p.write_text(s+entry)
cases=json.loads((OUT/'cases.json').read_text())
(OUT/'source-support.json').write_text(json.dumps({'sources':cases['sources'],'reading_record':str((OUT/'source-reading.md').relative_to(ROOT)),'support':[{'source':'eu20231803','anchors':['IAS2 9–27 34','IAS19 64 120–127','IFRIC14 7–24','IAS7 6 10–16 31–36 43–44','IFRIC1 1–8'],'use':'Dated rules plus conditional costing and funding derivations'},{'source':'ifric2012cashclassification','anchors':['cover status','AppendixA A35–43'],'use':'Nonbinding staff support and competing interpretation for rehabilitation payments'},{'source':'iasb2025cashclassification','anchors':['cover status','objective','47–54'],'use':'Context only; no new operative restoration rule inferred'}]},indent=2)+'\n')
print(json.dumps({'version':'3.10','preserved_sources':len(sources),'new_words':len(method.read_text().split())}))
