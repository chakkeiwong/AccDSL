"""Verify two failed primary recovery attempts; no unread-paper claims."""
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
def receipts():
 rows=[('01-paper','https://www.vldb.org/conf/2006/p953-benjelloun.pdf','https://www.vldb.org/conf/2006/p953-benjelloun.pdf',403,358,.679272,0,'pdf','=https'),
       ('02-original-record','http://dbpubs.stanford.edu/pub/2005-39','http://ILPubs.stanford.edu:8090/703/',200,4692,2.547901,4,'body','=http,https')]
 out=[]
 for stem,url,effective,status,size,seconds,redirects,suffix,protocol in rows:
  p=UNIT/'sources'/(stem+'.'+suffix);h=UNIT/'sources'/(stem+'.headers')
  assert p.stat().st_size==size
  out.append({'id':stem,'url':url,'effective_url':effective,'http_status':status,'exitcode':0,'bytes':size,
              'curl_seconds':seconds,'redirects':redirects,'trusted':True,'body':bind(p),'headers':bind(h),
              'actual_content':'HTML error page, not PDF or paper record',
              'command_argv':['curl','--silent','--show-error','--location','--connect-timeout','10',
                 '--max-time','35','--max-filesize','12582912','--proto',protocol,'--proto-redir',protocol,
                 '--dump-header',str(h.relative_to(ROOT)),'--output',str(p.relative_to(ROOT)),
                 '--write-out','%{json}'+chr(92)+'n',url],
              'receipt_provenance':'completed tool curl JSON transcription; original response headers and body retained'})
 return out
def check():
 assert read('source-ledger.json')['acquisitions']==receipts()
 first=(UNIT/'sources/01-paper.pdf').read_bytes();second=(UNIT/'sources/02-original-record.body').read_text()
 assert not first.startswith(b'%PDF-')
 assert '<title>Error - Stanford InfoLab Publication Server</title>' in second
 assert 'Failed to connect to database' in second
 assert 'The server encountered an internal error' in second
 d=read('disposition.json')
 assert d['technical_source_acquired'] is False and d['theorem_claims_admitted']==0
 for b in read('source-ledger.json')['retained_inputs']:assert bind(ROOT/b['path'])==b
 return {'status':'bounded primary-recovery barriers checked','acquisitions':2,
         'actual_pdfs':0,'http200_error_pages':1,'technical_reads':0,'theorem_claims_admitted':0,'whole_rows_closed':0}
if __name__=='__main__':
 if sys.argv[1:]==['--record-sources']:
  prior=ROOT/'data/accounting-master/r04-uldb-competitor-20261019'
  write('source-ledger.json',{'acquisitions':receipts(),'retained_inputs':[bind(prior/n) for n in ('source-ledger.json','disposition.json','completion.json')],
                            'scope':'Two distinct untested routes after completed prior source barrier; no primary text recovered.'})
  write('disposition.json',{'technical_source_acquired':False,'theorem_claims_admitted':0,'code_read':False,
                           'status':'source access unresolved; seven request receipts across prior and current units',
                           'next_requirement':'A genuinely new accessible full-text route; do not repeat recorded failures.',
                           'global_continuation_veto':False,'research_direction_rejected':False})
  print(json.dumps(check()))
 else:print(json.dumps(check()))
