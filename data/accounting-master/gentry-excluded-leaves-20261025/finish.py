"""Preserve the leaf inspection and advance the live design-audit queue."""
from pathlib import Path
from hashlib import sha256
import json,platform,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-current-design-reconciliation-20261025.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
assert not (HERE/'run-manifest.json').exists()
d=json.loads((HERE/'inspection.json').read_text())
assert d['bytes']==12984249 and d['member_count']==56
assert sha(HERE/'source_jp2.zip')==d['archive_sha256']
for row in d['leaves']:
    assert sha(ROOT/row['render'])==row['render_sha256']
    assert sha(HERE/('leaf-'+str(row['leaf'])+'.jp2'))==row['member_sha256']
text=(ROOT/'data/accounting-master/post-fiscal-reassessment-20261025/refresh.py').read_text()
start=text.index("NOTE='''");end=text.index('NAMES=',start)
note='''## Gentry excluded scan leaves inspected — 26 October 2026

Version 4.39 remains 534 pages, not_ready.
The exact 56-leaf archive matches the retained size and SHA1.
Four excluded leaves are scanner backgrounds/colour targets, with no technical text.
The missing derivation and 1979 edition equivalence remain unsupported.
Original 53 obligations, six interactions and 46 operations remain preserved.
Result: data/accounting-master/gentry-excluded-leaves-20261025/result.md.
S1–S5 partial; S6 held; S7/E3 deferred.
Next plan: docs/plans/accounting-current-design-reconciliation-20261025.md.

'''
text=text[:start]+'NOTE='+repr(note)+chr(10)+text[end:]
changes=[('accounting-gentry-excluded-leaves-20261025.md','accounting-current-design-reconciliation-20261025.md'),
 ("assert (HERE/'continuity.json').exists() and (ROOT/NEXT).exists()","assert (HERE/'inspection.json').exists() and (ROOT/NEXT).exists()"),
 ('do excluded source-scan leaves contain the missing Gentry derivation?','which current design obligations remain unspecified after the completed compositions?'),
 ('Post-fiscal reassessment:53/6/46 IDs through43 coverage files; excluded-source scan selected','Gentry excluded leaves visually inspected; no hidden technical pages recovered'),
 ('Inspect the four excluded Gentry scan leaves before current-design reconciliation','Reconcile current governing specification and original 53/6/46 obligations'),
 ("updated='2026-10-25'","updated='2026-10-26'")]
for a,b in changes:
    assert a in text,a
    text=text.replace(a,b)
assert not (HERE/'refresh.py').exists();(HERE/'refresh.py').write_text(text)
run=subprocess.run([sys.executable,'-B',str(HERE/'refresh.py')],check=True,capture_output=True,text=True)
files={str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.is_file() and p.name!='run-manifest.json'}
argv=['curl','--fail','--location','--connect-timeout','15','--max-time','55','--max-filesize','15000000',
 '--dump-header',REL+'/archive.headers','--output',REL+'/source_jp2.zip','--write-out',
 'http_code=%{http_code} size=%{size_download} time=%{time_total}'+chr(10),
 'https://archive.org/download/simulatingstrate180gent/simulatingstrate180gent_jp2.zip']
dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
 'recorded_date':'2026-10-26 Asia/Hong_Kong','retrieval_argv':argv,'retrieval_cwd':str(ROOT),
 'subsequent_commands':['CUDA_VISIBLE_DEVICES=-1 python3 -B '+REL+'/inspect_archive.py',
 'view_image: leaves 0,53,54,55,1,51,52 separately','CUDA_VISIBLE_DEVICES=-1 python3 -B '+REL+'/finish.py'],
 'environment':{'python':sys.version,'platform':platform.platform()},'cpu_gpu':'CPU only; no GPU use',
 'data_version':'Gentry1974 Archive JP2; exact SHA1 in inspection.json','random_seeds':'N/A source inspection',
 'wall_seconds':{'archive_transfer':17.491447,'other_work':'Not separately timed'},
 'plan':'docs/plans/accounting-gentry-excluded-leaves-20261025.md','result':REL+'/result.md',
 'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'docs/plans/accounting-gentry-excluded-leaves-20261025.md',ROOT/'data/accounting-master/simulator-survey-source-recovery-20261025/gentry1974-archive-metadata.json',ROOT/'data/accounting-master/simulator-survey-source-recovery-20261025/gentry1974-scandata.xml']},
 'artifacts':files,'next_plan':NEXT})
print(run.stdout.strip())
