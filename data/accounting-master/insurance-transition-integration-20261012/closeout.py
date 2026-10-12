"""Make the checked transition explanation current without closing readiness."""
import datetime
import json
import platform
import sys
from build_candidate import ROOT, OUT, BASE, CAND, sha, save

assert not (OUT/'completion.json').exists()
b=json.loads((OUT/'baseline.json').read_text());c=json.loads((OUT/'integration-checks.json').read_text())
assert c['passed']==125 and not c['failed'] and c['pages']==186
pdf=CAND/'accounting-product-proposal.pdf';assert sha(pdf)==c['pdf_sha256']
old='''Integrate the checked transition-method and information-limit explanation
in a separate Version 2.48. Preserve Version 2.47, the ASBE/AASB distinction,
C5A/C25 exceptions and the unresolved AASB 108/13 dependencies. Plan:
`docs/plans/accounting-insurance-transition-integration-20261012.md`.'''
new='''Follow the newly acquired official AASB portal/search lead for historically
applicable AASB 108 and AASB 13 primary text. Resolve impracticability/hindsight
and group-fair-value dependencies without repeating the two failed PDF URLs.
Preserve Version 2.48 and the ASBE distinction. Plan:
`docs/plans/accounting-transition-dependencies-20261012.md`.'''
summary='''Version 2.48 explains transition methods and their information limits on PDF
140–141. It retains the C5A fair-value election and C25 date exceptions and
distinguishes insurance-group fair value from underlying investments. All 125
integration checks pass; earlier prose, 48 displays and 93 references remain.
Nine final pages were inspected and the final build is clean. The 43-check
source inquiry stays frozen. AASB 108/13 details, actual group facts and
independent/human/domain acceptance remain open; full readiness is not_ready.
Result: `data/accounting-master/insurance-transition-integration-20261012/result.md`.
'''
heading='## Current Version 2.48 transition methods and information\n\n'
def once(s,a,z):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)
prepared=[]
for r in b['pointer_snapshots']:
    p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot']);s=p.read_text()
    if p.name=='accounting-master-checkpoint.md':
        s=once(s,'## Current candidate\n\n','## Current candidate\n\n**Version 2.48, 186 pages**\nPDF: '
            +str(pdf.relative_to(ROOT))+'\nSHA256: '+sha(pdf)+'\n\n'+summary
            +'\n## Preserved Version 2.47 direct participation and guarantees\n\n')
    elif p.name=='next-plan.md':
        s=once(s,'**184-page Version 2.47**','**186-page Version 2.48**')
        s=once(s,str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),str(pdf.relative_to(ROOT)))
        s=once(s,b['pdf_sha256'],sha(pdf))
        s=once(s,'Result: data/accounting-master/insurance-vfa-integration-20261012/result.md',
                 'Result: data/accounting-master/insurance-transition-integration-20261012/result.md')
        s=once(s,'## Completed boundary\n\n','## Completed boundary\n\n'+summary
                 +'\n## Preserved Version 2.47 direct participation and guarantees\n\n')
    elif p.name=='accounting-continuation-requirements-20261007.md':
        s=once(s,'## Current Version 2.47 direct participation and guarantees',heading
          +'E07/C05, E01/C03, P18/C08; MC05/08/11/19/22/28/30/32–35, G7/G8/G13/G16.\n'+summary
          +'Next internal unit: `docs/plans/accounting-transition-dependencies-20261012.md`.\n'
          +'\n## Preserved Version 2.47 direct participation and guarantees')
    else:
        s=once(s,'Version 2.47 adds the direct-participation and guarantee explanation.',
            'Version 2.48 adds transition-method and information-limit explanation.\nVersion 2.47 preserves the direct-participation and guarantee explanation.')
        s=once(s,'**184-page Version 2.47**','**186-page Version 2.48**');s=once(s,b['pdf_sha256'],sha(pdf))
        s=once(s,'Current through Version 2.47 and the insurance guarantee inquiry','Current through Version 2.48 and the transition inquiry')
        s=once(s,'transition source inquiry complete; next integrate Version 2.48','Version 2.48 integrated; next resolve the AASB 108/13 source dependencies')
        s=once(s,'Current through Version 2.47 and the latest bounded source inquiries','Current through Version 2.48 and the latest bounded source inquiries')
        s=once(s,'or Version 2.47 outputs','or Version 2.48 outputs')
        s=once(s,'Bounded integration delivered through Version 2.47','Bounded integration delivered through Version 2.48')
        s=once(s,'The current baseline is Version 2.47;','The current baseline is Version 2.48;')
        s=once(s,'## Current Version 2.47 direct participation and guarantees',heading+summary+'\n## Preserved Version 2.47 direct participation and guarantees')
        s=once(s,'and Version 2.47 explanation |','and Version 2.47 explanation; transition method/information limits in Version 2.48 |')
        s=once(s,'transition-method source preparation is complete; next integrate its information limits in Version 2.48.',
                 'transition-method preparation and Version 2.48 are complete; next resolve AASB 108/13 primary-source dependencies.')
        s=once(s,'1. Follow the direct next plan: inspect full, modified-retrospective and\n   fair-value insurance transition and their information limits.',
                 '1. Follow the direct next plan: resolve the historically applicable AASB\n   108/13 dependencies through the new official index/search lead.')
    if p.name!='accounting-continuation-requirements-20261007.md':s=once(s,old,new)
    s=once(s,'No actual group, valuation or impracticability judgment is supplied. Version\n2.47 stays current pending 2.48 integration; full readiness remains not_ready.',
             'No actual group, valuation or impracticability judgment is supplied. Version\n2.48 now integrates the explanation; full readiness remains not_ready.')
    prepared.append((p,r,s))
