"""Reconstruct native source records from retained inputs under a read audit."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import xml.etree.ElementTree as E
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('--root',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args = parser.parse_args()
root, out = args.root.resolve(), args.output.resolve()
assert out.is_relative_to(root) and out != root
assert Path(__file__).resolve().is_relative_to(root)
out.mkdir(exist_ok=False)
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
sys.dont_write_bytecode = True
environment = [Path(p).resolve() for p in {sys.prefix,sys.base_prefix}]
accesses, libraries, violations = set(), set(), []
started = time.monotonic()

def category(path):
    if path.is_relative_to(out): return 'output'
    if path.is_relative_to(root): return 'bundle'
    if any(path.is_relative_to(p) for p in environment): return 'installed_environment'
    return 'undeclared'

def refuse(event, detail):
    violations.append(dict(event=event,detail=str(detail)))
    raise RuntimeError('undeclared access: '+str(detail))

def audit(event, values):
    if event == 'open':
        path, mode, flags = values
        if isinstance(path,int):
            if path not in (0,1,2): refuse(event,path)
            return
        p = Path(os.fsdecode(path)).resolve()
        write = bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        kind = category(p)
        accesses.add((str(p),'write' if write else 'read',kind))
        if (write and kind!='output') or (not write and kind=='undeclared'): refuse(event,p)
    elif event == 'ctypes.dlopen':
        path = values[0]
        libraries.add(str(path))
        if path is not None and (not os.path.isabs(path) or category(Path(path).resolve())=='undeclared'):
            refuse(event,path)
    elif event in ['os.mkdir','os.remove','os.rmdir','os.chmod','os.utime']:
        if category(Path(os.fsdecode(values[0])).resolve())!='output': refuse(event,values[0])
    elif event in ['os.rename','os.link','os.symlink']:
        if any(category(Path(os.fsdecode(p)).resolve())!='output' for p in values[:2]): refuse(event,values[:2])
    elif event in ['socket.connect','socket.bind','subprocess.Popen','os.system','os.exec']:
        refuse(event,values[0])

sys.addaudithook(audit)
checks = []
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()
def dump(name,value):
    with (out/name).open('x') as stream: json.dump(value,stream,indent=2);stream.write('\n')
def check(name,actual,expected=True):
    passed = actual == expected
    checks.append(dict(name=name,passed=passed))
    if not passed: raise AssertionError(name)

try:
    manifest = read(root/'source-manifest.json')
    check('isolated Python',sys.flags.isolated,1)
    check('Python version',sys.version.split()[0],'3.11.15')
    for name,row in manifest['entries'].items(): check('before '+name,digest(root/name),row['sha256'])
    sys.path.insert(0,str(root/'scripts'))
    import retained_statement_network_v1 as network
    import z3
    import importlib.metadata
    check('Z3 version',z3.get_version_string(),'4.16.0')
    base = root/'data/accounting-master'
    old = next(r for r in read(base/'retained-population-overlap-20261025/exchanges.json')
               if r['name']=='full_source_dash')
    body, budget = deepcopy(old['source_request']), deepcopy(old['budget'])
    before = deepcopy([body,budget])
    parent = network.assess(body,budget)
    dump('source-parent.json',dict(request=body,budget=budget,result=parent))
    check('complete original source parent',parent,old['result']['source_result'])
    check('unmodified reconstruction input',[body,budget],before)
    selected = read(base/'debt-reading-network-20261027/attempt-01/full-result.json')
    check('parent actually consumed by selected reader',parent,selected['source_parent'])
    check('original unresolved status',parent['status'],'unresolved')
    check('complete source population',len(parent['preserved_report']['observations']),256)
    check('complete source relations',len(parent['preserved_report']['relations']),143)
    check('selected measurements',len(parent['definition']['observations']),236)
    check('selected equations',len(parent['definition']['relations']),101)
    observation='a69f27d314a20d2f5dc69ae2bc795a7abf5a8c1ae49e695b29e1547109910752'
    check('original unknown dash interval',parent['definition']['observations'][observation]['interval'],None)

    source_dir = base/'debt-dash-source-20261027'
    facts, binding = read(source_dir/'source-inspection-01/facts.json'), read(source_dir/'selected-binding.json')
    archive = root/'docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.zip'
    pdf = root/'docs/design/cases/apple/annual-2024.pdf'
    check('archive identity',digest(archive),binding['archive_sha256'])
    check('PDF identity',digest(pdf),binding['pdf_sha256'])
    with zipfile.ZipFile(archive) as zip_source: raw=zip_source.read('aapl-20240928_htm.xml')
    check('instance identity',sha256(raw).hexdigest(),binding['instance_sha256'])
    xml = E.fromstring(raw)
    by_id = {n.attrib['id']:n for n in xml if 'id' in n.attrib}
    ns={'x':'http://www.xbrl.org/2003/instance'}
    local=lambda name:name.rsplit('}',1)[-1]
    for fact in facts:
        ident = fact['id']
        node,context,unit = by_id[ident],by_id[fact['context_ref']],by_id[fact['unit_ref']]
        check(ident+' original fact XML',E.tostring(node,encoding='unicode'),fact['raw_xml'])
        check(ident+' original concept',node.tag,fact['concept'])
        check(ident+' original value',node.text,fact['value'])
        check(ident+' original accuracy',node.attrib.get('decimals'),fact['decimals'])
        check(ident+' raw context',E.tostring(context,encoding='unicode'),fact['context']['raw_xml'])
        check(ident+' raw unit',E.tostring(unit,encoding='unicode'),fact['unit_xml'])
        check(ident+' context binding',node.attrib['contextRef'],fact['context_ref'])
        check(ident+' unit binding',node.attrib['unitRef'],fact['unit_ref'])
        check(ident+' nil flag',node.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}nil') in ['true','1'],fact['nil'])
        entity=context.find('x:entity',ns); identifier=entity.find('x:identifier',ns)
        parsed=dict(entity=dict(scheme=identifier.attrib['scheme'],identifier=identifier.text),
            period={local(n.tag):n.text for n in context.find('x:period',ns)},
            dimensions=[E.tostring(n,encoding='unicode') for n in context.iter() if local(n.tag) in ['explicitMember','typedMember']],
            other_children=[E.tostring(n,encoding='unicode') for n in context if local(n.tag) not in ['entity','period']]
                +[E.tostring(n,encoding='unicode') for n in entity if local(n.tag)!='identifier'],
            raw_xml=E.tostring(context,encoding='unicode'))
        check(ident+' independent parsed context',parsed,fact['context'])
        measures=unit.findall('x:measure',ns)
        check(ident+' simple USD unit',len(unit)==len(measures)==1 and measures[0].text=='iso4217:USD')
        check(ident+' declared USD unit',fact['unit'],'{http://www.xbrl.org/2003/iso4217}USD')
    spec=importlib.util.spec_from_file_location('source_reading',source_dir/'source_reading_v2.py')
    reading=importlib.util.module_from_spec(spec);sys.modules['source_reading']=reading;spec.loader.exec_module(reading)
    before=deepcopy([facts,binding]); result=reading.select(facts,binding)
    dump('selected-reading.json',result)
    check('complete frozen reading',result,read(source_dir/'attempt-01/reading.json'))
    check('reading consumed by selected composer',result,selected['reading'])
    check('reading inputs unchanged',[facts,binding],before)
    check('reported zero only',result['displayed_value_usd_million'],'0/1')
    check('not exact latent zero',result['exact_economic_zero'],False)
    check('no information cutoff',result['historical_information_cutoff_checked'],False)
    check('original dash retained',result['original_literal'],'—')
    for name,row in manifest['entries'].items(): check('after '+name,digest(root/name),row['sha256'])
    modules=sorted({str(Path(m.__file__).resolve()) for m in list(sys.modules.values())
        if getattr(m,'__file__',None) and not m.__file__.startswith('<')})
    for path in modules:
        check('declared module '+path,category(Path(path)) in ['bundle','installed_environment'])
    for path,mode,kind in list(accesses):
        if kind=='bundle' and mode=='read' and Path(path).is_file():
            check('inventoried read '+path,Path(path).name=='source-manifest.json' or str(Path(path).relative_to(root)) in manifest['entries'])
    check('no undeclared access',violations,[])
    versions={n:importlib.metadata.version(n) for n in ['z3-solver','jsonschema','attrs','referencing','rpds-py','jsonschema-specifications']}
    summary=dict(passed=True,checks=len(checks),raw_facts=len(facts),source_observations=256,
        source_relations=143,selected_observations=236,selected_relations=101,normalization='none')
    dump('checks.json',{**summary,'details':checks})
    dump('run-manifest.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
        command=[sys.executable,'-I','-B',*sys.argv],python=sys.version,distributions=versions,
        environment_roots=[str(p) for p in environment],observed_modules=modules,
        git_commit='N/A: unusable .git marker preserved',random_seeds='N/A: exact reconstruction',
        cpu_gpu='CPU only; GPUs intentionally hidden before project imports',wall_seconds=time.monotonic()-started,
        data_version=digest(root/'source-manifest.json'),plan=manifest['plan'],
        result='data/accounting-master/retained-source-reconstruction-20261027/result.md',
        artifacts=['source-parent.json','selected-reading.json','checks.json','access-audit.json']))
    print(json.dumps(summary))
except Exception as exc:
    dump('failure.json',dict(type=type(exc).__name__,error=str(exc),checks=checks))
    raise
finally:
    dump('access-audit.json',dict(hook_before_project_imports=True,
        accesses=[dict(path=p,mode=m,classification=k) for p,m,k in sorted(accesses)],
        dynamic_libraries=sorted(libraries),violations=violations,
        limit='Python-visible calls only; interpreter startup and arbitrary native OS syscalls excluded'))
