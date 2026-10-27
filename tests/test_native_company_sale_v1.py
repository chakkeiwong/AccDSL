from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import native_company_sale_v1 as adapter
spec=importlib.util.spec_from_file_location('native_company_sale_examples',ROOT/'data/accounting-master/native-company-sale-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)


class NativeCompanySaleTests(unittest.TestCase):
    def run_case(self,state,event,status='proposed'):
        original=deepcopy((state,event));body=adapter.request(state,event);result=adapter.propose(state,body)
        self.assertEqual(result['status'],status,result)
        self.assertEqual((state,event),original)
        for flag in adapter.FLAGS:self.assertFalse(result[flag])
        return body,result

    def test_complete_native_comparison_suite(self):
        result=ex.compare();self.assertEqual(len(result['cases']),23)
        self.assertEqual([x['name'] for x in result['checks'] if not x['passed']],[])

    def test_two_lot_independent_financial_results(self):
        state,event=ex.two_lots();body,result=self.run_case(state,event)
        self.assertEqual(result['after']['balances']['cash'],'494/1')
        self.assertEqual(result['after']['balances']['inventory'],'5/1')
        self.assertEqual(result['after']['balances']['cogs'],'71/1')
        self.assertEqual(result['after']['lots']['unsold'],state['lots']['unsold'])
        for key in state:
            if key not in ['balances','date','seen','flows','lots']:self.assertEqual(result['after'][key],state[key],key)

    def test_adapter_never_calls_native_transition_for_effects(self):
        state,event=ex.two_lots()
        with patch.object(adapter.native,'transition',side_effect=AssertionError('native transition must remain comparator only')):
            body,result=self.run_case(state,event)
            self.assertEqual(adapter.apply(state,body,result)['status'],'applied_provisional')

    def test_second_lot_sale_and_duplicate_refusal(self):
        state,event=ex.two_lots();body,result=self.run_case(state,event);state=result['after']
        event.update(id='second-sale',date='2025-10-01',lot_id='unsold',proceeds='8/1')
        body,result=self.run_case(state,event);self.assertEqual(result['after']['balances']['inventory'],'0/1')
        self.assertEqual(result['after']['balances']['cash'],'502/1')
        self.run_case(result['after'],event,'invalid')

    def test_native_unknown_and_funding_statuses(self):
        for name,state,event in ex.cases():
            if name in ['unknown_proceeds','unknown_performance']:self.run_case(state,event,'unresolved')
            elif name=='negative_cash':self.run_case(state,event,'funding_failure')

    def test_structural_malformations_rejected(self):
        for kind in ['extra','missing','source','date','balance']:
            state,event=ex.start()
            if kind=='extra':state['extra']='unrecognized'
            elif kind=='missing':state.pop('source')
            elif kind=='source':state['source']['packet_sha256']='not-a-hash'
            elif kind=='date':state['lots'][event['lot_id']]['acquired']='yesterday'
            else:state['balances']['cash']='908/2'
            self.run_case(state,event,'invalid')

    def test_stale_state_event_and_rehashed_tampering(self):
        state,event=ex.two_lots();body,result=self.run_case(state,event)
        state['source']['meaning']='changed';self.assertEqual(adapter.propose(state,body)['status'],'invalid')
        state,event=ex.two_lots();body,result=self.run_case(state,event);body['event']['proceeds']='1/1'
        self.assertEqual(adapter.propose(state,body)['status'],'invalid')
        for kind in ['flag','complement','lot','journal']:
            state,event=ex.two_lots();body,result=self.run_case(state,event)
            if kind=='flag':result['committed']=0
            elif kind=='complement':result['after']['source']['meaning']='changed'
            elif kind=='lot':result['after']['lots']['unsold']['carrying']='999/1'
            else:result['journal']['cash']='999/1'
            result['after_sha256']=adapter.digest(result['after'])
            self.assertEqual(adapter.apply(state,body,result)['status'],'invalid')

    def test_empty_selected_population_and_unknown_event_shape(self):
        state,event=ex.start();state['other_inventory']='20/1';state['lots']={};self.run_case(state,event,'invalid')
        state,event=ex.start();event['callback']='untrusted';self.run_case(state,event,'invalid')
        state,event=ex.start();event['kind']='settle';self.run_case(state,event,'unsupported')

    def test_native_dependency_pins(self):
        state,event=ex.start()
        with patch.dict(adapter.PINS,{'company_method_clock_v1.py':'0'*64}):self.run_case(state,event,'invalid')


if __name__=='__main__':unittest.main()
