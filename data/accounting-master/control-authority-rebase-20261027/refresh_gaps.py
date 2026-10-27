"""Add scoped finance evidence without rewriting the frozen programme."""
from pathlib import Path
from hashlib import sha256
import copy, json
H=Path(__file__).resolve().parent;R=H.parents[2]
D=H/'edition-date-repair-02';G=H.parent/'gap-control-history-refresh-20261027'
def j(p):return json.loads(p.read_text())
def digest(p):return sha256(p.read_bytes()).hexdigest()
assert j(D/'verification.json')['status']=='PASS'
assert (H/'author-review.md').exists() and (H/'result.md').exists()
a=j(R/'scripts/accounting_master_catalog.json')['active_execution_note']
assert a['current_candidate'].startswith('5.25;')
OLD=(R/a['full_gap_program']).parent
assert OLD.name=='gap-source-policy-refresh-20261027'
G.mkdir(exist_ok=False)
def save(n,x):(G/n).write_text(json.dumps(x,indent=2)+'\n')
lock={str(p.relative_to(R)):digest(p) for p in OLD.iterdir() if p.is_file()}
save('predecessor-lock.json',lock)
audit=j(OLD/'audit-status.json');original=copy.deepcopy(audit)
audit['predecessor']=str(OLD.relative_to(R))
audit['baseline']='Version 5.26 preserves 5.25 source policies and adds funding/measurement distinctions and conditional whole-interval control history.'
items=[('Conditional actor-specific whole-interval control history','control-history-contract-20261026/result.md','22 cases,14 controls,214 assertions; exact half-open partitions and actor revisions retain gaps, conflicts and unknown availability. Conditional source coverage is not actual control or reporting admission.'),('Protected finance and control-history integration','control-authority-rebase-20261027/result.md','Both 5.26 editions preserve the live source-policy baseline and the earlier rejected/stale candidates. Funding feasibility, measurement and interval evidence are distinct. Independent reader/domain acceptance remains pending.')]
for title,path,scope in items:
    p=H.parent/path
    audit['successor_deltas'].append(dict(id='D'+str(len(audit['successor_deltas'])+1),title=title,requirements=['MC05','MC17','MC19','MC20','MC24','MC25','MC28','MC30','MC31','MC32','MC33','MC34','MC35','W01','W05','W06','W07','W08','W11','W12','W16','W17'],evidence=str(p.relative_to(R)),sha256=digest(p),current_disposition=scope))
save('audit-status.json',audit)
fail=j(OLD/'failure-register.json');oldfail=copy.deepcopy(fail)
for failure,case in [('Matching control endpoints are treated as uninterrupted control','Partition supplied whole-interval evidence; retain unresolved gaps and intervening gain/loss alternatives.'),('Complete conditional coverage is treated as source truth or permission to consolidate','Carry source, actor and interval identity separately; all source/accounting/posting admission flags remain false.')]:
    fail['cross_interface'].append(dict(id='X'+str(len(fail['cross_interface'])+1),failure=failure,closure_packages=['W05','W06','W08','W12','W16'],discriminating_case=case,status='Selected interval cases pass; group-method binding and real admission remain open',evidence='data/accounting-master/control-history-contract-20261026/result.md'))
save('failure-register.json',fail)
packages=j(OLD/'closure-packages.json');oldpackages=copy.deepcopy(packages)
for row in packages['packages']:
    ident=row['id']
    if ident in ['W01','W05','W06','W08','W11','W12','W16']:
        row['existing_support']+=' Conditional whole-interval control assertions now preserve exact boundaries, actor revisions and unresolved coverage in22 cases; no admission follows.'
    if ident in ['W05','W06']:
        row['next_action']='Bind the checked interval history to group-reporting scope under accounting-control-group-boundary-20261027.md; then complete dated authority, acquisition measurement and missing financing methods.'
    if ident=='W08':
        row['next_action']='Check control-history correspondence at the current stable/full-ownership report boundary; specify acquisition-period continuation with NCI, prior interests and intragroup eliminations under dated authority.'
    if ident=='W17':
        row['existing_support']+=' Version5.26 integrates the funding/measurement and interval-history arguments while preserving the5.25 source-policy edition.'
        row['next_action']='Integrate subsequent group-boundary, dated-authority and source-clock results; continue whole-document coherence and independent reader/domain acceptance.'
    assert row['status']=='open'
save('closure-packages.json',packages)
text='# Full closure program after control-history integration\n\n27 October2026. All18 broad packages remain open. No conditional source result establishes actual accounting admission.\n'
for row in packages['packages']:
    text+='\n## '+row['id']+' — '+row['title']+'\n\n'
    for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
        value=row[key];text+=label+': '+(', '.join(value) or 'none' if isinstance(value,list) else value)+'\n\n'
(G/'closure-program.md').write_text(text)
(G/'remaining-work.md').write_text('# Complete remaining-work queue\n\nThe interval-history companion is checked and integrated. Group-method binding, dated acquisition authority and measurement remain open. Source-time/private-access work continues independently.\n\n'+'\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in packages['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred. All53 obligations, six interactions,46 operations and18 packages remain open. No global continuation veto has fired.\n')
(G/'plan-review.md').write_text('Audit passes: the current5.25 source-policy edition, not stale5.24, is preserved. Whole-interval assertions remain conditional; complete coverage does not authenticate sources or admit journals. Counts and builds do not establish scientific or human acceptance. Keep the independent source-time plan and all inherited obligations.\n')
assert audit['groups']==original['groups'] and audit['literature']==original['literature']
assert audit['successor_deltas'][:-2]==original['successor_deltas']
assert all(fail[k]==oldfail[k] for k in ['original','literature_extensions'])
assert fail['cross_interface'][:-2]==oldfail['cross_interface']
for row,old in zip(packages['packages'],oldpackages['packages']):
    assert all(row[k]==v for k,v in old.items() if k not in ['existing_support','next_action'])
for p,h in lock.items():assert digest(R/p)==h
counts=dict(j(OLD/'verification.json')['counts'])
counts.update(successor_deltas=len(audit['successor_deltas']),cross_interface_challenges=len(fail['cross_interface']))
save('verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
(G/'result.md').write_text('# Full-program control-history refresh\n\n27 October2026. All original obligations, interactions, operations, literature gaps and failures remain. Two scoped deltas and two interface challenges credit the interval reference and protected integration. All18 packages stay open; the next financing unit binds conditional history to the existing group-reporting boundary.\n')
print(json.dumps(dict(status='PASS',counts=counts,predecessor_files=len(lock))))
