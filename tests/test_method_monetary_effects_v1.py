"""Independent exact results and adversarial monetary-language boundaries."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import method_monetary_effects_v1 as effects
spec=importlib.util.spec_from_file_location('monetary_fixture_examples', ROOT/'data/accounting-master/typed-monetary-effects-20261024/examples.py')
examples=importlib.util.module_from_spec(spec)
spec.loader.exec_module(examples)
core=effects.core
CONTEXT={'entity':'test','book_role':'legal','at':'2025-01-01'}


def fixture():
    definition=examples.program('settle',CONTEXT,
        ['cash','refund_liability','recovery_asset','inventory','revenue','cogs','selling_expense'])
    values={k:{'status':'known','value':v} for k,v in {
        'n':'2/1','p':'20/1','c':'12/1','d':'2/1','h':'4/1','nrv':'19/1',
        'refund_before':'60/1','recovery_before':'24/1'}.items()}
    return definition,values


class MonetaryEffectsTests(unittest.TestCase):
    def test_independent_settlement_result_and_input_immutability(self):
        definition,values=fixture();before=deepcopy((definition,values))
        result=examples.run(definition,values)
        self.assertEqual(result['status'],'derived',result)
        self.assertEqual(result['journal'],{'cash':'-48/1','refund_liability':'60/1',
            'recovery_asset':'-24/1','inventory':'19/1','revenue':'-20/1','cogs':'5/1','selling_expense':'8/1'})
        self.assertEqual([x['amount'] for x in result['flows']],['-40/1','-8/1'])
        self.assertEqual((definition,values),before)
        for flag in effects.BOUNDARY:
            if flag!='scope':self.assertFalse(result[flag])

    def test_exact_fractions_and_transitive_dependencies(self):
        definition,values=fixture();values['n']['value']='1/3'
        result=examples.run(definition,values)
        found={x['id']:x for x in result['diagnostics']['calculations']}
        self.assertEqual(found['refund']['binding']['value'],'20/3')
        self.assertEqual(found['carrying']['binding']['value'],'10/3')
        self.assertEqual(found['carrying']['dependencies'],['c','d','n','nrv'])
        values['n']={'status':'unknown','reason':'not counted'}
        result=examples.run(definition,values)
        self.assertEqual(result['status'],'unresolved')
        self.assertNotIn('journal',result)
        self.assertEqual(result['unresolved_inputs'],{'n':'not counted'})
        found={x['id']:x for x in result['diagnostics']['calculations']}
        self.assertEqual(found['tax_adjustment']['binding']['value'],'-36/1')

    def test_unknown_times_zero_and_min_remain_unknown(self):
        for key in ['n','c','nrv']:
            definition,values=fixture();values[key]={'status':'unknown','reason':'unobserved'}
            values['p']['value']='0/1';values['h']['value']='0/1'
            self.assertEqual(examples.run(definition,values)['status'],'unresolved')
        definition,values=fixture();values.pop('nrv')
        result=examples.run(definition,values)
        self.assertEqual(result['unresolved_inputs'],{'nrv':'missing_input'})

    def test_min_on_either_side_ties_and_negative_coefficients(self):
        for cap,expected in [('5/1','5/1'),('20/1','20/1'),('100/1','20/1'),('-3/1','-3/1')]:
            definition,values=fixture();values['nrv']['value']=cap
            result=examples.run(definition,values)
            self.assertEqual(result['status'],'derived')
            self.assertEqual(result['journal']['inventory'],expected)
        # Algebra deliberately does not invent the financial nonnegative domain.

    def test_exact_context_dimension_and_scale_mismatches(self):
        for field,value in [('context',{**CONTEXT,'at':'2025-01-02'}),
                            ('dimensions',{'currency:EUR':1}),('scale','1000/1')]:
            definition,values=fixture();definition['inputs']['nrv']['type'][field]=value
            self.assertEqual(examples.run(definition,values)['status'],'invalid')
        definition,values=fixture();definition['accounts']['inventory']['scale']='1000/1'
        self.assertEqual(examples.run(definition,values)['status'],'invalid')

    def test_dimensional_scale_product_uses_existing_algebra(self):
        definition,values=fixture()
        definition['inputs']['n']['type']['scale']='1000/1'
        for key in ['p','c','d','h']:definition['inputs'][key]['type']['scale']='1/1000'
        self.assertEqual(examples.run(definition,values)['status'],'derived')
        definition['inputs']['c']['type']['scale']='1/100'
        self.assertEqual(examples.run(definition,values)['status'],'invalid')

    def test_forward_cycles_collisions_and_exact_dependencies(self):
        edits=[lambda d:d['calculations'][0].update(expression=examples.ref('carrying')),
               lambda d:d['calculations'][0].update(expression=examples.ref('refund')),
               lambda d:d['calculations'][0].update(id='n'),
               lambda d:d['calculations'][0].update(requires=['n']),
               lambda d:d['postings'][0].update(requires=['refund_before','n']),
               lambda d:d['inputs'].update(unused=deepcopy(d['inputs']['n']))]
        for edit in edits:
            definition,values=fixture();edit(definition)
            self.assertEqual(examples.run(definition,values)['status'],'invalid')

    def test_closed_forms_unknown_operators_and_registries(self):
        edits=[lambda d:d.update(callback='anything'),lambda d:d.update(profile='MethodMonetaryEffects/2'),
               lambda d:d['calculations'][0]['expression'].update(op='div'),
               lambda d:d['postings'][0].update(account='absent'),
               lambda d:d.update(cash_account='absent'),
               lambda d:d['flows'][0].update(activity='uncategorized'),
               lambda d:d['inputs']['n'].update(role='caller_finding'),
               lambda d:d['postings'][1].update(id=d['postings'][0]['id']),
               lambda d:d['flows'][1].update(id=d['flows'][0]['id'])]
        for edit in edits:
            definition,values=fixture();edit(definition)
            self.assertEqual(examples.run(definition,values)['status'],'invalid')
        definition,values=fixture();h=core.digest(definition)
        self.assertEqual(effects.derive({},h,values)['status'],'unsupported')
        self.assertEqual(effects.derive({'0'*64:definition},'0'*64,values)['reason'],'definition_digest_mismatch')

    def test_malformed_known_and_unknown_values(self):
        for bad in [True,1,1.5,'1','2/2','0/2','1/0','NaN']:
            definition,values=fixture();values['n']['value']=bad
            self.assertEqual(examples.run(definition,values)['status'],'invalid')
        for item in [{'status':'unknown'}, {'status':'unknown','reason':''},
                     {'status':'known','value':'1/1','reason':'extra'}]:
            definition,values=fixture();values['n']=item
            self.assertEqual(examples.run(definition,values)['status'],'invalid')

    def test_unbalanced_and_cash_mismatch_rejected(self):
        definition,values=fixture();definition['postings'].pop()
        self.assertEqual(examples.run(definition,values)['reason'],'unbalanced_derived_journal')
        definition,values=fixture();definition['flows'].pop()
        self.assertEqual(examples.run(definition,values)['reason'],'derived_gross_cash_mismatch')

    def test_zero_flows_remain_separate_and_ordered(self):
        definition,values=fixture();values['h']['value']='0/1'
        result=examples.run(definition,values)
        self.assertEqual([(x['origin'],x['amount']) for x in result['flows']],
                         [('refund','-40/1'),('handling','0/1')])

    def test_balanced_wrong_measurement_does_not_equal_native(self):
        definition,values=fixture()
        money=examples.types(CONTEXT)[0]
        carrying=definition['calculations'][2]
        carrying['expression']=examples.binary('add',carrying['expression'],
            {'op':'const','type':money,'value':'1/1'})
        result=examples.run(definition,values)
        self.assertEqual(result['status'],'derived')
        self.assertEqual(sum(Fraction(x) for x in result['journal'].values()),0)
        self.assertNotEqual(result['journal']['inventory'],'19/1')
        self.assertNotEqual(result['journal']['cogs'],'5/1')
        self.assertFalse(result['method_eligible'])

    def test_global_node_and_each_category_bounds(self):
        definition,values=fixture()
        node=examples.ref('n')
        for i in range(12):node=examples.binary('add',deepcopy(node),deepcopy(node))
        definition['calculations'][0]['expression']=node
        self.assertEqual(examples.run(definition,values)['reason'],'expression_limit')
        for category in ['calculations','postings','flows']:
            definition,values=fixture();definition[category]=[definition[category][0]]*257
            self.assertEqual(examples.run(definition,values)['reason'],category+'_limit')
        definition,values=fixture()
        definition['inputs']={str(i):deepcopy(definition['inputs']['n']) for i in range(257)}
        self.assertEqual(examples.run(definition,values)['reason'],'input_limit')
        definition,values=fixture()
        definition['accounts']={str(i):deepcopy(definition['accounts']['cash']) for i in range(257)}
        self.assertEqual(examples.run(definition,values)['reason'],'account_limit')

    def test_bounded_bits_entries_depth_and_definition_size(self):
        definition,values=fixture();values['n']['value']=str(2**4096)+'/1'
        self.assertEqual(examples.run(definition,values)['reason'],'rational_bit_limit')
        definition,values=fixture();values['n']['value']=str(2**4090)+'/1';values['p']['value']='1024/1'
        self.assertEqual(examples.run(definition,values)['reason'],'rational_bit_limit')
        definition,values=fixture();definition['flows']*=257
        self.assertEqual(examples.run(definition,values)['reason'],'flows_limit')
        definition,values=fixture();node=examples.ref('n')
        for i in range(50):node=examples.binary('add',node,examples.ref('n'))
        definition['calculations'][0]['expression']=node
        self.assertEqual(examples.run(definition,values)['reason'],'expression_limit')
        definition,values=fixture();definition['method_id']='x'*1_000_001
        self.assertEqual(examples.run(definition,values)['reason'],'definition_size_limit')

    def test_recomputed_native_comparators(self):
        rows=examples.comparisons()
        self.assertEqual(len(rows),10)
        for row in rows:self.assertTrue(row['passed'],row['case'])


if __name__=='__main__':
    unittest.main()
