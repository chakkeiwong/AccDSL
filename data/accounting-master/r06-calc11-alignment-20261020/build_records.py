"""One-time construction of alignment evidence; completed replay has no flags."""
import importlib.util
import json
from pathlib import Path
U=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('calc11_alignment',U/'compare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
R,B=m.R,m.B

def write(name,v):
    with (U/name).open('x') as f:json.dump(v,f,indent=2);f.write(chr(10))

assert not (U/'alignment.json').exists()
r=m.derive();cases=m.fixtures()
paths={m.MAP,m.CALC,U/'compare.py',U/'build_records.py',
 B/'r06-oim-mapping-20261020/compare.py',B/'r06-calculation-bindings-20261020/compare.py',
 B/'r06-dimensional-network-20261020/compare.py',B/'r06-typed-domain-dates-20261020/compare.py',
 B/'r06-numeric-accuracy-20261020/compare.py',B/'r06-numeric-lexical-20261020/compare.py',m.oim.COVER}
for row in m.load(m.old.n.MAP):paths.add(R/row['retained_path'])
paths.add(m.old.n.MAP)
anchors=[]
for name,spans in [('02-calc11',[(180,207),(220,237),(397,412)]),('03-oim',[(439,455),(492,506)])]:
 p=B/'r06-calculations11-source-20261020/sources'/f'{name}.visible.txt';paths.add(p)
 paths.add(p.with_name(name+'-trusted.body'))
 for a,b in spans:anchors.append({'source':m.bind(p),'first_line':a,'last_line':b,'excerpt':chr(10).join(p.read_text().splitlines()[a-1:b])})
write('source-ledger.json',{'bindings':[m.bind(p) for p in sorted(paths)],'anchors':anchors,
 'source_issue':'§5.1 definition lacks converse; compare both orientations and symmetric equality without selecting policy'})
write('alignment.json',r);write('fixtures.json',cases)
write('acquisitions.json',{'attempts':[],'reason':'retained sources only; live search yielded no usable clarification'})
write('source-support-ledger.json',{'sources':['corrected Calculations1.1 REC2023-02-22 errata2024-02-14','OIM REC2021-10-13'],
 'inspected_sections':['Calc1.1 4.1,4.2,5.1,AppendixB','OIM5.1,6'],
 'allowed':'exact wording and finite directional-join comparison','forbidden':'authoritative correction or conformance'})
write('citation-venue-ledger.json',{'status':'not applicable to finite normative-source inquiry'})
write('backward-snowball-ledger.json',{'dependencies':['frozen XBRL2.1 effective network','frozen OIM dimension mapping'],'new_acquisitions':False})
write('forward-snowball-ledger.json',{'status':'open','next':'official clarification or pinned implementation behavior; static code is not normative authority'})
write('claim-support-ledger.json',{'claims':[{'claim':'Missing converse affects possible alignment relation','support':'source-ledger.json'},
 {'claim':'Actual directional sensitivity and denominator bridge','support':'alignment.json'}]})
write('omission-risk-ledger.json',{'open':['authoritative alignment interpretation','Calc1.1 duplicate cross-reference ambiguity',
 'normative schema copy','full schema/OIM/installed validation'],'effect':'no calculation or conformance promotion'})
print(json.dumps({'counts':r['counts'],'modes':r['modes'],'fixtures':len(cases),'anchors':len(anchors),'bindings':len(paths)}))
