"""Independent PV/cash-flow oracles and failure-atomicity checks for P08."""
import copy
from dataclasses import replace
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from corporate_financing_v1 import (AuthorityBook, BondBook, Contract, Unsupported,
                                   compare_same_facts, run_case, rational)


class FinancingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authority = AuthorityBook()

    def book(self, **kwargs):
        return BondBook(Contract(), self.authority, **kwargs)

    def ready(self, book):
        book.apply('issue', 'issue', book.contract.issue_date)
        for i, day in enumerate(book.contract.coupon_dates()):
            book.apply(f'a{i}', 'accrue', day)
            book.apply(f'c{i}', 'coupon', day)
        return book

    def atomic(self, book, *args):
        before = book.state
        with self.assertRaises(Unsupported):
            book.apply(*args)
        self.assertEqual(before, book.state)

    def test_issue_independent_present_value(self):
        b = self.book()
        b.apply('i', 'issue', '2024-01-01')
        expected = F(5, 1) / F(11, 10) + F(105, 1) / F(121, 100)
        self.assertEqual(expected, F(11050, 121))
        self.assertEqual(-b.state['ledger']['liability'], expected)
        self.assertEqual(-b.state['ledger']['conversion_equity'], 100 - expected)
        self.assertEqual(b.state['principal_outstanding'], 100)

    def test_two_coupons_and_both_settlements(self):
        for settlement, cash, shares in [('redeem', 10, 0), ('convert', 110, 10)]:
            b = self.book(); b.apply('i', 'issue', '2024-01-01')
            for i, expected in enumerate([F(1050, 11), F(100)], 1):
                day = f'{2023+i}-12-31'
                b.apply(f'a{i}', 'accrue', day); b.apply(f'c{i}', 'coupon', day)
                self.assertEqual(-b.state['ledger']['liability'], expected)
            self.assertEqual(b.state['ledger']['interest_expense'], F(2260, 121))
            b.apply('s', settlement, '2025-12-31')
            state = b.state; ledger = state['ledger']
            self.assertEqual(ledger['cash'], cash)
            self.assertEqual(ledger['liability'], 0)
            self.assertEqual(ledger['conversion_equity'], -F(1050, 121))
            self.assertEqual(state['principal_outstanding'], 0)
            self.assertEqual(state['shares'], shares)
            self.assertEqual(ledger['share_equity'], -100 if shares else 0)
            self.assertEqual(sum(ledger.values()), 0)
            for entry in state['journal']:
                self.assertEqual(sum(entry['postings_debit_positive'].values()), 0)
                self.assertEqual(sum(entry['state_after'].values()), 0)

    def test_second_parameters_and_cashflow_oracle(self):
        c = replace(Contract(), principal='240', proceeds='245', instrument_fair_value='245',
                    annual_coupon='12', comparable_yield='2/25', conversion_shares=24)
        pv = F(12)*F(25,27) + F(252)*F(625,729)
        for method in ('redeem', 'convert'):
            r = run_case(c, method, opening_cash='30', authority=self.authority)
            self.assertEqual(F(r['initial_liability']), pv)
            # Total effective interest = total contractual cash flows less issue liability.
            self.assertEqual(F(r['state']['ledger']['interest_expense']), 264-pv)
            self.assertEqual(F(r['state']['ledger']['cash']), 30+245-24-(240 if method=='redeem' else 0))

    def test_three_periods_and_zero_rate(self):
        c = replace(Contract(), issue_date='2023-01-01', years=3)
        r = run_case(c, authority=self.authority)
        pv = sum((F(5)*F(10,11)**n for n in (1,2,3)), F(0)) + 100*F(10,11)**3
        self.assertEqual(F(r['initial_liability']), pv)
        self.assertEqual(F(r['state']['ledger']['interest_expense']), 115-pv)
        c = replace(Contract(), annual_coupon='0', comparable_yield='0')
        self.assertEqual(run_case(c, authority=self.authority)['state']['ledger']['interest_expense'], '0')

    def test_note_reconciliation_and_links(self):
        r = run_case(authority=self.authority)
        notes = r['notes']; total = F(0)
        self.assertEqual(len(notes['periods']), 2)
        for p in notes['periods']:
            self.assertEqual(F(p['opening_liability'])+F(p['issue_liability'])+F(p['interest_expense'])-F(p['coupons'])-F(p['settlement_liability']), F(p['closing_liability']))
            total += F(p['interest_expense'])
            self.assertTrue(set(p['event_ids']) <= set(r['state']['used_event_ids']))
        self.assertEqual(total, F(r['state']['ledger']['interest_expense']))
        for links in notes['links'].values():
            self.assertTrue(set(links) <= set(self.authority.claims))

    def test_sequence_duplicate_conflict_and_settlement_atomicity(self):
        b = self.book()
        self.atomic(b, 'a', 'accrue', '2024-12-31')
        b.apply('i', 'issue', '2024-01-01')
        self.atomic(b, 'i', 'accrue', '2024-12-31')
        self.atomic(b, 'c', 'coupon', '2024-12-31')
        self.atomic(b, 'a', 'accrue', '2025-12-31')
        self.atomic(b, 's', 'convert', '2024-12-31')
        for i, day in enumerate(b.contract.coupon_dates()):
            b.apply(f'a{i}', 'accrue', day); b.apply(f'c{i}', 'coupon', day)
        b.apply('s', 'redeem', '2025-12-31')
        self.atomic(b, 's2', 'convert', '2025-12-31')

    def test_insufficient_cash_is_atomic(self):
        b = self.ready(self.book(opening_cash='0'))
        self.atomic(b, 's', 'redeem', '2025-12-31')
        b.apply('s', 'convert', '2025-12-31')
        self.assertEqual(b.state['shares'], 10)

    def test_ineligible_contracts(self):
        changes = [{'functional_currency':'USD'}, {'conversion_right':'variable_shares'},
                   {'measurement':'fair_value'}, {'issue_date':'2024-02-01'}, {'years':0},
                   {'years':True}, {'conversion_shares':0}, {'principal':'0'},
                   {'comparable_yield':'-1/10'}, {'proceeds':'1','instrument_fair_value':'1'},
                   {'instrument_fair_value':'99'}, {'annual_coupon':5.0}]
        changes += [{'unsupported_features':(f,)} for f in ('tax','fees','cash_option','guarantee','early_conversion','modification','default','put','reset','embedded_derivative','FVPL_designation','contingent_consideration')]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(Unsupported):
                BondBook(replace(Contract(), **change), self.authority)

    def test_jurisdiction_tier_period_veto(self):
        for change in ({'basis':'US GAAP'}, {'jurisdiction':'US'}, {'tier':'Tier 2'},
                       {'entity_scope':'not-for-profit'}, {'issue_date':'2022-01-01'},
                       {'issue_date':'2026-01-01'}):
            with self.subTest(change=change), self.assertRaises(Unsupported):
                BondBook(replace(Contract(), **change), self.authority)
        # 2026 calendar period starts before the 1 July edition limit.
        BondBook(replace(Contract(), issue_date='2026-01-01', years=1), self.authority)

    def test_source_and_claim_vetoes(self):
        def broken(mutator):
            d = copy.deepcopy(self.authority.records); mutator(d)
            with self.assertRaises(Unsupported): AuthorityBook(records=d)
        broken(lambda d: d['claims'].pop(0))
        broken(lambda d: d['authorities'][0].update(access_status='overview_only'))
        broken(lambda d: d['authorities'][0].update(kind='company_practice'))
        broken(lambda d: d['authorities'][0]['retained'].update(sha256='0'*64))
        broken(lambda d: d['authorities'][0]['retained'].update(path='does-not-exist.pdf'))
        broken(lambda d: d['claims'][0]['anchors'][0].update(quote='invented authority'))
        broken(lambda d: d['claims'][0]['anchors'][0].update(pdf_page=0))
        broken(lambda d: d['note_links']['financing_equity'].append('absent'))

    def test_same_fact_comparisons_do_not_inherit(self):
        r = compare_same_facts(authority=self.authority)
        self.assertEqual(len({x['facts_sha256'] for x in r['rows']}), 1)
        self.assertEqual(r['rows'][0]['initial_liability'], '11050/121')
        for row in r['rows'][1:]:
            self.assertEqual(row['status'], 'unresolved')
            self.assertIsNone(row['initial_liability']); self.assertIsNone(row['initial_equity'])
            self.assertEqual(row['claims'], [])
        self.assertIsNone(r['supported_difference'])

    def test_state_copies_are_not_mutation_handles(self):
        b=self.book(); state=b.state; state['ledger']['cash']=F(-100)
        self.assertEqual(b.state['ledger']['cash'],20)


if __name__ == '__main__':
    unittest.main()
