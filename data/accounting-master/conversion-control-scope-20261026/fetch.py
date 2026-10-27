from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
H=Path(__file__).resolve().parent;O=H/sys.argv[1];O.mkdir(exist_ok=False)
items={
'aasb10-2026.pdf':'https://standards.aasb.gov.au/sites/default/files/2026-03/AASB10_07-15_ACOMPnov24_01-26.pdf',
'aasb127-2022.pdf':'https://www.aasb.gov.au/admin/file/content105/c9/AASB127_08-15_COMPdec21_01-22.pdf',
'aasb3-2026.pdf':'https://standards.aasb.gov.au/sites/default/files/2026-10/AASB3_08-15_COMPdec22_07-26.pdf',
'aasb2024-4b.pdf':'https://aasb.gov.au/admin/file/content105/c9/AASB2024-4b_11-24_01-28.pdf',
'aasb2014-10.pdf':'https://www.aasb.gov.au/admin/file/content105/c9/AASB2014-10_12-14.pdf',
'aasb2026-3.pdf':'https://standards.aasb.gov.au/sites/default/files/2026-09/AASB2026-3_08-26.pdf',
'aasb2026-4.pdf':'https://standards.aasb.gov.au/sites/default/files/2026-09/AASB2026-4_08-26_0.pdf',
'standards-index.html':'https://standards.aasb.gov.au/accounting-standards',
'aasb10-index.html':'https://standards.aasb.gov.au/aasb-10-nov-2024-0',
'aasb127-index.html':'https://standards.aasb.gov.au/aasb-127-dec-2021',
'aasb3-index.html':'https://standards.aasb.gov.au/aasb-3-dec-2022-0'}
manifest=[]
for name,url in items.items():
 start=datetime.now(timezone.utc).isoformat();p=O/name
 cmd=['curl','--location','--fail','--silent','--show-error','--connect-timeout','10','--max-time','30','--max-filesize','20971520','--dump-header',str(O/(name+'.headers')),'--output',str(p),'--write-out','%{http_code}\t%{url_effective}\t%{size_download}',url]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
 row={'name':name,'url':url,'started_utc':start,'ended_utc':datetime.now(timezone.utc).isoformat(),'command':cmd,'returncode':r.returncode,'response':r.stdout,'error':r.stderr,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None,'bytes':p.stat().st_size if p.exists() else None}
 manifest.append(row);(O/'acquisition.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:row[k] for k in ['name','returncode','bytes','error']}),flush=True)
 if r.returncode:break
