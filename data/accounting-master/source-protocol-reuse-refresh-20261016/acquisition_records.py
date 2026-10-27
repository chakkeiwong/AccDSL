from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
OUT=Path(__file__).resolve().parent
rows=[]
base='https://raw.githubusercontent.com/jsvine/pdfplumber/4c64b92d5caccd71c645e98e0fabb0c4dba7ff45/'
requests=[('pdfplumber-pyproject','pdfplumber-pyproject.toml',base+'pyproject.toml'),
('pdfplumber-setup','pdfplumber-setup.py.txt',base+'setup.py'),
('pdfplumber-requirements.txt','pdfplumber-requirements.txt.txt',base+'requirements.txt'),
('pdfplumber-LICENSE.txt','pdfplumber-LICENSE.txt.txt',base+'LICENSE.txt'),
('pdfplumber-pdfplumber-_version.py','pdfplumber-pdfplumber-_version.py.txt',base+'pdfplumber/_version.py'),
('pdfminer-release','pdfminer-release.json','https://pypi.org/pypi/pdfminer.six/20260107/json'),
('pypdfium-minimum','pypdfium-minimum.json','https://pypi.org/pypi/pypdfium2/5.9.0/json'),
('pillow-minimum','pillow-minimum.json','https://pypi.org/pypi/Pillow/12.2.0/json'),
('xbrl21','xbrl21.html','https://www.xbrl.org/2003/XBRL-2.1-2003-12-31+corrected-2013-02-20.html'),
('xbrl-legal','xbrl-legal.html','https://www.xbrl.org/the-consortium/about/legal/')]
for stem,body,url in requests:
    h=OUT/(stem+'.headers');p=OUT/body
    codes=re.findall(r'^HTTP/\S+\s+(\d+)',h.read_text(),re.M)
    limit=['--max-filesize','5000000' if stem=='xbrl21' else '2000000'] if stem in ('xbrl21','xbrl-legal') else []
    rows.append(dict(url=url,body=body,headers=h.name,http_status=int(codes[-1]),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,command_reconstruction=['curl','-L','--connect-timeout','10','--max-time','35']+limit+['-sS','-D',str(h),'-o',str(p),url],wall_seconds=None,wall_time_note='Per-request wall duration was not separately retained; no timing claim.',disposition='not found' if codes[-1]=='404' else 'metadata/source inspected'))
(OUT/'acquisition-manifest.json').write_text(json.dumps(dict(recorded_utc=datetime.now(timezone.utc).isoformat(),requests=rows,searches=[dict(query='IAS32 original-term early conversion; IAS36 zero carrying amount reversal',result='web search returned no inspectable results')],scope='read-only source downloads; no installation, source-code execution or rights clearance'),indent=2)+'\n')
print(json.dumps(dict(requests=len(rows),statuses={s:sum(r['http_status']==s for r in rows) for s in sorted(set(r['http_status'] for r in rows))})))
