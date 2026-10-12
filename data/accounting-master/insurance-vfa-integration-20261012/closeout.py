"""Promote the bounded 2.47 candidate, preserving full not-ready status."""
import datetime
import json
import platform
import sys
from build_candidate import ROOT, OUT, BASE, CAND, sha, save

assert not (OUT / 'completion.json').exists()
b = json.loads((OUT / 'baseline.json').read_text());c = json.loads((OUT / 'integration-checks.json').read_text())
assert c['passed'] == 123 and not c['failed'] and c['pages'] == 184
pdf = CAND / 'accounting-product-proposal.pdf';assert sha(pdf) == c['pdf_sha256']
old = '''Integrate the checked direct-participation and guarantee explanation in a
separate Version 2.47, preserving Version 2.46 and the correct conditional
10% share example. Distinguish settlement payoff, FCF and CSM; preserve the
historical AASB 17 edition and all wider limitations. Plan:
`docs/plans/accounting-insurance-vfa-integration-20261012.md`.'''
new = '''Inspect the retained insurance transition provisions to distinguish full
retrospection, modified retrospection and fair-value transition, including
method-selection and information limits. Preserve the issuer/AASB authority
distinction and Version 2.47. Plan:
`docs/plans/accounting-insurance-transition-source-20261012.md`.'''
summary = '''Version 2.47 explains direct-participation eligibility and a minimum-benefit
guarantee on PDF 136–137. The valid 10% share calculation remains, with the
settlement payoff, FCF and complete CSM movement distinguished. All 123
integration checks pass; all earlier prose, 48 displays and 93 references
remain. Eight final pages were read and the final build is clean. Thirty
source checks and fifteen exact-arithmetic checks support the bounded addition.
Actual contracts, measured inputs, current amendments and independent/human/
domain acceptance remain open. Full readiness stays not_ready.
Result: `data/accounting-master/insurance-vfa-integration-20261012/result.md`.
'''
heading = '## Current Version 2.47 direct participation and guarantees\n\n'
def once(s, old, new):
    assert s.count(old) == 1, (old, s.count(old));return s.replace(old, new, 1)
prepared = []
for r in b['pointer_snapshots']:
    p = ROOT / r['live'];assert sha(p) == r['sha256'] == sha(ROOT / r['snapshot'])
    s = p.read_text()
    if p.name == 'accounting-master-checkpoint.md':
        s = once(s, '## Current candidate\n\n', '## Current candidate\n\n**Version 2.47, 184 pages**\nPDF: '
            + str(pdf.relative_to(ROOT)) + '\nSHA256: ' + sha(pdf) + '\n\n' + summary
            + '\n## Preserved Version 2.46 token syntax and cell geometry\n\n')
    elif p.name == 'next-plan.md':
        s = once(s, '**183-page Version 2.46**', '**184-page Version 2.47**')
        s = once(s, str((BASE / 'accounting-product-proposal.pdf').relative_to(ROOT)), str(pdf.relative_to(ROOT)))
        s = once(s, b['pdf_sha256'], sha(pdf))
        s = once(s, 'Result: data/accounting-master/otsl-integration-20261012/result.md',
                 'Result: data/accounting-master/insurance-vfa-integration-20261012/result.md')
        s = once(s, '## Completed boundary\n\n', '## Completed boundary\n\n' + summary
                 + '\n## Preserved Version 2.46 token syntax and cell geometry\n\n')
    elif p.name == 'accounting-continuation-requirements-20261007.md':
        s = once(s, '## Current Version 2.46 token syntax and cell geometry', heading
            + 'E07/C05, P18/C08; MC16/19/22/28/30/32–35, G7/G8/G16.\n' + summary
            + '\n## Preserved Version 2.46 token syntax and cell geometry')
    else:
        s = once(s, 'Version 2.46 adds the token-syntax/cell-geometry distinction and decoder source finding.',
            'Version 2.47 adds the direct-participation and guarantee explanation.\nVersion 2.46 preserves the token-syntax/cell-geometry distinction and decoder source finding.')
        s = once(s, '**183-page Version 2.46**', '**184-page Version 2.47**')
        s = once(s, b['pdf_sha256'], sha(pdf))
        s = once(s, 'Current through Version 2.46 and the OTSL inquiry', 'Current through Version 2.47 and the insurance guarantee inquiry')
        s = once(s, 'VFA source inquiry complete; next unit integrates the guarantee explanation in Version 2.47',
                 'Version 2.47 integrated; next unit inspects insurance transition methods and information limits')
        s = once(s, 'Current through Version 2.46 and the latest bounded source inquiries', 'Current through Version 2.47 and the latest bounded source inquiries')
        s = once(s, 'or Version 2.46 outputs', 'or Version 2.47 outputs')
        s = once(s, 'Bounded integration delivered through Version 2.46', 'Bounded integration delivered through Version 2.47')
        s = once(s, 'The current baseline is Version 2.46;', 'The current baseline is Version 2.47;')
        s = once(s, '## Current Version 2.46 token syntax and cell geometry', heading + summary + '\n## Preserved Version 2.46 token syntax and cell geometry')
        s = once(s, 'selected VFA eligibility/guarantee/mitigation provisions and an exact settlement-component example |',
                 'selected VFA eligibility/guarantee/mitigation provisions, an exact settlement-component example and Version 2.47 explanation |')
        s = once(s, 'direct-participation/guarantee source preparation is complete and the next unit integrates its explanation.',
                 'direct-participation/guarantee preparation and Version 2.47 are complete; next inspect transition-method information limits.')
        s = once(s, '1. Follow the direct next plan: integrate the checked direct-participation\n   and guarantee explanation in a separate Version 2.47.',
                 '1. Follow the direct next plan: inspect full, modified-retrospective and\n   fair-value insurance transition and their information limits.')
    if p.name != 'accounting-continuation-requirements-20261007.md': s = once(s, old, new)
    s = once(s, 'Version 2.46 stays current until the planned 2.47 integration; not_ready.',
             'Version 2.47 now integrates the explanation; full readiness remains not_ready.')
    prepared.append((p, r, s))
