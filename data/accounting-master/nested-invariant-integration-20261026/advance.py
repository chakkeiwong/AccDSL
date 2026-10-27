"""Advance reviewed candidate only while all current control hashes still match."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,re,subprocess,sys
import integrate as m
HERE=m.HERE;ROOT=m.ROOT
v=m.read(HERE/'verification.json');assert v['version']=='5.14' and v['pages']==744
assert v['passed_preservation'] and not v['new_warnings'] and not v['out_of_page_text_blocks']
assert m.sha(ROOT/v['pdf'])==v['pdf_sha256']
assert (HERE/'review.md').exists() and (HERE/'result.md').exists()
preservation=m.read(HERE/'source-preservation.json')
for name,h in preservation['sources'].items():
    assert m.sha(m.SOURCE/name)==h and (m.TARGET/name).read_text()==m.expected(name,(m.SOURCE/name).read_text()),name
assert m.sha(m.TARGET/m.NEW)==preservation['added_source_sha256']
for name,h in preservation['evidence'].items():assert m.sha(ROOT/name)==h,name
assert m.sha(ROOT/'docs/AccDSL-latest.pdf')==m.BASE
assert m.sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==m.STANDALONE
expected=m.read(HERE/'control-input-hashes.json');before={n:(ROOT/n).read_bytes() for n in expected}
for n,h in expected.items():assert sha256(before[n]).hexdigest()==h,'concurrent_control_change:'+n
backup=HERE/'control-before';assert not backup.exists(),'already_advanced'
plan='docs/plans/accounting-term-structural-admission-20261026.md'
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
literature='data/accounting-master/literature-closure-20261026/remaining-work.md'
note=f'''## Current governing candidate — Version 5.14 — 26 October 2026

Version 5.14 is the 744-page governing design candidate, not_ready. Nested
projection/query, guarded binding, per-parent/per-child templates and event
membership now compose into six explicit term-state semantic checks. The
bundle passes 51 complete comparisons/36 controls/576 assertions with 106
protected dependencies; 22 retained states pass and 27 semantic corruptions
reject. Native financial callbacks are disabled during candidate comparisons.
A separate structural-scope discriminator preserves the admission boundary.
All 234 predecessor manuscript sources survive under three named edits and
one new subsection A.54.21. All 26 simulation chapters and standalone literature
Version 5.12 (183 total/165 body pages) remain unchanged. No new warnings;
cover, physical 279 and 705–710 inspected. All 53 obligations, six interactions
and 46 operations remain; no whole requirement closes. S1–S5 partial, S6 held,
E3 deferred. Independent and human acceptance remain pending.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Literature residuals: {literature}.
Next plan: {plan}.

'''
markdown=[n for n in expected if n.startswith('docs/plans/') or n in ('data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md')]
proposed={}
for n in markdown:
    first,rest=before[n].decode().split(chr(10),1)
    rest=re.sub(r'## Current governing candidate — Version ([^\n]+)',r'## Prior governing candidate — Version \1',rest)
    value=first+chr(10)*2+note+rest.lstrip(chr(10))
    lines=[]
    for line in value.splitlines():
        if line.startswith('Current question:'):line='Current question: which native structural/migration conditions must bind the checked semantic bundle?'
        elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
        elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
        lines.append(line)
    proposed[n]=chr(10).join(lines)+chr(10)
for n in ('data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json'):
    record=json.loads(before[n]);a=record.get('active_execution',record.get('active_execution_note'))
    a.update(active_work_plan=plan,latest_result=result,current_candidate='5.14;744 pages;not_ready',
      current_pdf=v['pdf'],current_pdf_sha256=v['pdf_sha256'],remaining_work=remaining,
      latest_internal_result='data/accounting-master/term-semantic-composition-20261026/result.md',literature_remaining_work=literature)
    if 'completed_increments' in a:a['completed_increments'].extend([
      'Nested templates:51 runs;120 full instances;29 controls;612 assertions',
      'Nested semantic declarations:83 runs;32 controls;706 assertions;36 native oracle cases',
      'Term semantic bundle:51 full comparisons;36 controls;576 assertions;50 native oracle cases',
      'Version5.14:744 pages;234 predecessor sources preserved;bounded rendered review;not_ready'])
    if 'latest_results' in a:a['latest_results'].extend([a['latest_internal_result'],result])
    a['next']=['Audit and declare native term-state structural/migration admission',
      'Add direct reviewed nested source authoring, then exact event/carry binding',
      'Preserve literature and wider source/domain gaps; S6 held; E3 deferred']
    proposed[n]=json.dumps(record,indent=2)+chr(10)
n='MISSION_CONTROL.md';value=before[n].decode()
assert 'Version 5.13 is the current 741-page' in value
value=value.replace('Version 5.13 is the current 741-page','Version 5.14 is the current 744-page',1)
value=re.sub(r'\[active plan\]\(docs/plans/[^)]+\) reassesses the next language dependency against existing history, population and fiscal work\.',
  '[active plan]('+plan+') binds the checked nested semantics to explicit native structural and migration conditions.',value,count=1)
marker='## Purpose';assert value.count(marker)==1
value=value.replace(marker,'The [nested semantic integration]('+result+') preserves prior sources and distinguishes semantic satisfaction from native structural admission.'+chr(10)*2+marker,1)
proposed[n]=value
n='docs/README.md';value=before[n].decode();assert '**Version 5.13, 741 pages**' in value
proposed[n]=value.replace('**Version 5.13, 741 pages**','**Version 5.14, 744 pages**',1)
n='docs/design/README.md';value=before[n].decode()
value=re.sub(r'(governing PDF\]\(\.\./AccDSL-latest.pdf\), Version )5\.\d+,',r'\g<1>5.14,',value,count=1)
value=value.replace('741 pages','744 pages',1);proposed[n]=value
proposed['data/accounting-master/recovery-current-20261026.md']='# Current recovery pointer'+chr(10)*2+note+'''All grouped-query, guarded composition, nested-template, event-membership and
term-semantic writers are complete and frozen. Do not rerun them. The governing
links now select Version5.14; standalone literature remains Version5.12.
Next: structural/migration admission audit, then direct source and event/carry
binding. No process is running. Keep all literature residuals and unrelated
work. The old 728-page Unicode candidate was never advanced. The first5.14
layout candidate is archived under nested-invariant-integration-20261026/attempt-01.
'''
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in m.read(scope)['groups'].items()};assert counts==dict(obligations=53,interactions=6,operations=46)
for n,b in before.items():
    q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
for n,b in before.items():assert (ROOT/n).read_bytes()==b,'concurrent_control_change:'+n
for n,value in proposed.items():(ROOT/n).write_text(value)
links=[]
for suffix in ('pdf','tex'):
    path=ROOT/('docs/AccDSL-latest.'+suffix);target=m.TARGET/('accounting-product-proposal.'+suffix)
    old=os.readlink(path);temporary=path.with_name(path.name+'.next')
    assert not temporary.exists() and not temporary.is_symlink()
    relative=os.path.relpath(target,path.parent);os.symlink(relative,temporary);os.replace(temporary,path)
    links.append(dict(path=str(path.relative_to(ROOT)),before_target=old,after_target=relative,sha256=m.sha(path)))
controls=markdown+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json'];assert len(controls)==10
for n in controls:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text()
assert m.sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==m.STANDALONE
m.dump('control-refresh.json',dict(updated_files={n:dict(before=sha256(before[n]).hexdigest(),after=m.sha(ROOT/n)) for n in proposed},
  links=links,ten_controls_agree=True,original_scope=counts,whole_requirements_closed=0,standalone_unchanged=True,next_plan=plan))
build=m.read(HERE/'build.json');git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
m.dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
  commands=['integrate.py prepare','integrate.py build','integrate.py verify','repair_layout.py','integrate.py build','integrate.py verify','advance.py'],
  environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=build['wall_seconds'],
  wall_time_scope='Corrected manuscript build',data_version=m.sha(scope),plan_file='docs/plans/accounting-nested-invariant-integration-20261026.md',
  result_file=result,artifact_paths=['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate='5.14',pages=744,controls=10,main_links=2,standalone_unchanged=True,next_plan=plan)))
