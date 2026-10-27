from pathlib import Path
import json,sys,hashlib,fitz
D=Path(__file__).resolve().parent;R=D.parents[3]
packet=Path(sys.argv[1]);r=json.loads(packet.read_text());I=D/r['inventory'];j=json.loads(I.read_text());v=next(x for x in j['volumes'] if x['name']==r['volume']);assert r['pdf_sha256']==v['pdf_sha256'];assert 1<=len(r['pages'])<=6;assert r['pages']==list(range(r['pages'][0],r['pages'][-1]+1));prior=[x for x in j['read_segments'] if x['volume']==r['volume']]
if prior:
 assert r['pages'][0]==prior[-1]['pages'][-1]+1
 assert r['entry_state']==prior[-1]['exit_state']
else:assert r['pages'][0]==1
assert r['exit_state'] and r['observations'];assert all(x.get('finding') and x.get('disposition') for x in r['observations'])
for page in r['pages']:
 p=v['pages'][page-1];assert p['author_continuous_read']=='not_read';p['author_continuous_read']='author_read';p['reading_segment']=r['id']
j['read_segments'].append(r);I.write_text(json.dumps(j,indent=2)+chr(10));print(json.dumps({'segment':r['id'],'read_pages':r['pages'],'volume_read_total':sum(p['author_continuous_read']=='author_read' for p in v['pages']),'total_pages':len(v['pages']),'status':'author_read_only'}))