rows = []
for p, r, s in prepared:
    p.write_text(s);q = OUT / 'pointers-after' / r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json', rows)
plans = ['docs/plans/accounting-insurance-vfa-integration-20261012.md', 'docs/plans/accounting-insurance-transition-source-20261012.md']
deps = [BASE / 'accounting-product-proposal.pdf', ROOT / 'data/accounting-master/insurance-vfa-source-20261012/run-manifest.json',
        ROOT / 'data/accounting-master/insurance-vfa-source-20261012/completion.json']
paths = [p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [p for p in CAND.rglob('*') if p.is_file()] + [ROOT / p for p in plans]
now = datetime.datetime.now(datetime.timezone.utc)
m = {'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),
     'plans':plans,'result':str((OUT / 'result.md').relative_to(ROOT)),
     'commands':[['python3',str((OUT / n).relative_to(ROOT))] for n in ['render_before.py','build_candidate.py','render_review.py','verify_integration.py','refine_layout.py','render_review.py','verify_integration.py','closeout.py']],
     'build_commands':['initial-build-run.json','build-run.json'],'surface_commands':'surface-runs.json',
     'reviewed_final_pages':[1,5,135,136,137,138,139,184],
     'environment':{'python':sys.executable,'version':platform.python_version(),'tex':'LuaLaTeX/BibTeX through latexmk'},
     'cpu_gpu':'CPU document processing; CUDA_VISIBLE_DEVICES=-1 for builds; no ML import or GPU probe',
     'data_version':'Protected 2.46 source and exact historical AASB 17 inquiry with finite-payoff diagnostic',
     'random_seeds':'N/A: deterministic document integration',
     'wall_seconds':{'elapsed_including_review':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
                     'checks':c['wall_seconds'],'final_build':json.loads((OUT/'build-run.json').read_text())['wall_seconds']},
     'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in deps},
     'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
     'pdf_sha256':sha(pdf),'pages':c['pages'],'readiness':'not_ready','runtime':'held','next_plan':plans[-1]}
save('run-manifest.json',m)
for p,h in (m['input_hashes'] | m['artifact_hashes']).items(): assert sha(ROOT/p)==h
save('completion.json',{'status':'bounded integration complete; independent_reader_pending','integration_checks':c['passed'],'failed':0,
     'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(m['artifact_hashes']),'readiness':'not_ready',
     'pdf_sha256':sha(pdf),'pages':c['pages'],'next_plan':plans[-1]})
print(json.dumps({'checks':c['passed'],'artifacts':len(m['artifact_hashes']),'controls':len(rows),'pdf_sha256':sha(pdf)}))
