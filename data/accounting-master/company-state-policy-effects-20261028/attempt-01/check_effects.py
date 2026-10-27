"""Discriminate policy effects using independently expected native amounts."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import effects

ROOT = effects.ROOT
HERE = Path(__file__).resolve().parent
PLAN = 'docs/plans/company-state-policy-effects-20261028.md'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    packet_path = ROOT / 'data/accounting-master/company-path-exchanges-20261023/packet.json'
    packet = json.loads(packet_path.read_text())
    records = packet['record_registry']
    root = records[packet['root_ref']['digest']]['body']
    chosen = [records[r['digest']]['body'] for r in root['path_refs']
              if records[r['digest']]['body']['name']=='second_year_price_revision']
    assert len(chosen)==1
    inputs = {packet_path, ROOT/PLAN, HERE/'effects.py', Path(__file__)}
    def blob(ref):
        path = ROOT / packet['blobs'][ref['digest']]['path']
        raw = path.read_bytes(); inputs.add(path)
        assert sha256(raw).hexdigest()==ref['digest'] and len(raw)==ref['byte_length']
        return json.loads(raw)
    path = blob(chosen[0]['path_blob'])
    baseline = blob(chosen[0]['result_blob'])
    policy_path = ROOT/'data/accounting-master/company-policy-20261023/policy.json'
    policy = json.loads(policy_path.read_text()); inputs.add(policy_path)
    source_path = ROOT/path['initial_year']['source']['path']
    source = source_path.read_bytes(); inputs.add(source_path)
    original = deepcopy((path, policy))
    results, checks = {}, []
    def check(name, actual, expected):
        checks.append(dict(name=name, passed=actual==expected,
                           actual=effects.rel.wire(actual), expected=effects.rel.wire(expected)))
    def request(p, pol, role):
        return dict(profile='CompanyPolicyEffectRequest/1', owner=effects.OWNER, role=role,
                    path_sha256=effects.rel.native.digest(p), source_sha256=sha256(source).hexdigest(),
                    context=deepcopy(p['initial_year']['context']),
                    information=dict(use='audit_only', view='archival_exogenous_stress'), policy=deepcopy(pol))
    def run(name, p, pol, role):
        req=request(p,pol,role); saved=deepcopy((req,p,pol))
        result=effects.inspect(req,p,source); results[name]=result
        check(name+' immutable inputs',(req,p,pol),saved)
        for flag in ['source_admission','actor_information_admission','legal_authority_admission',
                     'real_behavior_evidence','forecast_admission','full_company_constructor']:
            check(name+' '+flag,result[flag],False)
        return result
    for role, status in [('generate_inputs','generated_inputs'),('validate_equalities','violates_equalities'),('compare_targets','compared_targets')]:
        r=run(role,path,policy,role);check(role+' status',r['status'],status)
        check(role+' native complete',r['native_execution_complete'],True)
        check(role+' exact owner',r['financial_effect_owner'],effects.OWNER)
        if role=='generate_inputs':
            check('generated installment',r['materialization']['allocation_trace'][0]['generated_amount'],'432/5')
            check('verified existing generator',r['materialization_verification']['status'],'verified_materialization')
            check('earlier complete year preserved',r['native_result']['years'][0],baseline['years'][0])
        else:
            check(role+' complete native baseline',r['native_result'],baseline)
            check(role+' unchanged path identity',r['evaluated_path_sha256'],r['input_path_sha256'])
            check(role+' does not rewrite history',r['history_rewritten'],False)
            check(role+' comparison count',len(r['comparisons']),4)
            check(role+' actuals',[x['actual'] for x in r['comparisons']],['396/5']*4)
            check(role+' targets',[x['target'] for x in r['comparisons']],['432/5']*4)
            check(role+' independent difference',[x['actual_minus_target'] for x in r['comparisons']],['-36/5']*4)
    check('target has no equality verdict',results['compare_targets']['equality_constraint_result'],None)
    check('target rows carry no hard constraints',any('satisfies_equality' in x for x in results['compare_targets']['comparisons']),False)
    check('known violated equalities',len(results['validate_equalities']['known_violations']),4)
    child=results['generate_inputs']['materialization']['path']
    child_policy=deepcopy(policy);child_policy['parent_path_sha256']=effects.rel.native.digest(child)
    r=run('matching child',child,child_policy,'validate_equalities')
    check('matching child equality status',r['status'],'satisfies_equalities')
    check('matching child native exact',r['native_result'],results['generate_inputs']['native_result'])
    check('matching child differences',[x['actual_minus_target'] for x in r['comparisons']],['0/1']*4)
    full=deepcopy(policy);full['fraction']='1/1'
    r=run('full settlement',path,full,'generate_inputs')
    check('generation is separate from native success',r['status'],'generated_inputs')
    check('full settlement later native refusal',r['native_result']['status'],'partial')
    check('full settlement later reason',r['native_result']['years'][-1]['run']['reason'],'over_settlement')
    check('full settlement incomplete native execution',r['native_execution_complete'],False)
    # Two completed allocations differ; a later collection cannot execute.
    stopped=deepcopy(path)
    op=next(x for x in stopped['continuations'][0]['operations'] if x['id']==policy['collection_operations'][1])
    next(a for a in op['payload']['allocations'] if a['claim_id']==policy['claim_ids'][0])['amount']='200/1'
    stopped_policy=deepcopy(policy);stopped_policy['parent_path_sha256']=effects.rel.native.digest(stopped)
    for role in ['compare_targets','validate_equalities']:
        r=run('stopped '+role,stopped,stopped_policy,role)
        check(role+' preserves partial native',r['native_result']['status'],'partial')
        check(role+' incomplete comparison',r['status'],'unresolved')
        check(role+' unavailable rows',sum(x['actual'] is None for x in r['comparisons']),2)
        check(role+' known rows',sum(x['actual']=='396/5' for x in r['comparisons']),2)
        if role=='validate_equalities':check('partial violations survive',len(r['known_violations']),2)
    unknown=deepcopy(path);unknown['initial_year']['opening_claims'][0]['amount']='unknown'
    unknown_policy=deepcopy(policy);unknown_policy['parent_path_sha256']=effects.rel.native.digest(unknown)
    r=run('unknown opening',unknown,unknown_policy,'compare_targets')
    check('unknown opening status',r['status'],'unresolved')
    check('unknown opening no actuals',[x['actual'] for x in r['comparisons']],[None]*4)
    check('unknown opening no fabricated population',r['population_inspection']['population_inspection'],None)
    zero=deepcopy(policy);zero['fraction']='0/1'
    zero_child=effects.policy_module.generate(path,zero)['path']
    zero['parent_path_sha256']=effects.rel.native.digest(zero_child)
    r=run('executed zero',zero_child,zero,'compare_targets')
    check('zero rows known',[x['actual'] for x in r['comparisons']],['0/1']*4)
    check('zero rows exact',[x['actual_minus_target'] for x in r['comparisons']],['0/1']*4)
    for name, mutation, status, reason in [
        ('other owner',lambda r:r.update(owner='Other/1'),'unsupported','native_owner'),
        ('other role',lambda r:r.update(role='predict_behavior'),'unsupported','policy_effect'),
        ('actor view',lambda r:r['information'].update(use='manager_policy'),'unsupported','actor_information_request'),
        ('stale path',lambda r:r.update(path_sha256='0'*64),'invalid','path_digest'),
        ('stale source',lambda r:r.update(source_sha256='0'*64),'invalid','source_digest'),
        ('wrong context',lambda r:r['context'].update(currency='EUR'),'invalid','context_mismatch'),
        ('extra field',lambda r:r.update(tolerance='1/10'),'invalid','request_schema'),
        ('missing role',lambda r:r.pop('role'),'invalid','request_schema'),
        ('stale policy parent',lambda r:r['policy'].update(parent_path_sha256='0'*64),'invalid','native_policy_refusal'),
        ('unknown policy',lambda r:r['policy'].update(fraction='unknown'),'unresolved','native_policy_refusal'),
    ]:
        req=request(path,policy,'compare_targets');mutation(req)
        r=effects.inspect(req,path,source);results[name]=r
        check(name+' status',r['status'],status);check(name+' reason',r['reason'],reason)
        check(name+' no generated child','materialization' in r,False)
    check('original inputs unchanged',(path,policy),original)
    for module in list(sys.modules.values())+[effects.policy_module,effects.rel.native]:
        f=getattr(module,'__file__',None)
        if f and Path(f).is_file() and Path(f).resolve().is_relative_to(ROOT):inputs.add(Path(f).resolve())
    failed=[c for c in checks if not c['passed']]
    verification=dict(status='fail' if failed else 'pass',checks=len(checks),failed=failed,cases=len(results))
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  command=[sys.executable,*sys.argv],environment=sys.version,
                  cpu_gpu='CPU-only exact arithmetic; no accelerator imports',random_seeds='N/A deterministic',
                  data_version='Retained second_year_price_revision parent and SettlementPolicyDraft/1',
                  utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
                  plan_file=PLAN,result_file=str((HERE/'result.md').relative_to(ROOT)),
                  source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)})
    for name,data in [('checks',checks),('results',results),('verification',verification),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(effects.rel.wire(data),indent=2)+chr(10))
    for name in ['effects.py','check_effects.py']:(out/name).write_bytes((HERE/name).read_bytes())
    print(json.dumps(verification))
    return bool(failed)


if __name__=='__main__':
    raise SystemExit(main())
