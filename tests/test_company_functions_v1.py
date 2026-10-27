from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import company_functions_v1 as m
spec = importlib.util.spec_from_file_location('company_function_examples',ROOT/'data/accounting-master/company-functions-20261025/examples.py')
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)

class CompanyFunctionsTests(unittest.TestCase):
    def outcome(self, body, status='evaluated', value=None):
        before = deepcopy(body); result = m.evaluate(body)
        self.assertEqual(result['status'],status,result)
        self.assertEqual(body,before)
        self.assertTrue(all(result[k] is False for k in m.FLAGS))
        if value is not None:self.assertEqual(result['evaluation']['outputs']['result']['value'],value)
        return result

    def test_policy_matches_manually_inlined_outputs(self):
        body=e.policy_program();r=self.outcome(body)
        baseline=m.load_baseline()
        import json
        manual=json.loads((ROOT/'data/accounting-master/company-expressions-20261023/fixture.json').read_text())
        self.assertEqual(r['evaluation']['outputs'],baseline.evaluate(manual)['outputs'])
        self.assertEqual([r['evaluation']['outputs'][n]['value'] for n in body['outputs']],['9/10','1/2','1/2'])

    def test_nested_and_repeated_calls_are_hygienic(self):
        body=e.call_chain(3)
        body['nodes'] += [e.literal('b','2/7'),e.call('s','f2','b'),e.node('sum','add','r','s')]
        body['outputs']={'result':'sum'}
        r=self.outcome(body,value='5/7')['compilation']
        self.assertEqual(len(r['graph']['nodes']),len({n['id'] for n in r['graph']['nodes']}))
        self.assertTrue(all('scope' in origin for origin in r['origins'].values()))
        self.assertEqual(len(r['call_sites']),6)

    def test_function_local_names_do_not_capture_caller(self):
        f=e.function('fixed',[],[e.literal('same','2/1')],'same')
        b=e.program([e.literal('same','99/1'),e.call('r','fixed')],[f])
        self.outcome(b,value='2/1')

    def test_unknowns_and_conditional_dependency_reporting(self):
        b=e.policy_program();b['inputs']['ordinary']['value']=False;b['inputs']['discount']['value']='unknown'
        r=self.outcome(b)['evaluation']['outputs']['fraction']
        self.assertEqual(r['value'],'4/5')
        self.assertEqual(r['declared_dependencies'],['discount','ordinary'])
        self.assertEqual(r['evaluated_inputs'],['ordinary'])
        b['inputs']['ordinary']['value']=True;self.outcome(b,'unresolved')
        b['inputs']['ordinary']['value']='unknown';self.outcome(b,'unresolved')

    def test_unused_arguments_are_not_evaluated_but_stay_inspectable(self):
        f=e.function('fixed',[('ignored',e.SCALAR)],[e.literal('r','7/1')],'r')
        b=e.program([{'id':'x','op':'input','target':'x'},e.literal('zero','0/1'),e.node('bad','div','x','zero'),e.call('r','fixed','bad')],[f],{'x':{'type':deepcopy(e.SCALAR),'value':'unknown'}})
        r=self.outcome(b,value='7/1')
        site=r['compilation']['call_sites'][0]
        self.assertEqual(site['declared_argument_dependencies'],['x'])
        self.assertEqual(site['effective_result_dependencies'],[])
        self.assertEqual(r['evaluation']['outputs']['result']['evaluated_inputs'],[])
        b['nodes'][-1]['args']=['missing'];self.outcome(b,'invalid')

    def test_selected_division_by_zero_remains_invalid(self):
        b=e.program([e.literal('one','unknown'),e.literal('zero','0/1'),e.node('bad','div','one','zero'),e.call('r','identity','bad')],[e.identity()])
        self.outcome(b,'invalid')

    def test_argument_return_and_unused_parameter_types_checked(self):
        b=e.program([e.literal('a',True,e.BOOL),e.call('r','identity','a')],[e.identity()])
        self.outcome(b,'invalid')
        b['nodes'][0]=e.literal('a','1/1');b['functions'][0]['return_type']=deepcopy(e.BOOL);self.outcome(b,'invalid')
        f=e.function('fixed',[('ignored',e.BOOL)],[e.literal('r','1/1')],'r')
        b['functions']=[f];b['nodes'][-1]['function']='fixed';self.outcome(b,'invalid')

    def test_units_and_contexts_are_preserved(self):
        money={'kind':'number','dimensions':{'USD':1},'context':'Northstar:2026'}
        b=e.program([e.literal('a','5/3',money),e.call('r','identity','a')],[e.identity(money)])
        r=self.outcome(b,value='5/3');self.assertEqual(r['evaluation']['outputs']['result']['type'],money)
        for typ in [dict(money,context='Other:2026'),dict(money,dimensions={'EUR':1}),e.SCALAR]:
            bad=deepcopy(b);bad['nodes'][0]['type']=deepcopy(typ);self.outcome(bad,'invalid')

    def test_input_and_parameter_capture_are_refused(self):
        b=e.program([e.literal('a','1/1'),e.call('r','identity','a')],[e.identity()])
        for op,target in [('input','global'),('param','missing')]:
            bad=deepcopy(b);bad['functions'][0]['nodes'][0]={'id':'r','op':op,'target':target};self.outcome(bad,'invalid')
        bad=deepcopy(b);bad['nodes'][0]=e.param('a','x');self.outcome(bad,'invalid')

    def test_recursion_and_unused_cycles_are_refused(self):
        b=e.call_chain(2)
        b['functions'][0]['nodes'] += [e.call('loop','f1','r')];self.outcome(b,'invalid')
        b=e.program([e.literal('r','1/1')],[e.identity()]);b['functions'][0]['nodes'] += [e.node('loop','neg','loop')];self.outcome(b,'invalid')
        b=e.program([e.literal('r','1/1'),e.node('loop','neg','loop')]);self.outcome(b,'invalid')

    def test_forward_references_and_every_unused_definition_checked(self):
        b=e.program([e.call('r','identity','a'),e.literal('a','2/3')],[e.identity()]);self.outcome(b,value='2/3')
        bad=deepcopy(b);bad['functions'].append(e.function('unused',[],[e.literal('r','2/2')],'r'));self.outcome(bad,'invalid')

    def test_duplicate_names_and_missing_targets(self):
        b=e.call_chain(1)
        for mutation in ['function','parameter','node','argument','function_target','output','function_output']:
            bad=deepcopy(b)
            if mutation=='function':bad['functions']*=2
            elif mutation=='parameter':bad['functions'][0]['parameters']*=2
            elif mutation=='node':bad['nodes'].append(deepcopy(bad['nodes'][0]))
            elif mutation=='argument':bad['nodes'][-1]['args']=[]
            elif mutation=='function_target':bad['nodes'][-1]['function']='absent'
            elif mutation=='output':bad['outputs']['result']='absent'
            else:bad['functions'][0]['output']='absent'
            with self.subTest(mutation=mutation):self.outcome(bad,'invalid')

    def test_closed_fields_and_host_operators_rejected(self):
        b=e.call_chain(1)
        for bad in [dict(b,extra=True),dict(b,profile='other'),None,[],{'x':float('nan')}]:self.outcome(bad,'invalid')
        for op in ['python_eval','shell','import','state_write']:
            bad=deepcopy(b);bad['nodes'][0]={'id':'a','op':op,'args':[]};self.outcome(bad,'invalid')

    def test_canonical_values_and_types_not_coerced(self):
        for value in [True,1,0.5,'2/2','01/1','1/0']:
            b=e.program([e.literal('a',value),e.call('r','identity','a')],[e.identity()]);self.outcome(b,'invalid')
        for exp in [True,0,1.0]:
            typ={'kind':'number','dimensions':{'USD':exp},'context':'company'}
            b=e.program([e.literal('a','1/1',typ),e.call('r','identity','a')],[e.identity(typ)]);self.outcome(b,'invalid')

    def test_call_depth_boundary(self):
        self.outcome(e.call_chain(16),value='3/7')
        self.outcome(e.call_chain(17),'invalid')

    def test_function_and_parameter_count_boundaries(self):
        fs=[e.function('f'+str(i),[],[e.literal('r','1/1')],'r') for i in range(32)]
        b=e.program([e.call('r','f0')],fs);self.outcome(b,value='1/1')
        b['functions'].append(e.function('extra',[],[e.literal('r','1/1')],'r'));self.outcome(b,'invalid')
        f=e.function('many',[('x'+str(i),e.SCALAR) for i in range(16)],[e.literal('r','1/1')],'r')
        b=e.program([e.literal('a','1/1'),e.call('r','many',*(['a']*16))],[f]);self.outcome(b,value='1/1')
        b['functions'][0]['parameters'].append({'name':'extra','type':deepcopy(e.SCALAR)});b['nodes'][-1]['args'].append('a');self.outcome(b,'invalid')

    def test_scope_and_expression_depth_boundaries(self):
        b=e.program([e.literal('n'+str(i),'1/1') for i in range(256)],outputs={'result':'n0'});self.outcome(b,value='1/1')
        b['nodes'].append(e.literal('extra','1/1'));self.outcome(b,'invalid')
        nodes=[e.literal('n0','1/1')]+[e.node('n'+str(i),'neg','n'+str(i-1)) for i in range(1,64)]
        b=e.program(nodes,outputs={'result':'n63'});self.outcome(b,value='-1/1')
        b['nodes'].append(e.node('n64','neg','n63'));b['outputs']['result']='n64';self.outcome(b,'invalid')

    def test_expansion_and_request_byte_budgets(self):
        b=e.policy_program();n=m.compile_program(b)['validation_emitted_nodes']
        with patch.dict(m.LIMITS,emitted_nodes=n):self.outcome(b)
        with patch.dict(m.LIMITS,emitted_nodes=n-1):self.outcome(b,'invalid')
        size=len(m.canonical(b))
        with patch.dict(m.LIMITS,request_bytes=size):self.outcome(b)
        with patch.dict(m.LIMITS,request_bytes=size-1):self.outcome(b,'invalid')

    def test_expanding_dag_refused_before_unbounded_growth(self):
        fs=[e.identity()];last='identity'
        for i in range(1,12):
            ident='f'+str(i);fs.append(e.function(ident,[('x',e.SCALAR)],
                [e.param('x','x'),e.call('a',last,'x'),e.call('b',last,'x'),e.node('r','add','a','b')],'r'));last=ident
        b=e.program([e.literal('a','1/1'),e.call('r',last,'a')],fs)
        self.outcome(b,'invalid')

    def test_baseline_hash_and_unicode_request_identity(self):
        b=e.policy_program();b['name']='会社 — Économie';r=self.outcome(b)
        self.assertEqual(r['compilation']['request_sha256'],m.digest(b))
        changed=deepcopy(b);changed['name']='会社 — Economie';self.assertNotEqual(m.digest(b),m.digest(changed))
        with patch.object(m,'BASE_SHA256','0'*64):self.outcome(b,'invalid')

    def test_depth_after_parameter_substitution_is_bounded(self):
        local=[e.param('n0','x')]+[e.node('n'+str(i),'neg','n'+str(i-1)) for i in range(1,33)]
        f=e.function('deep',[('x',e.SCALAR)],local,'n32')
        nodes=[e.literal('n0','1/1')]+[e.node('n'+str(i),'neg','n'+str(i-1)) for i in range(1,31)]
        b=e.program(nodes+[e.call('r','deep','n30')],[f]);self.outcome(b,value='1/1')
        b['nodes'].insert(-1,e.node('n31','neg','n30'));b['nodes'][-1]['args']=['n31'];self.outcome(b,value='-1/1')
        b['nodes'].insert(-1,e.node('n32','neg','n31'));b['nodes'][-1]['args']=['n32'];self.outcome(b,'invalid')

    def test_alias_only_expansion_visits_are_bounded(self):
        b=e.call_chain(16)
        b['nodes']=[e.literal('a','1/1')]+[e.call('c'+str(i),'f15','a') for i in range(119)]
        b['outputs']={'result':'c0'};self.outcome(b,value='1/1')
        b['nodes'].append(e.call('extra','f15','a'));r=self.outcome(b,'invalid')
        self.assertIn('expansion_scope_limit',r['detail'])

    def test_function_conditionals_preserve_lazy_failure_and_static_checks(self):
        f=e.function('select',[('g',e.BOOL)],[e.param('g','g'),e.literal('one','1/1'),e.literal('zero','0/1'),e.node('bad','div','one','zero'),e.node('r','if','g','one','bad')],'r')
        b=e.program([e.literal('g',True,e.BOOL),e.call('r','select','g')],[f]);self.outcome(b,value='1/1')
        b['nodes'][0]['value']=False;self.outcome(b,'invalid')
        b['nodes'][0]['value']='unknown';self.outcome(b,'unresolved')
        b['nodes'][0]['value']=True;b['functions'][0]['nodes'][-1]['args'][-1]='g';self.outcome(b,'invalid')

if __name__ == '__main__':unittest.main()
