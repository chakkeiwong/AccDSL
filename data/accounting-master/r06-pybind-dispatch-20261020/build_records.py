"""One-time construction after the version-bounded source reading."""
import importlib.util
import json
from pathlib import Path

U=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('dispatch_compare',U/'compare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
names=['comparison.json','source-ledger.json','source-support-ledger.json','citation-venue-ledger.json',
       'backward-snowball-ledger.json','forward-snowball-ledger.json','claim-support-ledger.json','omission-risk-ledger.json']
assert not any((U/n).exists() for n in names)
value=m.derive()
spans={
 U/'sources/v220-sandbox.body':[(88,99),(123,162),(295,359),(430,519),(520,615),(616,695),(696,774),(795,808)],
 U/'sources/v2111-sandbox.body':[(163,179),(213,275),(465,568),(676,765),(766,852),(853,933),(934,1040),(1041,1152),(1164,1180)],
 U/'sources/v220-attr-sandbox.body':[(134,198)],U/'sources/v2111-attr-sandbox.body':[(191,269)],
 m.P/'sources/s00.body':[(1113,1154),(1808,1861)],
 m.P/'sources/s03.body':[(372,426),(1419,1486)],
 m.P/'sources/s02.body':[(855,872),(1280,1288)],
 m.P/'sources/s05.body':[(780,812),(1580,1596),(2420,2427)],
 m.P/'sources/helper0.body':[(196,208)],m.P/'sources/helper1.body':[(368,377)],
 m.L/'sources/04-source.body':[(1,40),(328,358)]}
anchors=[]
for path,ranges in spans.items():
    lines=path.read_text().splitlines()
    for first,last in ranges:
        assert 1<=first<=last<=len(lines)
        anchors.append({'source':m.bind(path),'first_line':first,'last_line':last,
                        'excerpt':'\n'.join(lines[first-1:last])})
paths=set(spans)|{U/'compare.py',U/'build_records.py',U/'source-plan-addendum.md',m.P/'result.md',
 m.R/'data/accounting-master/r06-pylcs-release-20261020/result.md'}
paths.update((U/'sources').iterdir())
paths.update(m.P/'sources'/f'{i}-{kind}.body' for i in range(2) for kind in ['commit','tree'])
records={
 'comparison.json':value,
 'source-ledger.json':{'bindings':[m.bind(p) for p in sorted(paths)],'anchors':anchors,
                      'scope':'listed source spans and complete dispatcher bodies; no native execution'},
 'source-support-ledger.json':{'sources':value['new_sources'],
    'read_scope':'binding registration,wrappers,dispatcher bodies,record defaults and selected retained caster/pytypes/helper spans',
    'allowed':['conditional nominal terminal TypeError','conversion failure precedes function body','version-bounded repr handling difference'],
    'forbidden':value['not_established'],
    'version_status':'exact pinned tags/commits inherited; no broad correction or all-version survey'},
 'citation-venue-ledger.json':{'date':'2026-10-20','venue':'official pybind11 repository',
    'citation_count':'not available; not an authority/correctness criterion','academic_ranking':'not applicable'},
 'backward-snowball-ledger.json':{'edges':['pylcs m.def -> module.def -> cpp_function wrapper',
    'std::string caster -> argument_loader -> TRY_NEXT_OVERLOAD -> dispatcher',
    'attr.h next/is_operator defaults','pytypes.h repr/string conversion/raise_from','common.h sentinel'],
    'limit':'only the failing-argument path; no complete native-library dependency closure'},
 'forward-snowball-ledger.json':{'scope':'two inherited release snapshots only',
    'installed_or_later_versions':'not queried','actual_binary':'not acquired or executed'},
 'claim-support-ledger.json':{'claims':[
    {'claim':'nominal failed-load diagnostic is TypeError','support':'complete linked source path in comparison.json with exact anchors'},
    {'claim':'original codec error is cleared','support':'both string load implementations'},
    {'claim':'single binding avoids overload fallback','support':'actual pylcs registration,record defaults and dispatcher overloaded condition'},
    {'claim':'newer repr handling catches error_already_set','support':'v2.11.1 terminal branch and retained repr helper'},
    {'claim':'no universal runtime outcome follows','support':'source/build gap and secondary diagnostic-failure branches'}]},
 'omission-risk-ledger.json':{'open':value['not_established'],
    'next':'audit current readiness queue for substantive independent gaps; do not turn source-query count into completeness',
    'preserved':'3.44/396/not_ready,53 obligations,six interactions,46 operations,zero whole-row closures'}
}
for name,obj in records.items():
    with (U/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
print(json.dumps({'constructed':True,'anchors':len(anchors),'bindings':len(paths),'new_blobs':4}))
