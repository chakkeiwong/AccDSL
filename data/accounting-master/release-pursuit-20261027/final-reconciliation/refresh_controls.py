"""Refresh current navigation; close the timed window only after its deadline."""
from pathlib import Path
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
UNIT = Path(__file__).resolve().parent
PURSUIT = UNIT.parent
PREFIX = str(UNIT.relative_to(ROOT))
DEADLINE = datetime(2026,10,27,15,19,56,tzinfo=timezone.utc)
MARKER = 'Historical assessments below are preserved.'
SELECTED = 'docs/design/proposal/manuscript-reference-v555r1-20261027'
MD_CONTROLS = ['MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
 'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
 'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md',
 'data/accounting-master/next-plan.md']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['progress','close'],required=True)
    parser.add_argument('--snapshot',required=True)
    parser.add_argument('--record-dir',required=True)
    args=parser.parse_args()
    now=datetime.now(timezone.utc)
    closing=args.mode=='close'
    if closing and now < DEADLINE:
        raise SystemExit('Refuse premature deadline closure')
    record=Path(args.record_dir).resolve()
    if record.exists():
        raise SystemExit('Refuse existing control record directory')
    snapshot=Path(args.snapshot).resolve()
    result=json.loads((snapshot/'verification.json').read_text())
    locks=json.loads((snapshot/'input-lock.json').read_text())
    if not result['passed'] or result['candidate'] != SELECTED:
        raise SystemExit('Final snapshot failed or selected candidate differs')
    for rel, expected in locks.items():
        if expected is not None and sha((ROOT/rel).read_bytes()) != expected:
            raise SystemExit('Snapshot input changed; reconcile before update: '+rel)
    inventory_rel='data/accounting-master/release-pursuit-20261027/manuscript-review/manuscript-release-prep-v552r2-20261027-inventory.json'
    main=next(x for x in result['reading_frontier'] if x['volume']=='accounting-product-proposal')
    frontier=main['contiguous_pages_read']; next_page=main['next_physical_page']
    for rel, info in result['links'].items():
        p=ROOT/rel
        if not p.is_symlink() or str(p.readlink())!=info['target'] or sha(p.read_bytes())!=info['sha256']:
            raise SystemExit('Canonical pointer changed: '+rel)
    stamp=now.isoformat()
    decision=PREFIX+'/release-decision.md'; remaining=PREFIX+'/remaining-program.md'
    status='window_ended_release_not_ready' if closing else 'active_final_reconciliation_release_not_ready'
    heading='Eight-hour effort concluded' if closing else 'Final release reconciliation in progress'
    timing=('The authorized window ended at 15:19:56 UTC (23:19:56 Hong Kong) on\n27 October 2026. The release objective remains unmet; no extension or autonomous\nbackground campaign is started.' if closing else 'The authorized effort continues until 15:19:56 UTC (23:19:56 Hong Kong)\non 27 October 2026. Final integrity and condition-level reconciliation are underway.')
    current=f'''## {heading} — 27 October 2026

Selected candidate **5.55-R1** remains **not_ready**: 837 main pages and
265 total / 244 body simulation pages. All four PDF/TeX links select the same
protected package. The former Version 1.2 archive retains all 32 declared files.
Main SHA256: 76c36e5af3b22ace09dd1cff8188d19410c4af36defed5ac4b932debaf5bd1f5.
Simulation SHA256: 71dccb1e354c3ad3befbb8110cdff2a2889f73bfa5fd4f661a92576e163bdf8e.

{timing}

Current release decision: {decision}.
Concrete remaining program: {remaining}.
Master sequence: docs/plans/accounting-release-closure-20261027.md.
Timed plan: docs/plans/accounting-release-eight-hour-20261027.md.
Final reconciliation plan: docs/plans/accounting-release-final-reconciliation-20261027.md.
Verified snapshot: {snapshot.relative_to(ROOT)}/verification.json.

The current 452-file package includes seven bounded companions. Both volumes
reproduce all normalized page text from a separate copy in the recorded
environment; no original-worktree TeX inputs were observed. Coupling assumptions,
particle ancestor weights, continuous financing amounts/settlement prefixes and
midpoint convergence are repaired. The latter includes a proof rather than a
monotonic-grid claim. Earlier 460 source/build checks and 12 rendered-page
bindings retain their local meanings. No clean installation is claimed.

The dated PAA roll-forward now reaches the common book/interim-report interface;
the bank map distinguishes AU/US profiles and the retained book-to-capital case.
Their former manuscript-integration tasks are delivered. Broader compatibility,
source applicability and independent acceptance remain. Separate source-construction
and intragroup replay archives are checked evidence outside the manuscript package.
All 27 mapped literature claims have bounded dispositions; the wider survey and
source population are unfinished. Actual issuer history/opening remains unknown.

Original 35 MC provisions, 114 acceptance rows and 156 authored clauses retain
their exact bytes. Sixty-nine later supplemental records bind 43 distinct facets;
they are evidence, not new acceptance counts. All 53 obligations, six interactions,
46 operations and 18 closure packages remain open. The 201 failure rows include
unexecuted tasks. S1–S5 partial; S6 held; E3 deferred.

The live ordered review of protected 5.52-R2 reaches physical page {frontier} of
831; resume at {next_page}. Separate simulation and node/equation review remains
incomplete. Local successor review does not establish whole-document coverage.
Finish compatible specification, full source/case/failure dispositions,
consequential dependencies and sources, whole-document review, then distinct
reader/domain/implementation acceptance. Complete feasible internal preparation
before focused referral. No outreach, fees, publication, installation, GPU work,
subagents or legacy controller are authorized by this update.

'''
    replacements={}
    def load(rel):
        data=(ROOT/rel).read_bytes()
        originals[rel]=data
        return data.decode()
    originals={}
    for rel in MD_CONTROLS:
        text=load(rel)
        if text.count(MARKER)!=1:
            raise SystemExit('Unexpected current/historical boundary: '+rel)
        title=text.splitlines()[0]
        tail=text.split(MARKER,1)[1]
        replacements[rel]=(title+'\n\n'+current+MARKER+tail).encode()
    for rel,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
        data=json.loads(load(rel)); a=data[key]
        a['updated']=stamp
        a['current_candidate']='5.55-R1;837 pages;not_ready'
        a['latest_result']=decision
        a['latest_internal_result']=decision
        a['remaining_work']=remaining
        a['active_work_plan']='docs/plans/accounting-release-closure-20261027.md' if closing else 'docs/plans/accounting-release-final-reconciliation-20261027.md'
        if key=='active_execution':
            a['historical_plan_before_final_reconciliation']=a.get('historical_plan_before_final_reconciliation',a.get('plan'))
            a['plan']=a['active_work_plan']
        a['current_program']='docs/plans/accounting-release-closure-20261027.md'
        a['current_release_decision']=decision
        a['additive_release_failures']=PREFIX+'/new-failure-supplement.json'
        a['final_reconciliation_snapshot']=str(snapshot.relative_to(ROOT))
        a['next']=[
            'Finish normative profile/version/effect/migration compatibility and connected company cases against original conditions',
            f'Resume ordered baseline reading at {next_page}; preserve exact inventory and review successor changes',
            'Complete consequential source/dependency/failure dispositions, then prepare distinct independent acceptance']
        a['manuscript_review_frontier']={'baseline':'5.52-R2','physical_pages_read':frontier,'next_page':next_page,'status':'partial_author_read; node and independent acceptance open','inventory':inventory_rel}
        pursuit=a['timed_release_pursuit']
        pursuit.update({'status':status,'release_status':'not_ready','objective_achieved':False,'decision':decision,'remaining_work':remaining,'snapshot':str(snapshot.relative_to(ROOT))})
        if closing:pursuit['closed_utc']=stamp
        replacements[rel]=(json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode()
    state_rel=str((PURSUIT/'state.json').relative_to(ROOT))
    state=json.loads(load(state_rel))
    state.update({'status':status,'release_status':'not_ready','objective_achieved':False,'current_unit':'Final release decision recorded; remaining program preserved' if closing else 'Final original-condition reconciliation and preservation checks','last_update_utc':stamp,'ordered_read_pages':frontier,'selected_candidate':SELECTED,'final_decision':decision,'remaining_program':remaining,'final_snapshot':str(snapshot.relative_to(ROOT)),'goal_tool_status_observed':'blocked on recovery; saved user authorization governed this timed effort; no completion or tool-resumption claim'})
    if closing:state['closed_utc']=stamp
    replacements[state_rel]=(json.dumps(state,indent=2,ensure_ascii=False)+'\n').encode()
    reset_rel=str((PURSUIT/'reset-memo.md').relative_to(ROOT));load(reset_rel)
    replacements[reset_rel]=('# Release pursuit reset memo\n\n'+current+'\nDo not rerun frozen one-shot writers or regenerate the populated review inventory.\nRead the live remaining program and original clauses before resuming authorized work.\nThe goal service reported blocked on recovery; no tool transition is asserted.\n').encode()
    progress_rel=str((PURSUIT/'progress.md').relative_to(ROOT)); progress=load(progress_rel)
    replacements[progress_rel]=(progress+f'\n## {stamp} — {heading}\n\nSelected 5.55-R1 remains not_ready. Final decision: {decision}.\nSnapshot: {snapshot.relative_to(ROOT)}. All declared package bytes, frozen\nacceptance, archive identities and saved review continuity pass. Ordered main\nreading reaches {frontier}; no node-level or independent acceptance inferred.\nRemaining work: {remaining}. Objective achieved: false.\n').encode()
    readme=load('docs/README.md')
    label='- [Current release decision and exact remaining conditions]'
    line=label+'(../'+decision+').\n- [Current remaining program](../'+remaining+').\n'
    if label not in readme:
        pos=readme.index('- [Release-readiness audit')
        readme=readme[:pos]+line+readme[pos:]
    readme=readme.replace('- [Current acceptance decisions]','- [Original frozen acceptance decisions]')
    readme=readme.replace('- [Full remaining-work queue]','- [Earlier remaining-work queue]')
    replacements['docs/README.md']=readme.encode()
    # Compare all inputs again before any live mutation, then preserve their bytes.
    for rel,raw in originals.items():
        if (ROOT/rel).read_bytes()!=raw:raise SystemExit('Concurrent control change: '+rel)
    if sha((ROOT/inventory_rel).read_bytes())!=locks[inventory_rel]:
        raise SystemExit('Reading frontier advanced; refresh snapshot first')
    record.mkdir(parents=True,exist_ok=False)
    for rel,raw in originals.items():
        p=record/'before'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    changes=[]
    for rel,new in replacements.items():
        p=ROOT/rel
        if p.read_bytes()!=originals[rel]:raise SystemExit('Concurrent change before individual write: '+rel)
        stage=p.with_name(p.name+'.release-reconciliation-tmp')
        with stage.open('xb') as handle:handle.write(new)
        os.replace(stage,p)
        if p.read_bytes()!=new:raise SystemExit('Failed write verification: '+rel)
        changes.append({'path':rel,'before':sha(originals[rel]),'after':sha(new)})
    record_data={'timestamp_utc':stamp,'mode':args.mode,'status':status,'release_status':'not_ready','objective_achieved':False,'candidate':SELECTED,'snapshot':str(snapshot.relative_to(ROOT)),'snapshot_sha256':sha((snapshot/'verification.json').read_bytes()),'reading_frontier':result['reading_frontier'],'changes':changes,'canonical_links_unchanged':result['links'],'acceptance_not_promoted':True}
    (record/'update.json').write_text(json.dumps(record_data,indent=2)+'\n')
    if closing:
        target=UNIT/'closure.json'
        with target.open('x') as h:json.dump(record_data,h,indent=2);h.write('\n')
    print(json.dumps({'status':status,'controls_updated':len(changes),'frontier':frontier,'record':str(record)},indent=2))

if __name__=='__main__':
    main()
