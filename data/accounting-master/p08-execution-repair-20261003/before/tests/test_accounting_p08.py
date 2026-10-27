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


class RecoveryValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from check_accounting_p08 import check_deliverable
        cls.validate = staticmethod(check_deliverable)
        cls.authority = AuthorityBook()
        cls.payload = json.loads((ROOT / 'data/accounting-master/deliverables/P08/authority-and-methods.json').read_text())

    def test_actual_deliverable_replays(self):
        self.assertEqual(self.validate(self.payload, self.authority), [])

    def test_every_required_claim_is_mandatory(self):
        from corporate_financing_v1 import REQUIRED
        for claim in REQUIRED:
            with self.subTest(claim=claim):
                records = copy.deepcopy(self.authority.records)
                records['claims'] = [c for c in records['claims'] if c['id'] != claim]
                with self.assertRaises(Unsupported): AuthorityBook(records=records)

    def test_every_required_claim_requires_nonempty_anchor(self):
        from corporate_financing_v1 import REQUIRED
        for claim in REQUIRED:
            for change in ('anchors', 'quote', 'paragraph'):
                records = copy.deepcopy(self.authority.records)
                target = next(c for c in records['claims'] if c['id'] == claim)
                if change == 'anchors': target['anchors'] = []
                else: target['anchors'][0][change] = ' '
                with self.subTest(claim=claim, change=change), self.assertRaises(Unsupported):
                    AuthorityBook(records=records)

    def test_authority_invalidated_after_admission_is_atomic(self):
        for claim in ('fair_value', 'residual_equity', 'amortised_cost'):
            authority = AuthorityBook()
            book = BondBook(Contract(), authority)
            before = book.state
            authority.records['claims'] = [c for c in authority.records['claims'] if c['id'] != claim]
            with self.assertRaises(Unsupported): book.apply('issue', 'issue', '2024-01-01')
            self.assertEqual(before, book.state)

    def test_later_authority_loss_preserves_committed_history(self):
        for target_kind, missing_claim in [('accrue', 'amortised_cost'),
                                           ('coupon', 'redemption'),
                                           ('redeem', 'residual_equity'),
                                           ('convert', 'conversion')]:
            authority = AuthorityBook()
            book = BondBook(Contract(), authority)
            book.apply('issue', 'issue', '2024-01-01')
            for index, day in enumerate(book.contract.coupon_dates()):
                if target_kind == 'accrue': break
                book.apply(f'a{index}', 'accrue', day)
                if target_kind == 'coupon': break
                book.apply(f'c{index}', 'coupon', day)
            before = book.state
            authority.records['claims'] = [c for c in authority.records['claims']
                                            if c['id'] != missing_claim]
            with self.subTest(event=target_kind), self.assertRaises(Unsupported):
                book.apply('rejected', target_kind, day)
            self.assertEqual(before, book.state)

    def test_access_history_and_research_dispositions_are_preserved(self):
        mutations = [
            lambda d: d['source_access'][1].update(access_status='inspected_primary'),
            lambda d: d['source_access_recovery'][0].update(sha256='0'*64),
            lambda d: d['source_access_recovery'].pop(),
            lambda d: d['research'][0].update(decision='adopt ACTUS without audit'),
            lambda d: d['method_queue'][0].update(method='bonds'),
        ]
        for index, mutation in enumerate(mutations):
            data = copy.deepcopy(self.payload); mutation(data)
            with self.subTest(mutation=index):
                self.assertTrue(self.validate(data, self.authority))

    def test_corrupted_stored_outputs_are_rejected(self):
        mutations = [
            lambda d: d['cases'][0].update(initial_liability='99'),
            lambda d: d['cases'][0]['journal'][0]['postings_debit_positive'].update(cash='99'),
            lambda d: d['cases'][0]['journal'][0].update(claims=['recognition']),
            lambda d: d['cases'][0]['final_state']['ledger'].update(cash='11'),
            lambda d: d['cases'][0]['notes']['periods'][0].update(interest_expense='9'),
            lambda d: d['cases'][0]['notes']['links'].update(financing_interest=['note_carrying']),
            lambda d: d['cases'][0]['independent_oracle'].update(total_interest='10'),
            lambda d: d['claims'][0].update(supported_statement='Fabricated primary claim'),
            lambda d: d['authorities'][0].update(jurisdiction='US'),
            lambda d: d['authorities'][0]['retained'].update(sha256='0'*64),
            lambda d: d['claims'].pop(),
            lambda d: d['operations'][0]['recognition']['authority_claims'].remove('fair_value'),
            lambda d: d['operations'][0]['note_links'].update(financing_carrying=['absent']),
            lambda d: d['manifest']['source_hashes'].update({'scripts/corporate_financing_v1.py':'0'*64}),
        ]
        for index, mutation in enumerate(mutations):
            d = copy.deepcopy(self.payload); mutation(d)
            with self.subTest(mutation=index): self.assertTrue(self.validate(d, self.authority))

    def test_comparison_hashes_are_derived_from_economics(self):
        d = copy.deepcopy(self.payload)
        for row in d['comparisons']['rows']: row['facts_sha256'] = 'f'*64
        self.assertTrue(self.validate(d, self.authority))

    def test_manifest_source_pins_must_match_retained_bytes(self):
        paths = [
            'docs/design/research/p08-v1/aasb7.pdf',
            'docs/design/research/p08-v2/fasb-storage.pdf',
            'docs/design/research/standards/aasb132.txt',
            'docs/design/research/p08-v2/access-records.json',
            'docs/design/research/standards/actus-techspecs.tex',
        ]
        for path in paths:
            data = copy.deepcopy(self.payload)
            data['manifest']['source_hashes'][path] = '0' * 64
            with self.subTest(path=path):
                findings = self.validate(data, self.authority)
                self.assertIn('stale manifest input hash: ' + path, findings)

    def test_manifest_requires_all_authority_inputs(self):
        required = {source[key]['path']
                    for source in self.authority.sources.values()
                    if source['access_status'] == 'inspected_primary'
                    for key in ('retained', 'text')}
        required.add('docs/design/research/p08-v2/source-inspection.json')
        for path in required:
            data = copy.deepcopy(self.payload)
            del data['manifest']['source_hashes'][path]
            with self.subTest(path=path):
                self.assertIn('missing manifest input pin: ' + path,
                              self.validate(data, self.authority))

    def test_manifest_rejects_unresolvable_or_unsafe_extra_pins(self):
        from check_accounting_p08 import check_manifest_pins
        for path in ('../outside.pdf', '/tmp/outside.pdf', './scripts/check_accounting_p08.py',
                     'docs/design/research/p08-v2/absent.pdf'):
            with self.subTest(path=path):
                self.assertTrue(check_manifest_pins({path: '0' * 64}, set()))
        self.assertTrue(check_manifest_pins([], set()))

    def test_altered_comparator_economics_even_with_rehashed_rows(self):
        from corporate_financing_v1 import economics_hash
        for key, value in [('principal', '101'), ('opening_cash', '30'), ('entity_scope', 'not-for-profit')]:
            d = copy.deepcopy(self.payload); c = d['comparisons']; c['economic_facts'][key] = value
            for row in c['rows']: row['facts_sha256'] = economics_hash(c['economic_facts'])
            with self.subTest(key=key): self.assertTrue(self.validate(d, self.authority))

    def test_each_supported_comparison_outcome_is_replayed(self):
        for settlement in ('redeem', 'convert'):
            d = copy.deepcopy(self.payload)
            d['comparisons']['rows'][0]['cases'][settlement]['notes']['periods'][1]['closing_liability'] = '1'
            self.assertTrue(self.validate(d, self.authority))

    def test_unresolved_cannot_be_promoted_or_filled(self):
        for mutation in (
            lambda d: d['comparisons']['rows'][1].update(initial_liability='100'),
            lambda d: d['comparisons']['rows'][1].update(total_interest='10'),
            lambda d: d['comparisons']['rows'][1].update(status='supported_bounded'),
            lambda d: d['comparisons'].update(criterion_status='complete_bounded'),
            lambda d: d['acceptance'].update(phase_criteria_complete=True),
        ):
            d = copy.deepcopy(self.payload); mutation(d)
            self.assertTrue(self.validate(d, self.authority))

    def test_empty_authority_period_rejected(self):
        records = copy.deepcopy(self.authority.records)
        records['authorities'][0]['period_start_exclusive'] = records['authorities'][0]['period_start_inclusive']
        with self.assertRaises(Unsupported): AuthorityBook(records=records)


