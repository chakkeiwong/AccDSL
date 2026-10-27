import json
import sys
import unittest
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import shared_tax_state_v1 as m


def known(value=True):
    return {'status': 'known', 'value': value, 'provenance': {
        'kind': 'assumption', 'reference': 'Synthetic financial tax control; no statutory admission'}}


def loss_case(name='consume_19_from_21'):
    rows = json.loads((ROOT / 'data/accounting-master/conditional-tax-losses-20261024/cases.json').read_text())
    return deepcopy(next(r['request'] for r in rows if r['case'] == name))


def accrual(name='consume_19_from_21'):
    return m.accrual_request(loss_case(name), 'tax-accrual', known())


def state():
    r = m.propose(accrual())
    assert r['status'] == 'proposed', r.get('reason')
    return r['after']


def payment(s=None, amount='1/4', identity='payment-1', day='2026-12-31'):
    return m.settlement_request(state() if s is None else s, identity, day, amount, known())


def lower_cash(body):
    x = deepcopy(body); q = x['loss_request']; t = q['reconciliation_request']; i = t['information_request']
    r = i['report_request']; opening = r['opening']; old = Q(opening['balances']['cash'])
    opening['balances']['cash'] = '0/1'
    opening['balances']['retained'] = m.book.fmt(Q(opening['balances']['retained']) + old)
    r['opening_sha256'] = m.book.digest(opening)
    i['report_request_sha256'] = m.book.digest(r)
    t['information_sha256'] = m.book.digest(i)
    q['reconciliation_sha256'] = m.book.digest(t)
    x['loss_request_sha256'] = m.book.digest(q)
    return x


