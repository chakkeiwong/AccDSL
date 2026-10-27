from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import shared_state_compatibility_v1 as m
spec=importlib.util.spec_from_file_location('compat_examples',ROOT/'data/accounting-master/shared-state-compatibility-20261024/examples.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)

class CompatibilityTests(unittest.TestCase):
    def test_all_cases_and_immutability(self):
        for row in e.cases():
            before=deepcopy(row['request']);r=m.assess(row['request'])
            self.assertEqual(r['status'],row['expected_status'],row['case'])
            self.assertEqual(before,row['request']);self.assertTrue(m.verify_result(before,r))
            self.assertTrue(all(r[k] is False for k in m.FLAGS))

    def test_native_positive_controls_preserve_effects_and_memory(self):
        import module_invocation_v1 as caller
        for key,row in e.originals().items():
            r=caller.invoke(row['request']);self.assertEqual(r,row['result'])
            before=e.states()[key];p=r['native_result']['proposal'];after=p['after']
            self.assertEqual(sum(Q(x) for x in p['journal'].values()),0)
            for name,value in before['balances'].items():self.assertEqual(Q(after['balances'][name])-Q(value),Q(p['journal'][name]))
            self.assertEqual(Q(p['journal']['cash']),sum(Q(f['amount']) for f in p['flows']))
            expected={'balances','component','date','flows','lots','seen','tax_adjustments'} if key=='typed_return' else {'balances','leases','seen'}
            self.assertEqual({k for k in before if before[k]!=after[k]},expected)
            for field in set(before)-expected:self.assertEqual(before[field],after[field])

    def test_shared_names_are_not_equivalence(self):
        row=next(x for x in e.cases() if x['case']=='return_lease');r=m.assess(row['request'])
        self.assertIn('cash',r['accounts']['shared_names']);self.assertFalse(r['accounts']['shared_names_prove_equivalence'])
        self.assertIn('cogs',r['accounts']['left_only']);self.assertIn('cost_of_sales',r['accounts']['right_only'])
        self.assertEqual(r['accounts']['mapping_status'],'unresolved')
        self.assertIn('module_memory',[x['field'] for x in r['missing_evidence']])

    def test_unknown_and_false_remain_distinct(self):
        rows={x['case']:m.assess(x['request']) for x in e.cases()}
        self.assertEqual(rows['unknown_membership']['status'],'unresolved')
        self.assertEqual(rows['same_invalid_state']['status'],'incompatible')
        self.assertEqual(rows['stale_digest']['status'],'invalid')

    def test_forged_compatibility_and_new_fields_rejected(self):
        row=e.cases()[2];r=m.assess(row['request']);r['status']='compatible'
        self.assertFalse(m.verify_result(row['request'],r))
        bad=deepcopy(row['request']);bad['account_map']={'cogs':'cost_of_sales'}
        self.assertEqual(m.assess(bad)['status'],'invalid')

    def test_unknown_profile_rejected(self):
        body=e.cases()[0]['request'];body['left']['module_id']='new_compatible_module'
        self.assertEqual(m.assess(body)['status'],'invalid')

    def test_unrelated_unknown_does_not_hide_invalid_balance(self):
        state=e.states()['typed_return'];state['component']['unit_refund']='unknown'
        state['balances']['cash']='0/1'
        r=m.assess(m.request('typed_return',state,'typed_return',state))
        self.assertEqual(r['status'],'incompatible')

if __name__=='__main__':unittest.main()
