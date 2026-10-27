"""One-shot local import of reviewed proposal evidence; never resumes the master."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
import fcntl
import hashlib
import json
import os
import platform
import shutil
import time

SOURCE = Path('/tmp/accdsl-independent-work-20261005')
ROOT = Path('/home/chakwong/python/AccDSL')
MASTER = ROOT/'data/accounting-master'
DEST = ROOT/'docs/design/proposal/methods/preparation-20261005-v1'
STAGE = DEST.with_name(DEST.name+'.importing')
RECEIPT = MASTER/'independent-preparation-20261005-v1'
SUPPLEMENT = ROOT/'docs/plans/accounting-independent-preparation-20261005.md'
CHECKPOINT = ROOT/'docs/plans/accounting-master-checkpoint.md'
STARTED = time.monotonic()


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def write_json(path, data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def atomic_text(path, text):
    temporary = path.with_name(path.name+'.packet-import-tmp')
    if temporary.exists():
        raise RuntimeError('Refusing existing temporary path: '+str(temporary))
    try:
        with temporary.open('x') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        if temporary.exists():
            temporary.unlink()


def assert_hashes(base, expected):
    errors=[]
    for rel, value in expected.items():
        path=base/rel
        if not path.is_file() or path.is_symlink() or digest(path)!=value:
            errors.append(rel)
    if errors:
        raise RuntimeError('Hash preservation failed: '+json.dumps(errors))


protection=read(MASTER/'partial-review-handoff-20261005/baseline.json')
protected_sets={'protected':protection['protected'],'external':protection['external_sources'],
                **protection['accepted']}
packet_manifests=['01-accounting/artifact-manifest.json','02-authority/MANIFEST.json',
                  '03-adapters/manifest.json','04-annotation/artifact-manifest.json']
for name in packet_manifests:
    path=SOURCE/name
    assert_hashes(path.parent,{f['path']:f['sha256'] for f in read(path)['files']})

cross=read(SOURCE/'03-adapters/annotation-cross-review.json')
for rel, h in cross['input_hashes'].items():
    path=Path(rel) if Path(rel).is_absolute() else SOURCE/'04-annotation'/rel
    if not path.is_file() or digest(path)!=h:
        raise RuntimeError('Annotation cross-review input changed: '+str(path))

a=read(SOURCE/'01-accounting/arithmetic-report.json')
b=read(SOURCE/'02-authority/arithmetic-and-source-check.json')
c=read(SOURCE/'03-adapters/checks/verification.json')
d=read(SOURCE/'04-annotation/verification.json')
assert a['status']=='PASS' and a['checks']==559 and a['negative_controls_detected']==5
assert b['status']=='passed' and b['check_count']==200
assert all(x['rejected'] for x in b['negative_controls'])
assert c['status']=='pass_bounded_source_and_specification_checks' and c['check_count']==202
assert d['status']=='pass_bounded_checks' and d['labels']==31 and d['amount_labels']==12

include=[]
for folder in ['01-accounting','02-authority','03-adapters','04-annotation','reference-snapshot']:
    for path in sorted((SOURCE/folder).rglob('*')):
        if path.is_symlink():
            raise RuntimeError('Symlink not allowed in packet: '+str(path))
        if path.is_file():
            include.append(str(path.relative_to(SOURCE)))
include += ['WORK_PACKETS.md','EXECUTION_PLAN.md','manifest.json',
            'supervisor/README.md','supervisor/REVIEW.md','supervisor/IMPORT_PLAN.md',
            'supervisor/candidate-inputs.json','supervisor/import_reviewed_packets.py']
inventory={rel:digest(SOURCE/rel) for rel in sorted(include)}
controls=['campaign.json','active-process.json','controller-review.json','state.json',
          'next-plan.json','next-plan.md']
control_hashes={name:digest(MASTER/name) for name in controls}
initial_state=read(MASTER/'state.json')

with ExitStack() as stack:
    for name in ['campaign.lock','runner.lock']:
        handle=stack.enter_context((MASTER/name).open('r+'))
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    campaign=read(MASTER/'campaign.json')
    active=read(MASTER/'active-process.json')
    if campaign['status']!='continuation_veto' or campaign.get('supervisor') is not None:
        raise RuntimeError('Campaign ownership/state changed; keep packets isolated')
    if active['status']!='finished' or active.get('survivors'):
        raise RuntimeError('Worker no longer safely finished')
    if read(MASTER/'controller-review.json')['verdict']!='REVISE':
        raise RuntimeError('Controller review changed; re-audit import')
    assert campaign['deadline_monotonic']==1940875.230219879
    assert campaign['deadline_utc']=='2026-10-06T16:29:46.450619+00:00'
    assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==campaign['boot_id']
    assert time.monotonic()<campaign['deadline_monotonic']
    identity=active['identity']
    for proc in Path('/proc').iterdir():
        if not proc.name.isdecimal():
            continue
        try:
            raw=(proc/'stat').read_text()
            fields=raw[raw.rfind(')')+2:].split()
            if int(fields[2])==identity['pgid'] and fields[0] not in {'Z','X'}:
                raise RuntimeError('Prior master worker group still live: '+proc.name)
            tokens=(proc/'cmdline').read_bytes().split(b'\0')
            if any(token.rsplit(b'/',1)[-1] in {b'run_accounting_master.py',b'accounting_master_worker.py'} for token in tokens):
                raise RuntimeError('Master process exists: '+proc.name)
        except (FileNotFoundError, ProcessLookupError):
            continue
    assert_hashes(MASTER,control_hashes)
    for values in protected_sets.values():
        assert_hashes(ROOT,values)
    assert_hashes(SOURCE,inventory)
    for path in [DEST,STAGE,RECEIPT,SUPPLEMENT]:
        if path.exists():
            raise RuntimeError('Refusing to overwrite existing import path: '+str(path))
    RECEIPT.mkdir()
    before=RECEIPT/'before'
    before.mkdir()
    for name in controls:
        shutil.copy2(MASTER/name,before/name)
    shutil.copy2(CHECKPOINT,before/'accounting-master-checkpoint.md')
    write_json(RECEIPT/'import-status.json',{'status':'in_progress','acceptance':False,
               'destination':str(DEST.relative_to(ROOT))})
    STAGE.mkdir()
    for rel in inventory:
        dst=STAGE/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(SOURCE/rel,dst)
    assert_hashes(STAGE,inventory)
    assert_hashes(SOURCE,inventory)
    write_json(STAGE/'import-manifest.json',{'status':'reviewed_candidate_preparation',
        'phase_acceptance':False,'source_workspace':str(SOURCE),'files':inventory,
        'review':'supervisor/REVIEW.md','registry':'supervisor/candidate-inputs.json'})
    os.rename(STAGE,DEST)
    supplement=(SOURCE/'supervisor/requirements-supplement.md').read_text()
    atomic_text(SUPPLEMENT,supplement)
    old=CHECKPOINT.read_text()
    header='''
## Current status — 5 October, isolated preparation imported

The four authorized work packets are complete and reviewed as **candidate P16/P17
inputs**: lease/tax methods, matched accounting authority, filing-adapter source
audit, and 31 provisional located annotations across four reports. See the
[packet index](../design/proposal/methods/preparation-20261005-v1/supervisor/README.md)
and [requirement evidence supplement](accounting-independent-preparation-20261005.md).
The governing proposal remains incomplete; no phase or whole requirement was accepted.

**The master is stopped**, after controller review `REVISE` in run
`20261005T005619-5a850819`. The latest controller findings remain unresolved;
the campaign's generic reason string is stale. P15 remains accepted internally,
P16 needs review/completion, and P17–P19 are pending. Repair the controller before
any restart, then finish P16 and integrate these candidates. This import did not
resume the campaign or reset its original 48-hour deadline.

The stopped import held campaign then runner locks and verified original source,
corpus and accepted-evidence hashes. Its receipt and preserved prior state are in
`data/accounting-master/independent-preparation-20261005-v1/`. Current ASC/official
ASBE authority, actual contract/tax-law support, full method coverage, runtime
adapter evaluation and adjudicated annotation remain open. Product implementation
remains disabled. Earlier checkpoint sections below are historical.

'''
    assert old.startswith('# Accounting master checkpoint\n')
    atomic_text(CHECKPOINT,old.replace('# Accounting master checkpoint\n',
                                     '# Accounting master checkpoint\n'+header,1))
    for values in protected_sets.values():
        assert_hashes(ROOT,values)
    assert_hashes(MASTER,control_hashes)
    assert_hashes(DEST,inventory)
    assert read(MASTER/'state.json')==initial_state
    result={'status':'imported_reviewed_candidates','recorded_at':datetime.now(timezone.utc).isoformat(),
        'phase_acceptance':False,'product_implementation_enabled':False,
        'campaign_status_unchanged':campaign['status'],'controller_verdict_unchanged':'REVISE',
        'original_deadline_utc':campaign['deadline_utc'],
        'original_deadline_monotonic':campaign['deadline_monotonic'],
        'remaining_hours_at_import':round((campaign['deadline_monotonic']-time.monotonic())/3600,3),
        'locks':['campaign.lock','runner.lock'],'destination':str(DEST.relative_to(ROOT)),
        'files_copied':len(inventory),'copied_bytes':sum((DEST/r).stat().st_size for r in inventory),
        'preservation_checks':sum(map(len,protected_sets.values())),
        'control_hashes_unchanged':control_hashes,'packet_manifest_sha256':digest(DEST/'import-manifest.json'),
        'documents_updated':{str(p.relative_to(ROOT)):digest(p) for p in [CHECKPOINT,SUPPLEMENT]},
        'command':'python3 /tmp/accdsl-independent-work-20261005/supervisor/import_reviewed_packets.py',
        'environment':platform.python_version(),'wall_seconds':time.monotonic()-STARTED,
        'plan':'docs/design/proposal/methods/preparation-20261005-v1/supervisor/IMPORT_PLAN.md',
        'result':'docs/plans/accounting-independent-preparation-20261005.md'}
    write_json(RECEIPT/'receipt.json',result)
    write_json(RECEIPT/'import-status.json',{'status':'complete','acceptance':False,
                                         'receipt':'receipt.json'})
    print(json.dumps({k:result[k] for k in ['status','files_copied','preservation_checks',
                     'remaining_hours_at_import','campaign_status_unchanged']}))
