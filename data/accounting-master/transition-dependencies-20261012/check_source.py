"""Check provenance, edition boundaries and exact dependency excerpts."""
import hashlib
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
start=time.monotonic();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:' '.join(s.split());checks=[]
def ck(n,v):checks.append({'name':n,'passed':bool(v)})
b=json.loads((OUT/'baseline.json').read_text());e=json.loads((OUT/'source-evidence.json').read_text())
for p,h in b['inputs'].items():ck('protected '+p,sha(ROOT/p)==h)
for r in b['pointer_snapshots']:ck('snapshot '+r['live'],sha(ROOT/r['snapshot'])==r['sha256'])
for name,s in e['sources'].items():
    ck('source '+name,sha(ROOT/s['path'])==s['sha256'] and (ROOT/s['path']).read_bytes().startswith(b'%PDF'))
ck('text identity',all(sha(ROOT/p)==h for p,h in e['text_hashes'].items()))
ck('45 selected pages',e['read_page_count']==45)
for a in json.loads((OUT/'source-anchors.json').read_text()):
    s=norm((ROOT/a['text_path']).read_text());i=a['normalized_start'];v=a['exact_normalized_excerpt']
    ck('anchor '+a['id'],s[i:i+len(v)]==v)
access=json.loads((OUT/'acquisition.json').read_text())
ck('eight successful bounded responses',len(access)==8 and all(r['status']==200 for r in access))
ck('response identities',all(sha(ROOT/r['path'])==r['sha256'] for r in access))
for link in json.loads((OUT/'discovery-links.json').read_text()):
    row=next(r for r in access if r['id']==link['parent']);soup=BeautifulSoup((ROOT/row['path']).read_bytes(),'html.parser')
    ck('official discovery '+link['target'],any(a['href']==link['url'] for a in soup.select('a[href]')))
for name,phrase in [('aasb108','on or after 1 January 2023'),('aasb13','on or after 1 July 2021')]:
    ck('PDF edition '+name,phrase in norm((OUT/'text'/f'{name}-1.txt').read_text()))
soup=BeautifulSoup((OUT/'acquisition/aasb13-page.html').read_bytes(),'html.parser')
ck('later edition explicitly differs','on or after 1 January 2024' in norm(soup.get_text(' ',strip=True)))
ck('historical search query retained',any('field_commencing_date=01-01-2023' in r['url'] for r in access))
ck('renders bound, inspection distinguished',len(e['renders'])==20 and sum(r['author_inspected'] for r in e['renders'])==10 and all(sha(ROOT/r['path'])==r['sha256'] for r in e['renders']))
failed=[r['name'] for r in checks if not r['passed']]
out={'checks':checks,'passed':len(checks)-len(failed),'failed':failed,'wall_seconds':time.monotonic()-start,
     'scope':'Identity, edition and exact-excerpt checks; accounting interpretation remains author reviewed.'}
(OUT/'source-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['passed','failed']}));raise SystemExit(bool(failed))
