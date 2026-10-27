"""Independent finite semantics checks; these do not certify accounting methods."""
from copy import deepcopy
from itertools import product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import method_requirements_v1 as m


def typ(kind='rational', **context):
    return {'kind':kind, 'context':context}


def ref(key):
    return {'op':'ref', 'id':key}


def const(value, t):
    return {'op':'const', 'type':deepcopy(t), 'value':value}


def binary(op, a, b):
    return {'op':op, 'left':a, 'right':b}


def known(value):
    return {'status':'known', 'value':value}


def unknown():
    return {'status':'unknown', 'reason':'not_observed'}


def manifest(predicate, declarations, consequence='invalid'):
    inputs = {k:{'type':deepcopy(t), 'role':'state', 'source_ref':'fixture:'+k}
              for k,t in declarations.items()}
    return {'profile':m.PROFILE, 'method_id':'test.method', 'version':'1',
            'inputs':inputs, 'requirements':[{'id':'condition', 'predicate':predicate,
                'requires':sorted(inputs), 'admission_refs':[], 'on_false':consequence,
                'on_unknown':'unresolved'}], 'capabilities':['test.capability'],
            'residual_prerequisites':['Full method admission is outside this selected check.']}


def run(definition, values, capabilities=None):
    key = m.digest(definition)
    return m.assess({key:definition}, key, values,
                    ['test.capability'] if capabilities is None else capabilities)


