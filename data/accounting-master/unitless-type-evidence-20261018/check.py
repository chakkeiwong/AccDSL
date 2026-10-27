"""Static retained schema declaration chains; never XSD/XBRL validation."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
MAP=ROOT/'data/accounting-master/native-offline-resolution-20261018/resource-map.json'
FULL=ROOT/'data/accounting-master/native-full-portable-20261018'
PLAN=ROOT/'docs/plans/accounting-unitless-type-evidence-20261018.md'
XS='http://www.w3.org/2001/XMLSchema'
XI='http://www.xbrl.org/2003/instance'
DEI='http://xbrl.sec.gov/dei/2024'
AAPL='http://www.apple.com/20240928'
EXPECTED={'f-57':('gYearItemType','gYear'),'f-59':('centralIndexKeyItemType','token'),
          'f-13':('normalizedStringItemType','normalizedString'),'f-14':('normalizedStringItemType','normalizedString'),
          'f-934':('gYearItemType','gYear'),'f-935':('gYearItemType','gYear'),'f-1127':('nonemptySequenceNumberItemType','token')}

def require(ok,label):
    if not ok: raise ValueError(label)

def sha(raw): return hashlib.sha256(raw).hexdigest()
def binding(path): return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
def load(path): return json.loads(path.read_bytes())
def write(path,value):
    with path.open('x') as h: json.dump(value,h,indent=2,ensure_ascii=False);h.write('\n')

def schemas():
    selected={}
    for row in load(MAP):
        ns=row['target_namespace']
        if ns not in (XI,DEI,AAPL): continue
        path=ROOT/row['retained_path'];raw=path.read_bytes()
        require(sha(raw)==row['expected_blob']['digest'],'SOURCE_MAP_HASH')
        root=ET.fromstring(raw)
        if root.tag!='{'+XS+'}schema': continue
        require(ns not in selected,'AMBIGUOUS_SCHEMA')
        namespaces=dict(v for _,v in ET.iterparse(BytesIO(raw),events=('start-ns',)))
        selected[ns]={'path':path,'raw':raw,'root':root,'namespaces':namespaces,'receipt':row['acquisition_receipt']}
    require(set(selected)=={XI,DEI,AAPL},'SCHEMA_SET')
    return selected

def expanded(token,source):
    prefix,local=token.split(':',1) if ':' in token else ('',token)
    return '{'+source['namespaces'][prefix]+'}'+local

def anchor(source,element):
    name=element.get('name');kind=element.tag.split('}')[-1]
    marker=('name="'+name+'"').encode();raw=source['raw']
    positions=[m.start() for m in re.finditer(re.escape(marker),raw)]
    candidates=[]
    for pos in positions:
        start=raw.rfind(b'<',0,pos);end=raw.index(b'>',pos)+1
        token=re.match(br'<([^\s>]+)',raw[start:end]).group(1)
        if token.decode().split(':')[-1]!=kind: continue
        if raw[end-2:end]!=b'/>': end=raw.index(b'</'+token+b'>',end)+len(token)+3
        candidates.append((start,end))
    require(len(candidates)==1,'ANCHOR_UNIQUE:'+name)
    start,end=candidates[0]
    return {'source':binding(source['path']),'byte_start':start,'byte_end':end,
            'first_line':raw[:start].count(b'\n')+1,'last_line':raw[:end].count(b'\n')+1,
            'sha256':sha(raw[start:end]),'text':raw[start:end].decode()}

def definition(all_schemas,qname,kind):
    namespace,local=qname[1:].split('}',1);source=all_schemas[namespace]
    entries=[e for e in source['root'] if e.tag=='{'+XS+'}'+kind and e.get('name')==local]
    require(len(entries)==1,'UNIQUE_DEFINITION:'+qname)
    return source,entries[0]

def chain(all_schemas,type_name):
    rows=[];visited=set()
    while not type_name.startswith('{'+XS+'}'):
        require(type_name not in visited,'CYCLIC_BASE');visited.add(type_name)
        source,element=definition(all_schemas,type_name,'complexType')
        content=element.find('{'+XS+'}simpleContent')
        require(content is not None,'NOT_SIMPLE_CONTENT')
        bases=[e for e in content if e.tag in ('{'+XS+'}extension','{'+XS+'}restriction')]
        require(len(bases)==1,'BASE_COUNT')
        base=bases[0];next_type=expanded(base.get('base'),source)
        rows.append({'type':type_name,'derivation':base.tag.split('}')[-1],'base':next_type,
            'facets':[{'kind':e.tag.split('}')[-1],'attributes':dict(e.attrib)} for e in base if e.tag!='{'+XS+'}attributeGroup'],
            'attribute_groups':[expanded(e.get('ref'),source) for e in base if e.tag=='{'+XS+'}attributeGroup'],
            'anchor':anchor(source,element)})
        type_name=next_type
    return rows,type_name

def construct():
    all_schemas=schemas();packet=load(FULL/'native-packet.json');facts={f['id']:f for f in packet['facts']}
    rows=[]
    for key in EXPECTED:
        fact=facts[key];source,element=definition(all_schemas,fact['expanded_concept'],'element')
        declared=expanded(element.get('type'),source);layers,terminal=chain(all_schemas,declared)
        rows.append({'fact_id':key,'source_concept':fact['expanded_concept'],'original_token':fact['decoded_text'],
            'source_context_id':fact['source_context_id'],'source_unit_id':fact['source_unit_id'],
            'declared_type':declared,'declaration_attributes':dict(element.attrib),'declaration_anchor':anchor(source,element),
            'chain':layers,'terminal_builtin':terminal,'portable_value_status':'unchanged_Unknown',
            'validation_status':'not_run'})
    shared=[]
    for name in ['nonNumericItemAttrs','itemAttrs','factAttrs']:
        source,element=definition(all_schemas,'{'+XI+'}'+name,'attributeGroup')
        shared.append({'name':name,'anchor':anchor(source,element)})
    return {'scope':'retained_declaration_evidence_only','source_packet':binding(FULL/'native-packet.json'),
        'schemas':[{'source':binding(s['path']),'acquisition_receipt':s['receipt']} for s in all_schemas.values()],
        'rows':rows,'shared_attributes':shared,'schema_copy_status':'Retained XBRL header calls this copy non-normative; asserted identity to normative Appendix A not independently verified',
        'validation_run':False,'upstream_executed':False}

def validate(evidence):
    expected=construct();checks=[]
    def check(label,ok): require(ok,label);checks.append(label)
    check('CLOSED_ROOT',set(evidence)==set(expected))
    check('SEVEN_ROWS',[r['fact_id'] for r in evidence['rows']]==list(EXPECTED))
    check('NO_VALIDATION',evidence['validation_run'] is False and evidence['upstream_executed'] is False)
    for row,ref in zip(evidence['rows'],expected['rows']):
        key=row['fact_id'];declared,terminal=EXPECTED[key]
        check('DECLARED_TYPE:'+key,row['declared_type'].split('}')[-1]==declared)
        check('TERMINAL:'+key,row['terminal_builtin']=='{'+XS+'}'+terminal)
        check('ORIGINAL_TOKEN:'+key,row['original_token']==ref['original_token'])
        check('DECLARATION:'+key,row['declaration_attributes']==ref['declaration_attributes'])
        check('CHAIN:'+key,row['chain']==ref['chain'])
        check('UNKNOWN_PRESERVED:'+key,row['portable_value_status']=='unchanged_Unknown' and row['validation_status']=='not_run')
        for location in [row['declaration_anchor']]+[x['anchor'] for x in row['chain']]:
            raw=(ROOT/location['source']['path']).read_bytes();chunk=raw[location['byte_start']:location['byte_end']]
            check('ANCHOR:'+key+':'+str(location['byte_start']),sha(chunk)==location['sha256'] and chunk.decode()==location['text'])
    check('CIK_ZEROS',next(r for r in evidence['rows'] if r['fact_id']=='f-59')['original_token']=='0000320193')
    check('EXACT_EVIDENCE',evidence==expected)
    return checks

def negatives(evidence):
    tests=[('wrong-type',lambda d:d['rows'][0].__setitem__('declared_type','{'+XI+'}integerItemType'),'DECLARED_TYPE:f-57'),
        ('wrong-builtin',lambda d:d['rows'][0].__setitem__('terminal_builtin','{'+XS+'}integer'),'TERMINAL:f-57'),
        ('leading-zeros-lost',lambda d:d['rows'][1].__setitem__('original_token','320193'),'ORIGINAL_TOKEN:f-59'),
        ('inherited-base-lost',lambda d:d['rows'][1]['chain'].pop(),'CHAIN:f-59'),
        ('restriction-pattern-lost',lambda d:d['rows'][1]['chain'][0].__setitem__('facets',[]),'CHAIN:f-59'),
        ('false-validation',lambda d:d.__setitem__('validation_run',True),'NO_VALIDATION'),
        ('candidate-promoted',lambda d:d['rows'][6].__setitem__('portable_value_status','admitted_integer'),'UNKNOWN_PRESERVED:f-1127'),
        ('source-copy-qualification-lost',lambda d:d.__setitem__('schema_copy_status','normative_verified'),'EXACT_EVIDENCE')]
    out=[]
    for name,edit,wanted in tests:
        altered=deepcopy(evidence);edit(altered)
        try:validate(altered)
        except ValueError as error:
            require(str(error)==wanted,'WRONG_NEGATIVE:'+name+':'+str(error));out.append({'case':name,'rejected':str(error)})
        else:raise ValueError('ACCEPTED:'+name)
    return out

def main():
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--record',action='store_true');mode.add_argument('--check-only',action='store_true')
    args=parser.parse_args();tick=time.monotonic()
    evidence=construct() if args.record or args.check_only else load(OUT/'declarations.json')
    checks=validate(evidence);corruptions=negatives(evidence)
    findings={'checks':checks,'negative_cases':corruptions,'declared_types':[{k:r[k] for k in ['fact_id','original_token','declared_type','terminal_builtin']} for r in evidence['rows']]}
    if args.record:
        for name in ['declarations.json','checks.json','run-manifest.json']:require(not (OUT/name).exists(),'ALREADY_RECORDED')
        write(OUT/'declarations.json',evidence);write(OUT/'checks.json',findings)
        inherited=load(FULL/'run-manifest.json')['protected_inputs']
        protected=inherited+[binding(p) for p in [PLAN,MAP,FULL/'completion.json',FULL/'checks.json',FULL/'run-manifest.json']]
        for item in evidence['schemas']:protected.extend([item['source'],item['acquisition_receipt']])
        manifest={'recorded_utc':datetime.now(timezone.utc).isoformat(),'command':'python3 data/accounting-master/unitless-type-evidence-20261018/check.py --record',
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'environment':{'executable':sys.executable,'python':platform.python_version(),'conda_env':'tfgpu','cpu_gpu':'CPU standard-library schema/source checks; no numerical framework or GPU'},
            'data_version':binding(FULL/'native-packet.json'),'random_seeds':'N/A: deterministic','wall_seconds':time.monotonic()-tick,
            'plan_file':str(PLAN.relative_to(ROOT)),'result_file':str((OUT/'result.md').relative_to(ROOT)),
            'protected_inputs':protected,'artifacts':[binding(OUT/n) for n in ['check.py','declarations.json','checks.json']]}
        write(OUT/'run-manifest.json',manifest)
    elif not args.check_only:
        require(findings==load(OUT/'checks.json'),'REPLAY_CHANGED')
        manifest=load(OUT/'run-manifest.json')
        for item in manifest['protected_inputs']+manifest['artifacts']:require(binding(ROOT/item['path'])==item,'PROTECTED:'+item['path'])
    print(json.dumps({'mode':'check_only' if args.check_only else 'record' if args.record else 'read_only_replay','checks':len(checks),'rejected_corruptions':len(corruptions),'rows':len(evidence['rows']),'schema_validation':'not_run','status':'pass'}))

if __name__=='__main__':main()
