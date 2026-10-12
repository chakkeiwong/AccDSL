"""Close the bounded integration once; preserve all earlier evidence."""
import datetime, json, platform, sys
from build_candidate import ROOT, OUT, BASE, CAND, sha, save
assert not (OUT/'completion.json').exists()
b=json.loads((OUT/'baseline.json').read_text())
c=json.loads((OUT/'integration-checks.json').read_text())
assert c['passed']==137 and not c['failed'] and c['pages']==187
pdf=CAND/'accounting-product-proposal.pdf';assert sha(pdf)==c['pdf_sha256']
tick=chr(96)
next_plan='docs/plans/accounting-munich-transition-disclosures-20261012.md'
this_plan='docs/plans/accounting-transition-dependencies-integration-20261012.md'
old="""Integrate the newly supported hindsight, market-participant valuation and
own-non-performance-risk distinctions in a separate Version 2.49. Preserve
Version 2.48, historical editions, insurance-specific exceptions and actual
group/valuation limitations. Plan:
"""+tick+this_plan+tick+'.'
new="""Inspect the retained Munich Re 2023 annual report's transition methods,
measurement assumptions and disclosed opening balances. Preserve historical
rule/issuer distinctions, actual-input unknowns and corpus exposure. Plan:
"""+tick+next_plan+tick+'.'
summary="""Version 2.49 explains the reasonable-effort and historical-information tests
on PDF 140 and market-participant valuation and own-non-performance-risk
differences on PDF 141. All 137 integration checks pass; prior prose, 48 displays
and 93 references survive, with two references added. Eight final pages were
inspected and the build is clean. Actual group judgments, valuation, current
applicability and independent/human/domain acceptance remain open. Full
readiness stays not_ready.
Result: """+tick+'data/accounting-master/transition-dependencies-integration-20261012/result.md'+tick+'.\n'
heading='## Current Version 2.49 hindsight and measurement bases\n\n'
prior='## Preserved Version 2.48 transition methods and information'
def once(s,a,z):
    assert s.count(a)==1,(a,s.count(a))
    return s.replace(a,z,1)
prepared=[]
for r in b['pointer_snapshots']:
    p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot'])
    s=p.read_text()
    if p.name=='accounting-master-checkpoint.md':
        s=once(s,'## Current candidate\n\n','## Current candidate\n\n**Version 2.49, 187 pages**\nPDF: '
            +str(pdf.relative_to(ROOT))+'\nSHA256: '+sha(pdf)+'\n\n'+summary+'\n'+prior+'\n\n')
    elif p.name=='next-plan.md':
        for a,z in [('**186-page Version 2.48**','**187-page Version 2.49**'),
                    (str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),str(pdf.relative_to(ROOT))),
                    (b['pdf_sha256'],sha(pdf)),
                    ('Result: data/accounting-master/insurance-transition-integration-20261012/result.md',
                     'Result: data/accounting-master/transition-dependencies-integration-20261012/result.md')]:
            s=once(s,a,z)
        s=once(s,'## Completed boundary\n\n','## Completed boundary\n\n'+summary+'\n'+prior+'\n\n')
    elif p.name=='accounting-continuation-requirements-20261007.md':
        s=once(s,'## Current Version 2.48 transition methods and information',
            heading+'E07/C05, E01/C03, P18/C08; MC05/19/22/28/30/32–35.\n'+summary
            +'Next internal unit: '+tick+next_plan+tick+'.\n\n'+prior)
        s=once(s,'Next internal unit: '+tick+this_plan+tick+'.',
            'This historical integration is complete; current next unit is above.')
    else:
        pairs=[
            ('Version 2.48 adds transition-method and information-limit explanation.',
             'Version 2.49 explains retrospective information and fair-value/FCF distinctions.\nVersion 2.48 preserves transition-method and information-limit explanation.'),
            ('**186-page Version 2.48**','**187-page Version 2.49**'),
            (b['pdf_sha256'],sha(pdf)),
            ('Current through Version 2.48 and the transition inquiry','Current through Version 2.49 and the transition dependency inquiry'),
            ('AASB 108/13 dependency source review complete; next integrate Version 2.49','Version 2.49 integrated; next inspect Munich Re transition disclosures'),
            ('Current through Version 2.48 and the latest bounded source inquiries','Current through Version 2.49 and the latest bounded source inquiries'),
            ('or Version 2.48 outputs','or Version 2.49 outputs'),
            ('Bounded integration delivered through Version 2.48','Bounded integration delivered through Version 2.49'),
            ('The current baseline is Version 2.48;','The current baseline is Version 2.49;'),
            ('## Current Version 2.48 transition methods and information',heading+summary+'\n'+prior),
            ('transition method/information limits in Version 2.48 |','transition method/information limits in Version 2.48 and hindsight/measurement bases in Version 2.49 |'),
            ('selected AASB 108/13 dependencies are now inspected; next integrate the supported distinctions in Version 2.49.',
             'selected AASB 108/13 dependencies are inspected and integrated in Version 2.49; next inspect Munich Re 2023 transition methods and measurement disclosures.'),
            ('1. Follow the direct next plan: integrate the checked hindsight and\n   fair-value/FCF distinctions in a separate Version 2.49.',
             '1. Follow the direct next plan: inspect Munich Re 2023 transition methods,\n   measurement assumptions and disclosed opening balances.')]
        for a,z in pairs:s=once(s,a,z)
    if p.name!='accounting-continuation-requirements-20261007.md':s=once(s,old,new)
    s=once(s,'remain open. Version 2.48 stays current pending 2.49 integration; not_ready.',
        'remain open. Version 2.49 now integrates these distinctions; not_ready.')
    prepared.append((p,r,s))