class RequirementTests(unittest.TestCase):
    def test_explicit_truth_tables(self):
        states = [known(True), known(False), unknown()]
        expected = {
            'all':[['true','false','unknown'], ['false','false','false'], ['unknown','false','unknown']],
            'any':[['true','true','true'], ['true','false','unknown'], ['true','unknown','unknown']]}
        for op, i, j in product(['all','any'], range(3), range(3)):
            with self.subTest(op=op, a=i, b=j):
                spec = manifest({'op':op, 'args':[ref('a'), ref('b')]}, {'a':m.BOOL,'b':m.BOOL})
                result = run(spec, {'a':states[i], 'b':states[j]})
                self.assertEqual(result['findings'][0]['truth'], expected[op][i][j])
                self.assertEqual(result['findings'][0]['dependencies'], ['a','b'])
                self.assertEqual(set(result['findings'][0]['unresolved_inputs']),
                                 {k for k,n in [('a',i),('b',j)] if n==2})
        for value, expected in zip(states, ['false','true','unknown']):
            result = run(manifest({'op':'not','arg':ref('a')}, {'a':m.BOOL}), {'a':value})
            self.assertEqual(result['findings'][0]['truth'], expected)

    def test_all_children_typechecked_even_when_decisive(self):
        spec = manifest({'op':'all','args':[const(False,m.BOOL),ref('a')]}, {'a':typ()})
        self.assertEqual(run(spec, {'a':known('1/1')})['status'], 'invalid')

    def test_unknown_preserves_identity_without_symbolic_proof(self):
        for expr in [binary('eq',ref('x'),ref('x')),
                     binary('eq',binary('sub',ref('x'),ref('x')),const('0/1',typ()))]:
            result = run(manifest(expr,{'x':typ()}),{'x':unknown()})
            self.assertEqual(result['status'],'unresolved')
            self.assertEqual(result['findings'][0]['dependencies'],['x'])
            self.assertEqual(result['findings'][0]['unresolved_inputs'],{'x':'not_observed'})
        p = {'op':'any','args':[ref('x'),{'op':'not','arg':ref('x')}]}
        self.assertEqual(run(manifest(p,{'x':m.BOOL}),{'x':unknown()})['status'],'unresolved')

    def test_exact_arithmetic_and_boundaries(self):
        cases = [('1/3','2/3','1/1'),('-7/4','1/2','-5/4'),
                 ('9007199254740993/1','1/1','9007199254740994/1')]
        for a,b,c in cases:
            expr = binary('eq',binary('add',ref('a'),ref('b')),const(c,typ()))
            self.assertEqual(run(manifest(expr,{'a':typ(),'b':typ()}),
                                 {'a':known(a),'b':known(b)})['status'],'requirements_satisfied')
        for op, a, b, truth in [('lt','1/3','1/3','false'),('le','1/3','1/3','true'),
                                ('lt','-1/3','0/1','true'),('eq','-1/3','1/3','false')]:
            result = run(manifest(binary(op,ref('a'),const(b,typ())),{'a':typ()}),{'a':known(a)})
            self.assertEqual(result['findings'][0]['truth'],truth)

    def test_types_and_contexts_are_not_coerced(self):
        for first,second in [(typ(currency='USD'),typ(currency='EUR')),
                             (typ(unit='million'),typ(unit='unit')),
                             (typ(book='legal'),typ(book='consolidated')),
                             (typ(entity='P'),typ(entity='S')),
                             (typ(at='2025-01-01'),typ(at='2025-12-31')),
                             (typ(basis='IFRS'),typ(basis='GAAP')),
                             (typ(),typ('text'))]:
            self.assertEqual(run(manifest(binary('eq',ref('a'),ref('b')),{'a':first,'b':second}),
                                 {'a':known('1/1'),'b':known('1/1')})['status'],'invalid')
        for value in ['1','2/2','-0/1','1/0','01/1','1/-1',1,1.0,True,float('nan')]:
            self.assertEqual(run(manifest(binary('eq',ref('a'),const('1/1',typ())),{'a':typ()}),
                                 {'a':known(value)})['status'],'invalid')
        self.assertEqual(run(manifest(ref('a'),{'a':m.BOOL}),{'a':known(1)})['status'],'invalid')

    def test_unknown_text_missing_value_and_dates(self):
        t = typ('text')
        spec = manifest(binary('eq',ref('a'),const('unknown',t)),{'a':t})
        self.assertEqual(run(spec,{'a':known('unknown')})['status'],'requirements_satisfied')
        result = run(spec,{})
        self.assertEqual(result['findings'][0]['unresolved_inputs'],{'a':'missing_input'})
        d = typ('date',calendar='Gregorian')
        spec = manifest(binary('lt',ref('a'),const('2025-01-01',d)),{'a':d})
        self.assertEqual(run(spec,{'a':known('2024-02-29')})['status'],'requirements_satisfied')
        for value in ['2023-02-29','20240101','2024-2-9']:
            self.assertEqual(run(spec,{'a':known(value)})['status'],'invalid')

    def test_selected_hash_and_absent_capability(self):
        spec = manifest(ref('a'),{'a':m.BOOL})
        key = m.digest(spec)
        changed = deepcopy(spec)
        changed['version'] = '2'
        self.assertEqual(m.assess({key:changed},key,{'a':known(True)},[])['status'],'invalid')
        self.assertEqual(m.assess({},key,{},[])['status'],'unsupported')
        result = run(spec,{'a':known(True)},[])
        self.assertEqual(result['missing_capabilities'],['test.capability'])
        self.assertEqual(result['status'],'unsupported')
        # A known contradiction is retained even if a capability is unavailable.
        self.assertEqual(run(spec,{'a':known(False)},[])['status'],'invalid')

    def test_immutable_and_no_admission(self):
        spec = manifest(ref('a'),{'a':m.BOOL})
        spec['inputs']['a']['role'] = 'caller_finding'
        spec['requirements'][0]['admission_refs'] = ['review:needed']
        values = {'a':known(True)}
        before = deepcopy((spec,values))
        result = run(spec,values)
        self.assertEqual(before,(spec,values))
        for key in ['executed','source_admission','accounting_admission','method_eligible']:
            self.assertIs(result[key],False)
        self.assertEqual(result['scope'],'selected_requirements_only')
        self.assertEqual(result['findings'][0]['admission_refs'],['review:needed'])
        self.assertEqual(result['input_declarations']['a']['role'],'caller_finding')
        result['input_declarations']['a']['role'] = 'state'
        self.assertEqual(spec['inputs']['a']['role'],'caller_finding')

    def test_consequence_precedence_preserves_all_findings(self):
        spec = manifest(ref('a'),{'a':m.BOOL})
        for key,consequence in [('b','unsupported'),('c','invalid')]:
            spec['inputs'][key] = deepcopy(spec['inputs']['a'])
            spec['requirements'].append({'id':key,'predicate':ref(key),'requires':[key],
                'admission_refs':[],'on_false':consequence,'on_unknown':'unresolved'})
        cases = [(unknown(),known(False),known(False),'invalid'),
                 (unknown(),known(False),known(True),'unsupported'),
                 (unknown(),known(True),known(True),'unresolved')]
        for a,b,c,status in cases:
            result = run(spec,{'a':a,'b':b,'c':c})
            self.assertEqual(result['status'],status)
            self.assertEqual(len(result['findings']),3)

    def test_closed_manifest_and_malformed_nodes(self):
        original = manifest(ref('a'),{'a':m.BOOL})
        changes = [lambda s:s.update(extra=True),
                   lambda s:s['requirements'][0].update(extra=True),
                   lambda s:s['inputs']['a'].update(role='authority'),
                   lambda s:s['inputs']['a'].update(extra=True),
                   lambda s:s['requirements'][0].update(requires=[]),
                   lambda s:s['requirements'][0].update(requires=['a','a']),
                   lambda s:s['requirements'][0].update(on_unknown='satisfied'),
                   lambda s:s.update(residual_prerequisites=[]),
                   lambda s:s['requirements'].append(deepcopy(s['requirements'][0])),
                   lambda s:s['inputs'].update(unused=deepcopy(s['inputs']['a'])),
                   lambda s:s['requirements'][0].update(predicate={'op':'call','name':'arbitrary'}),
                   lambda s:s['requirements'][0].update(predicate={'op':'all','args':[]}),
                   lambda s:s['requirements'][0].update(predicate={'op':'ref','id':'missing'})]
        for i,change in enumerate(changes):
            with self.subTest(case=i):
                spec = deepcopy(original)
                change(spec)
                self.assertEqual(run(spec,{'a':known(True)})['status'],'invalid')
        for values in [{'extra':known(True)}, {'a':{'status':'known','value':True,'extra':1}},
                       {'a':{'status':'unknown','reason':'x','value':0}}, {'a':True}]:
            self.assertEqual(run(original,values)['status'],'invalid')

    def test_resource_limits(self):
        node = ref('a')
        for _ in range(m.MAX_DEPTH+1):
            node = {'op':'not','arg':node}
        self.assertEqual(run(manifest(node,{'a':m.BOOL}),{'a':known(True)})['status'],'invalid')
        spec = manifest({'op':'all','args':[ref('a')]*(m.MAX_NODES+1)},{'a':m.BOOL})
        self.assertEqual(run(spec,{'a':known(True)})['status'],'invalid')


if __name__ == '__main__':
    unittest.main()
