"""Three source-copy comparisons; no XSD/XBRL validation."""
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
PRIOR=ROOT/'data/accounting-master/r06-normative-schema-20261018'
SOURCE=ROOT/'data/accounting-master/taxonomy-reuse-20261007/sources'
sp=importlib.util.spec_from_file_location('prior_compare',PRIOR/'compare.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
CONFIG=[('linkbase','xbrl-linkbase-2003-12-31.xsd','_Ref64365645','import-04-trusted.body','http://www.xbrl.org/2003/linkbase'),
        ('xlink','xlink-2003-12-31.xsd','_Ref47240596','dep-e31dcebaf73e-trusted.body','http://www.w3.org/1999/xlink'),
        ('xl','xl-2003-12-31.xsd','_Ref47240610','dep-53c316b3dbf3-trusted.body','http://www.xbrl.org/2003/XLink')]

def sha(b):return hashlib.sha256(b).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
def read(name):return json.loads((UNIT/name).read_text())
def write(name,v):
    with (UNIT/name).open('x') as f:json.dump(v,f,indent=2);f.write(chr(10))

def compute():
    rtf=(PRIOR/'sources/05-normative.body').read_bytes()
    result=[];texts={}
    for short,filename,bookmark,source,namespace in CONFIG:
        mark=(chr(92)+'bkmkstart '+bookmark).encode();assert rtf.count(mark)==1
        heading=rtf.index(mark);a=rtf.index(b'<?xml',heading);z=rtf.index(b'</schema>',a)+len(b'</schema>')
        assert (filename+' (normative)').encode() in rtf[heading:a]
        raw=rtf[a:z].decode('ascii');norm,controls=m.rtf_decode(raw)
        original=(SOURCE/source).read_bytes();retained=original.decode().replace(chr(13)+chr(10),chr(10))
        assert '2008-07-02' in retained[:1800] and 'non-normative' in retained[:1800]
        ns,rs=m.structure(norm),m.structure(retained)
        assert dict(ns[0][1])['targetNamespace']==dict(rs[0][1])['targetNamespace']==namespace
        n,r=m.remove_header_comment(norm),m.remove_header_comment(retained)
        delta=chr(10).join(difflib.unified_diff(r.splitlines(),n.splitlines(),fromfile='retained',tofile='normative-RTF',lineterm=''))+chr(10)
        result.append({'id':short,'filename':filename,'namespace':namespace,'retained':bind(SOURCE/source),
                       'normative_source':bind(PRIOR/'sources/05-normative.body'),
                       'bookmark':bookmark,'heading_byte':heading,'xml_byte_start':a,'xml_byte_end_exclusive':z,
                       'slice_sha256':sha(rtf[a:z]),'rtf_controls':controls,'non_ascii_slice_bytes':0,
                       'retained_elements':len(rs),'normative_elements':len(ns),
                       'raw_bytes_equal':original==norm.encode(),
                       'equal_after_crlf_and_leading_comment':r==n,
                       'equal_after_crlf_comment_and_final_lf':r==n+chr(10),
                       'namespace_structure_equal':rs==ns,
                       'text_diff_lines':len(delta.splitlines()) if delta.strip() else 0,
                       'structure_differences':[{'position':i,'retained':x,'normative':y} for i,(x,y) in enumerate(zip(rs,ns)) if x!=y]})
        texts[short]=(norm,delta)
    return result,texts

def presentation():
    result,texts=compute();answer=[]
    for r in result:
        norm=texts[r['id']][0]
        retained=(ROOT/r['retained']['path']).read_bytes().decode().replace(chr(13)+chr(10),chr(10))
        n=m.remove_header_comment(norm);s=m.remove_header_comment(retained)
        def lines(t):
            return [line.strip(' '+chr(9)) for line in t.split(chr(10)) if line.strip(' '+chr(9))]
        assert lines(n)==lines(s), r['id']
        answer.append({'id':r['id'],'equal_nonblank_lines_after_ascii_indentation_trim':True,
                       'normalizations':['CRLF to LF','remove first prolog XML notice comment',
                                         'remove blank lines containing only ASCII space/tab','trim ASCII space/tab at line edges'],
                       'nonblank_lines':len(lines(n)), 'normalised_line_sha256':sha(chr(10).join(lines(n)).encode()),
                       'retained_tab_count':s.count(chr(9)), 'normative_tab_count':n.count(chr(9)),
                       'other_whitespace_removed':False,'internal_line_content_modified':False})
    return answer

def check():
    result,texts=compute();assert read('comparisons.json')==json.loads(json.dumps(result))
    assert read('presentation.json')==presentation()
    rejected=[]
    for r in result:
        name=r['id'];norm,delta=texts[name]
        assert (UNIT/(name+'-normative.xsd')).read_text()==norm
        assert (UNIT/(name+'-differences.diff')).read_text()==delta
        baseline=m.structure(norm)
        # Every changed namespace is checked even when lexical QName prefixes
        # themselves remain identical. Exact text tests retain internal comments.
        mutations={
          'target_namespace':norm.replace('targetNamespace="'+r['namespace']+'"','targetNamespace="urn:changed"',1),
          'binding':norm.replace('xmlns="http://www.w3.org/2001/XMLSchema"','xmlns="urn:changed"',1),
          'declaration':re.sub(r'name="([^"]+)"',r'name="Changed_\1"',norm,count=1),
          'annotation':norm.replace('<documentation>', '<documentation>Added text.',1),
        }
        for label,changed in mutations.items():
            assert changed!=norm,(name,label)
            assert m.structure(changed)!=baseline,(name,label)
            rejected.append(name+':'+label)
    for b in read('source-ledger.json')['bindings']:
        assert bind(ROOT/b['path'])==b
    assert read('source-ledger.json')['new_acquisitions']==0
    return {'status':'three finite companion source comparisons checked','schemas':3,
            'normative_elements':sum(r['normative_elements'] for r in result),
            'equal_after_three_adjustments':[r['id'] for r in result if r['equal_after_crlf_comment_and_final_lf']],
            'namespace_structure_equal':[r['id'] for r in result if r['namespace_structure_equal']],
            'rejected_mutations':rejected,'new_acquisitions':0,'runtime_admissions':0,'whole_rows_closed':0}

if __name__=='__main__':
    if sys.argv[1:]==['--extract']:
        result,texts=compute();write('comparisons.json',result)
        for name,(norm,delta) in texts.items():
            for suffix,text in [('-normative.xsd',norm),('-differences.diff',delta)]:
                with (UNIT/(name+suffix)).open('x') as f:f.write(text)
        write('source-ledger.json',{'new_acquisitions':0,'normative_edition':'2008-07-02',
              'bindings':[bind(PRIOR/'sources/05-normative.body'),bind(PRIOR/'source-ledger.json'),bind(PRIOR/'completion.json'),bind(PRIOR/'compare.py')]+[bind(SOURCE/c[3]) for c in CONFIG],
              'scope':'Three retained source copies and exact bookmarked normative Appendix A schemas; no full-specification or runtime review.'})
        print(json.dumps([{k:r[k] for k in ['id','retained_elements','normative_elements','equal_after_crlf_and_leading_comment','equal_after_crlf_comment_and_final_lf','namespace_structure_equal','text_diff_lines']} for r in result]))
    else:print(json.dumps(check()))
