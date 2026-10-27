"""Construct source-release records once, after all input checks succeed."""
import importlib.util
import json
from pathlib import Path
import hashlib

U=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('release_comparison',U/'compare.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
names=['comparison.json','source-ledger.json','source-support-ledger.json','citation-venue-ledger.json',
       'backward-snowball-ledger.json','forward-snowball-ledger.json','claim-support-ledger.json','omission-risk-ledger.json']
assert not (U/'views').exists() and not any((U/n).exists() for n in names)
value=m.derive()
release,entries,files,expanded=m.reader.read_archive()
paths={U/'archive_reader.py',U/'compare.py',U/'build_records.py',U/'source-plan-addendum.md',
       m.reader.METADATA,m.reader.PRIOR/'sources/03-tree.body',m.reader.PRIOR/'result.md',
       m.R/'data/accounting-master/r04-pybind-strings-20261020/result.md'}
paths.update(m.reader.PRIOR/'sources'/n for n in m.SELECTED.values())
paths.update((U/'sources').iterdir())
bindings=[m.bind(p) for p in sorted(paths)]
anchors=[]
for name,target in m.VIEWS.items():
    raw=files[name]
    item={'path':str((U/'views'/target).relative_to(m.R)),'sha256':hashlib.sha256(raw).hexdigest()}
    bindings.append(item)
    if name in ['src/main.cpp','pylcs/__init__.py','setup.py']:
        spans={'src/main.cpp':[(b'void utf8',0,0)],
               'pylcs/__init__.py':[(b'from _pylcs import *',0,21)],
               'setup.py':[(b'class get_pybind_include',0,540),(b'def cpp_flag',0,600),
                           (b'class BuildExt',0,950),(b'setup(',0,750)]}[name]
        if name=='src/main.cpp':
            # The entire raw file is compared; no newly read algorithm span is claimed.
            spans=[]
        for i,(needle,before,after) in enumerate(spans):
            start=raw.index(needle)-before;end=min(len(raw),start+len(needle)+after)
            anchors.append({'id':target+'-'+str(i),'source':item,'start':start,'end':end,
                            'excerpt':raw[start:end].decode()})
    else:
        end=raw.index(b'\r\n\r\n') if name.endswith('PKG-INFO') else len(raw)
        anchors.append({'id':target,'source':item,'start':0,'end':end,'excerpt':raw[:end].decode()})
records={
 'comparison.json':value,
 'source-ledger.json':{'bindings':bindings,'anchors':anchors,
    'reading_scope':'all small packaging/build metadata; complete setup.py and initializer inherited equal after declared line ending conversion; prior native read scope remains1–61/328–365',
    'comparison_scope':'three full files; no imported upstream module or executed build'},
 'source-support-ledger.json':{'source':'pylcs0.1.1 published source archive',
    'url':release['url'],'upload':release['upload_time_iso_8601'],'local':m.bind(m.reader.ARCHIVE),
    'digest_source':m.bind(m.reader.METADATA),'repository_pin':'5eee78a655fbe34ef24c8240304646f7cd07543b',
    'release_status':'unyanked in retained metadata snapshot; no new metadata query',
    'allowed':['exact archive identity','three files equal modulo CRLF-to-LF','declared unpinned build recipe'],
    'forbidden':['raw source identity','whole repository equality','historical build identity','installed correctness','licence clearance']},
 'citation-venue-ledger.json':{'date':'2026-10-20','venue':'PyPI source-release metadata and official author repository',
    'citation_count':'not available; not a validity criterion','academic_venue_ranking':'not applicable'},
 'backward-snowball-ledger.json':{'dependencies':[
    {'name':'setuptools>=42','role':'build backend','resolved_version':'not established'},
    {'name':'pybind11>=2.2','role':'build headers and declared install dependency','resolved_version':'not established'},
    {'name':'compiler/standard library/Python ABI','role':'conditional native build','resolved_identity':'not established'}],
    'scope':'documentary dependency edges, not a complete software bill of materials'},
 'forward-snowball-ledger.json':{'scope':'retained author head versus exact0.1.1 source release only',
    'later_releases':'not queried','distributed_wheels':'not acquired or inspected','installed_module':'not queried'},
 'claim-support-ledger.json':{'claims':[
    {'claim':'raw bytes differ for all three selected files','support':'comparison.json byte counts and SHA256'},
    {'claim':'only CRLF-to-LF is needed for complete selected-file equality','support':'direct byte replacement comparison; no broader whitespace normalization'},
    {'claim':'pybind11/runtime identity is not fixed by this release','support':'pyproject.toml,setup.py,egg requires and conditional compiler flags'},
    {'claim':'source manifest omits two generated archive metadata files','support':'all20 members and13 listed source paths; no missing listed member'}]},
 'omission-risk-ledger.json':{'open':['exact wheel build attestation','actual installed identity','resolved backend/headers/compiler/ABI',
    'uninspected native functions','full transitive/native dependencies','build-specific terms'],
    'next_source_question':'version-bounded pybind11 dispatcher behavior after failed std::string argument conversion',
    'effect':'no promotion from source equality to native-runtime or downstream financial validity'}
}
# No outputs are written until all derivation, anchor and record construction succeeds.
(U/'views').mkdir()
for name,target in m.VIEWS.items():
    with (U/'views'/target).open('xb') as handle:handle.write(files[name])
for name,obj in records.items():
    with (U/name).open('x') as handle:json.dump(obj,handle,indent=2);handle.write('\n')
print(json.dumps({'constructed':True,'members':len(entries),'files':len(files),
                  'bindings':len(bindings),'anchors':len(anchors),'raw_equal':0,'crlf_equal':3}))
