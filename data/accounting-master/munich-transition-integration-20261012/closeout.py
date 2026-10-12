"""Close the checked real-insurer example once and refresh four live controls."""
import datetime,json,platform,sys
from build_candidate import ROOT,OUT,BASE,CAND,sha,save
assert not (OUT/'completion.json').exists()
b=json.loads((OUT/'baseline.json').read_text());c=json.loads((OUT/'integration-checks.json').read_text())
assert c['passed']==133 and not c['failed'] and c['pages']==190
pdf=CAND/'accounting-product-proposal.pdf';assert sha(pdf)==c['pdf_sha256']
tick=chr(96);this_plan='docs/plans/accounting-munich-transition-integration-20261012.md'
next_plan='docs/plans/accounting-munich-publication-imprints-20261012.md'
old="""Integrate the checked Munich Re transition disclosure, rounded equity bridge
and separate issued/held margins in Version 2.50. Preserve the dated method
populations, issuer-specific inputs and actual-group unknowns. Plan:
"""+tick+this_plan+tick+'.'
new="""Follow the explicit report-imprint lead to inspect declared publication dates
in the retained Munich Re 2018–2025 annual/interim sequence. Distinguish issuer
date statements from independent historical byte availability. Plan:
"""+tick+next_plan+tick+'.'
summary="""Version 2.50 adds the Munich Re transition case on PDF 143–144: method
populations, rounded equity bridge, separate issued/held margins and dated
issuer risk-adjustment inputs. All 133 integration checks pass; prior prose,
48 displays and 95 references survive, with one reference added. Ten final
pages were inspected and the final build is clean. The initial split-paragraph
layout is preserved and repaired. Actual groups, valuation inputs, applicable
authority and independent/human/domain acceptance remain open; not_ready.
Result: """+tick+'data/accounting-master/munich-transition-integration-20261012/result.md'+tick+'.\n'
heading='## Current Version 2.50 Munich Re transition disclosure\n\n'
prior='## Preserved Version 2.49 hindsight and measurement bases'
def once(s,a,z):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)
prepared=[]
for r in b['pointer_snapshots']:
    p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot']);s=p.read_text()
    if p.name=='accounting-master-checkpoint.md':
        s=once(s,'## Current candidate\n\n','## Current candidate\n\n**Version 2.50, 190 pages**\nPDF: '
            +str(pdf.relative_to(ROOT))+'\nSHA256: '+sha(pdf)+'\n\n'+summary+'\n'+prior+'\n\n')
    elif p.name=='next-plan.md':
        for a,z in [('**187-page Version 2.49**','**190-page Version 2.50**'),
                    (str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),str(pdf.relative_to(ROOT))),
                    (b['pdf_sha256'],sha(pdf)),
                    ('Result: data/accounting-master/transition-dependencies-integration-20261012/result.md',
                     'Result: data/accounting-master/munich-transition-integration-20261012/result.md')]:s=once(s,a,z)
        s=once(s,'## Completed boundary\n\n','## Completed boundary\n\n'+summary+'\n'+prior+'\n\n')
    elif p.name=='accounting-continuation-requirements-20261007.md':
        s=once(s,'## Current Version 2.49 hindsight and measurement bases',
            heading+'E01/C03, E07/C05, P18/C08; MC02/03/05/19/22/28/30/32–35.\n'+summary
            +'Next internal unit: '+tick+next_plan+tick+'.\n\n'+prior)
        s=once(s,'Next internal unit: '+tick+this_plan+tick+'.','This historical integration is complete; current next unit is above.')
    else:
        pairs=[
            ('Version 2.49 explains retrospective information and fair-value/FCF distinctions.',
             'Version 2.50 adds a checked real-insurer transition disclosure example.\nVersion 2.49 preserves retrospective information and fair-value/FCF distinctions.'),
            ('**187-page Version 2.49**','**190-page Version 2.50**'),(b['pdf_sha256'],sha(pdf)),
            ('Current through Version 2.49 and the transition dependency inquiry','Current through Version 2.50 and the Munich Re transition inquiry'),
            ('Munich Re transition disclosure inquiry complete; next integrate Version 2.50','Version 2.50 integrated; next inspect Munich Re publication imprints'),
            ('Current through Version 2.49 and the latest bounded source inquiries','Current through Version 2.50 and the latest bounded source inquiries'),
            ('or Version 2.49 outputs','or Version 2.50 outputs'),
            ('Bounded integration delivered through Version 2.49','Bounded integration delivered through Version 2.50'),
            ('The current baseline is Version 2.49;','The current baseline is Version 2.50;'),
            ('## Current Version 2.49 hindsight and measurement bases',heading+summary+'\n'+prior),
            ('hindsight/measurement bases in Version 2.49 |','hindsight/measurement bases in Version 2.49 and the Munich Re transition case in Version 2.50 |'),
            ('the Munich Re 2023 disclosure inquiry is complete; next integrate the supported case in Version 2.50.',
             'the Munich Re 2023 disclosure inquiry and Version 2.50 case are complete. The new imprint-date lead now feeds E01 source timing.'),
            ('1. Follow the direct next plan: integrate the checked Munich Re transition\n   methods, rounded bridge and scoped margin evidence in Version 2.50.',
             '1. Follow the direct next plan: inspect declared publication dates in the\n   retained Munich Re report sequence using the new explicit imprint lead.')]
        for a,z in pairs:s=once(s,a,z)
    if p.name!='accounting-continuation-requirements-20261007.md':s=once(s,old,new)
    s=once(s,'open. Added author-annotation exposure is recorded. Version 2.49 stays current\npending 2.50 integration; readiness remains not_ready.',
        'open. Added author-annotation exposure is recorded. Version 2.50 integrates\nthe bounded example; readiness remains not_ready.')
    prepared.append((p,r,s))
