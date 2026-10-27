"""Documentary archive/file comparison. Never executes acquired source."""
import ast
import configparser
from email.parser import BytesParser
import hashlib
import importlib.util
import json
from pathlib import Path
import tomllib

U = Path(__file__).resolve().parent
R = U.parents[2]
spec = importlib.util.spec_from_file_location('release_archive_reader', U/'archive_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
SELECTED = {'src/main.cpp':'04-source.body', 'pylcs/__init__.py':'05-source.body', 'setup.py':'06-source.body'}
VIEWS = {'src/main.cpp':'main.cpp.txt', 'pylcs/__init__.py':'init.py.txt', 'setup.py':'setup.py.txt',
         'pyproject.toml':'pyproject.toml.txt', 'setup.cfg':'setup.cfg.txt', 'PKG-INFO':'PKG-INFO.txt',
         'pylcs.egg-info/PKG-INFO':'egg-PKG-INFO.txt', 'pylcs.egg-info/SOURCES.txt':'SOURCES.txt',
         'pylcs.egg-info/dependency_links.txt':'dependency_links.txt',
         'pylcs.egg-info/requires.txt':'requires.txt', 'pylcs.egg-info/top_level.txt':'top_level.txt',
         'pylcs.egg-info/not-zip-safe':'not-zip-safe.txt'}


def bind(p):
    return {'path':str(p.relative_to(R)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}


def load(p):
    return json.loads(p.read_text())


def derive():
    release, entries, files, expanded = reader.read_archive()
    receipt = load(U/'sources/sdist-receipt.json')
    response = json.loads(receipt['result']['output'])
    assert receipt['result']['exit_code'] == response['exitcode'] == 0
    assert response['http_code'] == 200 and response['size_download'] == release['size']
    assert response['url'] == response['url_effective'] == release['url']
    comparisons = []
    for path, original in SELECTED.items():
        a, b = files[path], (reader.PRIOR/'sources'/original).read_bytes()
        assert a != b
        assert a.replace(b'\r\n', b'\n') == b
        assert a.count(b'\r') == a.count(b'\r\n') and b'\r' not in b
        assert len(a)-len(b) == a.count(b'\r\n')
        comparisons.append({'member':path,'release_bytes':len(a),'git_bytes':len(b),
                            'release_sha256':hashlib.sha256(a).hexdigest(),
                            'pinned_file':bind(reader.PRIOR/'sources'/original),
                            'exact_equal':False,'crlf_to_lf_equal':True,
                            'crlf_pairs':a.count(b'\r\n')})
    project = tomllib.loads(files['pyproject.toml'].decode())
    assert project == {'build-system':{'requires':['setuptools>=42','pybind11>=2.2'],
                                      'build-backend':'setuptools.build_meta'}}
    setup = ast.parse(files['setup.py'].decode())
    calls = [n for n in ast.walk(setup) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='setup']
    assert len(calls)==1
    keywords = {k.arg:k.value for k in calls[0].keywords}
    declared = {k:ast.literal_eval(keywords[k]) for k in ['name','version','install_requires','packages','zip_safe','license']}
    assert declared['name']=='pylcs' and declared['version']=='0.1.1'
    assert declared['install_requires']==['pybind11>=2.2']
    metadata = BytesParser().parsebytes(files['PKG-INFO'])
    assert metadata['Name']=='pylcs' and metadata['Version']=='0.1.1'
    assert files['PKG-INFO']==files['pylcs.egg-info/PKG-INFO']
    assert files['pylcs.egg-info/requires.txt'].decode().splitlines()==declared['install_requires']
    cfg = configparser.ConfigParser()
    cfg.read_string(files['setup.cfg'].decode())
    assert dict(cfg['egg_info'])=={'tag_build':'','tag_date':'0'}
    listed = files['pylcs.egg-info/SOURCES.txt'].decode().splitlines()
    assert len(listed)==len(set(listed))
    missing = sorted(set(listed)-files.keys())
    extras = sorted(files.keys()-set(listed))
    assert missing==[] and extras==['PKG-INFO','setup.cfg']
    assert not any(name.endswith(('.so','.pyd','.dll','.dylib','.whl')) for name in files)
    assert not any(name.startswith('pybind11/') for name in files)
    return {'archive':{'filename':release['filename'],'sha256':release['digests']['sha256'],
                       'bytes':release['size'],'expanded_bytes':expanded,'members':entries,
                       'files':len(files),'upload':release['upload_time_iso_8601'],
                       'yanked_at_metadata_snapshot':release['yanked']},
            'comparisons':comparisons,'build_system':project['build-system'],'setup':declared,
            'packaging':{'source_manifest_entries':len(listed),'missing_members':missing,
                          'extra_generated_metadata':extras,'package_metadata_copies_equal':True,
                          'top_level':files['pylcs.egg-info/top_level.txt'].decode().splitlines(),
                          'pkg_info_requires_dist':metadata.get_all('Requires-Dist',[]),
                          'egg_requires':declared['install_requires']},
            'claim_scope':'three complete files agree after CRLF-to-LF only; no whole-repository or binary equivalence',
            'build_identity':'not established: ranges and conditional compiler options, no resolved attestation'}


def check():
    result = derive()
    assert result==load(U/'comparison.json')
    _,_,files,_ = reader.read_archive()
    for name, target in VIEWS.items():
        assert (U/'views'/target).read_bytes()==files[name]
    ledger = load(U/'source-ledger.json')
    for item in ledger['bindings']:
        assert bind(R/item['path'])==item,item['path']
    for a in ledger['anchors']:
        raw=(R/a['source']['path']).read_bytes()
        assert bind(R/a['source']['path'])==a['source']
        assert raw[a['start']:a['end']].decode()==a['excerpt']
    return {'status':'source archive and declared line-ending comparisons verified',
            'acquisitions':1,'archive_members':len(result['archive']['members']),
            'archive_files':result['archive']['files'],'raw_equal_files':0,'crlf_equal_files':3,
            'bindings':len(ledger['bindings']),'anchors':len(ledger['anchors']),
            'build_identity_established':False,'runtime_admitted':False,'whole_rows_closed':0}