class EUPreparationTests(unittest.TestCase):
    def test_retained_dossier_and_independent_namespace(self):
        from corporate_authority_eu_v1 import EUAuthorityPreparation, CLAIMS
        p = EUAuthorityPreparation()
        self.assertFalse(p.records['admission_allowed'])
        self.assertTrue(CLAIMS <= {c['id'] for c in p.records['claims']})
        self.assertEqual(len(p.records['amendment_matrix']), 4)
        self.assertEqual({e['event_date'] for e in p.records['event_applicability']},
                         {'2024-01-01', '2024-12-31', '2025-12-31'})

    def test_caller_cannot_promote_or_relabel_preparation(self):
        from corporate_authority_eu_v1 import EUAuthorityPreparation, AuthorityDependencyError
        records = EUAuthorityPreparation().records
        mutations = [lambda d: d.update(admission_allowed=True),
                     lambda d: d['claims'].pop(0),
                     lambda d: d['claims'][0].update(id='classification'),
                     lambda d: d['event_applicability'][0].update(status='applicable'),
                     lambda d: d['missing_authority'].clear(),
                     lambda d: d['amendment_matrix'][0].update(decision='no effect')]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                d=copy.deepcopy(records); mutation(d)
                with self.assertRaises(AuthorityDependencyError): EUAuthorityPreparation(records=d)

    def test_retained_source_bytes_are_revalidated(self):
        import tempfile, shutil
        from corporate_authority_eu_v1 import EUAuthorityPreparation, AuthorityDependencyError, REGISTER
        records = EUAuthorityPreparation().records
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in [REGISTER] + [p['path'] for p in records['source_pins']]:
                target=root/name; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/name, target)
            EUAuthorityPreparation(root)
            source=root/'docs/design/research/p08-v3/scope.txt'
            source.write_text(source.read_text()+'tampered')
            with self.assertRaisesRegex(AuthorityDependencyError, 'stale EU source hash'):
                EUAuthorityPreparation(root)

    def test_context_period_and_missing_authority_reject_admission(self):
        from corporate_authority_eu_v1 import EUAuthorityPreparation, AuthorityDependencyError
        p=EUAuthorityPreparation()
        c=replace(Contract(), basis='EU-endorsed IFRS', jurisdiction='EU',
                  tier='EU listed consolidated', book='consolidated')
        for candidate, message in [(Contract(), 'context mismatch'),
                                   (replace(c, issue_date='2023-01-01'), '2024–2025'),
                                   (c, 'authority uninspected')]:
            with self.subTest(candidate=candidate), self.assertRaisesRegex(AuthorityDependencyError,message):
                p.require_admitted(candidate)
        with self.assertRaisesRegex(Unsupported, 'authority uninspected'):
            BondBook(c)

    def test_eu_relabelling_cannot_mutate_committed_aasb_state(self):
        for outcome in ('redeem', 'convert'):
            b=BondBook(Contract())
            b.apply('issue','issue','2024-01-01')
            for i, day in enumerate(b.contract.coupon_dates()):
                b.apply('a'+str(i),'accrue',day); b.apply('c'+str(i),'coupon',day)
            before=b.state
            b.contract=replace(b.contract, basis='EU-endorsed IFRS', jurisdiction='EU',
                               tier='EU listed consolidated',book='consolidated')
            with self.assertRaisesRegex(Unsupported,'authority uninspected'):
                b.apply('settle',outcome,'2025-12-31')
            self.assertEqual(before,b.state)

    def test_deliverable_eu_preparation_and_pins_are_checked(self):
        from check_accounting_p08 import check_deliverable
        original=json.loads((ROOT/'data/accounting-master/deliverables/P08/authority-and-methods.json').read_text())
        authority=AuthorityBook()
        for mutation in [lambda d:d['eu_authority_preparation']['missing_authority'].clear(),
                         lambda d:d['manifest']['source_hashes'].pop('docs/design/research/p08-v3/scope.pdf'),
                         lambda d:d.update(eu_authority_preparation_sha256='0'*64)]:
            d=copy.deepcopy(original);mutation(d)
            self.assertTrue(check_deliverable(d,authority))


if __name__ == '__main__':
    unittest.main()