class TaxStateTests(unittest.TestCase):
    def test_accrual_and_independent_statements(self):
        r = m.propose(accrual()); self.assertEqual(r['status'], 'proposed')
        b = r['after']['balances']; native = r['native_report']['execution']['after']
        self.assertEqual((b['current_tax'], b['income_tax_payable'], b['cash']), ('1/2', '-1/2', '500/1'))
        self.assertEqual(r['recorded_statements']['balance_sheet'], {
            'total_assets': '886/1', 'total_liabilities': '589/2', 'equity_including_profit': '1183/2'})
        self.assertEqual(r['recorded_statements']['recorded_profit'], '-1/2')
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'], '0/1')
        self.assertEqual(r['after']['assessed_until'], '2027-01-01')
        self.assertEqual(r['after']['native_tax_closed_until'], '2026-01-01')
        for k in native['balances']:
            if k != 'current_tax': self.assertEqual(b[k], native['balances'][k], k)

    def test_partial_then_full_payment(self):
        r = m.propose(payment()); self.assertEqual(r['status'], 'proposed')
        self.assertEqual(r['journal']['income_tax_payable'], '1/4')
        self.assertEqual(r['journal']['cash'], '-1/4')
        self.assertEqual(r['after']['balances']['cash'], '1999/4')
        self.assertEqual(r['recorded_statements']['indirect_operating']['net'], '-1/4')
        q = payment(r['after'], '1/4', 'payment-2'); full = m.propose(q)
        self.assertEqual(full['status'], 'proposed')
        self.assertEqual(full['after']['balances']['income_tax_payable'], '0/1')
        self.assertEqual(full['after']['balances']['cash'], '999/2')
        self.assertEqual(full['recorded_statements']['balance_sheet'], {
            'total_assets': '1771/2', 'total_liabilities': '294/1', 'equity_including_profit': '1183/2'})
        self.assertEqual(full['recorded_statements']['indirect_operating']['net'], '-1/2')
        self.assertEqual(len(full['recorded_statements']['cash_flows']['gross_origins']), 2)

    def test_loss_generation_and_zero_tax(self):
        r = m.propose(accrual('generate_19')); self.assertEqual(r['status'], 'proposed')
        self.assertEqual(r['after']['loss_state']['lots'][0]['remaining'], '19/1')
        self.assertEqual(r['after']['balances']['current_tax'], '0/1')
        self.assertEqual(r['recorded_statements']['recorded_profit'], '5/1')
        self.assertEqual(r['recorded_statements']['balance_sheet'], {
            'total_assets': '701/1', 'total_liabilities': '104/1', 'equity_including_profit': '597/1'})
        self.assertTrue(all(Q(v) == 0 for v in r['journal'].values()))
        zero = m.propose(accrual('zero_taxable_profit')); self.assertEqual(zero['status'], 'proposed')
        self.assertEqual(zero['after']['balances']['income_tax_payable'], '0/1')

    def test_no_use_and_fractional_use(self):
        no = m.propose(accrual('zero_explicit_use')); self.assertEqual(no['status'], 'proposed')
        self.assertEqual(no['after']['balances']['current_tax'], '21/4')
        q = accrual(); q['loss_request']['uses'][0]['amount'] = '1/3'
        q['loss_request_sha256'] = m.book.digest(q['loss_request'])
        r = m.propose(q); self.assertEqual(r['status'], 'proposed')
        self.assertEqual(r['after']['balances']['current_tax'], '31/6')
        self.assertEqual(r['after']['loss_state']['lots'][0]['remaining'], '56/3')

    def test_unknown_false_recognition_preserves_loss_result(self):
        for value, status in [({'status': 'unknown', 'reason': 'No finding'}, 'unresolved'), (known(False), 'unsupported')]:
            q = accrual(); q['recognition'] = value; r = m.propose(q)
            self.assertEqual(r['status'], status); self.assertEqual(r['loss_result']['status'], 'proposed')
            self.assertNotIn('after', r)

    def test_payment_authority_and_quantity(self):
        for value, expected in [(known(False), 'unsupported'), ({'status': 'unknown', 'reason': 'No instruction'}, 'unresolved')]:
            q = payment(); q['event']['authorization'] = value
            self.assertEqual(m.propose(q)['status'], expected)
        for quantity in ['0/1', '-1/4', '3/4', '0.25', True]:
            with self.subTest(quantity=quantity): self.assertEqual(m.propose(payment(amount=quantity))['status'], 'invalid')

    def test_funding_failure_does_not_invalidate_accrual(self):
        r = m.propose(lower_cash(accrual())); self.assertEqual(r['status'], 'proposed')
        p = m.propose(payment(r['after'])); self.assertEqual(p['status'], 'funding_failure')
        self.assertEqual(p['reason'], 'cash_shortage')

    def test_dates_and_duplicates(self):
        for day in ['2026-12-30', '2027-01-01', '2026-02-30']:
            self.assertEqual(m.propose(payment(day=day))['status'], 'invalid')
        r = m.propose(payment()); q = payment(r['after'], identity='payment-1')
        self.assertEqual(m.propose(q)['status'], 'invalid')
        self.assertEqual(m.propose(payment(identity='tax-accrual'))['status'], 'invalid')
        q = accrual('generate_19')
        original = q['loss_request']['reconciliation_request']['information_request']['report_request']
        q['id'] = original['events'][0]['event']['id']
        self.assertEqual(m.propose(q)['status'], 'invalid')

    def test_stale_hash_and_forged_financial_state(self):
        q = accrual(); q['loss_request_sha256'] = '0' * 64
        self.assertEqual(m.propose(q)['status'], 'invalid')
        for key, value in [('date', '2026-12-30'), ('native_tax_closed_until', '2027-01-01'), ('assessed_until', '2027-02-01'), ('native_closing_sha256', '0'*64)]:
            q = payment(); q['state'][key] = value; q['state_sha256'] = m.book.digest(q['state'])
            self.assertEqual(m.propose(q)['status'], 'invalid')
        q = payment(); q['state']['balances']['cash'] = '501/1'; q['state']['balances']['retained'] = '-13/1'
        q['state_sha256'] = m.book.digest(q['state']); self.assertEqual(m.propose(q)['status'], 'invalid')

    def test_complete_proposal_comparison(self):
        q = accrual(); r = m.propose(q); self.assertEqual(m.apply(q, r)['status'], 'applied')
        for field, value in [('committed', 0), ('annual_close_ready', True), ('journal', {})]:
            altered = deepcopy(r); altered[field] = value
            self.assertEqual(m.apply(q, altered)['status'], 'invalid')
        altered = deepcopy(r); altered['native_report']['coverage']['annual_completion'] = 'complete'
        self.assertEqual(m.apply(q, altered)['status'], 'invalid')
        payment_q = payment(); payment_r = m.propose(payment_q)
        self.assertEqual(m.apply(payment_q, payment_r)['status'], 'applied')

    def test_full_native_loss_preservation_and_flags(self):
        q = accrual(); r = m.propose(q); expected = m.losses.propose(q['loss_request'])
        self.assertEqual(m.book.caller.canonical(r['loss_result']), m.book.caller.canonical(expected))
        self.assertEqual(r['native_report'], expected['reconciliation_result']['information_result']['native_report'])
        self.assertTrue(all(r[k] is False for k in m.FLAGS))
        self.assertEqual(set(r['recorded_statements']['reconciliations'].values()), {'0/1'})
        self.assertEqual([r['after']['balances'][k] for k in ['dta','dtl','deferred_tax']], ['10/1','-4/1','0/1'])

    def test_upstream_rejection_and_unknowns_survive(self):
        for name, status in [('generation_eligibility_unknown','unresolved'), ('generation_ineligible','unsupported'), ('forged_state_identity','invalid')]:
            r = m.propose(accrual(name))
            self.assertEqual(r['status'], status)
            self.assertEqual(r['loss_result']['status'], status)
            self.assertNotIn('after', r)

    def test_unsupported_existing_tax_and_invalid_extra_fields(self):
        q = accrual(); loss = q['loss_request']; calc = loss['reconciliation_request']
        info = calc['information_request']; report = info['report_request']; opening = report['opening']
        opening['balances']['current_tax'] = '1/1'; opening['balances']['retained'] = '-13/1'
        report['opening_sha256'] = m.book.digest(opening); info['report_request_sha256'] = m.book.digest(report)
        calc['information_sha256'] = m.book.digest(info); loss['reconciliation_sha256'] = m.book.digest(calc)
        q['loss_request_sha256'] = m.book.digest(loss)
        self.assertEqual(m.propose(q)['status'], 'unsupported')
        for q in [accrual(), payment()]:
            q['posted'] = True; self.assertEqual(m.propose(q)['status'], 'invalid')
        q = payment(); q['state_sha256'] = '0'*64
        self.assertEqual(m.propose(q)['status'], 'invalid')


if __name__ == '__main__': unittest.main()
