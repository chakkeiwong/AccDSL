from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;T=R/'docs/design/proposal/manuscript-release-prep-v551r1-20261027';slash=chr(92)
p=T/'chapters/01-purpose.tex';t=p.read_text();old='The first release must answer the following complete workflow.';assert old in t;t=t.replace(old,'The first executable product release must answer the following complete workflow.');p.write_text(t)
p=T/'chapters/10-validation.tex';t=p.read_text();old='''The parser/API comparison in P2 covers the matched debt fragment. Complete
textual authoring of the corporate profile is a further frontend task;
its absence does not remove corporate declarations from the typed API.''';new='''The parser/API comparison in P2 originally covered the matched debt fragment.
The selected company source profiles in Section~'''+slash+'''ref{sec:common-program-authoring}
now author complete methods and ordered commands with retained typed-result
comparisons. Their supplied resource and eligibility boundaries still limit
which programs they admit. General corporate textual authoring and compatible
profile migration remain further work; these selected extensions do not imply
that every corporate operation has a text frontend.''';assert old in t;t=t.replace(old,new);p.write_text(t)
components=[]
for name,short in [('release-bundle-recovery-20261027','historical-core0'),('selected-term-bundle-20261027','selected-term')]:
 src=R/'data/accounting-master'/name/'attempt-02/bundle';dst=T/'companions'/short
 assert not dst.exists();shutil.copytree(src,dst);components.append({'name':short,'source':str(src.relative_to(R)),'path':str(dst.relative_to(T)),'source_manifest_sha256':hashlib.sha256((src/'bundle-manifest.json').read_bytes()).hexdigest(),'status':'bounded_local_reproduction; independent accounting acceptance and public distribution rights not established'})
src=T/'companions/historical-core0/docs/design/fixtures';dst=T/'fixtures';shutil.copytree(src,dst)
refs=json.loads((T/'reference-map.json').read_text())
for x in refs:
 if x['reference'] not in ['spec/core-contract.md','spec/core-ir.schema.json']:x['scope']='Retained supplementary design profile; does not override a later named portable profile.'
for p in dst.iterdir():
 if p.is_file():refs.append({'reference':'fixtures/'+p.name,'source':str((R/'docs/design/fixtures'/p.name).relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Historical Core 0 authored fixture; no actual-company admission'})
(T/'reference-map.json').write_text(json.dumps(refs,indent=2)+chr(10));(T/'component-index.json').write_text(json.dumps(components,indent=2)+chr(10))
p=T/'README.md';t=p.read_text();start=t.index('Two existing executable components');end=t.index('No retained paper',start);t=t[:start]+'''Two executable components are included under companions/historical-core0 and
companions/selected-term. From this candidate directory, in the recorded Python
environment, run:

    env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B companions/historical-core0/scripts/verify_relocated.py "$(pwd)/companions/historical-core0/output-01"
    env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B companions/selected-term/scripts/verify_relocated.py output-01

Use a new output name each time. The historical command resolves output relative
to the working directory, while the selected-term command resolves it within its
bundle; the explicit historical absolute path prevents ambiguity. Each component
retains its observed environment, exact reference manifest and limitations. Do
not run archival writer main functions. Neither component covers all modern
company/sector interfaces. The top-level fixtures directory preserves the exact
historical records referenced by spec/core-contract.md; runnable source code and
its original repository layout live in the historical component.

'''+t[end:];p.write_text(t)
changes=json.loads((H/'manuscript-source-comparison.json').read_text());changes['additional_repairs']=[{'file':'chapters/01-purpose.tex','repair':'Specify first executable product release separately from manuscript acceptance.'},{'file':'chapters/10-validation.tex','repair':'Reconcile delivered selected company source authoring with retained general frontend limits.'}];changes['packaged_components']=components;(H/'manuscript-source-comparison.json').write_text(json.dumps(changes,indent=2)+chr(10))
p=H/'check_manuscript.py';t=p.read_text().replace("'simulation/temporal-frontier.tex']),changed)","'simulation/temporal-frontier.tex','chapters/10-validation.tex']),changed)");t=t.replace("'Core grammar, records']","'Core grammar, records','The parser/API comparison in P2 originally']");p.write_text(t)
print('Packaged',len(components),'components and',len(list(dst.iterdir())),'historical fixture files')
