"""One-time evidence construction; no installation or upstream runtime."""
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
sp=importlib.util.spec_from_file_location('semantics',UNIT/'compare.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

def write(name,data):
    if (UNIT/name).exists():
        assert name=='source-ledger.json' and json.loads((UNIT/name).read_text())==data
        return
    with (UNIT/name).open('x') as f:json.dump(data,f,indent=2);f.write(chr(10))

rows=[('01-datatypes','https://www.w3.org/TR/xmlschema-2/',644011,1085,.977915,'retained XBRL SCHEMA-2 reference'),
      ('02-dated','https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/',644011,1085,.575972,'explicit This version link from first response'),
      ('03-structures','https://www.w3.org/TR/2004/REC-xmlschema-1-20041028/structures.html',903817,991,.794744,'Part 2 whiteSpace link to normalization during validation')]
acquisitions=[]
for stem,url,size,hsize,seconds,lead in rows:
    body=UNIT/'sources'/f'{stem}.body';headers=UNIT/'sources'/f'{stem}.headers'
    assert body.stat().st_size==size and headers.stat().st_size==hsize
    acquisitions.append({'id':stem,'url':url,'effective_url':url,'lead':lead,'http_status':200,'exitcode':0,
                         'bytes':size,'curl_seconds':seconds,'content_type':'text/html; charset=utf-8',
                         'redirects':0,'trusted':True,'body':m.bind(body),'headers':m.bind(headers),
                         'command_argv':['curl','--silent','--show-error','--location','--connect-timeout','10',
                           '--max-time','35','--max-filesize','12582912','--proto','=https','--proto-redir','=https',
                           '--dump-header',str(headers.relative_to(ROOT)),'--output',str(body.relative_to(ROOT)),
                           '--write-out','%{json}'+chr(92)+'n',url],
                         'receipt_provenance':'completed tool curl JSON transcription; original headers and bodies retained'})
write('source-ledger.json',{'acquisitions':acquisitions,'edition':'XML Schema 1.0 Second Edition, 28 October 2004',
                          'generic_and_dated_identical':(UNIT/'sources/01-datatypes.body').read_bytes()==(UNIT/'sources/02-dated.body').read_bytes(),
                          'scope':'selected sections, not full-spec reading or errata-wide survey; no XSD 1.1 substitution',
                          'web_open':'Server open returned no source content; local official acquisitions used.'})
passages=[]
def add(identifier,file,a,z,kind):
    p=UNIT/'sources'/file;b=p.read_bytes();raw=b[a:z]
    passages.append({'id':identifier,'source':m.bind(p),'byte_start':a,'byte_end_exclusive':z,
                     'slice_sha256':m.sha(raw),'text':m.plain(raw.decode()),'scope':kind})
def section(identifier,file,start,end):
    b=(UNIT/'sources'/file).read_bytes();a=b.index(('id="'+start+'"').encode());a=b.rfind(b'<',0,a)
    z=b.index(('id="'+end+'"').encode(),a+1);z=b.rfind(b'<',a,z)
    add(identifier,file,a,z,'complete bounded source section')
f='02-dated.body'
for identifier,a,z in [('gYear','gYear','gMonthDay'),('string','string','boolean'),
                       ('normalizedString','normalizedString','token'),('token','token','language'),
                       ('pattern','rf-pattern','rf-enumeration'),('whiteSpace','rf-whiteSpace','rf-maxInclusive'),
                       ('year-zero','year-zero','dateTime-lexical-representation'),
                       ('year-lexical','dateTime-lexical-representation','dateTime-canonical-representation'),
                       ('regex','regexs','charcter-classes'),('char-range','dt-charrange','cces')]:
    section(identifier,f,a,z)
section('normalization-stage','03-structures.body','d0e1654','cAttribute_Declarations')
b=(UNIT/'sources'/f).read_bytes()
for typ in ('normalizedString','token','gYear'):
    start=b.index(('&lt;xs:simpleType name=&quot;'+typ+'&quot;').encode())
    end=b.index(b'&lt;/xs:simpleType&gt;',start)+len(b'&lt;/xs:simpleType&gt;')
    add('builtin-'+typ,f,start,end,'complete built-in declaration in normative Appendix A')
write('passages.json',passages)
write('interpretations.json',{'scope':'seven selected tokens under retained declarations, documentary type checks only',
                            'rows':m.rows(),'frozen_values_changed':False,'full_schema_validation':False})
write('examples.json',m.examples())
print(json.dumps({'sources':3,'passages':len(passages),'facts':7,'examples':len(m.examples())}))
