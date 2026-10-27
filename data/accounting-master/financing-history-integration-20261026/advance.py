"""One-shot reviewed 5.16 advancement with unchanged control/source guards."""
from datetime import datetime,timezone
from hashlib import sha256
import json,os,re,sys
import integrate as m
HERE,ROOT=m.HERE,m.ROOT
v=m.read(HERE/'verification.json');p=m.read(HERE/'source-preservation.json')
assert v['version']=='5.16' and v['pages']==750 and v['passed_preservation']
assert not v['new_warnings'] and not v['out_of_page_text_blocks']
assert m.sha(ROOT/v['pdf'])==v['pdf_sha256']
for n in ['review.md','result.md','remaining-work.md']:assert (HERE/n).is_file()
for n,h in p['sources'].items():
    assert m.sha(m.SOURCE/n)==h,n
    assert (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text()),n
assert m.sha(m.TARGET/m.NEW)==p['added_source_sha256']
for n,h in p['evidence'].items():assert m.sha(ROOT/n)==h,n
assert m.sha(ROOT/'docs/AccDSL-latest.pdf')==m.BASE
assert m.sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==m.STANDALONE
expected=m.read(HERE/'control-input-hashes.json')
before={n:(ROOT/n).read_bytes() for n in expected}
for n,h in expected.items():assert sha256(before[n]).hexdigest()==h,'concurrent_control_change:'+n
backup=HERE/'control-before';assert not backup.exists() and not (HERE/'control-refresh.json').exists(),'already_advanced'
plan='docs/plans/accounting-financing-carry-20261026.md';assert (ROOT/plan).is_file()
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
gap='data/accounting-master/gap-program-20261026/remaining-work.md'
literature='data/accounting-master/literature-closure-20261026/remaining-work.md'
note=f'''## Current governing candidate — Version 5.16 — 26 October 2026

Version 5.16 is the 750-page governing design candidate, not_ready. A.54.23
integrates selected financing claim/share/missed-payment history, opening and
transition conditions, conditional remedies and the repaired same-day stale
finding. E01 and the selected E03 continuation have a scoped explanation;
the broader source inventory and E02 supplement retain separate integration needs.
The financing unit passes 20 full comparisons/34 controls/283 assertions;
the repaired remedy unit passes 58 classifications/eight transitions/15 controls/
332 assertions. The rejected date-only result and its discriminator are preserved.
All 236 predecessor sources survive under three named edits; 89 evidence files
remain protected. No new warnings or clipped text; physical pages 1, 279 and
711–716 received bounded author review. Standalone literature Version 5.12
(183 total/165 body pages) remains unchanged. All 53 obligations, six interactions,
46 operations and 18 broad packages remain. S1–S5 partial; S6 held; E3 forecasting
deferred. No whole requirement closes. Independent reader and domain review remain
pending; they do not block feasible internal work.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.
Full gap queue: {gap}.
Literature residuals: {literature}.

'''
proposed={}
for n,b in before.items():
    if n.endswith('.json'):
        record=json.loads(b);key='active_execution_note' if n.startswith('scripts/') else 'active_execution';a=record[key]
        protected={k:json.loads(json.dumps(x)) for k,x in a.items() if k.startswith(('full_gap','gap_program','literature'))}
        previous=a['active_work_plan']
        a.update(active_work_plan=plan,latest_result=result,current_candidate='5.16;750 pages;not_ready',
          current_pdf=v['pdf'],current_pdf_sha256=v['pdf_sha256'],remaining_work=remaining,
          latest_internal_result='data/accounting-master/financing-remedy-state-binding-20261026/result.md',
          next=['W05: financing and conditional-memory fiscal carry, including unpaid claims',
                'Continue dated funding/rights and remaining source-integration gaps',
                'Continue full gap/literature queues; S6 held and E3 deferred'])
        if 'active_work_plans' in a:a['active_work_plans']=[plan]+[x for x in a['active_work_plans'] if x not in [previous,plan]]
        if 'completed_increments' in a:
            for unit in ['financing-opening-invariants','financing-remedy-binding','financing-remedy-state-binding','financing-history-integration']:
                path='data/accounting-master/'+unit+'-20261026/result.md'
                if path not in a['completed_increments']:a['completed_increments'].append(path)
        assert all(a[k]==x for k,x in protected.items())
        proposed[n]=json.dumps(record,indent=2,ensure_ascii=False)+chr(10)
    elif n=='docs/README.md':
        s=b.decode();assert '**Version 5.15, 747 pages**' in s
        s=s.replace('**Version 5.15, 747 pages**','**Version 5.16, 750 pages**',1)
        s=s.replace('[Current integration and checks](../data/accounting-master/term-execution-integration-20261026/result.md)',
                    '[Current integration and checks](../'+result+')',1);proposed[n]=s
    elif n=='docs/design/README.md':
        s=b.decode();assert 'Version 5.15,' in s;proposed[n]=s.replace('Version 5.15,','Version 5.16,',1)
    elif n.endswith('recovery-current-20261026.md'):
        proposed[n]='# Current recovery pointer'+chr(10)*2+note+'''The 5.16 integration and selected financing/remedy checks are complete and frozen.
Do not rerun successful writers. Stable PDF and TeX links now select Version 5.16.
No process is running. Continue the audited financing-carry plan. Preserve the
date-only failure, original gap/literature results and all unrelated work.
'''
    else:
        first,rest=b.decode().split(chr(10),1)
        rest=rest.replace('## Current internal work — financing invariants —','## Prior internal work — financing invariants —',1)
        rest=rest.replace('## Current governing candidate — Version 5.15','## Prior governing candidate — Version 5.15')
        rest=rest.replace('Status: active mission; Version 5.15 is the current 747-page design candidate.',
                          'Status: active mission; Version 5.16 is the current 750-page design candidate.')
        s=first+chr(10)*2+note+rest.lstrip(chr(10));lines=[]
        for line in s.splitlines():
            if line.startswith('Current question:'):line='Current question: which financing/history and conditional-memory rules must bind fiscal carry?'
            elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
            elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
            lines.append(line)
        proposed[n]=chr(10).join(lines)+chr(10)
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in m.read(scope)['groups'].items()}
assert counts==dict(obligations=53,interactions=6,operations=46)
assert set(proposed)==set(expected)
links=[]
for suffix in ('pdf','tex'):
    path=ROOT/('docs/AccDSL-latest.'+suffix);assert path.is_symlink()
    links.append(dict(path=str(path.relative_to(ROOT)),before_target=os.readlink(path),
      after_target=os.path.relpath(m.TARGET/('accounting-product-proposal.'+suffix),path.parent)))
