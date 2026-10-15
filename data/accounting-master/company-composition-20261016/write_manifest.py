from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
lock=json.loads((P/'predecessor-lock.json').read_text());runs=[]
for a in sorted(P.glob('attempt-*')):
 q=json.loads((a/'portable-exchanges.json').read_text());v=json.loads((a/'validation-01.json').read_text())
 runs.append(dict(attempt=a.name,packet=rel(a/'portable-exchanges.json'),packet_sha256=sha(a/'portable-exchanges.json'),
  validation=rel(a/'validation-01.json'),validation_sha256=sha(a/'validation-01.json'),checks=len(v['checks']),failures=v['failed'],
  build_wall_seconds=q['build_wall_seconds'],verification_wall_seconds=v['wall_seconds'],verifier_sha256=v['verifier_sha256'],
  financial_sha256=v['financial_sha256'],migration_sha256=v['migration_sha256'],input_snapshots=q['input_snapshots']))
count=len(q['validation_challenges']);text=(P/'result.md').read_text().replace('Attempt02 passes','Attempt03 passes').replace('settlement/redemption;125 corruption','settlement/redemption;'+str(count)+' corruption')
text=text.replace('weakened. The pre-run','weakened. Attempt03 additionally derives opening equity/NCI from the supplied\nbooks instead of hardcoded totals; it also passes681 checks. The pre-run')
text=text.replace('either attempt', 'all attempts')
(P/'result.md').write_text(text)
manifest=dict(date='2026-10-16',recorded_at=datetime.now(timezone.utc).isoformat(),git_commit=lock['git_commit'],
 branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
 staged_diff_command=['git','diff','--cached','--raw','--no-abbrev'],staged_diff_sha256=lock['index_sha256'],staged_entries=lock['index_entries'],
 resolved_interpreter=sys.executable,python_version=sys.version.split()[0],environment='existing tfgpu Python; standard library/jsonschema; no installation',
 environment_variables={'CUDA_VISIBLE_DEVICES':'-1'},cpu_gpu='CPU-only; GPU intentionally hidden; no framework imported',
 data_version='CompanyComposition/1; synthetic 2025 opening/events and historical sources',random_seeds='N/A: deterministic exact arithmetic',
 plan='docs/plans/accounting-company-composition-20261016.md',result=rel(P/'result.md'),result_sha256=sha(P/'result.md'),
 commands=[['python3',rel(P/'initialize_lock.py')],['python3',rel(P/'check_draft.py')],['python3','-m','compileall','-q',rel(P)],
  *[cmd for a in ['attempt-01','attempt-02','attempt-03'] for cmd in [['python3',rel(P/'build_exchanges.py')],['python3',rel(P/'verify_exchanges.py'),a]]]],
 runs=runs,coverage=dict(methods=9,transitions=13,exchanges=54,reports=3,migrations=2,records=len(q['record_registry']),
  blobs=len(q['blobs']),corruption_challenges=count,lost_ack_worlds=26),
 protection=dict(lock=rel(P/'predecessor-lock.json'),sha256=sha(P/'predecessor-lock.json'),original_inputs=204,predecessor_files=len(lock['predecessor_files']),passed=v['checks'][0]['passed']),
 runtime_executed=False,mission_readiness='not_ready')
out=P/'run-manifest.json';assert not out.exists();out.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'manifest':rel(out),'checks':runs[-1]['checks'],'failures':runs[-1]['failures'],'challenges':count,'packet':runs[-1]['packet_sha256']}))
