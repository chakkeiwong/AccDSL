"""Construct once; completed evidence is replayed without flags."""
import importlib.util,json
from pathlib import Path
U=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('textblock_policy',U/'compare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
R,B=m.R,m.B
def write(name,v):
 with (U/name).open('x') as f:json.dump(v,f,indent=2);f.write(chr(10))
assert not (U/'policy.json').exists()
r=m.derive()
paths={U/'compare.py',U/'build_records.py',U/'dependency-plan-addendum.md',m.TEXT,
 B/'r06-enumeration-domain-20261020/extract_visible.py',B/'r06-textblock-fragments-20261020/result.md',
 B/'r06-textblock-fragments-20261020/real-entity-example.json',
 B/'native-concept-type-coverage-20261018/coverage.json',
 R/'docs/design/proposal/manuscript-early-conversion-20261018/sections/adapter-methods.tex'}
paths.update(p for p in (U/'sources').iterdir() if p.is_file())
spans=[(m.SOURCE,[(22,31),(240,247),(524,577),(579,640),(640,692)]),
 (U/'sources/DTR.visible.txt',[(1,29),(180,239),(249,295)]),
 (U/'sources/edbody.dtd-sandbox.body',[(1,45),(130,200),(533,600)]),
 (U/'sources/xhtml1-strict-ix.dtd-sandbox.body',[(1,39),(186,214),(350,364),(856,884)])]
anchors=[]
for p,ranges in spans:
 lines=p.read_text().splitlines()
 for a,b in ranges:
  assert 1<=a<=b<=len(lines)
  anchors.append({'source':m.bind(p),'first_line':a,'last_line':b,'excerpt':chr(10).join(lines[a-1:b])})
write('source-ledger.json',{'bindings':[m.bind(p) for p in sorted(paths)],'anchors':anchors,
 'scope':'DTR structure metadata and selected pinned filing-profile branches; no legal/compliance or current-policy advice'})
write('policy.json',r)
write('acquisitions.json',{'attempts':[{'path':str((U/'sources'/(n+'-receipt.json')).relative_to(R))} for n in ('DTR','ValidateFilingText','edbody.dtd','xhtml1-strict-ix.dtd')]})
write('source-support-ledger.json',{'sources':['DTR structure CR2018 linked by OIM','pinned ValidateFilingText and two DTDs','retained DTR2020/2022 annotations'],
 'allowed':'source-specific policy distinctions and authored projection consequences','forbidden':'full56-fragment validity, generic DTR acceptance, actual runtime/caller activation'})
write('citation-venue-ledger.json',{'status':'not applicable to normative/software-source inquiry'})
write('backward-snowball-ledger.json',{'dependencies':['xhtml-lat1.ent','xhtml-symbol.ent','xhtml-special.ent','caller/profile configuration'],
 'status':'explicit remaining source/runtime duties; not fetched or inferred complete'})
write('forward-snowball-ledger.json',{'status':'not a latest-version or filing-rules survey','scope':'exact linked edition and already selected pin'})
write('claim-support-ledger.json',{'claims':[{'claim':'selected validator is profile-specific','support':'DTDs and source guards'},
 {'claim':'validation projection is not content preserving','support':'10 authored/source-bound witnesses'},
 {'claim':'XML structure does not close fullDTR/XHTML duty','support':'policy.json separated duties'}]})
write('omission-risk-ledger.json',{'open':['generic XHTML fragment interpretation','selected profile and caller','DTD entity files','actual parser/environment','full validator execution','rendered financial semantics'],
 'effect':'dependent validity/admission remain unestablished; source and original values preserved'})
print(json.dumps({'findings':len(r['source_findings']),'witnesses':len(r['witnesses']),'duties':len(r['duties']),'anchors':len(anchors),'bindings':len(paths)}))
