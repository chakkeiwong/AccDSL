"""Binding identity, pointer semantics and independent missing/context cases."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_input_binding_v1 as binder
spec=importlib.util.spec_from_file_location('binding_examples',
    ROOT/'data/accounting-master/method-input-binding-20261024/examples.py')
examples=importlib.util.module_from_spec(spec)
spec.loader.exec_module(examples)


def definition(kind='rational',role='state'):
    t={'kind':kind,'context':{'entity':'Sample','book_role':'legal','unit':'USD'} if kind=='rational' else {}}
    value={'rational':'1/1','boolean':True,'text':'unknown','date':'2025-01-01'}[kind]
    return {'profile':core.PROFILE,'method_id':'independent.binding','version':'1',
        'inputs':{'x':{'type':t,'role':role,'source_ref':'replaced-by-exact-record'}},
        'requirements':[{'id':'equals','predicate':{'op':'eq','left':{'op':'ref','id':'x'},
              'right':{'op':'const','type':deepcopy(t),'value':value}},'requires':['x'],
              'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'}],
        'capabilities':[],'residual_prerequisites':['Full source and accounting admission remain separate.']}


def sample(data=None,pointer='/amount',kind='rational',encoding='scalar',missing='invalid'):
    if data is None:
        data={'amount':'1/1'}
    return examples.packet(definition(kind),core.canonical(data),{'x':pointer},
                           {'x':encoding},{'x':missing})


class InputBindingTests(unittest.TestCase):
    def test_retained_records_match_explicit_bridge(self):
        for name,case in examples.retained().items():
            with self.subTest(name=name):
                before=deepcopy(case['packet'])
                result=examples.assess(case['packet'])
                self.assertEqual(result['status'],'bound')
                self.assertEqual(result['values'],case['expected_values'])
                self.assertEqual(result['assessment']['status'],'requirements_satisfied')
                self.assertEqual(before,case['packet'])
                for key in ['executed','source_admission','accounting_admission','method_eligible']:
                    self.assertFalse(result[key])

    def test_raw_and_manifest_hashes_are_mandatory(self):
        value=sample()
        h=next(iter(value['blobs']))
        value['blobs'][h]=b'{"amount":"2/1"}'
        self.assertEqual(examples.assess(value)['reason'],'raw_digest_mismatch')
        value=sample()
        m=next(iter(value['manifests']))
        value['manifests'][m]['version']='2'
        self.assertEqual(examples.assess(value)['reason'],'manifest_digest_mismatch')
        for registry in ['blobs','manifests','schemas']:
            value=sample()
            value[registry].clear()
            self.assertEqual(examples.assess(value)['status'],'unsupported')

    def test_repin_changed_value_and_preserve_actual_source(self):
        first=sample()
        changed=sample({'amount':'2/1'})
        self.assertNotEqual(first['plan']['manifest_digest'],changed['plan']['manifest_digest'])
        result=examples.assess(changed)
        self.assertEqual(result['values']['x'],{'status':'known','value':'2/1'})
        self.assertEqual(result['assessment']['status'],'invalid')
        h=sha256(next(iter(changed['blobs'].values()))).hexdigest()
        self.assertEqual(result['lineage']['x']['source_ref'],'sha256:'+h+'#/amount')
        value=deepcopy(changed)
        manifest=next(iter(value['manifests'].values()))
        manifest['inputs']['x']['source_ref']='fixture.json#/amount'
        value['manifests']={core.digest(manifest):manifest}
        value['plan']['manifest_digest']=core.digest(manifest)
        self.assertEqual(examples.assess(value)['reason'],'binding_source_ref_mismatch')

    def test_explicit_missing_and_unknown_encodings(self):
        value=sample({},missing='unresolved')
        result=examples.assess(value)
        self.assertEqual(result['values']['x'],{'status':'unknown','reason':'missing_declared_path'})
        self.assertEqual(result['assessment']['status'],'unresolved')
        self.assertEqual(examples.assess(sample({}))['status'],'invalid')
        for encoding,status in [('scalar','invalid'),('legacy_unknown_string','bound')]:
            result=examples.assess(sample({'amount':'unknown'},encoding=encoding))
            self.assertEqual(result['status'],status)
        result=examples.assess(sample({'amount':'unknown'},kind='text'))
        self.assertEqual(result['assessment']['status'],'requirements_satisfied')
        result=examples.assess(sample({'amount':{'status':'unknown','reason':'not measured'}},encoding='tagged_binding'))
        self.assertEqual(result['values']['x'],{'status':'unknown','reason':'not measured'})
        self.assertEqual(examples.assess(sample({'amount':None}))['status'],'invalid')
        self.assertEqual(examples.assess(sample({'amount':True}))['status'],'invalid')

    def test_pointer_escapes_and_array_indices(self):
        for data,path in [({'a/b':{'~key':['1/1']}},'/a~1b/~0key/0'),
                          ({'':'1/1'},'/'),('1/1','')]:
            self.assertEqual(examples.assess(sample(data,path))['assessment']['status'],'requirements_satisfied')
        for path in ['/a~2','/missing/bad~2','amount','/a/-1','/a/01','/a/+0','/a/-']:
            self.assertEqual(examples.assess(sample({'a':['1/1']},path,missing='unresolved'))['status'],'invalid')
        self.assertEqual(examples.assess(sample({'a':['1/1']},'/a/1',missing='unresolved'))['assessment']['status'],'unresolved')
        self.assertEqual(examples.assess(sample({'a':'1/1'},'/a/missing',missing='unresolved'))['reason'],'scalar_pointer_traversal')

    def test_schema_swap_and_context_role_mismatch(self):
        for field,replacement in [('role','reported_measurement'),('type',{'kind':'rational',
                        'context':{'entity':'Sample','book_role':'consolidated','unit':'USD'}})]:
            value=sample()
            schema=next(iter(value['schemas'].values()))
            schema['fields']['/amount'][field]=replacement
            h=core.digest(schema)
            value['schemas']={h:schema}
            value['plan']['records']['supplied']['schema_digest']=h
            self.assertEqual(examples.assess(value)['status'],'invalid')
        value=sample()
        schema=next(iter(value['schemas'].values()))
        schema['fields']['/amount']['missing']='unresolved'
        self.assertEqual(examples.assess(value)['reason'],'schema_digest_mismatch')

    def test_duplicate_or_incomplete_mapping(self):
        for change in [lambda v:v['plan']['bindings'].clear(),
                       lambda v:v['plan']['bindings'].append(deepcopy(v['plan']['bindings'][0])),
                       lambda v:v['plan']['bindings'][0].update(input='absent'),
                       lambda v:v['plan']['bindings'][0].update(pointer='/not-declared'),
                       lambda v:v['plan']['records'].update(extra=deepcopy(v['plan']['records']['supplied'])),
                       lambda v:v['plan'].update(extra=True)]:
            value=sample()
            change(value)
            self.assertEqual(examples.assess(value)['status'],'invalid')

    def test_strict_decoder_and_structure_bounds(self):
        for raw in [b'{"amount":"1/1","amount":"2/1"}',b'{"amount":1.0}',
                    b'{"amount":NaN}',b'{"amount":"1/1","z":{"a":1,"a":2}}',
                    b'\xff',b'[] []']:
            value=examples.packet(definition(),raw,{'x':'/amount'})
            self.assertEqual(examples.assess(value)['status'],'invalid')
        data='1/1'
        for _ in range(core.MAX_DEPTH+2):
            data=[data]
        value=sample(data,'/0',missing='unresolved')
        self.assertEqual(examples.assess(value)['status'],'invalid')

    def test_bound_copies_do_not_mutate_caller(self):
        value=sample()
        before=deepcopy(value)
        result=examples.assess(value)
        result['values']['x']['value']='99/1'
        result['lineage']['x']['type']['context']['entity']='changed'
        self.assertEqual(value,before)


if __name__=='__main__':
    unittest.main()
