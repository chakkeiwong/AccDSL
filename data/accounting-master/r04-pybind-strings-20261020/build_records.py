"""One-time documentary record construction; no acquired code execution."""
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import sys

os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
U=Path(__file__).resolve().parent
R=U.parents[2]
S=U/'sources'

def write(path,value):
    with path.open('x',encoding='utf-8') as f:
        if isinstance(value,str): f.write(value)
        else: json.dump(value,f,indent=2,ensure_ascii=True);f.write('\n')

def bind(path):
    return {'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

class Text(HTMLParser):
    def __init__(self): super().__init__();self.parts=[]
    def handle_data(self,d):
        if d.strip(): self.parts.append(d.strip())

def main():
    assert not (U/'source-ledger.json').exists(),'construction is one-time'
    for name in ['python-unicode','python-bytes']:
        p=Text();p.feed((S/(name+'.body')).read_text())
        write(S/(name+'.txt'),'\n'.join(p.parts)+'\n')
    acquisitions=[]
    for p in sorted(S.glob('*.invocation.json')):
        stem=p.name.removesuffix('.invocation.json');inv=json.loads(p.read_text())
        acquisitions.append({'stem':stem,'request_url':inv['argv'][-1],
            'files':[bind(S/(stem+s)) for s in ['.body','.headers','.receipt.json','.invocation.json']]})
    blobs=[]
    selection=json.loads((U/'source-selection.json').read_text())
    selections=[(f's{n:02}',r['version_index'],r['path']) for n,r in enumerate(selection)]
    selections += [(f'helper{i}',i,'include/pybind11/detail/common.h') for i in range(2)]
    for stem,i,path in selections:
        tree=json.loads((S/f'{i}-tree.body').read_text())
        c=json.loads((S/f'{i}-commit.body').read_text())
        e=next(e for e in tree['tree'] if e['path']==path)
        blobs.append({'stem':stem,'version_index':i,'tag':['v2.2.0','v2.11.1'][i],
            'commit':c['sha'],'source_path':path,'git_blob':e['sha'],'source':bind(S/(stem+'.body'))})
    anchors=[]
    def anchor(name,path,start,end,meaning):
        lines=path.read_text().splitlines()
        anchors.append({'id':name,**bind(path),'first_line':start,'last_line':end,
            'excerpt':'\n'.join(lines[start-1:end]),'supports':meaning})
    specs=[
        ('old_type','s00',1098,1111,'CharT and UTF_N define eight-bit std::string encoding.'),
        ('old_dispatch','s00',1112,1135,'Python3 Unicode dispatch versus load_bytes.'),
        ('old_encode','s00',1137,1145,'UTF8 encode, cleared error on failure and explicit length.'),
        ('old_output','s00',1154,1162,'Separate return-direction string decode, unused by integer pylcs result.'),
        ('old_bytes','s00',1180,1203,'Raw bytes explicit length; no bytearray branch; std::basic_string caster.'),
        ('new_dispatch','s03',364,393,'String character type and Unicode/raw dispatch.'),
        ('new_encode','s03',394,407,'UTF8 API, cleared error on failure and explicit length.'),
        ('new_other_widths','s03',409,437,'Other character widths and string_view lifetime; not selected std::string path.'),
        ('new_output','s03',440,451,'String return-direction decode is distinct.'),
        ('new_raw_bytes','s03',469,483,'Raw bytes with explicit length.'),
        ('new_bytearray','s03',484,507,'Bytearray path and std::basic_string caster.'),
        ('old_doc_universal','s01',5,18,'Python3 scope and universal UTF8-encoding assertion.'),
        ('old_doc_bytes','s01',56,73,'Raw bytes and separate output-direction conversion.'),
        ('new_doc_universal','s04',4,10,'Universal UTF8-encoding assertion.'),
        ('new_doc_bytes','s04',47,66,'Raw bytes and separate output-direction conversion.'),
        ('old_helper','helper0',149,168,'Python3 bytes macros map to CPython byte APIs.'),
        ('new_helper','helper1',345,363,'Bytes macros map to CPython byte APIs.'),
        ('old_py_str_operator','s02',858,872,'Separate py::str operator is not the std::string argument load().'),
        ('new_py_str_operator','s05',1580,1595,'Separate py::str operator uses different throw behavior.'),
    ]
    for name,stem,start,end,meaning in specs: anchor(name,S/(stem+'.body'),start,end,meaning)
    for stem,term,endterm,name in [
        ('python-unicode','PyUnicode_AsEncodedString','PyUnicode_Encode','python_encoding_api'),
        ('python-unicode','PyUnicode_AsUTF8AndSize','PyUnicode_AsUTF8','python_utf8_size_api'),
        ('python-bytes','PyBytes_Size','PyBytes_GET_SIZE','python_bytes_size_api'),
        ('python-bytes','PyBytes_AsString','PyBytes_AS_STRING','python_bytes_buffer_api')]:
        p=S/(stem+'.txt');lines=p.read_text().splitlines();first=lines.index(term);last=lines.index(endterm,first+1)
        anchor(name,p,first+1,last,'Official API description; selected section only, dated documentation.')
    wrapper=R/'data/accounting-master/r04-pubtablesv2-20261019/sources/05-metric.py'
    anchor('wrapper_shortcut',wrapper,399,415,'String annotation, equality before binding, no runtime type guard, Python length denominator.')
    pylcs=R/'data/accounting-master/r04-pylcs-source-20261020/sources/04-source.body'
    anchor('pylcs_tokens',pylcs,12,27,'Continuation-byte grouping, no strict UTF8 validator.')
    anchor('pylcs_result',pylcs,31,61,'Integer LCS result; no string-output decode path.')
    write(U/'source-ledger.json',{'date':'2026-10-20','constructed_utc':datetime.now(timezone.utc).isoformat(),
        'acquisitions':acquisitions,'blobs':blobs,'anchors':anchors,
        'read_scope':'Selected spans listed by anchors; no full-header or full-Python-document reading claim.',
        'source_boundaries':['Python3 built-in input types only','Two selected pybind11 snapshots, not all >=2.2',
            'No function dispatcher inspection; final exception class unresolved','No distribution/build/installed equality']})
    spec=importlib.util.spec_from_file_location('local_comparison',U/'compare.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    write(U/'witnesses.json',m.finite_examples())
    write(U/'claim-support-ledger.json',{'summary':m.EXPECTED_CLAIMS,
        'claims':[
            {'claim':'Scalar-valid Unicode uses UTF8 with explicit length, preserving NUL.',
             'class':'IMPLEMENTATION_EVIDENCE','anchors':['old_encode','new_encode','python_encoding_api','python_utf8_size_api']},
            {'claim':'Raw bytes can bypass UTF8 validation; modern snapshot also accepts bytearray.',
             'class':'IMPLEMENTATION_EVIDENCE','anchors':['old_bytes','new_raw_bytes','new_bytearray','old_helper','new_helper']},
            {'claim':'The statement that all Python str encode in UTF8 is wrong for strict encoding of surrogate-containing str.',
             'class':'PROJECT_DERIVATION','anchors':['old_doc_universal','new_doc_universal','old_encode','new_encode'],
             'local_evidence':'witnesses.json: three surrogate-containing inputs rejected by strict standard-library encoding; no binding executed'},
            {'claim':'Unequal non-ASCII bytes/mixed inputs do not use a consistent codepoint denominator; outside annotated str domain.',
             'class':'PROJECT_DERIVATION','anchors':['wrapper_shortcut','pylcs_tokens'],'local_evidence':'witnesses.json'},
            {'claim':'Equality shortcut can bypass conversion, including equal surrogate or bytearray inputs.',
             'class':'IMPLEMENTATION_EVIDENCE','anchors':['wrapper_shortcut'],'local_evidence':'witnesses.json'},
        ],'whole_rows_closed':0})
    write(U/'source-support-ledger.json',{'classification':'IMPLEMENTATION_OR_SOFTWARE',
        'sources':[{'source':'pybind11','versions':['v2.2.0','v2.11.1'],'identity':'source-ledger.json',
            'publication_status':'official tagged software source, not a paper','retraction_quarantine':'N/A for paper retraction; version and documentary discrepancy retained',
            'read_scope':'source-ledger.json anchors only','allowed':'selected conversion contracts',
            'forbidden':'all dependency versions, binary correspondence, performance or accounting claims'},
            {'source':'CPython3.10 documentation','identity':'source-ledger.json','read_scope':'selected four C API sections',
             'allowed':'documented UTF8/byte length and error contracts','forbidden':'pinned implementation or installed runtime evidence'}],
        'predecessor':'data/accounting-master/r04-pylcs-source-20261020/','manuscript_changed':False})
    write(U/'citation-venue-ledger.json',{'scope':'Software source follow-up, no new academic paper',
        'citation_count':'not available; not queried','venue_metric':'not applicable',
        'meaning':'Neither version age nor package popularity is a correctness criterion.'})
    write(U/'backward-snowball-ledger.json',{'route':'pylcs setup dependency -> pybind11 selected casters -> same-version common.h -> official Python API documentation',
        'disposition':'Source trace complete for selected load branches; dispatcher and distribution build provenance unresolved.',
        'paper_bibliography':'No new paper bibliography; original GriTS references remain frozen in predecessor.'})
    write(U/'forward-snowball-ledger.json',{'query':'No new paper citation query in this focused source inquiry.',
        'software_comparison':'v2.11.1 is a later selected comparator to v2.2.0, not a latest-version claim.',
        'scope_gap':'Intervening/later releases and pylcs binary build identity uninspected.'})
    write(U/'omission-risk-ledger.json',{'items':[
        {'gap':'pylcs distribution/build identity','status':'open','risk':'Selected dependency source may differ from compiled wheel.'},
        {'gap':'All pybind11>=2.2 versions','status':'open','risk':'Two snapshots do not establish range-wide behavior.'},
        {'gap':'Dispatcher exception class','status':'not checked','risk':'Caster clears the codec error; cannot call final exception UnicodeEncodeError.'},
        {'gap':'Subclasses and custom equality','status':'outside finite illustrations','risk':'User-defined Python behavior may alter wrapper path.'},
        {'gap':'Normalization/grapheme policy','status':'unselected','risk':'Changing strings changes metric target; no silent normalization.'},
        {'gap':'Historical benchmark protocol and dataset identity','status':'open','risk':'Source findings cannot reconstruct published results.'},
    ]})
    print(json.dumps({'constructed':True,'acquisitions':len(acquisitions),'blobs':len(blobs),'anchors':len(anchors)}))

if __name__=='__main__': main()
