"""One-shot advancement of the preserved, visually reviewed 5.15 candidate."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json, os, re, sys
import integrate as m

HERE, ROOT = m.HERE, m.ROOT
v = m.read(HERE/'verification.json')
assert v['version']=='5.15' and v['pages']==747
assert v['passed_preservation'] and not v['new_warnings'] and not v['out_of_page_text_blocks']
assert m.sha(ROOT/v['pdf'])==v['pdf_sha256']
for n in ('review.md','result.md','remaining-work.md'):
    assert (HERE/n).is_file()
p=m.read(HERE/'source-preservation.json')
for n,h in p['sources'].items():
    assert m.sha(m.SOURCE/n)==h, n
    assert (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text()), n
assert m.sha(m.TARGET/m.NEW)==p['added_source_sha256']
for n,h in p['evidence'].items():
    assert m.sha(ROOT/n)==h, n
assert m.sha(ROOT/'docs/AccDSL-latest.pdf')==m.BASE
assert m.sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==m.STANDALONE
expected=m.read(HERE/'control-input-hashes.json')
before={n:(ROOT/n).read_bytes() for n in expected}
for n,h in expected.items():
    assert sha256(before[n]).hexdigest()==h, 'concurrent_control_change:'+n
backup=HERE/'control-before'
assert not backup.exists() and not (HERE/'control-refresh.json').exists(), 'already_advanced'
plan='docs/plans/accounting-financing-opening-invariants-20261026.md'
assert (ROOT/plan).is_file()
result=str((HERE/'result.md').relative_to(ROOT))
remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
gap='data/accounting-master/gap-program-20261026/remaining-work.md'
literature='data/accounting-master/literature-closure-20261026/remaining-work.md'
note=f'''## Current governing candidate — Version 5.15 — 26 October 2026

Version 5.15 is the 747-page governing design candidate, not_ready. The selected
term-state contract, explicit nested source, nested construction and complete
amendment/assessment/collection/carry continuation are integrated in A.54.22.
The source-driven successor passes 20 complete comparisons in two continuous
synthetic traces, nine controls and 1,018 assertions. Its 562 Unicode span
checks preserve direct source evidence. Native financial callbacks are disabled.
All 235 predecessor sources survive under four named edits; 233 evidence files
remain protected. No new warnings or clipped text remain after the archived
layout repair. Physical pages 1, 279 and 708–713 received bounded author review.
Standalone literature Version 5.12 (183 total/165 body pages) is unchanged.
All 53 obligations, six interactions, 46 operations and 18 broad packages remain.
S1–S5 partial; S6 held; E3 forecasting deferred. No whole requirement closes.
Independent reader, whole-document and domain acceptance remain pending.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.
Full gap queue: {gap}.
Literature residuals: {literature}.
E01/E02/E03 retain their separate companion/manuscript-integration scope.

'''
markdown=[n for n in expected if n.startswith('docs/plans/') or n in
          ('MISSION_CONTROL.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md')]
proposed={}
for n in markdown:
    first,rest=before[n].decode().split(chr(10),1)
    rest=re.sub(r'\n## Current internal work — 26 October 2026\n.*?(?=\n## )','',rest,count=1,flags=re.S)
    rest=rest.replace('## Reconciled execution checkpoint — 26 October 2026',
                      '## Earlier reconciled execution checkpoint — 26 October 2026',1)
    rest=rest.replace('## Current governing candidate — Version 5.14',
                      '## Prior governing candidate — Version 5.14')
    value=first+chr(10)*2+note+rest.lstrip(chr(10))
    value=value.replace('Status: active mission; Version 5.14 is the current 744-page design candidate.',
                        'Status: active mission; Version 5.15 is the current 747-page design candidate.')
    lines=[]
    for line in value.splitlines():
        if line.startswith('Current question:'):
            line='Current question: which financing claim/share/history invariants and opening premises are required by E01?'
        elif line.startswith('Next action:'):
            line='Next action: execute '+plan+'.'
        elif line.startswith('Current residuals:'):
            line='Current residuals: '+remaining+'.'
        lines.append(line)
    proposed[n]=chr(10).join(lines)+chr(10)
completed=['nested-contract-source','nested-assessment-construction','term-event-carry-binding',
           'term-full-event-binding','term-event-source','term-execution-integration']
for n,key in [('scripts/accounting_master_catalog.json','active_execution_note'),
              ('data/accounting-master/next-plan.json','active_execution')]:
    record=json.loads(before[n]); a=record[key]
    a.update(active_work_plan=plan,latest_result=result,current_candidate='5.15;747 pages;not_ready',
        current_pdf=v['pdf'],current_pdf_sha256=v['pdf_sha256'],remaining_work=remaining,
        latest_internal_result='data/accounting-master/term-event-source-20261026/result.md',
        full_gap_remaining_work=gap,literature_remaining_work=literature,
        next=['W05: reusable financing claim/share/missed-history invariants and opening admission',
              'Bind E03 conditional remedies after the selected financing contract',
              'Continue full gap/literature queues; S6 held and E3 deferred'])
    if 'active_work_plans' in a:
        old=a['active_work_plans']
        retired={'docs/plans/accounting-nested-contract-source-20261026.md',
                 'docs/plans/accounting-nested-query-template-20261026.md'}
        a['active_work_plans']=[plan]+[x for x in old if x not in retired and x!=plan]
    if 'completed_increments' in a:
        for unit in completed:
            path='data/accounting-master/'+unit+'-20261026/result.md'
            if path not in a['completed_increments']:a['completed_increments'].append(path)
    proposed[n]=json.dumps(record,indent=2,ensure_ascii=False)+chr(10)
n='docs/README.md'
value=before[n].decode();assert '**Version 5.14, 744 pages**' in value
value=value.replace('**Version 5.14, 744 pages**','**Version 5.15, 747 pages**',1)
value=value.replace('[Current integration and checks](../data/accounting-master/literature-closure-20261026/result.md)',
                    '[Current integration and checks](../'+result+')',1)
proposed[n]=value
n='docs/design/README.md';value=before[n].decode();assert 'Version 5.14,' in value
proposed[n]=value.replace('Version 5.14,','Version 5.15,',1)
proposed['data/accounting-master/recovery-current-20261026.md']='# Current recovery pointer'+chr(10)*2+note+'''All six selected term-structure/source/construction/event writers are complete
and frozen. Do not rerun successful verification, prepare, repair or advancement
writers. Version 5.15 is selected by the stable PDF and TeX links. Next execute
the W05 financing-opening plan from the existing E01 evidence. No process is
running. Preserve full gap-program, literature and unrelated work. The first
5.15 layout candidate is archived under term-execution-integration-20261026/attempt-01.
'''
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in m.read(scope)['groups'].items()}
assert counts==dict(obligations=53,interactions=6,operations=46)
assert set(proposed)==set(expected)
links=[]
for suffix in ('pdf','tex'):
    path=ROOT/('docs/AccDSL-latest.'+suffix)
    assert path.is_symlink()
    target=m.TARGET/('accounting-product-proposal.'+suffix)
    links.append(dict(path=str(path.relative_to(ROOT)),before_target=os.readlink(path),
                      after_target=os.path.relpath(target,path.parent)))
for n,b in before.items():
    q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
for n,b in before.items():assert (ROOT/n).read_bytes()==b, 'concurrent_control_change:'+n
for n,value in proposed.items():(ROOT/n).write_text(value)
for link in links:
    path=ROOT/link['path'];temporary=path.with_name(path.name+'.next')
    assert not temporary.exists() and not temporary.is_symlink()
    os.symlink(link['after_target'],temporary);os.replace(temporary,path)
    link['sha256']=m.sha(path)
assert m.sha(ROOT/'docs/AccDSL-latest.pdf')==v['pdf_sha256']
assert m.sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==m.STANDALONE
controls=[n for n in expected if n.startswith('docs/plans/') or n in
 ('data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
  'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json')]
assert len(controls)==10
for n in controls:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text()
m.dump('control-refresh.json',dict(updated_files={n:dict(before=sha256(before[n]).hexdigest(),after=m.sha(ROOT/n)) for n in proposed},
 links=links,ten_controls_agree=True,original_scope=counts,whole_requirements_closed=0,
 standalone_unchanged=True,next_plan=plan))
build=m.read(HERE/'build.json')
m.dump('run-manifest.json',dict(git_commit='unavailable: existing .git marker is not a usable repository; no initialization',
 commands=['integrate.py prepare','integrate.py build','integrate.py verify','repair_layout.py',
           'integrate.py build','integrate.py verify','advance.py'],environment=sys.version,
 cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=build['wall_seconds'],
 wall_time_scope='corrected manuscript build',data_version=m.sha(scope),
 plan_file='docs/plans/accounting-term-execution-integration-20261026.md',result_file=result,
 artifact_paths=['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],
 timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate='5.15',pages=747,updated_files=len(proposed),controls=10,
                     main_links=2,standalone_unchanged=True,next_plan=plan)))
