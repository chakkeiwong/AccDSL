"""Independent guarded activation tables and refusal semantics."""
from copy import deepcopy
from itertools import product
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import method_requirements_v1 as v1
import method_requirements_v2 as v2
import method_requirements_v3 as v3


def ref(key):
    return {'op':'ref','id':key}


def known(value):
    return {'status':'known','value':value}


def unknown():
    return {'status':'unknown','reason':'not observed'}


def fixture():
    return {'profile':v3.PROFILE,'method_id':'guard.activation','version':'3',
        'inputs':{k:{'type':deepcopy(v1.BOOL),'role':'caller_finding','source_ref':'constructed:'+k}
                  for k in ['guard','body']},
        'requirements':[{'id':'guarded','guard':ref('guard'),'guard_requires':['guard'],
                         'predicate':ref('body'),'requires':['body'],'admission_refs':[],
                         'on_false':'invalid','on_unknown':'unresolved'}],
        'required_known':[],'capabilities':['guarded'],
        'residual_prerequisites':['Actual applicability, authority and execution are separate.']}


def run(definition,values,available=None):
    key=v1.digest(definition)
    return v3.assess({key:definition},key,values,['guarded'] if available is None else available)


class GuardTests(unittest.TestCase):
    def test_nine_activation_pairs(self):
        values=[known(True),known(False),unknown()]
        expected=[['requirements_satisfied','invalid','unresolved'],
                  ['no_active_requirements','no_active_requirements','no_active_requirements'],
                  ['unresolved','unresolved','unresolved']]
        for g,b in product(range(3),repeat=2):
            with self.subTest(guard=g,body=b):
                result=run(fixture(),{'guard':values[g],'body':values[b]})
                self.assertEqual(result['status'],expected[g][b])
                finding=result['findings'][0]
                self.assertEqual(finding['activation'],['active','inactive','unknown'][g])
                self.assertEqual(finding['body_truth'],['true','false','unknown'][b])
                self.assertEqual(finding['dependencies'],['body','guard'])
                self.assertEqual(set(finding['unresolved_inputs']),
                                 {k for k,n in [('guard',g),('body',b)] if n==2})

    def test_required_facts_survive_false_guard(self):
        spec=fixture()
        spec['required_known']=['body']
        result=run(spec,{'guard':known(False),'body':unknown()})
        self.assertEqual(result['status'],'unresolved')
        self.assertEqual(result['findings'][0]['consequence'],'not_applicable')
        self.assertEqual(result['required_known_findings'][0]['reason'],'not observed')
        spec['inputs']['extra']={'type':{'kind':'text','context':{}},'role':'state','source_ref':'case:extra'}
        spec['required_known'].append('extra')
        result=run(spec,{'guard':known(False),'body':known(False),'extra':known('unknown')})
        self.assertEqual(result['status'],'no_active_requirements')
        result=run(spec,{'guard':known(False),'body':known(False)})
        self.assertEqual(result['required_known_findings'][1]['reason'],'missing_input')

    def test_false_guard_still_typechecks_body(self):
        spec=fixture()
        for node in [{'op':'call','name':'untrusted'},
                     {'op':'const','type':{'kind':'text','context':{}},'value':'true'}]:
            changed=deepcopy(spec)
            changed['requirements'][0]['predicate']=node
            changed['requirements'][0]['requires']=[]
            changed['required_known']=['body']
            self.assertEqual(run(changed,{'guard':known(False),'body':known(True)})['status'],'invalid')
        self.assertEqual(run(spec,{'guard':known(False),'body':known(0)})['status'],'invalid')

    def test_guard_and_body_dependency_declarations(self):
        for edit in [lambda d:d['requirements'][0].update(guard_requires=[]),
                     lambda d:d['requirements'][0].update(requires=[]),
                     lambda d:d.update(required_known=['absent']),
                     lambda d:d.update(required_known=['body','body']),
                     lambda d:d['requirements'].append(deepcopy(d['requirements'][0])),
                     lambda d:d['requirements'][0].update(guard={'op':'ref','id':'absent'})]:
            spec=fixture()
            edit(spec)
            self.assertEqual(run(spec,{'guard':known(False),'body':known(True)})['status'],'invalid')

    def test_changed_guard_requires_new_identity(self):
        spec=fixture()
        key=v1.digest(spec)
        changed=deepcopy(spec)
        changed['requirements'][0]['guard']={'op':'not','arg':ref('guard')}
        result=v3.assess({key:changed},key,{'guard':known(False),'body':known(True)},['guarded'])
        self.assertEqual(result['reason'],'definition_digest_mismatch')
        self.assertEqual(v3.assess({},key,{},[])['status'],'unsupported')

    def test_multiple_requirements_precedence_and_inactive_diagnostic(self):
        spec=fixture()
        second=deepcopy(spec['requirements'][0])
        second.update(id='active',guard={'op':'const','type':v1.BOOL,'value':True},guard_requires=[],on_false='unsupported')
        spec['requirements'].append(second)
        result=run(spec,{'guard':known(False),'body':known(False)})
        self.assertEqual(result['status'],'unsupported')
        self.assertEqual([f['consequence'] for f in result['findings']],['not_applicable','unsupported'])
        spec['requirements'][0]['guard']={'op':'const','type':v1.BOOL,'value':True}
        spec['requirements'][0]['guard_requires']=[]
        spec['required_known']=['guard']
        result=run(spec,{'guard':unknown(),'body':known(False)})
        self.assertEqual(result['status'],'invalid')
        self.assertEqual(result['required_known_findings'][0]['consequence'],'unresolved')

    def test_capabilities_and_no_admission(self):
        spec=fixture()
        values={'guard':known(False),'body':known(False)}
        before=deepcopy((spec,values))
        result=run(spec,values,[])
        self.assertEqual(result['status'],'unsupported')
        self.assertEqual(result['findings'][0]['consequence'],'not_applicable')
        for flag in ['executed','method_eligible','source_admission','accounting_admission']:
            self.assertFalse(result[flag])
        self.assertEqual(before,(spec,values))

    def test_guarded_product_reuses_v2(self):
        spec=fixture()
        t={'kind':'rational','context':{},'dimensions':{},'scale':'1/1'}
        spec['inputs']['body'].update(type=t,role='assumption')
        spec['requirements'][0]['predicate']={'op':'eq',
            'left':{'op':'mul','left':ref('body'),'right':ref('body')},
            'right':{'op':'const','type':t,'value':'4/1'}}
        for g,b,status in [(True,'2/1','requirements_satisfied'),(True,'3/1','invalid'),
                           (False,'3/1','no_active_requirements')]:
            result=run(spec,{'guard':known(g),'body':known(b)})
            self.assertEqual(result['status'],status)
            self.assertEqual(len(result['products']),1)
            self.assertEqual(result['findings'][0]['body_dependencies'],['body'])


if __name__=='__main__':
    unittest.main()
