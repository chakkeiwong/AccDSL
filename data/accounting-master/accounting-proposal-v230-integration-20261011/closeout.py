#!/usr/bin/env python3
"""Bind the final reviewed Version 2.30 and its control snapshots."""
import hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2)+chr(10))
def main():
    start=time.monotonic(); checks=[]
    def ck(name,yes): checks.append({'check':name,'passed':bool(yes)})
    ms=json.loads((OUT/'manuscript-checks.json').read_text())
    baseline=json.loads((OUT/'baseline.json').read_text())
    render=json.loads((OUT/'render-manifest.json').read_text())
    ck('91/0 manuscript checks',ms['passed']==91 and ms['failed']==0)
    for key in ['baseline_pdf','candidate_pdf']:
        item=ms[key]; ck(key+' bytes match',sha(ROOT/item['path'])==item['sha256'])
    ck('final ten-page render bound',render['pdf_sha256']==ms['candidate_pdf']['sha256'] and len(render['rendered_pages'])==10 and all(sha(ROOT/x['image'])==x['sha256'] for x in render['rendered_pages']))
    ck('four previous controls preserved',len(baseline['pointer_relocations'])==4 and all(sha(ROOT/x['preserved_path'])==x['sha256'] for x in baseline['pointer_relocations']))
    controls={x['historical_path']:sha(ROOT/x['historical_path']) for x in baseline['pointer_relocations']}
    for p in controls:
        t=(ROOT/p).read_text()
        ck('live control '+p,'Version 2.30' in t and ms['candidate_pdf']['sha256'] in t and 'not_ready' in t)
    for name in ['result.md','author-review.md','four-ledger-review.md','next-source-frontier.md']:
        ck(name+' exists',(OUT/name).is_file())
    source=ROOT/'data/accounting-master/jpmorgan-default-remedies-20261011'
    sr=json.loads((source/'run-manifest.json').read_text())
    ck('source manifest records 175/0',sr['source_checks']=={'passed':175,'failed':0})
    ck('source artifact hashes remain valid',all(sha(ROOT/p)==h for p,h in sr['artifact_hashes'].items()))
    if any(not x['passed'] for x in checks):
        write('closeout-checks.json',{'checks':checks,'failed':sum(not x['passed'] for x in checks)})
        raise SystemExit(1)
    paths=[p for p in OUT.rglob('*') if p.is_file() and p.name not in {'run-manifest.json','closeout-checks.json','completion.json'} and '__pycache__' not in p.parts]
    paths += [ROOT/ms['plan'],ROOT/'docs/plans/accounting-jpmorgan-default-remedy-summaries-20261011.md',source/'run-manifest.json']
    manifest={'recorded_at':'2026-10-11','unit':'Version 2.30 default/remedy manuscript integration','git_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip(),'git_branch':'main','git_state':'Unrelated work preserved; read-only .git prevents commit; no retry.','plan':ms['plan'],'result':str((OUT/'result.md').relative_to(ROOT)),'candidate_pdf':ms['candidate_pdf'],'baseline_pdf':ms['baseline_pdf'],'commands':['TEXMFVAR=/tmp/accdsl-texmfvar TEXMFCACHE=/tmp/accdsl-texmfvar latexmk -g -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex','CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v230-integration-20261011/check_integration.py','CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/accounting-proposal-v230-integration-20261011/closeout.py'],'environment':{'tex':'LuaHBTeX 1.24.0 / Latexmk 4.88 / TinyTeX','python':'Python 3.11','cpu_gpu':'CPU-only documentary checks; GPU intentionally hidden','random_seeds':'N/A; deterministic'},'wall_time':{'build':'Not measured end-to-end; no inferred duration','verification':json.loads((OUT/'check-run.json').read_text())['wall_seconds'],'closeout_seconds':time.monotonic()-start},'data_version':sr['data_version'],'source_checks':175,'manuscript_checks':91,'controls':controls,'pointer_relocations':baseline['pointer_relocations'],'source_manifest':{'path':str((source/'run-manifest.json').relative_to(ROOT)),'sha256':sha(source/'run-manifest.json')},'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in paths},'readiness':'not_ready','independent_reader':'pending','domain_acceptance':'pending','legal_acceptance':'pending'}
    write('run-manifest.json',manifest)
    report={'recorded_at':'2026-10-11','checks':checks,'passed':len(checks),'failed':0,'run_manifest_sha256':sha(OUT/'run-manifest.json'),'wall_seconds':time.monotonic()-start}
    write('closeout-checks.json',report)
    write('completion.json',{'status':'closed_bounded_integration','recorded_at':'2026-10-11','candidate_pdf':ms['candidate_pdf'],'source_checks':175,'manuscript_checks':91,'closeout_checks':len(checks),'run_manifest_sha256':report['run_manifest_sha256'],'readiness':'not_ready','next_frontier':str((OUT/'next-source-frontier.md').relative_to(ROOT))})
    print(json.dumps({'passed':len(checks),'failed':0,'candidate':ms['candidate_pdf']}))
if __name__=='__main__': main()