for n,b in before.items():
    q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
for n,b in before.items():assert (ROOT/n).read_bytes()==b,'concurrent_control_change:'+n
for n,s in proposed.items():(ROOT/n).write_text(s)
for link in links:
    path=ROOT/link['path'];temp=path.with_name(path.name+'.next');assert not temp.exists() and not temp.is_symlink()
    os.symlink(link['after_target'],temp);os.replace(temp,path);link['sha256']=m.sha(path)
assert m.sha(ROOT/'docs/AccDSL-latest.pdf')==v['pdf_sha256']
assert m.sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==m.STANDALONE
controls=[n for n in expected if n.startswith('docs/plans/') or n in
 ['data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
  'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']]
assert len(controls)==10
for n in controls:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text()
m.dump('control-refresh.json',dict(updated_files={n:dict(before=sha256(before[n]).hexdigest(),after=m.sha(ROOT/n)) for n in proposed},
 links=links,ten_controls_agree=True,original_scope=counts,whole_requirements_closed=0,standalone_unchanged=True,next_plan=plan))
build=m.read(HERE/'build.json')
m.dump('run-manifest.json',dict(git_commit='unavailable: unusable repository marker; preserved unchanged',
 commands=['integrate.py prepare','integrate.py build','integrate.py verify','advance.py'],
 environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=build['wall_seconds'],
 wall_time_scope='manuscript build',data_version=m.sha(scope),plan_file='docs/plans/accounting-financing-history-integration-20261026.md',
 result_file=result,artifact_paths=['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],
 timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate='5.16',pages=750,updated_files=len(proposed),controls=10,main_links=2,next_plan=plan)))
