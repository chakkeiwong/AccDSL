from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import importlib.util,json,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import company_function_text_v1 as text
import company_functions_v1 as functions
spec=importlib.util.spec_from_file_location('function_text_examples',ROOT/'data/accounting-master/company-functions-20261025/examples.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)

class FunctionTextTests(unittest.TestCase):
    def setUp(self):
        self.body=e.policy_program();self.source=text.render(self.body)

    def refuse(self,source):
        with self.assertRaises((ValueError,TypeError)):text.lower(source)

    def check_spans(self,source,result):
        raw=source.encode('utf-8') if isinstance(source,str) else source
        physical=raw.splitlines(keepends=True);offsets=[0]
        for line in physical:offsets.append(offsets[-1]+len(line))
        self.assertEqual(result['source_sha256'],sha256(raw).hexdigest())
        self.assertEqual(len(result['declarations']),sum(bool(x.strip()) for x in physical))
        for span in result['declarations']:
            i=span['line']-1;full=physical[i].removesuffix(b'\n').removesuffix(b'\r');trimmed=full.strip(b' \t')
            start=offsets[i]+full.index(trimmed)
            self.assertEqual((span['byte_start'],span['byte_end']),(start,start+len(trimmed)))
            self.assertEqual(raw[span['byte_start']:span['byte_end']],trimmed)
            self.assertEqual(span['slice_sha256'],sha256(trimmed).hexdigest())
            decoded=full.decode('utf-8')
            self.assertEqual(decoded[span['column_start']-1:span['column_end']-1],trimmed.decode('utf-8'))
            cursor=result['request']
            for key in span['path']:cursor=cursor[key]

    def test_six_saved_requests_roundtrip_and_compile_exactly(self):
        saved=json.loads((ROOT/'data/accounting-master/company-functions-20261025/comparison.json').read_text())
        for name,case in saved['cases'].items():
            with self.subTest(name=name):
                body=case['request'];source=text.render(body);parsed=text.lower(source)
                self.assertEqual(parsed['request'],body);self.assertEqual(parsed['compilation'],case['compilation'])
                self.assertEqual(text.render(parsed['request']),source)
                self.assertTrue(all(parsed[k] is False for k in functions.FLAGS));self.check_spans(source,parsed)

    def test_unicode_quotes_and_command_looking_name_are_literal(self):
        b=deepcopy(self.body);b['name']='会社 Économie; "quoted" # $HOME $(not_a_command) '+chr(96)+'literal'+chr(96)
        source=text.render(b);parsed=text.lower(source);self.assertEqual(parsed['request'],b);self.check_spans(source,parsed)
        b['name']='E\u0301';a=text.render(b);b['name']='É';c=text.render(b)
        self.assertNotEqual(text.lower(a)['request_sha256'],text.lower(c)['request_sha256'])
        self.assertNotEqual(text.lower(a)['source_sha256'],text.lower(c)['source_sha256'])

    def test_crlf_indentation_blank_lines_and_no_final_newline(self):
        source='\r\n'+''.join('\t  '+line+' \t\r\n' for line in self.source.splitlines())
        parsed=text.lower(source.encode());self.assertEqual(parsed['request'],self.body);self.check_spans(source,parsed)
        changed=source.rstrip('\r\n');other=text.lower(changed);self.check_spans(changed,other)
        self.assertNotEqual(parsed['source_sha256'],other['source_sha256']);self.assertEqual(parsed['request_sha256'],other['request_sha256'])

    def test_multibyte_spans_use_bytes_not_codepoints(self):
        b=deepcopy(self.body);b['name']='北星财务';source=text.render(b);parsed=text.lower(source);self.check_spans(source,parsed)
        first=parsed['declarations'][0]
        self.assertGreater(first['byte_end']-first['byte_start'],first['column_end']-first['column_start'])
        self.assertGreater(parsed['declarations'][1]['byte_start'],len(source.splitlines()[0])+1)

    def test_forward_calls_and_main_declarations_between_functions(self):
        b=e.call_chain(3);b['functions'].reverse();source=text.render(b);lines=source.splitlines()
        main=[x for x in lines if x.startswith('literal a ') or x.startswith('call r ')]
        lines=[x for x in lines if x not in main];lines[1:1]=main
        parsed=text.lower('\n'.join(lines)+'\n');self.assertEqual(parsed['request'],b)
        self.assertEqual(functions.evaluate(parsed['request'])['evaluation']['outputs']['result']['value'],'3/7')

    def test_nested_functions_and_capture_are_rejected(self):
        for old,new in [('parameter discount','function nested;\nparameter discount'),('param_ref d discount;','input_ref d discount;'),('input_ref discount discount;','param_ref discount discount;')]:
            self.refuse(self.source.replace(old,new))

    def test_duplicates_and_json_duplicate_keys(self):
        for prefix in ['input discount ','parameter discount ','output fraction ']:
            line=next(x for x in self.source.splitlines() if x.startswith(prefix));self.refuse(self.source.replace(line,line+'\n'+line))
        self.refuse(self.source.replace('function half;','function complement;'))
        self.refuse(self.source.replace('"kind":"number"','"kind":"number","kind":"number"',1))
        self.refuse(self.source.replace('"dimensions":{}','"dimensions":{"USD":1,"USD":1}',1))

    def test_missing_repeated_misordered_markers(self):
        for token in ['end_program;','end_function;','result r;']:
            self.refuse(self.source.replace(token,'',1));self.refuse(self.source.replace(token,token+'\n'+token,1))
        self.refuse(self.source+'end_program;\n');self.refuse(self.source.replace('end_function;','end_program;',1))
        returns=next(x for x in self.source.splitlines() if x.startswith('returns '))
        self.refuse(self.source.replace(returns,returns+'\nparameter late '+returns[len('returns '):],1))
        self.refuse(self.source.replace('result r;','result r;\nliteral late '+returns[len('returns '):-1]+' 1/1;',1))

    def test_semicolons_comments_includes_extra_statements(self):
        self.refuse(self.source.replace(';','',1))
        for prefix in ['# comment\n','include private;\n','shell ls;\n','\n;\n']:
            self.refuse(self.source.replace('end_program;',prefix+'end_program;'))
        self.refuse(self.source.replace('end_program;','end_program; output extra fraction;'))

    def test_invalid_encoding_controls_and_nontext(self):
        for source in [b'\xff',b'\xef\xbb\xbf'+self.source.encode(),self.source.replace('\n','\r'),self.source+'\x00',self.source+'\x7f',self.source+'\v',None,[],42]:
            self.refuse(source)

    def test_json_constants_shapes_and_typed_value_errors(self):
        for replacement in ['NaN','Infinity','[]','true','{"kind":"number","dimensions":{},"context":null,"extra":1}']:
            first=next(x for x in self.source.splitlines() if x.startswith('returns '));self.refuse(self.source.replace(first,'returns '+repr(replacement)+';',1))
        for value in ['0.1','2/2','1/0','True']:self.refuse(self.source.replace(' 1/10;',' '+value+';',1))

    def test_semantic_cycles_missing_targets_and_wrong_types(self):
        for old,new in [('call regular complement discount;','call regular complement regular;'),('call regular complement discount;','call regular complement;'),('call half half;','call half absent;'),('param_ref d discount;','param_ref d absent;')]:
            self.refuse(self.source.replace(old,new))
        self.refuse(self.source.replace('node r sub one d;','node r and one d;'))

    def test_parsing_never_evaluates_arithmetic(self):
        b=e.program([e.literal('one','1/1'),e.literal('zero','0/1'),e.node('r','div','one','zero')]);source=text.render(b)
        with patch.object(functions,'evaluate',side_effect=AssertionError('evaluation called')):
            result=text.lower(source);self.assertEqual(result['status'],'compiled_source')
        self.assertEqual(functions.evaluate(result['request'])['status'],'invalid')
        self.refuse(self.source.replace('node r sub one d;','node r python_eval one d;'))

    def test_resource_limits_at_boundaries(self):
        raw=self.source.encode();n=len(text.lower(raw)['declarations']);line=max(len(x) for x in raw.splitlines())
        for key,size in [('source_bytes',len(raw)),('line_bytes',line),('declarations',n)]:
            with patch.dict(text.LIMITS,{key:size}):self.assertEqual(text.lower(raw)['request'],self.body)
            with patch.dict(text.LIMITS,{key:size-1}):self.refuse(raw)

    def test_raw_spacing_changes_only_source_identity(self):
        a=text.lower(self.source);b=text.lower('\n'+self.source.replace('literal one ','literal   one '))
        self.assertEqual(a['request_sha256'],b['request_sha256']);self.assertNotEqual(a['source_sha256'],b['source_sha256']);self.assertNotEqual(a['declarations'],b['declarations'])

    def test_compiler_pin_and_line_diagnostics(self):
        with patch.object(text,'COMPILER_SHA256','0'*64):self.refuse(self.source)
        malformed=self.source.replace('end_program;','unexpected;')
        with self.assertRaisesRegex(ValueError,'line '+str(len(self.source.splitlines()))):text.lower(malformed)

    def test_render_rejects_line_controls_without_mutation(self):
        before=deepcopy(self.body);text.render(self.body);self.assertEqual(before,self.body)
        for name in ['two\nlines','two\rlines','name\x00']:
            b=deepcopy(self.body);b['name']=name
            with self.assertRaises(ValueError):text.render(b)

    def test_unknowns_and_expansion_origins_remain_mapped(self):
        b=deepcopy(self.body);b['inputs']['ordinary']['value']=False;b['inputs']['discount']['value']='unknown'
        parsed=text.lower(text.render(b));out=functions.evaluate(parsed['request']);self.assertEqual(out['evaluation']['outputs']['fraction']['value'],'4/5')
        paths={tuple(s['path']) for s in parsed['declarations'] if s['kind'] not in ['end_program','end_function']}
        for origin in parsed['compilation']['origins'].values():
            if origin['scope']=='main':
                index=next(i for i,n in enumerate(b['nodes']) if n['id']==origin['node']);self.assertIn(('nodes',index),paths)
            else:
                f=next(i for i,f in enumerate(b['functions']) if 'function:'+f['name']==origin['scope'])
                index=next(i for i,n in enumerate(b['functions'][f]['nodes']) if n['id']==origin['node']);self.assertIn(('functions',f,'nodes',index),paths)

if __name__=='__main__':unittest.main()
