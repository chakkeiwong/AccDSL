"""Versioned text and binding preserve independently evaluated definitions."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_requirement_versions as versions
import method_requirement_text_v2 as text
import method_input_binding_v2 as binder
spec=importlib.util.spec_from_file_location('interoperability_examples',
    ROOT/'data/accounting-master/requirement-version-interoperability-20261024/examples.py')
examples=importlib.util.module_from_spec(spec)
spec.loader.exec_module(examples)


def repin_schema(p):
    shape=next(iter(p['schemas'].values()))
    h=core.digest(shape)
    p['schemas']={h:shape}
    p['plan']['records']['derived']['schema_digest']=h


class InteroperabilityTests(unittest.TestCase):
    def test_three_version_text_exchange_and_bound_equality(self):
        for version in [1,2,3]:
            d,values=examples.fixture(version)
            exchange=examples.exchange(d,values)
            baseline=versions.assess(d,values,d['capabilities'])
            self.assertEqual(baseline['status'],'requirements_satisfied')
            self.assertEqual(text.lower(text.render(exchange)),exchange)
            self.assertEqual(text.decode_exchange(core.canonical(exchange).decode()),exchange)
            self.assertEqual(text.assess_exchange(exchange),baseline)
            p=examples.packet(d,values)
            before=deepcopy(p)
            result=examples.assess(p)
            self.assertEqual(result['status'],'bound')
            self.assertEqual(result['values'],values)
            selected=p['manifests'][p['plan']['manifest_digest']]
            self.assertEqual(result['assessment'],versions.assess(selected,values,d['capabilities']))
            self.assertEqual(p,before)
            self.assertEqual(result['plan_digest'],core.digest(p['plan']))
            self.assertEqual(result['manifest_digest'],p['plan']['manifest_digest'])
            for key,item in result['lineage'].items():
                self.assertEqual(item['type'],d['inputs'][key]['type'])
                self.assertEqual(item['schema_digest'],p['plan']['records']['derived']['schema_digest'])
                self.assertEqual(item['source_ref'],selected['inputs'][key]['source_ref'])
            for flag in ['executed','source_admission','accounting_admission','method_eligible']:
                self.assertFalse(result[flag])
                self.assertFalse(result['assessment'][flag])

    def test_guard_unknown_inactive_and_required_known(self):
        for activation,status in [(False,'no_active_requirements'),(None,'unresolved')]:
            d,values=examples.fixture(3)
            values['total']=examples.known('7/1')
            values['active']=({'status':'unknown','reason':'applicability absent'} if activation is None
                              else examples.known(activation))
            p=examples.packet(d,values)
            result=examples.assess(p)
            self.assertEqual(result['assessment']['status'],status)
            selected=p['manifests'][p['plan']['manifest_digest']]
            e=examples.exchange(selected,result['values'])
            self.assertEqual(text.assess_exchange(text.lower(text.render(e))),result['assessment'])
        d,values=examples.fixture(3)
        values['active']=examples.known(False)
        del values['amount']
        result=examples.assess(examples.packet(d,values))
        self.assertEqual(result['assessment']['status'],'unresolved')
        self.assertEqual(result['values']['amount'],{'status':'unknown','reason':'missing_declared_path'})
        self.assertEqual(result['assessment']['findings'][0]['consequence'],'not_applicable')

    def test_explicit_unknown_product_reasons_survive(self):
        d,values=examples.fixture(2)
        values['amount']={'status':'unknown','reason':'尚未觀察'}
        result=examples.assess(examples.packet(d,values))
        self.assertEqual(result['assessment']['status'],'unresolved')
        self.assertEqual(result['assessment']['findings'][0]['unresolved_inputs'],{'amount':'尚未觀察'})
        e=examples.exchange(d,values)
        self.assertEqual(text.lower(text.render(e)),e)

    def test_schema_version_type_context_role_refusals(self):
        edits=[lambda s:s.update(requirements_profile='MethodRequirements/1'),
               lambda s:s.update(profile='RequirementInputSchema/1'),
               lambda s:s.pop('requirements_profile'),
               lambda s:s['fields']['/amount']['type'].update(scale='1000/1'),
               lambda s:s['fields']['/amount']['type'].update(dimensions={'EUR':1}),
               lambda s:s['fields']['/amount']['type']['context'].update(entity='Other'),
               lambda s:s['fields']['/amount'].update(role='assumption')]
        for edit in edits:
            p=examples.packet(*examples.fixture(2))
            edit(next(iter(p['schemas'].values())))
            repin_schema(p)
            self.assertEqual(examples.assess(p)['status'],'invalid')

    def test_exact_hashes_and_missing_registries(self):
        for registry in ['manifests','schemas','blobs']:
            p=examples.packet(*examples.fixture(3))
            p[registry].clear()
            self.assertEqual(examples.assess(p)['status'],'unsupported')
        for registry in ['manifests','schemas','blobs']:
            p=examples.packet(*examples.fixture(3))
            key=next(iter(p[registry]))
            if registry=='blobs':
                p[registry][key]+=b' '
            elif registry=='schemas':
                p[registry][key]['schema_id']='changed'
            else:
                p[registry][key]['requirements'][0]['guard']={'op':'not','arg':{'op':'ref','id':'active'}}
            self.assertEqual(examples.assess(p)['status'],'invalid')

    def test_binding_map_exactness_and_source_reference(self):
        edits=[lambda p:p['plan']['bindings'].pop(),
               lambda p:p['plan']['bindings'].append(deepcopy(p['plan']['bindings'][0])),
               lambda p:p['plan']['bindings'][0].update(pointer='/absent'),
               lambda p:p['plan']['records'].update(unused=deepcopy(p['plan']['records']['derived']))]
        for edit in edits:
            p=examples.packet(*examples.fixture(2))
            edit(p)
            self.assertEqual(examples.assess(p)['status'],'invalid')
        p=examples.packet(*examples.fixture(2))
        d=next(iter(p['manifests'].values()))
        d['inputs']['amount']['source_ref']='invented:source'
        h=core.digest(d)
        p['manifests']={h:d}
        p['plan']['manifest_digest']=h
        self.assertEqual(examples.assess(p)['reason'],'binding_source_ref_mismatch')

    def test_versions_are_closed_without_migration(self):
        for profile in ['MethodRequirements/4','scripts.custom','',None,{}]:
            d,values=examples.fixture(2)
            d['profile']=profile
            with self.assertRaises(core.Invalid):
                text.validate_exchange(examples.exchange(d,values))
        d,values=examples.fixture(1)
        d['profile']='MethodRequirements/2'
        with self.assertRaises(core.Invalid):
            versions.validate(d)

    def test_required_known_declaration_is_explicit_even_when_empty(self):
        d,values=examples.fixture(3)
        d['required_known']=[]
        source=text.render(examples.exchange(d,values))
        self.assertIn('required_known [];',source)
        for changed in [source.replace('required_known [];\n',''),
                        source.replace('required_known [];','required_known [];\nrequired_known [];')]:
            with self.assertRaises(core.Invalid):
                text.lower(changed)

    def test_duplicate_keys_and_incompatible_forms(self):
        d,values=examples.fixture(3)
        e=examples.exchange(d,values)
        raw=core.canonical(e).decode()
        with self.assertRaises(ValueError):
            text.decode_exchange(raw.replace('"profile":','"profile":"duplicate","profile":',1))
        source=text.render(e)
        for changed in [source.replace('guarded ','require ',1),
                        source.replace('"kind":"rational"','"kind":"text","kind":"rational"',1),
                        source.replace(e['selected_digest'],'0'*64),
                        source+'available "late";\n']:
            with self.assertRaises(ValueError):
                text.lower(changed)

    def test_malformed_body_rejected_even_with_false_guard(self):
        d,values=examples.fixture(3)
        values['active']=examples.known(False)
        d['requirements'][0]['predicate']['left']['op']='caller_callback'
        self.assertEqual(examples.assess(examples.packet(d,values))['status'],'invalid')
        with self.assertRaises(core.Invalid):
            text.validate_exchange(examples.exchange(d,values))

    def test_constant_only_definition_needs_no_records(self):
        d={'profile':core.PROFILE,'method_id':'constant','version':'1','inputs':{},
           'requirements':[{'id':'true','predicate':{'op':'const','type':core.BOOL,'value':True},
                            'requires':[],'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'}],
           'capabilities':[],'residual_prerequisites':['Full applicability remains separate.']}
        h=core.digest(d)
        plan={'profile':binder.PROFILE,'manifest_digest':h,'records':{},'bindings':[]}
        result=binder.assess_bound(plan,{h:d},{},{},[])
        self.assertEqual(result['assessment']['status'],'requirements_satisfied')

    def test_independently_authored_dimensional_and_guarded_text(self):
        for version in [2,3]:
            d,values=examples.fixture(version)
            j=lambda value:core.canonical(value).decode()
            rows=['requirements_exchange "MethodRequirementExchange/2" '+j(d['profile'])+
                  ' "independent.interoperability" '+j(str(version))+';']
            for key in d['inputs']:
                item=d['inputs'][key]
                rows.append('input '+j(key)+' '+j(item['type'])+' '+item['role']+' '+j(item['source_ref'])+';')
            body='(eq (mul (ref "amount") (ref "rate")) (ref "total"))'
            if version==3:
                rows.append('guarded "amount-relation" invalid unresolved ["active"] '+
                            '["amount","rate","total"] [] (ref "active") '+body+';')
                rows.append('required_known ["amount"];')
            else:
                rows.append('require "amount-relation" invalid unresolved ["amount","rate","total"] [] '+body+';')
            rows.extend(['capability "exact-assessment";',
                         'residual '+j(d['residual_prerequisites'][0])+';',
                         'select '+j(core.digest(d))+';'])
            rows.extend('bind '+j(key)+' known '+j(value['value'])+';' for key,value in values.items())
            rows.extend(['available "exact-assessment";','end_requirements_exchange;'])
            self.assertEqual(text.lower(chr(10).join(rows)),examples.exchange(d,values))

    def test_strict_raw_decoder_still_applies_after_version_lowering(self):
        from hashlib import sha256
        for raw in [b'{"amount":1,"amount":2}',b'{"amount":NaN}',b'[] []',b'\xff']:
            p=examples.packet(*examples.fixture(3))
            h=sha256(raw).hexdigest()
            p['blobs']={h:raw}
            p['plan']['records']['derived']['raw_sha256']=h
            d=next(iter(p['manifests'].values()))
            for entry in p['plan']['bindings']:
                d['inputs'][entry['input']]['source_ref']='sha256:'+h+'#'+entry['pointer']
            key=core.digest(d)
            p['manifests']={key:d}
            p['plan']['manifest_digest']=key
            self.assertEqual(examples.assess(p)['status'],'invalid')


if __name__=='__main__':
    unittest.main()
