"""One-shot advancement after final document and author checks."""
from pathlib import Path
from hashlib import sha256
import json,os
H=Path(__file__).resolve().parent;R=H.parents[2]
OLD=H.parent/'gap-credit-recovery-refresh-20261027'
G=H.parent/'gap-insurance-stage-refresh-20261027'
NEXT='docs/plans/accounting-master-acceptance-priority-20261027.md'
PLAN='docs/plans/accounting-insurance-stage-integration-20261027.md'
RESULT=str((H/'result.md').relative_to(R))
INTERNAL='data/accounting-master/insurance-recovery-stage-book-20261027/result.md'
AUDIT='data/accounting-master/insurance-shared-group-audit-20261027/result.md'
def read(p):return json.loads(p.read_text())
def digest(p):return sha256(p.read_bytes()).hexdigest()
def encode(x):return json.dumps(x,indent=2)+'\n'
def dump(p,x):p.write_text(encode(x))
assert not G.exists() and not (H/'advancement.json').exists()
v=read(H/'verification-02.json');lock=read(H/'source-preservation-v2.json')
assert v['status']=='PASS' and v['checks']==643 and (H/'author-review.md').is_file()
S,T=R/lock['source'],R/lock['target']
for group,base in [('sources',S),('evidence',R),('added',T),('integration_inputs',H)]:
    for p,h in lock[group].items():assert digest(base/p)==h,p
docs={d['document']:d for d in v['documents']}
for name,d in docs.items():assert digest(T/(name+'.pdf'))==d['sha256']
for p in [NEXT,PLAN,RESULT,INTERNAL,AUDIT]:assert (R/p).is_file(),p
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json',
       'docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md',
       'MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
       'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
       'docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={p:(R/p).read_bytes() for p in paths}
catalog,nextplan=[json.loads(before[p]) for p in paths[:2]]
a,b=catalog['active_execution_note'],nextplan['active_execution']
assert a['current_candidate']==b['current_candidate']=='5.50;827 pages;not_ready'
assert a['active_work_plan']==b['active_work_plan']=='docs/plans/accounting-insurance-shared-group-audit-20261027.md'
linknames=['docs/AccDSL-latest.pdf','docs/AccDSL-latest.tex',
           'docs/AccDSL-simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex']
links={p:str((R/p).resolve()) for p in linknames}
assert all(Path(p).parent==S for p in links.values())
oldlock={str(p.relative_to(R)):digest(p) for p in OLD.iterdir() if p.is_file()}
audit,packages=read(OLD/'audit-status.json'),read(OLD/'closure-packages.json')
group_identity=sha256(encode(audit['groups']).encode()).hexdigest()
assert len(audit['successor_deltas'])==126
audit['predecessor']=str(OLD.relative_to(R))
audit['baseline']='Version 5.51 integrates insurance call-chain and stage-only evidence; 5.50 preserved.'
for title,evidence,description in [
    ('Insurance report call-chain audit',AUDIT,'149 checks confirm the actual two-case fiscal boundary; recovery_change remains outside that adapter.'),
    ('Issued/held stage-only ledger',INTERNAL,'Two cases, eight full states, 178 assertions and 22 controls; no dates or separate group identities invented.'),
    ('Insurance stage manuscript integration',RESULT,'643 checks preserve 280 sources and 65 evidence files; repaired layout reviewed; independent acceptance pending.')]:
    assert not any(d['evidence']==evidence for d in audit['successor_deltas'])
    audit['successor_deltas'].append({'id':'D'+str(len(audit['successor_deltas'])+1),'title':title,
        'requirements':['MC03','MC05','MC11','MC13','MC15','MC17','MC18','MC19','MC20','MC24','MC25','MC26','MC28','MC33','MC34'],
        'evidence':evidence,'sha256':digest(R/evidence),'current_disposition':description})
