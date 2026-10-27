"""Construct once after source inspection; no acquired code executes."""
import importlib.util,json
from pathlib import Path
U=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('schema_recovery',U/'compare.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
names=['comparison.json','source-ledger.json','acquisitions.json','appendix-schema.xml',
       'source-support-ledger.json','citation-venue-ledger.json','backward-snowball-ledger.json',
       'forward-snowball-ledger.json','claim-support-ledger.json','omission-risk-ledger.json']
assert not any((U/n).exists() for n in names)
value=m.derive()
paths={U/'compare.py',U/'build_records.py',m.HTML,m.VISIBLE,m.PRIOR/'result.md',
       m.PRIOR/'prerequisites.json',m.PRIOR/'sources/05-schema-trusted.receipt.json',
       m.PRIOR/'sources/05-schema-trusted.headers',
       m.R/'docs/design/proposal/manuscript-early-conversion-20261018/sections/adapter-methods.tex'}
paths.update(p for p in (U/'sources').iterdir() if p.is_file())
spans=[(m.SCHEMA,[(1,len(m.SCHEMA.read_text().splitlines()))]),
       (m.VISIBLE,[(359,391)]),(m.HTML,[(467,505)])]
anchors=[]
for path,ranges in spans:
    lines=path.read_text().splitlines()
    for a,b in ranges:
        assert 1<=a<=b<=len(lines)
        anchors.append({'source':m.bind(path),'first_line':a,'last_line':b,'excerpt':'\n'.join(lines[a-1:b])})
def write(name,obj):
    with (U/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
with (U/'appendix-schema.xml').open('x') as f:f.write(m.appendix())
paths.add(U/'appendix-schema.xml')
write('comparison.json',value)
write('source-ledger.json',{'bindings':[m.bind(p) for p in sorted(paths)],'anchors':anchors,
                          'scope':'complete tiny publication schema and exact appendix comparison; no full processor validation'})
write('acquisitions.json',{'new_attempts':1,'new_receipt':m.bind(U/'sources/schema-receipt.json'),
                         'old_failure_preserved':m.bind(m.PRIOR/'sources/05-schema-trusted.receipt.json')})
write('source-support-ledger.json',{'sources':['exact Calculations1.1 publication schema','retained corrected2024 AppendixA'],
     'allowed':['publication-copy recovery','namespace-aware declaration equality','exact-byte identity result'],
     'forbidden':['installed schema correspondence','historical publication-byte identity','report adoption','5.4 prose correction','full DTS/XBRL conformance']})
write('citation-venue-ledger.json',{'status':'not applicable to a primary specification/schema inquiry'})
write('backward-snowball-ledger.json',{'imports':value['profile']['imports'],'includes':value['profile']['includes'],
     'redefines':value['profile']['redefines'],'limit':'no explicit XSD dependencies in this file; not whole-processor closure'})
write('forward-snowball-ledger.json',{'scope':'retained corrected2024 text and exact publication URL; no later-specification adoption'})
write('claim-support-ledger.json',{'claims':[{'claim':'normative publication copy is now retained','support':'schema receipt/bytes'},
     {'claim':'schema declarations agree with appendix under checked namespace-aware profile','support':'comparison.json and controls'},
     {'claim':'runtime and adoption remain separate','support':'AppendixA publication rules and unchanged prerequisites'}]})
write('omission-risk-ledger.json',{'open':['actual DTS discovery','installed version correspondence','5.4 normative cross-reference clarification',
     'filing-system rounding/adoption policy','full schema validation'],'effect':'scoped source-copy gap narrows without whole-row closure'})
print(json.dumps({'schema_bytes':value['retrieved_bytes'],'exact_equal':value['exact_utf8_equal'],
                  'profile_equal':True,'anchors':len(anchors),'bindings':len(paths),'fixtures':value['fixtures']}))