rows=[]
for p,r,s in prepared:
    p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
plans=['docs/plans/accounting-insurance-transition-integration-20261012.md','docs/plans/accounting-transition-dependencies-20261012.md']
deps=[BASE/'accounting-product-proposal.pdf',ROOT/'data/accounting-master/insurance-transition-source-20261012/run-manifest.json',
      ROOT/'data/accounting-master/insurance-transition-source-20261012/completion.json']
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [p for p in CAND.rglob('*') if p.is_file()] + [ROOT/p for p in plans]
now=datetime.datetime.now(datetime.timezone.utc)
commands=[['python3',str((OUT/n).relative_to(ROOT))] for n in ['build_candidate.py','refine_layout.py','verify_integration.py','closeout.py']]
commands += [['python3',str((OUT/'render_review.py').relative_to(ROOT)),*args] for args in
             [['--before','138','139'],['--before','140'],['140','141'],['140','141'],['138','139'],['142','143'],['1','5'],['186']]]
m={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),
   'plans':plans,'result':str((OUT/'result.md').relative_to(ROOT)),'commands':commands,
   'build_commands':['initial-build/build-run.json','build-run.json'],
   'surface_auditor':'/home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py',
   'surface_targets':['accounting-product-proposal.tex','sections/insurance-methods.tex'],
   'surface_options':{'max_examples':8,'outputs':['surface-root.json','surface-root.md','surface-section.json','surface-section.md']},
   'reviewed_final_pages':[1,5,138,139,140,141,142,143,186],
   'environment':{'python':sys.executable,'version':platform.python_version(),'tex':'LuaLaTeX/BibTeX through latexmk'},
   'cpu_gpu':'CPU document processing; CUDA_VISIBLE_DEVICES=-1 during builds; no ML import or GPU probe',
   'data_version':'Protected Version 2.47 and closed historical AASB 17 transition inquiry',
   'random_seeds':'N/A: deterministic document integration',
   'wall_seconds':{'elapsed_including_review':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
                   'checks':c['wall_seconds'],'final_build':json.loads((OUT/'build-run.json').read_text())['wall_seconds']},
   'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in deps},
   'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
   'pdf_sha256':sha(pdf),'pages':c['pages'],'readiness':'not_ready','next_plan':plans[-1]}
save('run-manifest.json',m)
for p,h in (m['input_hashes']|m['artifact_hashes']).items():assert sha(ROOT/p)==h
save('completion.json',{'status':'bounded integration complete; independent_reader_pending','integration_checks':c['passed'],'failed':0,
    'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(m['artifact_hashes']),
    'readiness':'not_ready','pdf_sha256':sha(pdf),'pages':c['pages'],'next_plan':plans[-1]})
print(json.dumps({'checks':c['passed'],'artifacts':len(m['artifact_hashes']),'controls':len(rows),'pdf_sha256':sha(pdf)}))
