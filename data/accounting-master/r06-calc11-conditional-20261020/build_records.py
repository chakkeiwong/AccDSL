"""One-time conditional arithmetic construction."""
import importlib.util,json
from pathlib import Path
U=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('conditional_calculations',U/'compare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
R,B=m.R,m.B
def write(name,v):
 with (U/name).open('x') as f:json.dump(v,f,indent=2);f.write(chr(10))
assert not (U/'conditional-calculations.json').exists()
r=m.derive();f=m.fixtures()
paths={m.MAP,m.ALIGN,m.LEX,m.CALC,U/'compare.py',U/'build_records.py',
 B/'r06-calculations11-source-20261020/compare.py',B/'r06-calc11-alignment-20261020/compare.py',
 B/'r06-calc11-processor-20261020/result.md',B/'r06-calculations11-source-20261020/prerequisites.json'}
anchors=[]
for name,ranges in [('02-calc11',[(180,207),(220,237),(239,324),(326,370)]),('03-oim',[(514,528)])]:
 p=B/'r06-calculations11-source-20261020/sources'/(name+'.visible.txt');paths.add(p);paths.add(p.with_name(name+'-trusted.body'))
 for a,b in ranges:anchors.append({'source':m.bind(p),'first_line':a,'last_line':b,'excerpt':chr(10).join(p.read_text().splitlines()[a-1:b])})
write('source-ledger.json',{'bindings':[m.bind(p) for p in sorted(paths)],'anchors':anchors,
 'scope':'conditional mathematical equality-alignment branch; no normative correction or issuer policy'})
write('conditional-calculations.json',r);write('fixtures.json',f)
write('acquisitions.json',{'attempts':[],'reason':'retained inputs reused'})
write('source-support-ledger.json',{'sources':['corrected Calculations1.1','linked OIM','retained exact instance/type/numeric evidence'],
 'allowed':'conditional per-mode finite arithmetic','forbidden':'conformance,accounting correctness,issuer rounding choice'})
write('citation-venue-ledger.json',{'status':'not applicable to deterministic conditional arithmetic'})
write('backward-snowball-ledger.json',{'dependencies':['frozen OIM mapping','frozen symmetric alignment','numeric lexical and accuracy','retained old calculation network'],
 'new_sources':False})
write('forward-snowball-ledger.json',{'remaining':'authoritative alignment and duplicate-definition clarification; no unsupported source substitution'})
write('claim-support-ledger.json',{'claims':[{'claim':'conditional candidate outcomes and old denominator bridge','support':'conditional-calculations.json'},
 {'claim':'independent arithmetic agreement','support':'every candidate and numeric point plus fixtures'},
 {'claim':'unqualified conformance remains unadmitted','support':'explicit plan hypotheses and predecessor source ambiguities'}]})
write('omission-risk-ledger.json',{'open':['full schema/DTS/OIM validation','normative schema publication copy','authoritative source ambiguities','installed correspondence','issuer policy'],
 'effect':'finite conditional arithmetic only; no row closure'})
print(json.dumps({'counts':r['counts'],'fixtures':len(f),'anchors':len(anchors),'bindings':len(paths)}))
