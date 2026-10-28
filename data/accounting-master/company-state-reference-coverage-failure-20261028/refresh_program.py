"""Record original SIM-F002 and governing-reference evidence without closure."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
H = Path(__file__).resolve().parent
G = ROOT / 'data/accounting-master/company-state-governing-notes-20261028'
S = ROOT / 'data/accounting-master/construction-continuation-20261028'
def dump(path, value): path.write_text(json.dumps(value,indent=2)+'\n')
def rel(path): return str(path.relative_to(ROOT))
hash_count = 0
for base, count in [(H,179),(G,60)]:
    result = json.loads((base/'attempt-01/verification.json').read_text())
    assert result['status']=='pass' and result['checks']==count
    hashes = json.loads((base/'attempt-01/run-manifest.json').read_text())['source_hashes']
    assert all(sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    hash_count += len(hashes)
    assert (base/'result.md').is_file()
p = ROOT/'data/accounting-master/unified-program-20261028/program.json'
program = json.loads(p.read_text()); old = deepcopy(program)
f = S/'failure-dispositions.json'; dispositions = json.loads(f.read_text())
with (H/'navigation-before.json').open('x') as out: json.dump(dict(program=old,dispositions=dispositions),out,indent=2)
originals = {r['original_row']['id']:r['original_row'] for r in json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())['rows']}
assert len(dispositions['rows'])==28 and not any(r['id']=='SIM-F002' for r in dispositions['rows'])
dispositions['rows'].append(dict(id='SIM-F002',original_row=originals['SIM-F002'],
    disposition='exact_original_scanned_reference_coverage_discriminator',
    comparison='Synthetic raster-only incorporated debt80 covenant: missing retrieval/parsing/modeling prevents execution; native cap refuses100 and40+41, accepts80 and40+40. Two account maps and15 tamper cases preserve source and cumulative meanings.',
    evidence=[rel(H/'attempt-01/verification.json'),rel(H/'result.md')],
    next_action='Actual-source document recovery, interpretation and complete reference discovery remain open; do not promote fixed synthetic semantics into general OCR or contract admission.',
    original_status_unchanged=True,broad_package_closed=False))
dispositions['rows'].sort(key=lambda r:r['id'])
dispositions['reviewed_rows']=len(dispositions['rows'])
dispositions['scope']='Twenty-nine original rows individually reviewed;172 outside this continuation. Original criteria/statuses persist; scoped evidence is not whole-company closure.'
for row in dispositions['rows']: assert row['original_row']==originals[row['id']]
dump(f,dispositions)
lines=['# Current original failure dispositions','','28 October2026. Twenty-nine original rows reviewed;172 outside this pass. All201 original rows/statuses persist. Coverage is not closure.','','| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
lines += ['| '+r['id']+' | '+r['comparison']+' | '+r['next_action']+' |' for r in dispositions['rows']]
(S/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
for task in program['tasks']:
    if task['id'] in ['T03','C04']:
        task['evidence'].extend([rel(G/'result.md'),rel(H/'result.md')])
    if task['id']=='T03':
        task['next_action']='Eight Apple series provisionally match five certificate references plus two base indentures. Exact2019 certificate SEC403/trusted403/mirror timeout retained; other targets not newly declared inaccessible. Recover a justified distinct source route while continuing actual chronology/measurement work and independent ready construction.'
    if task['id']=='C04':
        task['next_action']='Twenty-nine original failures reviewed;172 outside this pass. Continue equity authorization/conversion/value and other original discriminators, actual source dependencies with T03, and ordered reading from337.'
        task['remaining']=[x for x in task['remaining'] if not x.startswith('Twenty-eight original rows')]
        task['remaining'].append('Twenty-nine original rows individually compared;172 outside this pass. Actual reference discovery/semantic admission and arbitrary operation completeness remain open.')
for before,after in zip(old['tasks'],program['tasks']):
    for key in ['id','status','depends_on','completion_criterion','requirements']: assert before[key]==after[key]
dump(p,program)
entry='''
## Missing incorporated-document discriminator — 28 October 2026

SIM-F002 passes179 checks across19 cases and15 tamper controls. A synthetic
raster-only debt80 covenant separates retrieval, parsing and modeling; missing
coverage cannot reach execution. Native enforcement rejects100 and40+41,
accepts80 and40+40, and preserves atomic refusal across two account maps.
Result: company-state-reference-coverage-failure-20261028/result.md under
data/accounting-master. No automatic source or contract admission follows.

The governing-source unit passes60 index/identity checks for eight Apple series,
five certificate references and two indentures. No governing body recovered:
exact2019 SEC403/trusted403 and mirror timeout retained. Other sources remain
open; this is a local access blocker. Continue independent ready work.

Twenty-nine original failures reviewed;172 outside this pass. Main reading
336/831, resume337. Original criteria/statuses/releases persist; E3 deferred.

'''
for name in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-master-checkpoint.md',
             'data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md',
             'docs/plans/company-state-research-release-program-20261028.md']:
    p=ROOT/name; title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
for name,key in [('scripts/accounting_master_catalog.json','active_execution_note'),('data/accounting-master/next-plan.json','active_execution')]:
    p=ROOT/name;d=json.loads(p.read_text());d[key]['reference_coverage_continuation_20261028']=dict(result=rel(H/'result.md'),
        governing_result=rel(G/'result.md'),checks=179,governing_checks=60,reviewed_original_failures=29,outside_pass=172,
        scope='Synthetic scanned-reference/native covenant discriminator; actual governing bodies unresolved');dump(p,d)
print(json.dumps(dict(reviewed=29,outside_pass=172,source_hashes_verified=hash_count,task_statuses_preserved=True)))
