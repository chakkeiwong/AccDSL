"""Check saved full cash identities and failed prefixes, then preserve once."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tarfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
read=lambda p:json.loads(p.read_text());digest=lambda p:sha256(p.read_bytes()).hexdigest()
def identity(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
info=read(HERE/'preparation-02/stage.json');stage=Path(info['stage']);run_dir=stage/'attempt-01'
unit=Path('data/accounting-master/insurance-paa-dated-book-20261027')
assert digest(HERE/'source-lock.json')==digest(stage/unit/'source-lock.json')==info['source_lock_sha256']
for p,h in info['source_lock'].items():assert digest(ROOT/p)==digest(stage/p)==h,p
verification=read(run_dir/'verification.json');assert verification['passed'] and verification['cases']==7 and verification['controls']==21
expected=read(HERE/'authored-expectations.json');cases=read(run_dir/'cases.json');controls=read(run_dir/'controls.json');checks=[]
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)));assert value,name
for row in cases:
    e=expected[row['id']];result=row['result'];execution=result['execution'];context=result['compiled']['opening']['context']
    full_flows=[dict(id=identity([f['event_id'],'cash']),entity=context['entity'],book=context['book'],currency=context['currency'],**deepcopy(f)) for f in e['flows']]
    check(row['id']+'/complete flow identities',execution['current']['flows']==full_flows)
    check(row['id']+'/complete report cash origins',row['report']['cash_flows']['gross_origins']==full_flows)
    check(row['id']+'/book preserved classes',execution['current']['accounts']==result['compiled']['opening']['accounts'])
    check(row['id']+'/eight event identities',execution['current']['seen']==[r['id'] for r in e['stages']])
    check(row['id']+'/no inferred actual admission',not any(row['report'][k] for k in ['source_admission','accounting_admission','method_eligible','posting_authorized','committed','physical_durability','fiscal_complete','notes_complete']))
baseline=cases[0]['result']['execution']
prefixes={'reordered_premiums':(0,'preconditions'),'duplicate_premium':(1,'duplicate_command_identity'),
          'wrong_event_date':(2,'preconditions'),'wrong_event_group':(2,'preconditions'),'omitted_claim_payment':(5,'preconditions')}
for row in controls:
    if row['id'] not in prefixes:continue
    n,reason=prefixes[row['id']];result=row['result'];stop=result['stop']
    check(row['id']+'/exact prior trace',result['trace']==baseline['trace'][:n])
    current=baseline['trace'][n-1]['result']['transition']['after'] if n else baseline['opening']
    check(row['id']+'/complete preserved current',result['current']==current)
    check(row['id']+'/exact refusal position',stop['index']==n and stop['reason']==reason)
    check(row['id']+'/unchanged state identity',stop['before_sha256']==identity(current) and stop.get('after_sha256',identity(current))==identity(current))
    check(row['id']+'/unexecuted suffix',result['remaining_commands']==row['compiled']['commands'][n:])
    check(row['id']+'/no report or carry archive',result['reports']==[] and result['archives']==[])
    check(row['id']+'/unchanged opening',result['opening']==baseline['opening'])
target=HERE/'attempt-01';assert not target.exists() and not (HERE/'preservation.json').exists()
shutil.copytree(run_dir,target);shutil.copyfile(stage/'attempt-01.log',target/'launcher.log')
smoke=HERE/'smoke-02';shutil.copytree(stage/'smoke-02',smoke);shutil.copyfile(stage/'smoke-02.log',smoke/'launcher.log')
outputs={}
for name in ['attempt-01','smoke-02']:
    for p in (HERE/name).rglob('*'):
        if not p.is_file():continue
        relative=p.relative_to(HERE/name);source=stage/(name+'.log') if p.name=='launcher.log' else stage/name/relative
        assert p.read_bytes()==source.read_bytes()
        outputs[str(p.relative_to(HERE))]=dict(sha256=digest(p),bytes=p.stat().st_size)
with (HERE/'complete-record-checks.json').open('x') as stream:json.dump(dict(passed=True,checks=checks,count=len(checks)),stream,indent=2);stream.write('\n')
archive=HERE/'paa-dated-book-bundle.tar.gz';names=sorted([*info['source_lock'],str(unit/'source-lock.json')])
with tarfile.open(archive,'x:gz') as stream:
    for name in names:stream.add(stage/name,arcname=name,recursive=False)
with tarfile.open(archive,'r:gz') as stream:
    members=stream.getmembers();assert len(members)==len(names) and {m.name for m in members}==set(names)
    for member in members:
        assert member.isfile()
        expected_hash=info['source_lock'].get(member.name,info['source_lock_sha256'])
        assert sha256(stream.extractfile(member).read()).hexdigest()==expected_hash,member.name
record=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),passed=True,inputs=len(names),
    cases=7,controls=21,native_checks=verification['checks'],complete_record_checks=len(checks),
    source_lock_sha256=info['source_lock_sha256'],authored_expectations_sha256=info['expected_sha256'],
    original_and_staged_inputs_verified=True,outputs=outputs,archive_members_verified=True,
    archive=dict(path=archive.name,sha256=digest(archive),bytes=archive.stat().st_size,members=len(members)),
    command=read(run_dir/'run-manifest.json')['command'],wall_seconds=read(run_dir/'run-manifest.json')['wall_seconds'],
    full_release_closure=False,actual_accounting_admission=False)
with (HERE/'preservation.json').open('x') as stream:json.dump(record,stream,indent=2);stream.write('\n')
print(json.dumps({k:record[k] for k in ['passed','cases','controls','native_checks','complete_record_checks','archive']}))
