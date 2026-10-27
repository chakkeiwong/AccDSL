"""Source-access disposition; never evaluates the unread paper."""
import hashlib
import json
from pathlib import Path
import sys
UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(name,data):
 with (UNIT/name).open('x') as f:json.dump(data,f,indent=2);f.write(chr(10))
def read(name):return json.loads((UNIT/name).read_text())
ROWS=[('01-proceedings','https://www.vldb.org/conf/2006/',0,403,358,.877698),
      ('02-author','https://cs.stanford.edu/people/widom/',0,200,24988,1.429867),
      ('03-publications','https://cs.stanford.edu/people/widom/pubs.html',0,200,102206,1.200855),
      ('04-paper-record','https://dbpubs.stanford.edu/pub/2005-39',7,0,0,.575211),
      ('05-trio','https://infolab.stanford.edu/trio/',7,0,0,.528092)]
def sources():
 records=[]
 for stem,url,exitcode,status,size,seconds in ROWS:
  body=UNIT/'sources'/(stem+'.body');headers=UNIT/'sources'/(stem+'.headers')
  assert (body.stat().st_size if body.exists() else 0)==size
  records.append({'id':stem,'url':url,'effective_url':url,'http_status':status,'exitcode':exitcode,
                  'bytes':size,'curl_seconds':seconds,'trusted':True,'redirects':0,
                  'body':bind(body) if body.exists() else None,'headers':bind(headers),
                  'command_argv':['curl','--silent','--show-error','--location','--connect-timeout','10',
                   '--max-time','35','--max-filesize','12582912','--proto','=https','--proto-redir','=https',
                   '--dump-header',str(headers.relative_to(ROOT)),'--output',str(body.relative_to(ROOT)),
                   '--write-out','%{json}'+chr(92)+'n',url],
                  'receipt_provenance':'transcribed completed tool JSON; original response files retained',
                  'access':'no route to host in trusted context' if exitcode==7 else ('HTTP403 directory' if status==403 else 'acquired navigation only')})
 return records
def disposition():
 return {'technical_source_acquired':False,'conference_paper_read':False,'journal_paper_read':False,
         'official_code_acquired':False,'theorem_transfer_evaluated':False,'implementation_admitted':False,
         'conference':{'title':'ULDBs: Databases with Uncertainty and Lineage','year':2006,'pages':'953-964',
                       'record':'http://dbpubs.stanford.edu/pub/2005-39','evidence':'official author bibliography'},
         'journal':{'title':'Databases with Uncertainty and Lineage','year':2008,'volume_issue':'17(2)',
                    'pages':'243-264','record':'http://dbpubs.stanford.edu/pub/2007-26',
                    'relation':'author bibliography says much conference material appears in journal version; technical equivalence not checked'},
         'official_project':'http://infolab.stanford.edu/trio',
         'blocked_routes':['VLDB2006 directory403','author-linked dbpubs HTTPS no route','author-linked Trio HTTPS no route'],
         'next_source_requirement':'Accessible primary full text and, for implementation claims, applicable official code; do not repeat exact failed routes.',
         'literature_absence_claim':False,'research_direction_rejected':False,'whole_rows_closed':0}
def check():
 assert read('source-ledger.json')['acquisitions']==sources()
 assert read('disposition.json')==disposition()
 author=(UNIT/'sources/02-author.body').read_text();pub=(UNIT/'sources/03-publications.body').read_text()
 assert 'href="http://cs.stanford.edu/people/widom/pubs.html"' in author
 assert 'href="http://infolab.stanford.edu/trio"' in author
 for s in ['http://dbpubs.stanford.edu/pub/2005-39','http://dbpubs.stanford.edu/pub/2007-26','pages 953-964','17(2):243-264']:
  assert s in pub
 for b in read('source-ledger.json')['retained_inputs']:assert bind(ROOT/b['path'])==b
 for r in read('spans.json'):
  p=ROOT/r['source']['path'];assert bind(p)==r['source']
  b=p.read_bytes()[r['start']:r['end']];assert hashlib.sha256(b).hexdigest()==r['sha256']
 return {'status':'finite source barrier recorded and checked','acquisitions':5,'navigation_pages':2,
         'access_failures':3,'technical_papers_read':0,'official_code_read':0,'inspected_spans':3,
         'theorem_claims_admitted':0,'whole_rows_closed':0}
if __name__=='__main__':
 if sys.argv[1:]==['--record-sources']:
  inputs=[ROOT/'docs/design/research'/n for n in ('omissions.json','backward-snowball.json','text/green2007.txt')]
  write('source-ledger.json',{'acquisitions':sources(),'retained_inputs':[bind(p) for p in inputs],
        'web_search':'Server search returned no usable source content. Unverified discovery wording was corrected before protection/acquisition.'})
  spans=[]
  for file,term,width in [('02-author.body',b'pubs.html',380),('02-author.body',b'infolab.stanford.edu/trio',300),('03-publications.body',b'http://dbpubs.stanford.edu/pub/2007-26',1900)]:
   p=UNIT/'sources'/file;b=p.read_bytes();i=b.index(term);a=max(0,i-160);z=i+width
   spans.append({'source':bind(p),'start':a,'end':z,'sha256':hashlib.sha256(b[a:z]).hexdigest(),
                 'scope':'Official navigation/bibliographic span; no technical theorem text'})
  write('spans.json',spans);write('disposition.json',disposition());print(json.dumps(check()))
 else:print(json.dumps(check()))
