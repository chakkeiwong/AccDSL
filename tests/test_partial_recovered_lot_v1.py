from copy import deepcopy
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
import os
import unittest

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'partial_lot_examples', ROOT / 'data/accounting-master/partial-recovered-lot-20261025/examples.py')
x = importlib.util.module_from_spec(spec); spec.loader.exec_module(x); m = x.m


class PartialRecoveredLotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = deepcopy(x.settled())

    def test_one_unit_independent_control(self):
        result = m.propose(self.state, x.sale()); self.assertEqual(result['status'], 'proposed')
        p = result['proposal']; b = p['after']['balances']; lot = p['after']['lots']['recovered']
        self.assertEqual((b['cash'], b['inventory']), ('467/1', '70/1'))
        self.assertEqual((lot['units'], lot['carrying'], lot['tax_base'], lot['disposed']), ('1/1', '10/1', '10/1', False))
        self.assertEqual({k: p['journal'][k] for k in ['cash', 'revenue', 'inventory', 'cogs']},
                         {'cash': '15/1', 'revenue': '-15/1', 'inventory': '-10/1', 'cogs': '10/1'})
        self.assertEqual(p['allocation']['fraction_of_remaining'], '1/2')

    def test_full_sale_matches_entire_native_state_journal_and_flows(self):
        for proceeds in ['30/1', '0/1', '1/3']:
            new = m.propose(self.state, x.sale('2/1', proceeds, 'sale'))
            old = m.book.propose(self.state, x.native_sale(proceeds=proceeds))
            self.assertEqual(new['status'], 'proposed'); self.assertEqual(old['status'], 'proposed')
            for key in ['after', 'journal', 'flows']:
                self.assertEqual(new['proposal'][key], old['proposal'][key])

    def test_repeated_sales_use_remaining_quantity(self):
        result = m.run_prefix(self.state, [x.sale(identity='first'), x.sale(identity='last')])
        self.assertEqual(result['status'], 'complete')
        self.assertEqual([r['proposal']['allocation']['fraction_of_remaining'] for r in result['trace']], ['1/2', '1/1'])
        lot = result['after']['lots']['recovered']
        self.assertEqual((lot['units'], lot['carrying'], lot['tax_base'], lot['disposed']), ('0/1', '0/1', '0/1', True))
        self.assertEqual(result['after']['balances']['cash'], '482/1')
        self.assertEqual(result['after']['balances']['inventory'], '60/1')
        whole = m.propose(self.state, x.sale('2/1', '30/1'))['proposal']
        self.assertEqual(result['after']['balances'], whole['after']['balances'])
        self.assertNotEqual(result['after']['seen'], whole['after']['seen'])
        self.assertNotEqual(result['after']['flows'], whole['after']['flows'])

    def test_fractional_quantity_exact_cost_and_conservation(self):
        p = m.propose(self.state, x.sale('1/3', '7/2'))['proposal']
        self.assertEqual(p['allocation']['released_carrying'], '10/3')
        lot = p['after']['lots']['recovered']
        self.assertEqual((lot['units'], lot['carrying']), ('5/3', '50/3'))
        self.assertEqual(Q(p['allocation']['released_carrying']) + Q(lot['carrying']), Q(20))
        self.assertEqual(sum(Q(v) for v in p['journal'].values()), 0)

    def test_zero_cost_positive_units_remain_live(self):
        state = deepcopy(self.state); state['lots']['recovered'].update(carrying='0/1', tax_base='0/1')
        state['balances']['inventory'] = '60/1'; state['balances']['cogs'] = m.fmt(Q(state['balances']['cogs']) + 20)
        r = m.run_prefix(state, [x.sale(identity='zero-cost-first'), x.sale(identity='zero-cost-last')])
        self.assertEqual(r['status'], 'complete')
        self.assertFalse(r['trace'][0]['proposal']['after']['lots']['recovered']['disposed'])
        self.assertTrue(r['after']['lots']['recovered']['disposed'])
        self.assertTrue(all(t['proposal']['allocation']['released_carrying'] == '0/1' for t in r['trace']))

    def test_other_lot_and_company_memory_remain_exact(self):
        state = deepcopy(self.state); other = deepcopy(state['lots']['recovered']); other['id'] = 'other'
        state['lots']['other'] = other
        state['other_inventory'] = '40/1'
        p = m.propose(state, x.sale())['proposal']
        self.assertEqual(p['after']['lots']['other'], other)
        for key in state:
            if key not in ['balances', 'lots', 'date', 'seen', 'flows']:
                self.assertEqual(p['after'][key], state[key])

    def test_statement_equations_and_full_native_report_agree(self):
        partial = m.propose(self.state, x.sale())['proposal']['after']
        control = x.statement_control(x.previous.opening(), partial)
        # Prior lease gain20 + settlement cost reversal4 - handling8 =16;
        # this sale adds proceeds15 - released cost10 =5.
        self.assertEqual(control['profit'], '21/1')
        self.assertEqual(control['operating_cash'], '-33/1')
        full = m.propose(self.state, x.sale('2/1', '30/1', 'sale'))['proposal']['after']
        direct = x.reports.calculate(x.reports.request(x.previous.opening(), x.previous.events()[:3]))
        self.assertEqual(direct['status'], 'recorded_prefix')
        control = x.statement_control(x.previous.opening(), full)
        self.assertEqual(control['profit'], direct['income_recorded']['recorded_profit'])
        self.assertEqual(control['operating_cash'], direct['cash_flows_recorded']['activities']['operating']['net'])
        self.assertEqual(control['reconciliations'], direct['reconciliations'])

    def test_negative_and_unknown_cases_preserve_inputs(self):
        for row in x.negatives():
            with self.subTest(case=row['case']):
                before = m.book.caller.canonical([row['before'], row['event']])
                r = m.propose(row['before'], row['event'])
                self.assertEqual(r['status'], row['expected'])
                self.assertIsNone(r['proposal'])
                self.assertEqual(before, m.book.caller.canonical([row['before'], row['event']]))

    def test_disposed_lot_cannot_be_sold_again(self):
        after = m.propose(self.state, x.sale('2/1', '30/1', 'first'))['proposal']['after']
        self.assertEqual(m.propose(after, x.sale(identity='again'))['reason'], 'lot_disposed')

    def test_failed_later_sale_preserves_successful_prefix(self):
        sales = [x.sale(identity='first'), x.sale('2/1', '30/1', 'oversale'), x.sale(identity='later')]
        result = m.run_prefix(self.state, sales)
        self.assertEqual(result['status'], 'stopped'); self.assertEqual(result['stop']['index'], 1)
        self.assertEqual(len(result['trace']), 1)
        self.assertEqual(result['remaining_sales'], sales[1:])
        self.assertEqual(result['after']['balances']['cash'], '467/1')

    def test_complete_apply_rejects_balanced_or_rehashed_tampering(self):
        event = x.sale(); p = m.propose(self.state, event)['proposal']
        self.assertEqual(m.apply(self.state, event, p)['status'], 'applied_diagnostic')
        mutations = [lambda z: z['after']['lots']['recovered'].update(units='1/2'),
                     lambda z: z['allocation'].update(fraction_of_remaining='1/3'),
                     lambda z: z['findings']['homogeneous_units'].update(provenance='Different premise'),
                     lambda z: z['after']['balances'].update(cash='468/1', revenue=m.fmt(Q(z['after']['balances']['revenue'])-1))]
        for change in mutations:
            altered = deepcopy(p); change(altered)
            self.assertEqual(m.apply(self.state, event, altered)['status'], 'invalid')

    def test_no_admission_or_mutation(self):
        state = deepcopy(self.state); event = x.sale(); before = m.book.caller.canonical([state, event])
        r = m.propose(state, event); m.apply(state, event, r['proposal'])
        self.assertEqual(before, m.book.caller.canonical([state, event]))
        for key in ['source_admission', 'accounting_admission', 'method_eligible', 'annual_ready', 'committed']:
            self.assertIs(r[key], False)


if __name__ == '__main__':
    unittest.main()