for row in packages['packages']:
    assert row['status']=='open'
    if row['id'] in ['W07','W08','W10','W11','W16','W17']:
        row['existing_support']+=' Version 5.51 preserves the checked insurance stage-only ledger and explicit fiscal/group boundary.'
    if row['id']=='W10':row['next_action']='Retain the two checked issued/held stage ledgers. Supply separately supported dates, group identities and a compatible fiscal opening before a dated adapter; preserve the mixed-origin termination-source gap.'
    if row['id'] in ['W11','W16']:row['next_action']='Execute accounting-master-acceptance-priority-20261027.md; inspect delivered complete-method, invariant and term-event source successors and choose a complete missing composition target.'
    if row['id']=='W17':row['next_action']='Version 5.51 is provisional. Repair whole-candidate consistency and current navigation; preserve all equations and sources, then seek separate independent implementability, reader and domain evidence.'
counts=read(OLD/'verification.json')['counts'];counts['successor_deltas']=len(audit['successor_deltas'])
assert counts['successor_deltas']==129 and len(packages['packages'])==18
assert sha256(encode(audit['groups']).encode()).hexdigest()==group_identity
base=str(G.relative_to(R));main=docs['accounting-product-proposal'];sim=docs['simulation-foundations']
changes=dict(updated='2026-10-27',current_candidate='5.51;828 pages;not_ready',latest_result=RESULT,
    latest_internal_result=INTERNAL,insurance_stage_result=INTERNAL,insurance_call_chain_result=AUDIT,
    active_work_plan=NEXT,current_program=PLAN,current_audit=base+'/audit-status.json',
    remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',
    current_pdf=str((T/'accounting-product-proposal.pdf').relative_to(R)),current_pdf_sha256=main['sha256'],
    standalone_pdf=str((T/'simulation-foundations.pdf').relative_to(R)),standalone_pdf_sha256=sim['sha256'],
    full_gap_plan=PLAN,full_gap_program=base+'/closure-program.md',closure_packages=base+'/closure-packages.json',
    failure_register=base+'/failure-register.json',latest_gap_program_result=base+'/result.md',
    gap_program_review=base+'/plan-review.md',gap_program_verification=base+'/verification.json',
    active_work_plans=[NEXT,a['financing_next_plan']],gap_program_trace_counts=counts,
    next=['Execute '+NEXT,'Continue package-specific source and composition work','Keep S6 held and E3 deferred'],
    gap_program_next=['Prioritize complete DSL acceptance dependencies','Preserve bank/insurance source gaps','Continue all 18 packages'],
    current_internal_status='Insurance stage-only result integrated; review complete acceptance dependencies without treating examples as closure.')
for obj in [a,b]:
    obj.update(changes)
    for key in ['latest_internal_results','latest_results']:
        if key in obj:
            for p in [AUDIT,INTERNAL,RESULT]:
                if p not in obj[key]:obj[key].append(p)
if 'completed_increments' in b:b['completed_increments'].append('Version 5.51: insurance stage-only scope; 643 document checks; not_ready.')
summary=f'''Updated 27 October 2026. Governing candidate **5.51**, 828 main pages, not_ready.
Simulation: 262 total / 241 body pages. Four stable PDF/TeX links select this candidate.
Main SHA256: {main['sha256']}.
Simulation SHA256: {sim['sha256']}.

Insurance call-chain and stage-only evidence are integrated. All 643 document
checks pass, preserving 280 sources and 65 evidence files. Both covers and all
added pages reviewed after layout repair. Independent reader, domain and
whole-document acceptance remain pending. Dates and group identities remain
unresolved for the issued/held recovery ledger.

Result: {RESULT}.
Method evidence: {INTERNAL}.
Call-chain audit: {AUDIT}.
Active execution plan: {NEXT}.
Financing evidence plan: {a['financing_next_plan']}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.

All 53 obligations, six interactions, 46 operations and 18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Source gaps block their dependent methods;
continue independent ready work. Narrow examples and page counts are not closure.
'''
new={paths[0]:encode(catalog),paths[1]:encode(nextplan)}
for p in paths[2:4]:new[p]='# Current AccDSL master program\n\n'+summary
for p in paths[4:9]:
    text=before[p].decode();title,rest=text.split('\n',1);first=rest.find('## ');second=rest.find('\n## ',first+3)
    assert first>=0 and second>=0,p
    # Retain older historical entries. The replaced live entry remains in control-before.
    new[p]=title+'\n\n## Insurance stages integrated — 27 October 2026\n\n'+summary+'\n'+rest[second+1:]