rows=[]
for p,r,s in prepared:
    p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
plans=[this_plan,next_plan]
deps=[BASE/'accounting-product-proposal.pdf',ROOT/'data/accounting-master/transition-dependencies-20261012/run-manifest.json',
      ROOT/'data/accounting-master/transition-dependencies-20261012/completion.json']
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [p for p in CAND.rglob('*') if p.is_file()] + [ROOT/p for p in plans]
now=datetime.datetime.now(datetime.timezone.utc)
commands=[['python3',str((OUT/n).relative_to(ROOT))] for n in ['build_candidate.py','verify_integration.py','closeout.py']]
commands += [['python3',str((OUT/'render_review.py').relative_to(ROOT)),*a] for a in [
    ['--before','140','141'],['--before','142'],['140','141'],['142','143'],['1','5'],['139','178']]]
m={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),
   'plans':plans,'result':str((OUT/'result.md').relative_to(ROOT)),'commands':commands,
   'build_command':json.loads((OUT/'build-run.json').read_text()),
   'surface_auditor':'/home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py',
   'surface_targets':['accounting-product-proposal.tex','sections/insurance-methods.tex'],
   'surface_options':{'max_examples':8,'outputs':['surface-root.json','surface-root.md','surface-section.json','surface-section.md']},
   'reviewed_final_pages':[1,5,139,140,141,142,143,178],
   'environment':{'python':sys.executable,'version':platform.python_version(),'tex':'LuaLaTeX/BibTeX through latexmk'},
   'cpu_gpu':'CPU document processing; CUDA_VISIBLE_DEVICES=-1 during build; no ML import or GPU probe',
   'data_version':'Protected Version 2.48 and closed historical AASB 108/13 dependency inquiry',
   'random_seeds':'N/A: deterministic document integration',
   'wall_seconds':{'elapsed_including_review':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
                   'checks':c['wall_seconds'],'build':json.loads((OUT/'build-run.json').read_text())['wall_seconds']},
   'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in deps},
   'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
   'pdf_sha256':sha(pdf),'pages':c['pages'],'readiness':'not_ready','next_plan':next_plan}
save('run-manifest.json',m)
for p,h in (m['input_hashes']|m['artifact_hashes']).items():assert sha(ROOT/p)==h
save('completion.json',{'status':'bounded integration complete; independent_reader_pending',
    'integration_checks':c['passed'],'failed':0,'manifest_sha256':sha(OUT/'run-manifest.json'),
    'bound_artifacts':len(m['artifact_hashes']),'readiness':'not_ready',
    'pdf_sha256':sha(pdf),'pages':c['pages'],'next_plan':next_plan})
print(json.dumps({'checks':c['passed'],'artifacts':len(m['artifact_hashes']),'controls':len(rows),'pdf_sha256':sha(pdf)}))
