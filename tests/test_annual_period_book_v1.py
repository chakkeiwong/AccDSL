from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
s=importlib.util.spec_from_file_location('annual_examples',ROOT/'data/accounting-master/reusable-annual-interface-20261025/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m

class AnnualPeriodBookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q=x.scenario();cls.r=m.run(cls.q)
        cls.repeated=x.repeated_scenario();cls.rr=m.run(cls.repeated)
        assert cls.r['status']==cls.rr['status']=='complete_provisional'

    def test_independent_three_liability_arithmetic(self):
        r=self.r;b=r['period_book']['after']['balances']
        self.assertEqual([v['closing_payable'] for v in r['period_book']['period_vintages']],['7/4','2/1','1/1'])
        self.assertEqual({k:b[k] for k in ['cash','current_tax','income_tax_payable']},{'cash':'701/2','current_tax':'3/1','income_tax_payable':'-19/4'})
        self.assertEqual(r['recorded_statements']['recorded_profit'],'-5/1')
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'],'-7/1')
        self.assertEqual(set(r['recorded_statements']['reconciliations'].values()),{'0/1'})

    def test_each_first_assessment_preserves_all_carried_vintages(self):
        before=m.seed(self.r['root_result']);first=self.r['trace'][0]['result']['after']
        states=[self.r['root_result']['opening'],self.r['root_result']['after']]+[t['result']['after'] for t in self.r['root_result']['trace']]
        rights={(a['component']['lease_id'],r['right_id']) for s in states for a in s['leases'] for r in a['component']['rights']}
        self.assertEqual({tuple(pair) for pair in before['period_rights']},rights)
        self.assertEqual(first['period_vintages'][:-1],before['period_vintages'])
        final=self.rr['period_book'];opening=self.rr['trace'][-2]['result']['after']
        self.assertEqual(len(final['period_vintages']),4)
        self.assertEqual(final['period_vintages'][:-1],opening['period_vintages'])

    def test_replacement_preserves_stable_id_payments_and_history(self):
        before=self.r['trace'][1]['result']['after'];after=self.r['period_book']
        self.assertEqual(before['period_vintages'][:2],after['period_vintages'][:2])
        self.assertEqual(before['period_vintages'][2]['id'],after['period_vintages'][2]['id'])
        self.assertEqual(before['period_vintages'][2]['settlements'],after['period_vintages'][2]['settlements'])
        self.assertEqual([a['tax_amount'] for a in after['current_assessments']],['4/1','3/1'])
        self.assertEqual(self.r['trace'][2]['result']['journal']['current_tax'],'-1/1')

    def test_replacement_below_paid_refuses_and_keeps_prefix(self):
        state=self.r['period_book'];bad=x.assessment(state,'4/1','refund-needed','replace')
        q=m.request(self.q['root_request'],self.q['operations']+[bad,x.previous.depreciation(day='2027-07-01')]);r=m.run(q)
        self.assertEqual(r['stop']['status'],'unsupported');self.assertEqual(r['stop']['reason'],'tax_receivable_or_refund_required')
        self.assertEqual(r['period_book'],state);self.assertEqual(len(r['remaining_operations']),2)
        self.assertEqual(m.apply(q,r)['status'],'applied_provisional')

    def test_carry_archives_actual_balances_and_resets_only_period_movements(self):
        final=self.rr['period_book'];archive=final['period_archive'][0]
        self.assertEqual(final['after']['balances']['retained'],'73/4')
        self.assertEqual(archive['report']['recorded_profit'],'-5/1')
        self.assertEqual(archive['report']['indirect_operating']['net'],'-7/1')
        self.assertEqual(final['after']['balances']['cash'],'701/2')
        self.assertEqual(final['after']['flows'],[])
        self.assertEqual([v['opening_payable'] for v in final['period_vintages']],['7/4','2/1','1/1','0/1'])
        self.assertEqual(final['historical_vintages'],self.r['root_result']['tax_vintages'])
        self.assertEqual(final['recognition_archive'],self.r['root_result']['archive'])
        self.assertEqual(self.rr['recorded_statements']['recorded_profit'],'-2/1')
        self.assertEqual(self.rr['recorded_statements']['indirect_operating']['net'],'0/1')

    def test_carry_needs_fresh_exact_state_deferred_measurement(self):
        ops=self.repeated['operations'][:5];state=self.rr['trace'][4]['result']['after']
        payment=x.payment(state,['0/1','0/1','1/1'],identity='after-deferred',day='2027-12-31')
        q=m.request(self.q['root_request'],ops+[payment,x.carry(state)]);r=m.run(q)
        self.assertEqual(r['stop']['status'],'unresolved');self.assertEqual(r['stop']['reason'],'assessments_incomplete')
        self.assertEqual(r['period_book']['current_period_deferred_tax'],'stale')
        self.assertEqual(len(r['period_book']['deferred_assessments']),1)

    def test_unknown_capacity_and_reused_measurement_do_not_renew(self):
        state=self.rr['trace'][3]['result']['after'];op=x.deferred(state)
        op['event']['recovery_capacity']={'status':'unknown','reason':'No new capacity'}
        with self.assertRaises(m.losses.Refused) as c:m.transition(state,op)
        self.assertEqual(c.exception.status,'unresolved')
        op=x.deferred(state);op['event']['measurement']['state_sha256']='0'*64
        with self.assertRaises(m.losses.Refused):m.transition(state,op)

    def test_missing_and_duplicate_allocations_keep_all_vintages(self):
        state=self.r['period_book']
        for mutate in [lambda e:e['allocations'].append(deepcopy(e['allocations'][0])),
                       lambda e:e['allocations'][0].update(vintage_id='missing'),
                       lambda e:e.update(amount='100/1')]:
            op=x.payment(state,['1/1','1/1','0/1']);mutate(op['event'])
            with self.assertRaises(m.losses.Refused):m.transition(state,op)
        self.assertEqual(state,self.r['period_book'])

    def test_actual_cash_shortage_after_new_assessment(self):
        origin,state=x.start();first=x.assessment(state,'2000/1');state=m.transition(state,first)['after']
        payment=x.payment(state,['0/1','0/1','400/1']);r=m.run(m.request(origin,[first,payment]))
        self.assertEqual(r['stop']['status'],'funding_failure');self.assertEqual(r['period_book'],state)

    def test_loss_replacement_restarts_original_opening(self):
        b=x.previous.previous
        root=x.previous.scenario([],b.request(b.previous.loss_scenario()))
        origin,state=x.start(root);self.assertEqual(sum(Q(l['remaining']) for l in state['opening_loss']['lots']),9)
        first=x.assessment(state,'8/1',uses=[{'lot_id':'replacement-loss','amount':'4/1'}],cap='9/1')
        state=m.transition(state,first)['after']
        replace=x.assessment(state,'8/1','loss-replace','replace',uses=[{'lot_id':'replacement-loss','amount':'3/1'}],cap='9/1')
        r=m.run(m.request(origin,[first,replace]));out=r['period_book']
        self.assertEqual(out['current_assessments'][-1]['tax_amount'],'5/4')
        self.assertEqual(sum(Q(l['remaining']) for l in out['loss_state']['lots']),6)
        self.assertEqual(sum(Q(l['remaining']) for l in out['opening_loss']['lots']),9)

    def test_expired_generated_loss_and_lifetime_id_reuse(self):
        origin,state=x.start();ops=[]
        def add(op):
            nonlocal state
            state=m.transition(state,op)['after'];ops.append(op)
        expiry={'kind':'date','end_exclusive':'2028-06-01','provenance':x.known()['provenance']}
        generation={'id':'new-loss','eligible':x.known(),'expiry':expiry}
        add(x.assessment(state,'-9/1',end='2028-01-01',generation=generation))
        add(x.deferred(state));add(x.carry(state))
        use=x.assessment(state,'8/1','expired-use','first','2029-01-01',uses=[{'lot_id':'new-loss','amount':'1/1'}],cap='9/1')
        with self.assertRaises(m.losses.Refused) as c:m.transition(state,use)
        self.assertEqual(c.exception.reason,'expired_lot_use')
        add(x.assessment(state,'8/1','expire-only','first','2029-01-01'))
        self.assertEqual(state['loss_state']['lots'][-1]['remaining'],'0/1')
        self.assertEqual(state['loss_state']['lots'][-1]['expired'],'9/1')
        reused=x.assessment(state,'-2/1','reused-loss','replace','2029-01-01',generation=generation)
        with self.assertRaises(m.losses.Refused) as c:m.transition(state,reused)
        self.assertEqual(c.exception.reason,'reused_historical_loss_id')
        r=m.run(m.request(origin,ops));self.assertEqual(r['status'],'complete_provisional')

    def test_same_generic_carry_can_repeat(self):
        q=deepcopy(self.repeated);state=self.rr['period_book']
        for op in [x.deferred(state,identity='next-deferred')]:
            state=m.transition(state,op)['after'];q['operations'].append(op)
        op=x.carry(state,identity='next-carry',end='2030-01-01');q['operations'].append(op)
        r=m.run(q);self.assertEqual(r['status'],'complete_provisional')
        state=r['period_book'];self.assertEqual(len(state['period_archive']),2)
        self.assertEqual(len(state['period_vintages']),4)
        self.assertEqual(state['after']['balances']['retained'],'81/4')
        self.assertEqual(state['current_period_tax'],state['current_period_deferred_tax'])
        self.assertEqual(state['current_period_tax'],'unassessed')

    def test_native_timing_and_unassessed_status(self):
        state=self.r['period_book'];op=x.previous.depreciation(identity='later-native',day='2027-07-01')
        after=m.transition(state,op)['after'];self.assertEqual(after['current_period_tax'],'activity_after_assessment')
        bad=x.previous.depreciation(identity='inside-assessed',day='2027-06-30')
        with self.assertRaises(m.native.Refused):m.transition(state,bad)

    def test_full_result_tampering_and_exact_replay(self):
        for key in ['period_book','root_result','trace','recorded_statements','remaining_operations']:
            bad=deepcopy(self.r);bad[key]={'tampered':True}
            self.assertEqual(m.apply(self.q,bad)['status'],'invalid')
        self.assertEqual(m.apply(self.q,self.r)['status'],'applied_provisional')
        self.assertEqual(m.run(self.q),self.r)

if __name__=='__main__':unittest.main()
