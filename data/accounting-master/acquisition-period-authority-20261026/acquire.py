"""Bounded retention of official sources newly found during the dated audit."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys,time
H=Path(__file__).resolve().parent
SOURCES={
 'index':[('accounting-index.html','https://standards.aasb.gov.au/accounting-standards')],
 'cash-page':[('aasb107-page.html','https://standards.aasb.gov.au/aasb-107-sep-2024')],
 'cash-pdf':[('aasb107-2026.pdf','https://standards.aasb.gov.au/sites/default/files/2026-03/AASB107_08-15_COMPsep24_01-26.pdf')],
 'separate-index':[('accounting-index-fifth.html','https://standards.aasb.gov.au/accounting-standards?field_commencing_date=01-07-2025&field_ending_date=30-06-2026&page=0%2C4%2C0')],
 'more-index':[('accounting-index-third.html','https://standards.aasb.gov.au/accounting-standards?field_commencing_date=01-07-2025&field_ending_date=30-06-2026&page=0%2C2%2C0'),
               ('accounting-index-fourth.html','https://standards.aasb.gov.au/accounting-standards?field_commencing_date=01-07-2025&field_ending_date=30-06-2026&page=0%2C3%2C0')],
 'followup':[('accounting-index-second.html','https://standards.aasb.gov.au/accounting-standards?field_commencing_date=01-07-2025&field_ending_date=30-06-2026&page=0%2C1%2C0'),
             ('aasb1061-appendix-c.pdf','https://standards.aasb.gov.au/sites/default/files/2026-06/AASB1061_04-26_AppendixC.pdf')],
 'pdfs':[('aasb2026-2-compiled.pdf','https://standards.aasb.gov.au/sites/default/files/2026-10/AASB2026-2_04-26_ACOMPaug26_07-29_0.pdf'),
         ('aasb20-appendix-d.pdf','https://standards.aasb.gov.au/sites/default/files/2026-10/AASB20_10-26_AppendixD.pdf')]}
kind,attempt=sys.argv[1:];out=H/attempt;out.mkdir(exist_ok=False);results=[]
for name,url in SOURCES[kind]:
    start=datetime.now(timezone.utc).isoformat();tick=time.monotonic()
    cmd=['curl','--fail','--location','--silent','--show-error','--connect-timeout','10','--max-time','30','--max-filesize','20971520','--dump-header',str(out/(name+'.headers')),'--output',str(out/name),'--write-out','%{json}',url]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=40)
    p=out/name
    item=dict(name=name,url=url,command=cmd,returncode=result.returncode,started_utc=start,finished_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-tick,stderr=result.stderr,transfer=result.stdout,bytes=p.stat().st_size if p.exists() else 0,sha256=sha256(p.read_bytes()).hexdigest() if p.exists() else None)
    results.append(item);(out/'acquisition.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({k:item[k] for k in ['name','returncode','bytes','sha256']}),flush=True)
    if result.returncode:raise SystemExit(result.returncode)
    if name.endswith('.pdf'):assert p.read_bytes().startswith(b'%PDF-')
