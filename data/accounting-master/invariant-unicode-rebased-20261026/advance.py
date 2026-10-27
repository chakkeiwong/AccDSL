"""Reconcile current controls without overwriting concurrent literature work."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,os,re,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
v=read(HERE/'verification.json');assert v['version']=='5.13' and v['pages']==741
assert v['passed_preservation'] and not v['new_warnings'] and not v['out_of_page_text_blocks']
assert sha(ROOT/v['pdf'])==v['pdf_sha256']
assert (HERE/'result.md').exists() and (HERE/'review.md').exists()
spec=importlib.util.spec_from_file_location('rebase',HERE/'integrate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=read(HERE/'source-preservation.json')
for n,h in p['sources'].items():
    assert sha(m.SOURCE/n)==h and (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text()),n
for n,h in p['evidence'].items():assert sha(ROOT/n)==h,n
assert sha(ROOT/'docs/AccDSL-latest.pdf')==p['source_pdf_sha256']
standalone='63bad80014136b6fa6e3cf1c984aa11df797fd33ac66ea56fb7ddbe7451846d5'
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==standalone
expected=read(HERE/'control-input-hashes.json')
before={n:(ROOT/n).read_bytes() for n in expected}
for n,h in expected.items():assert sha256(before[n]).hexdigest()==h,'concurrent_control_change:'+n
backup=HERE/'control-before';assert not backup.exists()
plan='docs/plans/accounting-nested-term-invariant-audit-20261026.md'
result=str((HERE/'result.md').relative_to(ROOT))
remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
literature='data/accounting-master/literature-closure-20261026/remaining-work.md'
note=f'''## Current governing candidate — Version 5.13 — 26 October 2026

Version 5.13 is the 741-page governing design candidate, not_ready. It preserves
the concurrent literature Version 5.12 and adds the nested-invariant Unicode
correction. Eight full programs/54 commands and 32 prior controls remain exact;
nine additional cases reproduce and repair the defect. The repair passes
41 controls/2,782 assertions and protects 584 files. All 234 predecessor
manuscript sources are preserved under three named edits. All literature
insertions, bibliography additions and 26 simulation chapters remain exact.
Standalone Version 5.12 stays at 183 pages/165 body pages. No new warnings;
cover and pages 703–707 inspected. All 53 obligations, six interactions and
46 operations remain; no whole requirement closes. S1–S5 partial, S6 held,
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
    first,rest=before[n].decode().split('\n',1)
    rest=re.sub(r'## Current governing candidate — Version ([^\n]+)',r'## Prior governing candidate — Version \1',rest)
    value=first+'\n\n'+note+rest.lstrip('\n')
    lines=[]
    for line in value.splitlines():
        if line.startswith('Current question:'):line='Current question: which nested claim-term and assessment relationships lack explicit declarative invariant support?'
        elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
        elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
        lines.append(line)
    proposed[n]='\n'.join(lines)+'\n'
for n in ('data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json'):
    d=json.loads(before[n]);a=d.get('active_execution',d.get('active_execution_note'))
    a.update(active_work_plan=plan,latest_result=result,current_candidate='5.13;741 pages;not_ready',
      current_pdf=v['pdf'],current_pdf_sha256=v['pdf_sha256'],remaining_work=remaining,
      latest_internal_result='data/accounting-master/invariant-unicode-repair-20261026/result.md',
      standalone_pdf='docs/design/proposal/manuscript-literature-methods-v512-20261026/simulation-foundations.pdf',
      standalone_pdf_sha256=standalone,literature_result='data/accounting-master/literature-closure-20261026/result.md',
      literature_remaining_work=literature)
    if 'completed_increments' in a:a['completed_increments'].extend(['Concurrent literature Version5.12 preserved:741-page main;183-page standalone','Version5.13:quoted Unicode invariant repair;all8 programs/54 commands and32 prior controls exact;9 reproduced defects'])
    if 'latest_results' in a:a['latest_results'].extend([a['literature_result'],a['latest_internal_result'],result])
    a['next']=['Audit nested term/assessment invariants against existing declarative primitives','Plan missing general bindings before replacing native term validation','Preserve current literature residuals, broader language/source/domain gaps; S6 held; E3 deferred']
    proposed[n]=json.dumps(d,indent=2)+'\n'
n='MISSION_CONTROL.md';value=before[n].decode()
assert 'Version 5.12 is the current 741-page' in value
value=value.replace('Version 5.12 is the current 741-page','Version 5.13 is the current 741-page',1)
value=value.replace('docs/plans/accounting-post-opening-language-reassessment-20261026.md',plan,1)
marker='## Purpose';assert value.count(marker)==1
value=value.replace(marker,f'The [current combined integration]({result}) preserves those literature changes and corrects nested-invariant Unicode source handling.\n\n'+marker,1)
proposed[n]=value
n='docs/README.md';value=before[n].decode();assert '**Version 5.12, 741 pages**' in value
proposed[n]=value.replace('**Version 5.12, 741 pages**','**Version 5.13, 741 pages**',1)
n='docs/design/README.md';value=before[n].decode()
value=re.sub(r'(governing PDF\]\(\.\./AccDSL-latest.pdf\), Version )5\.\d+,',r'\g<1>5.13,',value,count=1)
value=value.replace('155 body pages','165 body pages (183 total pages)',1)
proposed[n]=value
proposed['data/accounting-master/recovery-current-20261026.md']='# Current recovery pointer\n\n'+note+'''The complete-claims source and Unicode repair are frozen and integrated.
The concurrent literature work is preserved; its residual register remains
active. Next: nested term-invariant audit. Main links select Version 5.13;
standalone stays literature Version 5.12. No process is running. Do not rerun
completed writers. The local 728-page Unicode candidate was never advanced.
'''
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in read(scope)['groups'].items()};assert counts==dict(obligations=53,interactions=6,operations=46)
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
    links.append(dict(path=str(path.relative_to(ROOT)),before_target=old,after_target=relative,sha256=sha(path)))
controls=markdown+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
assert len(controls)==10
for n in controls:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text()
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==standalone
dump('control-refresh.json',dict(updated_files={n:dict(before=sha256(before[n]).hexdigest(),after=sha(ROOT/n)) for n in proposed},links=links,ten_controls_agree=True,original_scope=counts,whole_requirements_closed=0,standalone_unchanged=True,next_plan=plan))
build=read(HERE/'build.json');git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',commands=['configure.py','integrate.py prepare','integrate.py build','integrate.py verify','advance.py'],environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=build['wall_seconds'],wall_time_scope='Combined manuscript build',data_version=sha(scope),plan_file='docs/plans/accounting-invariant-unicode-integration-20261026.md',result_file=result,artifact_paths=['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate='5.13',pages=741,controls=10,main_links=2,literature_preserved=True,standalone_unchanged=True,next_plan=plan)))
