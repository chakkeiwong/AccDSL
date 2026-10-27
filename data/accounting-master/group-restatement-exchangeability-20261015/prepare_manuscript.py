from pathlib import Path
import hashlib,json,shutil,re
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-insurance-treaty-changes-20261015'
NEW=ROOT/'docs/design/proposal/manuscript-group-restatement-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not NEW.exists()
assert json.loads((OUT/'cases.json').read_text())['passed']
assert sha(OLD/'accounting-product-proposal.pdf')=='461ae8c011e7384379a2943b9c158877b47b417475a3a8652a288bd634c5fc96'
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline':str(OLD.relative_to(ROOT)),'pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.08')==1;p.write_text(s.replace('Version 3.08','Version 3.09'))
method=ROOT/'docs/design/proposal/methods/group-restatement-exchangeability-20261015.tex'
s=method.read_text()
# Readable spacing only in prose; keys and source identifiers remain intact.
words='cash|inventory|capital|equity|investment|receivable|payable|revenue|cost|profit|assets|liabilities|debt|loss|income|index|rate|amounts|percent|totaling|of|from|to|by|is|becomes|and|plus|less|against|than|for|ratio|rates|paragraph|paragraphs'
s=re.sub(r'\b('+words+r')(?=[0-9])',r'\1 ',s)
s=re.sub(r'(?<=[0-9])(?=January)',r' ',s)
s=s.replace('amendment2024/2862','amendment 2024/2862').replace('IFRS~10.B86','IFRS~10.B86')
method.write_text(s)
(NEW/'sections/group-restatement-exchangeability.tex').write_text(s)
p=NEW/'sections/groups-fx-methods.tex';s=p.read_text();p.write_text(s+'\n\\input{sections/group-restatement-exchangeability}\n')
entry=r'''
@misc{eu20242862,
  author = {{European Commission}},
  title = {{Commission Regulation (EU) 2024/2862: Lack of Exchangeability, amendments to IAS 21}},
  year = {2024},
  howpublished = {Official Journal of the European Union, 13 November 2024},
  url = {https://eur-lex.europa.eu/eli/reg/2024/2862/oj},
  note = {Dated official HTML retained locally; Article 2 and IAS 21 paragraphs 8--8B, 19A, 26, 57A--B, 60L--M and A2--A20 inspected.}
}
'''
p=NEW/'references.bib';s=p.read_text();assert 'eu20242862' not in s;p.write_text(s+entry)
cases=json.loads((OUT/'cases.json').read_text())
(OUT/'source-support.json').write_text(json.dumps({'sources':cases['sources'],'reading_record':str((OUT/'source-reading.md').relative_to(ROOT)),'support':[{'source':'eu20231803','anchors':['IFRS10 B86–88 B92–95','IAS21 42–47','IAS29 1–41','IFRIC7 1–5'],'use':'Dated accounting procedures; no current-law certification'},{'source':'eu20242862','anchors':['Article2','IAS21 8–8B 19A 26 57A–B 60L–M A2–A20'],'use':'Dated exchangeability rules and transition; actual rates unresolved'}],'fresh_access':'Web returned no usable result; trusted curl produced zero-byte PDF. Retained official HTML used.'},indent=2)+'\n')
print(json.dumps({'version':'3.09','preserved_sources':len(sources),'new_words':len(method.read_text().split())}))
