"""Caller-authored mappings for retained records and independent language tests."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_input_binding_v1 as binder


def packet(definition,raw,mapping,encodings=None,missing=None):
    """Create the caller declaration; production binder does not infer this map."""
    definition=deepcopy(definition)
    raw_hash=sha256(raw).hexdigest()
    shape={'profile':binder.SCHEMA,'schema_id':'selected-fields.'+definition['method_id'],'fields':{}}
    entries=[]
    for key,pointer in mapping.items():
        declaration=definition['inputs'][key]
        declaration['source_ref']='sha256:'+raw_hash+'#'+pointer
        shape['fields'][pointer]={'type':deepcopy(declaration['type']),'role':declaration['role'],
            'encoding':(encodings or {}).get(key,'scalar'),
            'missing':(missing or {}).get(key,'invalid')}
        entries.append({'input':key,'record':'supplied','pointer':pointer})
    manifest_digest=core.digest(definition)
    schema_digest=core.digest(shape)
    plan={'profile':binder.PROFILE,'manifest_digest':manifest_digest,
          'records':{'supplied':{'raw_sha256':raw_hash,'schema_digest':schema_digest}},'bindings':entries}
    return {'plan':plan,'manifests':{manifest_digest:definition},'schemas':{schema_digest:shape},
            'blobs':{raw_hash:raw},'available':definition['capabilities']}


def assess(example):
    return binder.assess_bound(example['plan'],example['manifests'],example['schemas'],
                              example['blobs'],example['available'])


def retained():
    path=HERE.parent/'method-requirements-20261024/bridge.py'
    spec=importlib.util.spec_from_file_location('input_binding_old_bridge',path)
    bridge=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    raw=(HERE.parent/'company-operations-20261023/example.json').read_bytes()
    operation=json.loads(raw)
    sys.path.insert(0,str(HERE.parent/'company-return-schema-20261023'))
    import retained_fixture
    import return_schema
    returned,source=retained_fixture.fixture()
    built={}
    for name,body,raw,build in [
        ('operations',operation,raw,bridge.operations_requirements),
        ('returns',returned,core.canonical(returned),lambda b:bridge.return_requirements(b,return_schema.FINDINGS))]:
        definition,expected=build(body)
        mapping={key:'/'+key for key in definition['inputs']}
        encodings={key:('scalar' if d['type']['kind']=='text' else 'legacy_unknown_string')
                   for key,d in definition['inputs'].items()}
        built[name]={'packet':packet(definition,raw,mapping,encodings),'expected_values':expected,
                     'body':body,'provenance':'original bytes' if name=='operations' else
                     'explicit retained_fixture projection; canonical bytes are a derived record',
                     'upstream_raw_sha256':sha256(source).hexdigest() if name=='returns' else sha256(raw).hexdigest()}
    return built
