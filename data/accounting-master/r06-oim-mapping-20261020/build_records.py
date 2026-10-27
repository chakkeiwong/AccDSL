"""One-time construction; completed unit is replayed only via verify.py."""
from pathlib import Path
import importlib.util
import json

U=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('oim_mapping',U/'compare.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R,B=m.R,m.B

def write(name,obj):
    with (U/name).open('x') as f:json.dump(obj,f,indent=2);f.write(chr(10))

assert not (U/'mapping.json').exists()
result=m.derive();fixtures=m.fixtures()
sources=B/'r06-calculations11-source-20261020/sources'
paths=set(m.INPUTS)
for row in m.load(m.COVER)['schema_inventory']:paths.add(R/row['source']['path'])
for name in ('03-oim','04-xbrlxml'):
    paths.add(sources/(name+'-trusted.body'));paths.add(sources/(name+'.visible.txt'))
paths.add(U/'compare.py');paths.add(U/'build_records.py')
anchors=[]
for file,terms in {
 '04-xbrlxml.visible.txt':['2.1.1 Non-dimensional segment/scenario content','2.1.2 Mixing segment and scenario elements',
 '2.1.3 Complex-typed dimensions','2.1.4 Tuples','2.1.5 Unsupported concept data types',
 '2.1.6 Use of non-standard footnote resource roles','2.1.7 Use of zero-precision numeric facts',
 '2.1.8 Direct references to linkbase documents','2.1.9 Use of non-discoverable, non-standard role types and arcrole types',
 '2.1.10 Unlinked footnotes','2.1.11 Use of @xml:base attribute','2.1.12 Unsupported legacy datatypes and derivation restrictions',
 'Mapping: Entity Core Dimension','Mapping: Period Core Dimension','Mapping: Unit Core Dimension',
 'Mapping: Language Core Dimension','Mapping: Taxonomy-defined Dimension','3.3.1 Text footnotes'],
 '03-oim.visible.txt':['A text fact is a fact with a datatype','Two dimension values are equal',
 '5.1.2 Taxonomy-defined dimension value equality','5.1.5 Canonical language value',
 'Two facts, a and b, are duplicate facts','If the identified dimension is a typed dimension then']
}.items():
    path=sources/file;raw=path.read_bytes();text=raw.decode()
    for term in terms:
        # Last heading occurrence selects the body, not table of contents.
        start=text.rfind(term);assert start>=0
        end=text.find(chr(10),start)
        if end<0:end=len(text)
        end2=text.find(chr(10),end+1)
        if end2<0:end2=len(text)
        end=end2
        a=len(text[:start].encode());z=len(text[:end].encode())
        anchors.append({'source_path':str(path.relative_to(R)),'source_sha256':m.m.digest(raw),
          'label':term,'byte_start':a,'byte_end':z,'text':text[start:end]})
write('source-ledger.json',{'scope':'retained primary technical specifications and exact local evidence; no new acquisitions',
  'bindings':[m.bind(p) for p in sorted(paths)],'anchors':anchors,
  'source_editions':['xBRL-XML REC-2021-10-13','OIM REC-2021-10-13'],
  'qualification':'§2.1.10 names xbrli:footnote; §3.3.1 maps link:footnote. Both absent here, so wording does not change this finite outcome.'})
write('mapping.json',result);write('fixtures.json',fixtures)
write('acquisitions.json',{'attempts':[],'reason':'exact retained editions reused; no download or upstream execution'})
write('source-support-ledger.json',{'sources':[{'path':str((sources/(s+'.visible.txt')).relative_to(R)),
 'status':'retained normative recommendation, exact 2021 edition','inspected':'compatibility, mapping, types and equality',
 'allowed':'finite dimension mapping','forbidden':'full processor conformance or financial admission'} for s in ('03-oim','04-xbrlxml')]})
write('citation-venue-ledger.json',{'status':'not applicable to finite normative-specification mapping; no paper ranking'})
write('backward-snowball-ledger.json',{'dependencies':['retained XBRL2.1','retained dimensions','retained XML Schema datatype evidence'],
 'new_acquisitions':False,'scope':'only already inspected dependencies used'})
write('forward-snowball-ledger.json',{'status':'not expanded','reason':'exact edition-matched successor, not latest standard survey'})
write('claim-support-ledger.json',{'claims':[{'claim':'Twelve compatibility constraints supported in this retained structure','evidence':'mapping.json compatibility/inventory'},
 {'claim':'OIM dimension grouping compared with frozen XML grouping','evidence':'mapping.json classes/partition_equal'},
 {'claim':'No generic processor or full value validation','evidence':'explicit finite profile and remaining duties'}]})
write('omission-risk-ledger.json',{'remaining':['full schema/DTS correspondence','full XHTML/DTR validity',
 'general S-Equal and V-Equal','generic OIM value normalization','generic footnote/effective relationship mapping',
 'normative Calculations1.1 schema publication copy','Calc1.1 duplicate cross-reference ambiguity','installed correspondence'],
 'omission_effect':'dependent claims remain unadmitted; independent documentary work continues'})
print(json.dumps({'counts':result['counts'],'fixtures':len(fixtures),'anchors':len(anchors),'bindings':len(paths)}))
