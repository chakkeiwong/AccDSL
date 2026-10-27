"""Verify retained identities and inspected anchors; no authority admission."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys,time,platform,subprocess,os,fitz,traceback
H=Path(__file__).resolve().parent;R=H.parents[2]
C=R/'data/accounting-master/conversion-control-scope-20261026/source-attempt-02'
F=R/'data/accounting-master/contingent-conversion-authority-20261026/source-attempt-02'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def norm(s):return ' '.join(s.split())
ROWS=[
 ('AASB3',C/'aasb3-2026.pdf',[(7,['date on which it obtains control','acquisition method']),(9,['non-controlling interests','proportionate share']),(12,['previously held equity interest','reassess']),(13,['remeasure its previously held equity interest']),(14,['shall not exceed one year']),(15,['pre-existing relationships','Acquisition-related costs']),(30,['pre-existing contractual relationship'])]),
 ('AASB10',C/'aasb10-2026.pdf',[(7,['begin from the date the investor obtains control']),(31,['B86','B88','B89','B90']),(32,['deficit balance','B96','B98']),(33,['B99'])]),
 ('AASB127',C/'aasb127-2022.pdf',[(6,['at cost','equity method','11B'])]),
 ('AASB18',F/'aasb18-full.pdf',[(51,['1 January 2027','1 January 2028','Earlier application'])]),
 ('AASB18D',F/'aasb18-appendix-d.pdf',[(5,['Paragraphs 50 and B64','64R']),(18,['paragraph C2','Paragraph AG1']),(49,['AASB 127','paragraph 18G']),(50,['paragraph 18J'])]),
 ('AASB2024-4',C/'aasb2024-4b.pdf',[(5,['before 1 January 2028','paragraphs 8–10']),(6,['B99A','2028'])]),
 ('AASB2014-10',C/'aasb2014-10.pdf',[(7,['Paragraphs 25–26']),(8,['B99A'])]),
 ('AASB2026-3',C/'aasb2026-3.pdf',[(5,['Application','1 January 2027']),(6,['18','joint venture'])]),
 ('AASB2026-4',C/'aasb2026-4.pdf',[(5,['1 January 2028','AASB 18 is also applied']),(10,['AusC1.1','1 January 2028']),(16,['Australian defined terms','31 December 2027'])]),
 ('AASB2026-2',H/'source-attempt-01/aasb2026-2-compiled.pdf',[(1,['1 July 2029','21 October 2026','31 December 2027']),(7,['1 July 2029','may be applied to annual periods beginning before 1 July 2029']),(16,['Amendments to AASB 3','AusCF1']),(17,['Aus64Q.1','all other amendments']),(18,['Amendments to AASB 10','AusCF1']),(48,['AASB 2026-4 [25]','AASB 18 is also applied'])]),
 ('AASB20D',H/'source-attempt-01/aasb20-appendix-d.pdf',[(1,['1 January 2029','Appendix E']),(3,['28C','64S','regulatory assets'])]),
 ('AASB1061C',H/'source-attempt-02/aasb1061-appendix-c.pdf',[(1,['1 July 2029','Paragraph AG1','Tier 1','Tier 2'])]),
 ('AASB107',H/'cash-source-attempt-02/aasb107-2026.pdf',[(1,['before 1 January 2027']),(11,['obtaining or losing control','net of cash and cash equivalents','financing activities']),(12,['conversion of debt to equity','cash flows and non- cash changes'])])]

assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
out=H/sys.argv[1];out.mkdir(exist_ok=False);checks=[];register=[]
started=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
def ck(name,condition):
    checks.append(dict(name=name,passed=bool(condition)))
    if not condition:raise AssertionError(name)
try:
    for ident,path,anchors in ROWS:
        doc=fitz.open(path);ck(ident+'/pdf',path.read_bytes().startswith(b'%PDF-'))
        details=[]
        for number,phrases in anchors:
            text=norm(doc[number-1].get_text())
            for phrase in phrases:ck(ident+'/'+str(number)+'/'+phrase,norm(phrase).lower() in text.lower())
            details.append(dict(physical_page=number,anchors=phrases,text_sha256=sha256(text.encode()).hexdigest()))
        register.append(dict(id=ident,path=str(path.relative_to(R)),sha256=digest(path),pages=len(doc),inspected_anchors=details,source_admission=False))
    for path in sorted(H.glob('*/acquisition.json')):
        for row in json.loads(path.read_text()):
            if row['returncode']!=0:continue
            p=path.parent/row['name'];ck('download_identity/'+str(p.relative_to(H)),digest(p)==row['sha256'])
            ck('download_size/'+row['name'],p.stat().st_size==row['bytes'])
    oldlock=json.loads((C.parent/'attempt-01/source-lock.json').read_text())
    for p,s in oldlock.items():ck('prior_input/'+p,digest(R/p)==s)
    group=R/'data/accounting-master/control-group-boundary-20261027/attempt-02'
    for p,s in json.loads((group/'source-lock.json').read_text()).items():ck('group_input/'+p,digest(R/p)==s)
    ck('group_baseline_success',json.loads((group/'verification.json').read_text())['status']=='PASS')
    files={Path(__file__),H/'authority-matrix.md',H/'acquisition-period-contract.md',H/'audit-entry.md',R/'docs/plans/accounting-acquisition-period-authority-20261026.md',R/'docs/plans/accounting-acquisition-period-authority-recovery-20261027.md'}
    files.update(p for p in H.rglob('*') if p.is_file() and out not in p.parents and (p.suffix in ['.pdf','.html','.headers','.json'] or p.name in ['acquire.py','index_inventory.py','late_index.py']))
    files.update(p for p in [group/'verification.json',group/'source-lock.json',group.parent/'result.md'] if p.exists())
    files.update(p for _,p,_ in ROWS)
    lock={str(p.relative_to(R)):digest(p) for p in files}
    for p in files:
        q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    for p,s in lock.items():ck('locked/'+p,digest(R/p)==s)
    (out/'source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
    result=dict(status='PASS',source_pdfs=len(register),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,scope='Retained identities and inspected paragraph anchors; substantive reading is recorded separately and does not admit future-period accounting.')
except Exception:result=dict(status='FAIL',assertions=len(checks),error=traceback.format_exc())
for name,obj in [('verification.json',result),('checks.json',checks),('source-register.json',register)]:
    (out/name).write_text(json.dumps(obj,indent=2)+'\n')
manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic source verification',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json if successful; source-register.json retains inspected sources otherwise',plan='docs/plans/accounting-acquisition-period-authority-recovery-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
(out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
if result['status']!='PASS':raise SystemExit(1)
