"""Validate actual reading continuity and refresh only live frontier fields."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
I=D/'manuscript-release-prep-v552r2-20261027-inventory.json'
j=json.loads(I.read_text());v=next(v for v in j['volumes'] if v['name']=='accounting-product-proposal')
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
errors=[]
for row in j['source_files']:
    if sha256((ROOT/j['candidate']/row['path']).read_bytes()).hexdigest()!=row['sha256']:errors.append(row['path'])
segments=[r for r in j['read_segments'] if r['volume']==v['name']]
cursor=1;prior=None
for r in segments:
    assert r['pages']==list(range(cursor,cursor+len(r['pages']))) and len(r['pages'])<=6
    if prior:assert r['entry_state']==prior['exit_state']
    assert r['pdf_sha256']==v['pdf_sha256']
    cursor=r['pages'][-1]+1;prior=r
frontier=cursor-1
assert frontier==288
assert [p['physical_page'] for p in v['pages'] if p['author_continuous_read']=='author_read']==list(range(1,frontier+1))
doc=fitz.open(ROOT/v['pdf'])
for p in v['pages']:
    assert sha256(doc[p['physical_page']-1].get_text().encode()).hexdigest()==p['text_sha256']
for start,end in [(265,270),(271,276),(277,282),(283,288)]:
    rb=json.loads((D/f'render-bindings-{start:04}-{end:04}.json').read_text())
    for p in rb['pages']:assert sha256((D/'rendered-main'/f'{p["page"]:04}.png').read_bytes()).hexdigest()==p['sha256']
assert not errors
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json',
       'data/accounting-master/release-pursuit-20261027/state.json',
       'data/accounting-master/unified-program-20261028/program.json',
       'data/accounting-master/construction-continuation-20261028/checkpoint.md',
       'data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md']
backup=HERE/'controls-before-0288';backup.mkdir(exist_ok=False)
for i,p in enumerate(paths):(backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
for p,container in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
    data=json.loads((ROOT/p).read_text());fields=data[container]['manuscript_review_frontier']
    fields['physical_pages_read']=frontier;fields['next_page']=frontier+1
    data[container]['ordered_review_continuation_20261028']=dict(physical_pages_read=frontier,next_page=frontier+1,
        result='data/accounting-master/company-state-ordered-review-20261028/result.md',
        scope='Actual ordered author reading; independent acceptance pending')
    (ROOT/p).write_text(json.dumps(data,indent=2)+'\n')
data=json.loads((ROOT/paths[2]).read_text());data['ordered_read_pages']=frontier
(ROOT/paths[2]).write_text(json.dumps(data,indent=2)+'\n')
program=json.loads((ROOT/paths[3]).read_text());before=deepcopy(program)
for task in program['tasks']:
    if task['id']=='R04':
        task['status']='in_progress'
        task['next_action']='Actual ordered main reading reaches288/831 on protected5.52-R2; resume289. Separate node/equation, simulation and successor-delta reviews remain incomplete.'
        assert 'data/accounting-master/company-state-ordered-review-20261028/result.md' in task['evidence']
for old,new in zip(before['tasks'],program['tasks']):
    for key in ['id','depends_on','completion_criterion','requirements']:assert old[key]==new[key]
    assert old['status']==new['status'] or (old['id']=='R04' and new['status']=='in_progress')
(ROOT/paths[3]).write_text(json.dumps(program,indent=2)+'\n')
entry='''
## Ordered manuscript review through288 — 28 October2026

Actual rendered reading advances from276 to288/831 on the retained5.52-R2
main PDF. Twelve more individual pages and127 exact local arithmetic checks cover
the joined tax/ownership carry, sector-company FX/NCI and historical Apple
measurement and conditional-stress examples.279 source
hashes,831 page-text hashes, exact exit/entry continuity and24 render bindings across265–288
verify. R04 is in_progress; node/equation, simulation, successor-delta and
independent review remain separate. No manuscript or release is changed.

Resume physical289. The current original-failure supplement covers11/201
rows; T01 is complete as a definition task, with common caller304 checks and
four original debt targets37 checks. The release remains not_ready and E3
deferred. Result: data/accounting-master/company-state-ordered-review-20261028/result.md.

'''
for p in paths[4:]:
    file=ROOT/p;title,rest=file.read_text().split('\n',1);file.write_text(title+'\n'+entry+rest)
verification=dict(passed=True,source_files=len(j['source_files']),page_text_hashes=len(v['pages']),
    segments=len(segments),frontier=frontier,next_page=frontier+1,rendered_pages=24,arithmetic_checks=183,
    pdf_sha256=v['pdf_sha256'],independent_reader='pending',human_acceptance='pending',
    hierarchy_node_review='separate incomplete obligation; no node completion inferred',
    source_hashes={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in [
        'docs/plans/company-state-ordered-review-20261028.md',str(Path(__file__).relative_to(ROOT)),
        str((D/'main-0277-0282.json').relative_to(ROOT)),str((D/'main-0283-0288.json').relative_to(ROOT))]})
(HERE/'verification-0288.json').write_text(json.dumps(verification,indent=2)+'\n')
print(json.dumps({k:verification[k] for k in ['passed','source_files','page_text_hashes','frontier','next_page','arithmetic_checks']}))
