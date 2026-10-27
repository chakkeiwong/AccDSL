"""Read selected release evidence; write a new report directory only."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import os
import platform
import re
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
UNIT = Path(__file__).resolve().parent
PURSUIT = UNIT.parent
PLAN = 'docs/plans/accounting-release-final-reconciliation-20261027.md'
SELECTED = 'docs/design/proposal/manuscript-reference-v555r1-20261027'
ADVANCE = 'data/accounting-master/release-pursuit-20261027/midpoint-reference/merged/advancement.json'
ACCEPTANCE = 'data/accounting-master/release-plan-execution-20261027/release-acceptance.json'
CLAUSES = 'data/accounting-master/release-plan-execution-20261027/acceptance-clauses.json'
INVENTORY = 'data/accounting-master/release-pursuit-20261027/manuscript-review/manuscript-release-prep-v552r2-20261027-inventory.json'
SUPPLEMENTS = [
 'data/accounting-master/internal-evidence-companion-20261027/acceptance-supplement.json',
 'data/accounting-master/intragroup-evidence-replay-20261027/acceptance-supplement.json',
 'data/accounting-master/bank-interface-consolidation-20261027/acceptance-supplement.json',
 'data/accounting-master/insurance-paa-dated-book-20261027/acceptance-supplement.json',
]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    out = Path(args.output_dir).resolve()
    if out.exists():
        raise SystemExit('Refuse existing output directory: ' + str(out))
    if out == ROOT or (ROOT / SELECTED) == out or (ROOT / SELECTED) in out.parents:
        raise SystemExit('Refuse output inside protected manuscript')
    start = time.monotonic()
    locks = {}
    checks = []
    def read(rel):
        p = ROOT / rel
        raw = p.read_bytes()
        locks[rel] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    def check(name, passed, detail=None):
        checks.append({'name':name, 'passed':bool(passed), 'detail':detail})
    advance = read(ADVANCE)
    manifest_rel = SELECTED + '/package-manifest.json'
    manifest = read(manifest_rel)
    check('selected_manifest_identity', locks[manifest_rel] == advance['package_manifest_sha256'])
    seen = set()
    for row in manifest['files']:
        rel = Path(row['path'])
        p = ROOT / SELECTED / rel
        valid = not rel.is_absolute() and '..' not in rel.parts and str(rel) not in seen
        valid = valid and p.is_file() and not any((ROOT / SELECTED / Path(*rel.parts[:i])).is_symlink() for i in range(1, len(rel.parts)+1))
        seen.add(str(rel))
        check('package:' + str(rel), valid and digest(p) == row['sha256'] and p.stat().st_size == row['bytes'])
    links = {}
    for rel, expected in advance['links'].items():
        p = ROOT / rel
        ok = p.is_symlink() and str(p.readlink()) == expected['after'] and digest(p) == expected['sha256']
        check('link:' + rel, ok)
        links[rel] = {'target':str(p.readlink()) if p.is_symlink() else None, 'sha256':digest(p) if p.is_file() else None}
    for category in ['preserved_release_records', 'evidence']:
        for rel, expected in advance[category].items():
            p = ROOT / rel
            actual = digest(p) if p.is_file() else None
            locks[rel] = actual
            check(category + ':' + rel, actual == expected)
    archive = read('docs/archive/accounting-product-design-v1.2-20261026/archive-manifest.json')
    for row in archive:
        p = ROOT/row['archive']
        check('archive:' + row['archive'], p.is_file() and digest(p) == row['sha256'])
        if row['operation'] == 'move':
            check('archived_old_root_removed:' + row['old'], not (ROOT/row['old']).exists())
    acceptance = read(ACCEPTANCE)
    clauses = read(CLAUSES)
    by_id = {row['id']:row for row in clauses['rows']}
    check('original_population_114', len(acceptance['rows']) == 114)
    check('original_MC_population_35', sum(row['id'].startswith('MC') for row in acceptance['rows']) == 35)
    check('authored_clause_population_156', len(by_id) == len(clauses['rows']) == 156)
    decisions_rel=str((UNIT/'current-condition-decisions.md').relative_to(ROOT))
    decisions=(ROOT/decisions_rel).read_text()
    locks[decisions_rel]=digest(ROOT/decisions_rel)
    covered=set()
    for parent,lo,hi in re.findall(r'(MC\d{2})\.(\d{2})–(\d{2})',decisions):
        covered.update(f'{parent}.{i:02d}' for i in range(int(lo),int(hi)+1))
    check('condition_navigation_exact_156_facets', covered == set(by_id), {'missing':sorted(set(by_id)-covered),'invalid':sorted(covered-set(by_id))})
    for name in ['release-decision.md','remaining-program.md']:
        rel=str((UNIT/name).relative_to(ROOT));locks[rel]=digest(ROOT/rel)
    repairs=read(str((UNIT/'local-repair-evidence.json').relative_to(ROOT)))
    for row in repairs['rows']:
        actual=digest(ROOT/row['result']);locks[row['result']]=actual
        check('repair_result_identity:'+row['id'],actual==row['result_sha256'])
        for clause in row['original_clauses']:
            original=by_id[clause['id']]
            check('repair_original_clause:'+row['id']+':'+clause['id'],clause['condition']==original['condition'] and clause['original_acceptance_sha256']==original['original_acceptance_sha256'])
    failures=read('data/accounting-master/gap-insurance-stage-refresh-20261027/failure-register.json')
    disposition=read('data/accounting-master/integrated-failure-dispositions-20261027/attempt-01/failure-dispositions.json')
    original_failures={r['id']:r for group in ['original','literature_extensions','cross_interface'] for r in failures[group]}
    new_failures=read(str((UNIT/'new-failure-supplement.json').relative_to(ROOT)))
    check('new_failure_original_register_identity',digest(ROOT/new_failures['original_register'])==new_failures['original_register_sha256'])
    for row in new_failures['rows']:
        check('new_failure_evidence:'+row['id'],digest(ROOT/row['evidence_result'])==row['evidence_sha256'] and all(x in original_failures for x in row['related_original_ids']) and row['full_failure_closed'] is False)
    check('failure_ids_201_preserved',len(original_failures)==201 and {r['id'] for r in disposition['rows']}==set(original_failures))
    for row in disposition['rows']:
        check('failure_original_record:' + row['id'],row['original_record']==original_failures[row['id']] and row['full_failure_closed'] is False)
    failure_lock=read('data/accounting-master/integrated-failure-dispositions-20261027/attempt-01/source-lock.json')
    for rel,expected in failure_lock.items():
        actual=digest(ROOT/rel) if (ROOT/rel).is_file() else None
        locks[rel]=actual
        check('failure_evidence_identity:'+rel,actual==expected)
    updates = collections.defaultdict(list)
    for rel in SUPPLEMENTS:
        supplement = read(rel)
        for original, expected in supplement['baseline_records'].items():
            check('supplement_baseline:' + rel + ':' + original, digest(ROOT/original) == expected)
        for source, expected in supplement['evidence'].items():
            actual = digest(ROOT/source) if (ROOT/source).is_file() else None
            locks[source] = actual
            check('supplement_evidence:' + rel + ':' + source, actual == expected)
        for row in supplement['rows']:
            original = by_id.get(row['id'])
            check('supplement_clause:' + rel + ':' + row['id'], original is not None and row['condition'] == original['condition'] and row['original_acceptance_sha256'] == original['original_acceptance_sha256'] and row['original_acceptance'] == original['original_acceptance'])
            updates[row['id']].append({'source':rel, 'source_sha256':locks[rel], 'row':row})
    inventory = read(INVENTORY)
    segment_checks = []
    for name in [v['name'] for v in inventory['volumes']]:
        previous_end = 0
        previous_exit = None
        for segment in [s for s in inventory['read_segments'] if s['volume'] == name]:
            pages = segment['pages']
            packet_rel = str(Path(INVENTORY).parent / (segment['id']+'.json'))
            packet = read(packet_rel)
            valid = packet == segment and pages == list(range(previous_end+1,pages[-1]+1)) and bool(segment['observations'])
            if previous_exit is not None:
                valid = valid and segment['entry_state'] == previous_exit
            check('ordered_packet:' + segment['id'], valid)
            if segment.get('render_binding'):
                binding_rel = str(Path(INVENTORY).parent / segment['render_binding'])
                binding = read(binding_rel)
                check('rendered_packet_identity:' + segment['id'], binding['pdf_sha256'] == segment['pdf_sha256'] and [p['page'] for p in binding['pages']] == pages)
                for page in binding['pages']:
                    image = ROOT/Path(INVENTORY).parent/'rendered-main'/('%04d.png'%page['page'])
                    check('rendered_page:' + segment['id'] + ':' + str(page['page']),image.is_file() and digest(image) == page['sha256'])
            previous_end = pages[-1]
            previous_exit = segment['exit_state']
    frontier = []
    for volume in inventory['volumes']:
        pages = volume['pages']
        contiguous = 0
        for page in pages:
            if page['physical_page'] != contiguous+1 or page['author_continuous_read'] != 'author_read':
                break
            contiguous += 1
        frontier.append({'volume':volume['name'], 'pdf':volume['pdf'], 'pdf_sha256':volume['pdf_sha256'], 'total_pages':len(pages), 'contiguous_pages_read':contiguous, 'next_physical_page':contiguous+1 if contiguous < len(pages) else None, 'page_status':dict(collections.Counter(p['author_continuous_read'] for p in pages)), 'node_status':dict(collections.Counter(n['review']['author_read'] for n in volume['nodes']))})
        check('reading_baseline_pdf:' + volume['name'], digest(ROOT/volume['pdf']) == volume['pdf_sha256'])
    component_dirs = sorted(p.name for p in (ROOT/SELECTED/'companions').iterdir() if p.is_dir())
    check('seven_declared_components', len(component_dirs) == 7)
    historical_index = read(SELECTED + '/component-index.json')
    components = []
    for name in component_dirs:
        prefix = 'companions/' + name + '/'
        rows = [row for row in manifest['files'] if row['path'].startswith(prefix)]
        instructions = prefix + ('RUN.md' if (ROOT/SELECTED/prefix/'RUN.md').is_file() else 'README.md')
        check('component_instructions:' + name, instructions in seen and len(rows) > 0)
        components.append({'name':name,'path':prefix.rstrip('/'),'instructions':instructions,'manifest_members':len(rows),'scope':'See exact component instructions and current release decision; no common runtime or acceptance implied.'})
    check('package_explicitly_incomplete', manifest['full_evidence_closure'] is False)
    relocation = read('data/accounting-master/release-pursuit-20261027/midpoint-reference/merged/relocation/result.json')
    check('both_copied_volume_records', len(relocation['reports']) == 2 and all(r['all_normalized_page_text_equal'] and not r['original_worktree_tex_inputs'] and r['build']['exit_code']==0 for r in relocation['reports']))
    check('copied_non_pdf_inputs_preserved', relocation['non_pdf_copied_inputs_preserved'])
    check('copied_numerical_results_equal', relocation['reference_companion_complete_result_equal'] and relocation['reference_companion_grid_cases_equal'])
    derived = []
    for row in clauses['rows']:
        derived.append({'id':row['id'], 'parent':row['parent'], 'condition':row['condition'], 'original_acceptance':row['original_acceptance'], 'original_acceptance_sha256':row['original_acceptance_sha256'], 'inherited_acceptance_status':row['acceptance_status'], 'later_evidence':updates.get(row['id'],[]), 'scope':'Additive binding only. Read release-decision.md for current integration and remaining conditions; no new independent acceptance.', 'full_requirement_closed':False, 'scope_waiver':False})
    result = {'schema':'AccDSLFinalReleaseSnapshot/1','timestamp_utc':datetime.now(timezone.utc).isoformat(),'candidate':SELECTED,'release_status':'not_ready','passed':all(c['passed'] for c in checks),'checks':checks,'package_files':len(seen),'package_manifest_sha256':locks[manifest_rel],'links':links,'frozen_acceptance_rows':len(acceptance['rows']),'authored_clause_facets':len(clauses['rows']),'later_supplement_row_count':sum(len(v) for v in updates.values()),'distinct_clauses_with_supplement':len(updates),'reading_frontier':frontier,'limits':'Integrity and binding only; no new replay, clean installation, independent acceptance, source-validity finding or full coverage claim.'}
    # Verify read inputs still agree before publishing a snapshot.
    unstable = [rel for rel,h in locks.items() if h is not None and digest(ROOT/rel) != h]
    if unstable:
        raise SystemExit('Inputs changed while reading; retry fresh output after reconciliation: '+str(unstable))
    out.mkdir(parents=True,exist_ok=False)
    def write(name,obj):
        (out/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
    write('verification.json',result)
    write('input-lock.json',locks)
    write('clause-evidence.json',{'original_clauses_sha256':locks[CLAUSES],'rows':derived,'full_release_closure':False})
    write('component-navigation.json',{'candidate':SELECTED,'manifest_sha256':locks[manifest_rel],'components':components,'historical_index_names':[x['name'] for x in historical_index],'note':'The packaged component-index.json retains two historical entries. Current README names all seven; this additive navigation is bound to the current manifest, without rewriting that package.'})
    write('run-manifest.json',{'command':[sys.executable,'-I','-B',*sys.argv],'cwd':str(Path.cwd()),'script_sha256':digest(Path(__file__)),'observed_isolated_python':sys.flags.isolated,'observed_bytecode_disabled':sys.dont_write_bytecode,'plan':PLAN,'plan_sha256':digest(ROOT/PLAN),'git_commit':'unavailable; unusable marker unchanged','python':sys.version,'executable':sys.executable,'platform':platform.platform(),'cpu_gpu':'CPU-only standard library; no framework/device calls','seeds':'N/A: deterministic integrity check','data_version':locks[manifest_rel],'wall_seconds':time.monotonic()-start,'result':str(out/'verification.json'),'status':'pass' if result['passed'] else 'fail'})
    print(json.dumps({k:result[k] for k in ['timestamp_utc','passed','package_files','later_supplement_row_count','distinct_clauses_with_supplement','reading_frontier']},indent=2))
    print('Failed checks:',[c for c in checks if not c['passed']])
    return 0 if result['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
