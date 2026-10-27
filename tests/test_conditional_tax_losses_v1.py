from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import conditional_tax_losses_v1 as m
spec=importlib.util.spec_from_file_location('loss_examples',ROOT/'data/accounting-master/conditional-tax-losses-20261024/examples.py')
examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)

class LossTests(unittest.TestCase):
    def test_saved_classifications_and_flags(self):
        for row in examples.cases():
            with self.subTest(case=row['case']):
                body=row['request'];before=m.book.digest(body);r=m.propose(body)
                self.assertEqual(r['status'],row['expected_status'],r.get('reason'))
                self.assertTrue(all(r[k] is False for k in m.FLAGS));self.assertEqual(before,m.book.digest(body))

    def test_generate_then_use_exact_conservation(self):
        gen=examples.generate();r=m.propose(gen);self.assertEqual(r['status'],'proposed')
        p=r['proposal'];self.assertEqual(p['totals'],{'opening':'0/1','generated':'19/1','used':'0/1','expired':'0/1','closing':'19/1'})
        applied=m.apply(gen,r);self.assertEqual(applied['status'],'applied');self.assertEqual(applied['after'],p['after'])
        use=examples.use();s=m.propose(use);self.assertEqual(s['status'],'proposed')
        p=s['proposal'];self.assertEqual(p['totals'],{'opening':'19/1','generated':'0/1','used':'19/1','expired':'0/1','closing':'0/1'})
        self.assertEqual(p['taxable_profit_after_losses'],'2/1');self.assertEqual(p['conditional_gross_current_tax'],'1/2')
        self.assertEqual(p['after']['seen'],['generate-19','use-2026'])
        self.assertEqual(p['after']['lots'][0]['original'],'19/1');self.assertEqual(p['after']['lots'][0]['used'],'19/1')

    def test_partial_and_expiry_boundaries(self):
        rows={r['case']:r for r in examples.cases()}
        for name,used,expired,closing in [('partial_use_7',7,0,12),
            ('expiry_on_usage_day_expires_all',0,19,0),
            ('expiry_at_endpoint_allows_use_then_expires',7,12,0),
            ('expiry_after_endpoint_preserves_remainder',7,0,12)]:
            r=m.propose(rows[name]['request']);self.assertEqual(r['status'],'proposed',r.get('reason'))
            totals=r['proposal']['totals']
            self.assertEqual([Q(totals[k]) for k in ['used','expired','closing']],[Q(used),Q(expired),Q(closing)])

    def test_apply_recomputes_and_rejects_tampering(self):
        body=examples.use();r=m.propose(body)
        for kind in ['remaining','amount','flag','native','origin']:
            bad=deepcopy(r)
            if kind=='remaining':bad['proposal']['after']['lots'][0]['remaining']='1/1'
            elif kind=='amount':bad['proposal']['conditional_gross_current_tax']='0/1'
            elif kind=='flag':bad['cash_refund']=0
            elif kind=='native':bad['reconciliation_result']['calculation']['taxable_profit']='22/1'
            else:bad['proposal']['after']['lots'][0]['origin_reference']='forged'
            self.assertEqual(m.apply(body,bad)['status'],'invalid')
        stale=deepcopy(body);stale['state']=deepcopy(r['proposal']['after']);examples.rehash(stale)
        self.assertEqual(m.apply(stale,r)['status'],'invalid')

    def test_native_report_preserved_and_no_financial_carry_claim(self):
        body=examples.use();r=m.propose(body);expected=m.tax.calculate(body['reconciliation_request'])
        self.assertEqual(m.book.caller.canonical(r['reconciliation_result']),m.book.caller.canonical(expected))
        self.assertFalse(r['native_financial_carry']);self.assertFalse(r['deferred_asset_recognized'])
        self.assertIn('Separate hypothetical 2026 opening',expected['information_result']['native_report']['source']['premise'])

    def test_state_conservation_history_and_identifiers(self):
        body=examples.use()
        for kind in ['lot_sum','history_sum','history_id','duplicate_lot','future_lot','extra_field']:
            x=deepcopy(body)
            if kind=='lot_sum':x['state']['lots'][0]['remaining']='18/1'
            elif kind=='history_sum':x['state']['history'][0]['closing']='18/1'
            elif kind=='history_id':x['state']['history'][0]['step_id']='different'
            elif kind=='duplicate_lot':x['state']['lots'].append(deepcopy(x['state']['lots'][0]))
            elif kind=='future_lot':x['state']['lots'][0]['available_from']='2026-02-01'
            else:x['state']['inferred_dta']='19/4'
            self.assertEqual(m.propose(examples.rehash(x))['status'],'invalid')

    def test_exact_fractional_use(self):
        body=examples.use('1/3');r=m.propose(body)
        self.assertEqual(r['status'],'proposed',r.get('reason'))
        self.assertEqual(r['proposal']['totals']['closing'],'56/3')
        self.assertEqual(r['proposal']['conditional_gross_current_tax'],'31/6')

    def test_individually_balanced_history_rows_must_connect(self):
        state=m.propose(examples.use())['proposal']['after']
        m.validate_state(state)
        # Each changed row remains balanced, but it invents one loss unit
        # between periods. The current lots and last closing remain unchanged.
        state['history'][1]['opening']='20/1'
        state['history'][1]['used']='20/1'
        with self.assertRaisesRegex(m.Refused,'history_balance_discontinuity'):
            m.validate_state(state)

    def test_no_loss_id_reuse_even_when_exhausted(self):
        body=examples.use();state=m.propose(body)['proposal']['after']
        calc=examples.future_request('-19/1');info=calc['information_request'];opening=info['report_request']['opening']
        opening['date']='2027-01-01';opening['period']={'start':'2027-01-01','end_exclusive':'2028-01-01'};opening['tax_closed_until']='2027-01-01'
        info['report_request']=m.tax.information.reports.request(opening,[]);info['report_request_sha256']=m.book.digest(info['report_request'])
        info['interval']={'start':'2027-01-01','end_exclusive':'2028-01-01','activity_through':'2027-12-31'}
        calc['information_sha256']=m.book.digest(info)
        x=m.request(state,calc,'new-loss',examples.model(),examples.known('0/1'),[],
            {'id':'loss-19','eligible':examples.known(True),'expiry':examples.no_expiry()})
        r=m.propose(x);self.assertEqual(r['status'],'invalid');self.assertEqual(r['reason'],'reused_loss_id')

if __name__=='__main__':unittest.main()
