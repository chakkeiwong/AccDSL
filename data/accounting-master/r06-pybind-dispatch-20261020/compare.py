"""Source-bound dispatcher account; no native or acquired code execution."""
import hashlib
import json
import re
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
P=R/'data/accounting-master/r04-pybind-strings-20261020'
L=R/'data/accounting-master/r04-pylcs-source-20261020'


def load(p):return json.loads(p.read_text())


def bind(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}


def derive():
    identities=[]
    for index,label in enumerate(['v220','v2111']):
        tree=load(P/'sources'/f'{index}-tree.body')
        commit=load(P/'sources'/f'{index}-commit.body')['sha']
        assert tree['truncated'] is False
        for suffix,path in [('', 'include/pybind11/pybind11.h'),('-attr','include/pybind11/attr.h')]:
            name=label+suffix
            source=U/'sources'/(name+'-sandbox.body')
            data=source.read_bytes()
            entry=next(e for e in tree['tree'] if e['path']==path)
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            assert blob==entry['sha'] and len(data)==entry['size']
            receipt=load(U/'sources'/(name+'-receipt.json'))
            response=json.loads(receipt['result']['output'])
            url='https://raw.githubusercontent.com/pybind/pybind11/'+commit+'/'+path
            assert response['url']==response['url_effective']==url
            assert response['http_code']==200 and response['size_download']==len(data)
            assert receipt['result']['exit_code']==response['exitcode']==0
            identities.append({'version':label,'commit':commit,'upstream_path':path,'git_blob':blob,'source':bind(source)})
    native=(L/'sources/04-source.body').read_text()
    registrations=re.findall(r'm\.def\("lcs_sequence_length"\s*,\s*&([A-Za-z_]+)',native)
    assert registrations==['lcs_sequence_length']
    assert 'int lcs_sequence_length(const string &str1, const string &str2)' in native
    for label in ['v220','v2111']:
        source=(U/'sources'/(label+'-sandbox.body')).read_text()
        record=(U/'sources'/(label+'-attr-sandbox.body')).read_text()
        assert 'function_record *next = nullptr;' in record and 'is_operator(false)' in record
        assert re.search(r'if \(!args_converter.load_args\(call\)\)\s*\{?\s*return PYBIND11_TRY_NEXT_OVERLOAD;',source)
        assert 'const bool overloaded = it != nullptr && it->next != nullptr;' in source
        assert 'if (overloaded && !second_pass.empty() && result.ptr() == PYBIND11_TRY_NEXT_OVERLOAD)' in source
        assert 'result = func.impl(call);' in source
        assert 'PyErr_SetString(PyExc_TypeError, msg.c_str());' in source
        assert 'Unable to convert function return value' in source
    old=(U/'sources/v220-sandbox.body').read_text()
    new=(U/'sources/v2111-sandbox.body').read_text()
    assert '<repr raised Error>' not in old
    assert new.count('msg += "<repr raised Error>";')==2
    assert 'raise_from(PyExc_TypeError, msg.c_str());' in new
    return {'new_sources':identities,'pylcs_target_registrations':len(registrations),
            'path':['string load clears encoding error and returns false',
                    'argument_loader returns false if a required caster rejects',
                    'wrapper returns non-null TRY_NEXT_OVERLOAD before invoking LCS',
                    'single non-operator binding has no second-pass alternative',
                    'terminal incompatible-arguments branch constructs diagnostic and sets TypeError'],
            'nominal_class':'TypeError, conditional on successful diagnostic construction',
            'original_encoding_error':'cleared, not directly propagated as UnicodeEncodeError',
            'repr_difference':{'v220':'direct repr at terminal error branch outside prior try/catch',
                               'v2111':'local error_already_set catch substitutes <repr raised Error>'},
            'scope':'ordinary two positional built-in strings in the inspected source paths; no runtime observation',
            'not_established':['actual pylcs build version','all pybind11 releases','universal diagnostic success',
                               'custom repr or allocation-failure runtime outcome','function-body or return-conversion errors']}


def check():
    result=derive();assert result==load(U/'comparison.json')
    ledger=load(U/'source-ledger.json')
    for item in ledger['bindings']:assert bind(R/item['path'])==item,item['path']
    for a in ledger['anchors']:
        lines=(R/a['source']['path']).read_text().splitlines()
        assert bind(R/a['source']['path'])==a['source']
        assert '\n'.join(lines[a['first_line']-1:a['last_line']])==a['excerpt']
    return {'status':'version-bounded source path verified','acquisitions':4,'git_blobs':4,
            'bindings':len(ledger['bindings']),'anchors':len(ledger['anchors']),
            'target_registrations':1,'nominal_class':'TypeError with stated conditions',
            'runtime_admitted':False,'whole_rows_closed':0}
