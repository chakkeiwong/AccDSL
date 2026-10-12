"""Discover report-specific date markers in retained text, without changing corpus."""
import datetime,hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'baseline.json').exists() and not (OUT/'completion.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
source=ROOT/'data/financial-report-benchmark/source-evidence.json'
selected={k:r for k,r in json.loads(source.read_text())['documents'].items() if r['issuer_id']=='munich_re'}
assert len(selected)==16
snapshots=[]
for p in ['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-current.md',
          'docs/plans/accounting-continuation-requirements-20261007.md','data/accounting-master/next-plan.md']:
    q=OUT/'pointers-before'/p;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,q)
    snapshots.append({'live':p,'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('baseline.json',{'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  'pointer_snapshots':snapshots,'source_evidence_sha256':sha(source),'readiness':'not_ready'})
save('selected-sources.json',selected)
pattern=r'online publication date|date of publication|publication date'
rows=[]
for key,r in sorted(selected.items()):
    assert sha(ROOT/r['local_path'])==r['sha256']
    text_path=ROOT/r['extracted_text_path']
    command=['rg','-n','-i','-m','5',pattern,str(text_path)]
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode in [0,1],result.stderr
    pages=text_path.read_text().split('\f')
    matches=[{'pdf_page':i,'markers':re.findall(pattern,t,re.I)}
             for i,t in enumerate(pages,1) if re.search(pattern,t,re.I)]
    rows.append({'document_id':key,'pdf':r['local_path'],'pdf_sha256':r['sha256'],
                 'text_path':r['extracted_text_path'],'text_sha256':sha(text_path),
                 'rg_command':command,'rg_exit_code':result.returncode,
                 'candidate_pages':matches,'status':'candidate' if matches else 'no explicit marker found in this search'})
save('discovery.json',rows)
print(json.dumps([{'id':r['document_id'],'pages':[m['pdf_page'] for m in r['candidate_pages']]} for r in rows]))
