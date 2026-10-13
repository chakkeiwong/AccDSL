"""Freeze the completed FX example, manuscript evidence and current pointers."""
import datetime
import json
import platform
import re
import time

import fitz

from build_candidate import CAND,OUT,ROOT,save,sha


def main():
    assert not (OUT/'completion.json').exists()
    started=time.monotonic();checks=[]
    baseline=json.loads((OUT/'baseline.json').read_text());source=json.loads((OUT/'source-checks.json').read_text())
    manuscript=json.loads((OUT/'manuscript-checks.json').read_text())

    def ck(name,yes):
        checks.append({'name':name,'passed':bool(yes)})

    ck('source checks pass',source['passed']==49 and not source['failed'])
    ck('manuscript checks pass',manuscript['passed']==124 and not manuscript['failed'])
    recovery=json.loads((ROOT/'data/accounting-master/munich-publication-imprints-20261012/recovery-baseline.json').read_text())
    for rel,digest in recovery['protected_hashes'].items():ck('frozen evidence '+rel,sha(ROOT/rel)==digest)
    controls={}
    for row in baseline['controls']:
        ck('prior control '+row['live'],sha(ROOT/row['snapshot'])==row['sha256'])
        p=ROOT/row['live'];t=p.read_text()
        ck('current control '+row['live'],all(x in t for x in ['Version 2.52','195 pages',manuscript['pdf_sha256'],
           'not_ready','intragroup-fx-20261013/result.md','accounting-readiness-refresh-20261013.md']))
        if 'requirements' not in p.name:
            ck('local links '+row['live'],all((p.parent/t.split('#')[0]).exists() for t in re.findall(r'\]\(([^)]+)\)',t) if not t.startswith(('http','#'))))
        controls[row['live']]=sha(p)
    failed=[c['name'] for c in checks if not c['passed']]
    if failed:
        print(json.dumps({'failed':failed}));raise SystemExit(1)
    plan='docs/plans/accounting-intragroup-fx-20261013.md';next_plan='docs/plans/accounting-readiness-refresh-20261013.md'
    paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [p for p in CAND.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark','.pdf'}]
    paths += [ROOT/plan,ROOT/next_plan]
    build=json.loads((OUT/'build-run.json').read_text())
    manifest={'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'git_commit':baseline['git_commit'],
        'plan':plan,'result':str((OUT/'result.md').relative_to(ROOT)),'next_plan':next_plan,
        'commands':['python3 data/accounting-master/intragroup-fx-20261013/check_evidence.py',
                    'python3 data/accounting-master/intragroup-fx-20261013/build_candidate.py',
                    'python3 data/accounting-master/intragroup-fx-20261013/check_manuscript.py',
                    'python3 data/accounting-master/intragroup-fx-20261013/closeout.py'],
        'final_build':build,'earlier_layout':'first-layout/',
        'environment':{'python':platform.python_version(),'pymupdf':fitz.VersionBind,
            'cpu_gpu':'CPU-only; GPU intentionally hidden during builds; no framework/GPU probes','seeds':'N/A deterministic exact arithmetic'},
        'data_version':'Retained original EU2023/1803 and date corrigendum; hashes in baseline.json',
        'wall_seconds':{'final_build':build['wall_seconds'],'source_checks':source['wall_seconds'],
                        'manuscript_checks':manuscript['wall_seconds'],'closeout':time.monotonic()-started,'interactive_work':'not timed'},
        'source_checks':49,'manuscript_checks':124,'closeout_checks':len(checks),
        'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in paths},'controls_at_closeout':controls,
        'pdf_sha256':manuscript['pdf_sha256'],'readiness':'not_ready','human_acceptance':'pending'}
    save('run-manifest.json',manifest);digest=sha(OUT/'run-manifest.json')
    save('closeout-checks.json',{'checks':checks,'passed':len(checks),'failed':[],'manifest_sha256':digest})
    save('completion.json',{'status':'closed_fx_case_and_v252_integration','source_checks':49,'manuscript_checks':124,
                         'closeout_checks':len(checks),'manifest_sha256':digest,'readiness':'not_ready'})
    print(json.dumps({'source_checks':49,'manuscript_checks':124,'closeout_checks':len(checks),'failed':[]}))


if __name__=='__main__':
    main()