rows=[]
for p,r,s in prepared:
    p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
plans=[this_plan,next_plan]
deps=[BASE/'accounting-product-proposal.pdf',ROOT/'data/accounting-master/munich-transition-disclosures-20261012/run-manifest.json',
 ROOT/'data/accounting-master/munich-transition-disclosures-20261012/completion.json',
 ROOT/'data/financial-report-benchmark/documents/munich_re/munich_re-2023-annual/original.pdf']
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [p for p in CAND.rglob('*') if p.is_file()] + [ROOT/p for p in plans]
now=datetime.datetime.now(datetime.timezone.utc)
commands=[['python3',str((OUT/n).relative_to(ROOT))] for n in ['build_candidate.py','refine_layout.py','verify_integration.py','closeout.py']]
commands += [['python3',str((OUT/'render_review.py').relative_to(ROOT)),*a] for a in [
 ['--before','140','141'],['--before','142','143'],['143','144'],['143','144'],['142','145'],['1','5'],['6','187'],['146','190']]]
m={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),'plans':plans,
 'result':str((OUT/'result.md').relative_to(ROOT)),'commands':commands,
 'build_commands':['initial-build/build-run.json','build-run.json'],
 'source_imprint':'Python/PyMuPDF extraction of source PDF page 330 to source-imprint-page-330.txt; identity in source-imprint.json',
 'surface_auditor':'/home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py',
 'surface_targets':['accounting-product-proposal.tex','sections/insurance-methods.tex'],
 'surface_options':{'max_examples':8,'outputs':['surface-root.json','surface-root.md','surface-section.json','surface-section.md']},
 'reviewed_final_pages':[1,5,6,142,143,144,145,146,187,190],
 'environment':{'python':sys.executable,'version':platform.python_version(),'tex':'LuaLaTeX/BibTeX through latexmk'},
 'cpu_gpu':'CPU document processing; CUDA_VISIBLE_DEVICES=-1 during builds; no ML import or GPU probe',
 'data_version':'Protected Version 2.49 and closed Munich Re 2023 disclosure inquiry; supplementary exact-report imprint',
 'random_seeds':'N/A: deterministic document integration',
 'wall_seconds':{'elapsed_including_review':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
                 'checks':c['wall_seconds'],'final_build':json.loads((OUT/'build-run.json').read_text())['wall_seconds']},
 'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in deps},
 'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
 'pdf_sha256':sha(pdf),'pages':c['pages'],'readiness':'not_ready','next_plan':next_plan}
save('run-manifest.json',m)
for p,h in (m['input_hashes']|m['artifact_hashes']).items():assert sha(ROOT/p)==h
save('completion.json',{'status':'bounded integration complete; independent_reader_pending',
 'integration_checks':c['passed'],'failed':0,'manifest_sha256':sha(OUT/'run-manifest.json'),
 'bound_artifacts':len(m['artifact_hashes']),'readiness':'not_ready','pdf_sha256':sha(pdf),'pages':c['pages'],'next_plan':next_plan})
print(json.dumps({'checks':c['passed'],'artifacts':len(m['artifact_hashes']),'controls':len(rows),'pdf_sha256':sha(pdf)}))
