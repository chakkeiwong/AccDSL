"""Build once; no upstream module is imported or evaluated."""
import importlib.util
import json
from pathlib import Path
U=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('processor_inquiry',U/'compare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
R,B=m.R,m.B

def write(name,v):
    with (U/name).open('x') as f:json.dump(v,f,indent=2);f.write(chr(10))

assert not (U/'examples.json').exists()
examples=m.examples();checks=m.static_checks()
paths={m.CALC,m.MODEL,U/'compare.py',U/'build_records.py',U/'dependency-plan-addendum.md',
 B/'r06-calculations11-source-20261020/compare.py',B/'r06-calculations11-source-20261020/examples.json',
 B/'r06-calc11-alignment-20261020/alignment.json',
 B/'arelle-fact-identity-20261013/source-findings.json',B/'arelle-fact-identity-20261013/source-receipts.json',
 B/'native-loader-source-20261018/source-manifest.json'}
anchors=[]
spans=[(m.CALC,[(112,167),(174,183),(230,250),(265,291),(330,349),(398,449),(463,520),(704,778)]),
 (m.MODEL,[(1294,1310),(1349,1408),(1649,1664)])]
for name in ('Contexts','Units','Equivalence'):
 p=U/'sources'/(name+'-sandbox.body');paths.update([p,p.with_name(name+'-sandbox.headers'),p.with_name(name+'-receipt.json')]);spans.append((p,[(1,len(p.read_text().splitlines()))]))
for name,ranges in [('02-calc11',[(180,207),(220,237),(250,262),(281,324),(326,370)]),('03-oim',[(514,528)])]:
 p=B/'r06-calculations11-source-20261020/sources'/(name+'.visible.txt');paths.add(p);paths.add(p.with_name(name+'-trusted.body'));spans.append((p,ranges))
for p,ranges in spans:
 for a,b in ranges:
  lines=p.read_text().splitlines();assert 1<=a<=b<=len(lines),(p,a,b,len(lines))
  anchors.append({'source':m.bind(p),'first_line':a,'last_line':b,'excerpt':chr(10).join(lines[a-1:b])})
write('source-ledger.json',{'bindings':[m.bind(p) for p in sorted(paths)],'anchors':anchors,
 'commit':'01f6a4656c2c6551d2f05f31c9d74366d133ee7e','upstream_execution':False,
 'interpretation':'finite source transition models; official processor practice does not repair normative text'})
write('examples.json',examples);write('static-checks.json',checks)
write('acquisitions.json',{'attempts':[{'path':str((U/'sources'/(n+'-receipt.json')).relative_to(R))} for n in ('Contexts','Units','Equivalence')],
 'scope':'3 missing helpers at existing pin; third justified by dependency addendum'})
write('source-support-ledger.json',{'sources':['pinned ValidateXbrlCalcs','pinned ModelInstanceObject','pinned Contexts/Units/Equivalence','retained Calc1.1/OIM'],
 'allowed':'identified source branches and exact authored consequences under declared inputs',
 'forbidden':'execution trace, current-release bug, actual filing result, authoritative source correction'})
write('citation-venue-ledger.json',{'status':'not applicable to exact software/normative-source inquiry'})
write('backward-snowball-ledger.json',{'dependencies':['Contexts -> Equivalence','Units -> Equivalence','binding -> ModelInstanceObject equality/hash','interval helper -> rangeValue/insignificantDigits'],
 'scope':'direct inspected dependencies only; no installed-runtime closure'})
write('forward-snowball-ledger.json',{'status':'not checked for later fixes','reason':'existing pin governs local proposed reuse; no latest-version claim'})
write('claim-support-ledger.json',{'claims':[{'claim':'Exact key joins rather than subset matching','support':'source-ledger binding/helper spans'},
 {'claim':'Same-precision flag overwritten','support':'examples same_precision_unequal plus static-checks'},
 {'claim':'Endpoint and precedence divergences','support':'examples exact boundaries/weight/overlap/large precision'},
 {'claim':'No actual filing impact established','support':'no upstream execution and constructed-only witnesses'}]})
write('omission-risk-ledger.json',{'open':['authoritative alignment correction','generic schema/OIM validation','actual native hash/collision behavior',
 'installed execution and decimal context','later source fixes','actual filing impact'],
 'effect':'conditional local mathematical diagnostics may continue; pinned processor cannot be treated as correctness oracle'})
print(json.dumps({'witnesses':len(examples),'static_checks':len(checks),'anchors':len(anchors),'bindings':len(paths)}))