text=before[paths[9]].decode()
for old,value in [('Version 5.50, 827 pages','Version 5.51, 828 pages'),('**261 pages**','**262 pages**'),
                  ('**240 body pages**','**241 body pages**'),(str(OLD.relative_to(R)),base),
                  ('credit-recovery-integration-20261027/result.md','insurance-stage-integration-20261027/result.md')]:
    assert old in text,old;text=text.replace(old,value)
new[paths[9]]=text
snapshot=H/'control-before';snapshot.mkdir(exist_ok=False)
for p,raw in before.items():
    assert (R/p).read_bytes()==raw;pout=snapshot/p;pout.parent.mkdir(parents=True,exist_ok=True);pout.write_bytes(raw)
dump(snapshot/'stable-links.json',links)
G.mkdir(exist_ok=False)
for name,value in [('predecessor-lock.json',oldlock),('audit-status.json',audit),('closure-packages.json',packages)]:dump(G/name,value)
(G/'failure-register.json').write_bytes((OLD/'failure-register.json').read_bytes())
lines=['# Full closure program after insurance stage integration','Version 5.51; all 18 packages remain open.']
for row in packages['packages']:
    lines+=['','## '+row['id']+' — '+row['title']]
    for k in ['requirements','depends_on','failure','existing_support','closure_evidence','next_action','limits','status']:
        value=row[k];lines+=['',k+': '+(', '.join(value) or 'none' if isinstance(value,list) else value)]
(G/'closure-program.md').write_text('\n'.join(lines)+'\n')
(G/'remaining-work.md').write_text('# Remaining work\n\n'+'\n'.join('- **'+r['id']+' '+r['title']+':** '+r['next_action'] for r in packages['packages'])+'\n\nS1-S5 partial; S6 held; E3 deferred.\n')
(G/'plan-review.md').write_text('Exact call-chain and complete stage comparisons support provisional 5.51. Missing dates/group identities and independent acceptance remain explicit. Prioritize complete acceptance dependencies next. All package criteria and historical requirement rows remain intact.\n')
(G/'result.md').write_text('Three scoped deltas added; no whole requirement or package closes. Compact current status replaces the previous live entry; its exact bytes remain in the integration control-before snapshot.\n')
dump(G/'verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
for p,text in new.items():
    assert (R/p).read_bytes()==before[p];tmp=(R/p).with_name(Path(p).name+'.v551.tmp');assert not tmp.exists()
    tmp.write_text(text);os.replace(tmp,R/p)
for p in links:
    stem='simulation-foundations' if 'simulation' in p else 'accounting-product-proposal';target=T/(stem+Path(p).suffix)
    tmp=(R/p).with_name(Path(p).name+'.v551-link');assert not tmp.exists();tmp.symlink_to(os.path.relpath(target,(R/p).parent));os.replace(tmp,R/p)
    assert (R/p).resolve()==target
for p,text in new.items():assert (R/p).read_text()==text
for p,h in oldlock.items():assert digest(R/p)==h
dump(H/'advancement.json',dict(status='PASS',candidate=a['current_candidate'],counts=counts,next=NEXT,changed_controls=list(new),all_packages_open=True,mission_complete=False))
print(json.dumps(dict(status='PASS',candidate=a['current_candidate'],next=NEXT,deltas=counts['successor_deltas'])))
