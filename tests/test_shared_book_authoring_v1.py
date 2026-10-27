from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import shared_book_authoring_v1 as m


class AuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT / 'data/accounting-master/shared-book-statements-20261024/cases.json').read_text())
        cls.program = m.from_request(cls.rows[0]['request'], 'mixed_lifecycle')
        cls.source = m.render(cls.program)

    def equal(self, a, b):
        self.assertEqual(m.book.caller.canonical(a), m.book.caller.canonical(b))

    def rejects(self, source, reason=None):
        with self.assertRaises(m.Invalid) as caught:
            m.lower(source)
        if reason:
            self.assertIn(reason, str(caught.exception))

    def test_all_original_requests(self):
        rejected = {'unsupported_tax': 'unsupported_module', 'stale_opening_digest': 'opening_digest',
                    'arbitrary_closing_state': 'closed_fields:request'}
        for row in self.rows:
            with self.subTest(case=row['case']):
                before = m.book.digest(row)
                if row['case'] in rejected:
                    with self.assertRaisesRegex(m.Invalid, rejected[row['case']]):
                        m.from_request(row['request'], row['case'])
                else:
                    program = m.from_request(row['request'], row['case'])
                    source = m.render(program)
                    self.equal(program, m.lower(source))
                    self.assertEqual(source, m.render(m.lower(source)))
                    self.equal(m.execute_program(program), row['result'])
                    self.equal(m.execute_text(source), row['result'])
                self.assertEqual(before, m.book.digest(row))

    def test_authored_cash_edit_preserves_native_funding_failure(self):
        body = deepcopy(self.program['request'])
        body['opening']['balances']['cash'] = '130/1'
        body['opening']['balances']['capital'] = '-230/1'
        body['events'] = [body['events'][0], body['events'][1], body['events'][3]]
        body = m.reports.request(body['opening'], body['events'])
        program = m.from_request(body, 'cash_edit')
        result = m.execute_text(m.render(program))
        self.equal(result, m.reports.calculate(body))
        self.assertEqual(result['coverage']['completed_events'], 2)
        self.assertEqual(result['coverage']['failed_event']['result']['status'], 'funding_failure')
        self.assertEqual(result['cash_flows_recorded']['closing_cash'], '82/1')

    def test_text_identity_separate_from_semantics(self):
        first = m.compile_text(self.source)
        spaced = m.compile_text('\n' + self.source.replace('\n', '\r\n'))
        self.assertNotEqual(first['source_text_sha256'], spaced['source_text_sha256'])
        self.assertEqual(first['program_sha256'], spaced['program_sha256'])
        renamed = deepcopy(self.program); renamed['name'] = 'other_name'
        other = m.compile_program(renamed)
        self.assertNotEqual(first['program_sha256'], other['program_sha256'])
        self.assertEqual(first['request_sha256'], other['request_sha256'])
        self.equal(m.execute_program(renamed), self.rows[0]['result'])

    def test_no_semantic_rejection_during_compilation(self):
        for name in ['empty_invalid_prefix', 'unknown_lease_membership', 'invalid_lease_allocation', 'unsupported_fx']:
            row = next(r for r in self.rows if r['case'] == name)
            program = m.from_request(row['request'], name)
            self.equal(m.compile_text(m.render(program))['program'], program)
            self.equal(m.execute_program(program), row['result'])

    def test_duplicate_keys_accounts_and_fields_have_lines(self):
        cases = [self.source.replace('"cash" "500/1"', '"cash" "500/1";\naccount "cash" "500/1"'),
                 self.source.replace('conditional true;', 'conditional true;\nconditional false;')]
        for source in cases: self.rejects(source, 'line ')
        self.rejects(self.source.replace('"currency":"USD"', '"currency":"USD","currency":"EUR"'), 'line ')
        lot = {'id': 'recovered', 'component_id': 'return_component', 'acquired': '2024-01-01',
               'units': '1/1', 'carrying': '1/1', 'tax_base': '1/1', 'disposed': False}
        declaration = 'lot "recovered" ' + m.token(lot) + ';\n'
        self.rejects(self.source.replace('lots;\nend_lots;', 'lots;\n' + declaration * 2 + 'end_lots;'), 'duplicate_lot')

    def test_missing_collections_balance_report_and_delimiters(self):
        cases = [self.source.replace('lots;\nend_lots;\n', ''),
                 self.source.replace('leases;', 'unknown_collection;', 1),
                 self.source.replace('account "cash" "500/1";\n', ''),
                 '\n'.join(l for l in self.source.splitlines() if not l.startswith('report ')),
                 self.source.replace('end_events;', '', 1), self.source.replace('end_program;', ''),
                 self.source + 'events;\n', self.source.replace('conditional true;', 'conditional true')]
        for source in cases:
            with self.subTest(source=source[:40]): self.rejects(source, 'line ')

    def test_wrong_scalars_unknown_syntax_methods_and_stale_digests(self):
        cases = [self.source.replace('conditional true;', 'conditional 1;'),
                 self.source.replace('account "cash" "500/1";', 'account "cash" 500;'),
                 self.source.replace('"one_year_elapsed":true', '"one_year_elapsed":1'),
                 self.source.replace('"systematic_allocation_supported":true', '"systematic_allocation_supported":1'),
                 self.source.replace('event "lease"', 'event "tax"', 1),
                 self.source.replace('"lease.reduce"', '"lease.arbitrary"', 1),
                 self.source.replace('conditional true;', 'include "/tmp/file";'),
                 self.source.replace('account "cash" "500/1";', 'account "cash" "501/1";'),
                 self.source.replace('"SyntheticReturnLeaseBook/1"', '"other/1"', 1)]
        for source in cases: self.rejects(source, 'line ')

    def test_unicode_depth_size_and_noninteger_limits(self):
        cases = [b'\xff', '\ufeff' + self.source, self.source + '\r', self.source + '\u2028',
                 self.source + '\ud800', ' ' * (m.lexical.core.MAX_BYTES + 1),
                 '[' * 49 + ']' * 49,
                 self.source.replace('conditional true;', 'conditional NaN;'),
                 self.source.replace('conditional true;', 'conditional 1.0;'),
                 self.source.replace('conditional true;', 'conditional 1000000000000;'),
                 self.source.replace('"USD"', '"\\ud800"'),
                 self.source.replace('conditional true;', 'conditional ' + 'true ' * 40 + ';')]
        for source in cases: self.rejects(source)
        self.equal(m.lower(self.source.encode('utf-8')), self.program)

    def test_false_and_null_findings_survive(self):
        body = deepcopy(self.program['request'])
        body['events'][4]['event']['parameters']['systematic_allocation_supported'] = None
        body['opening']['tax_premises']['recovery_supported'] = False
        body = m.reports.request(body['opening'], body['events'])
        program = m.from_request(body, 'unknown')
        self.equal(m.lower(m.render(program)), program)
        self.equal(m.execute_text(m.render(program)), m.reports.calculate(body))

    def test_nonselected_opening_lot_is_preserved(self):
        body = deepcopy(self.program['request'])
        body['opening']['lots']['opening_stock'] = {
            'id': 'opening_stock', 'component_id': 'return_component',
            'acquired': '2024-01-01', 'units': '1/1', 'carrying': '3/1',
            'tax_base': '3/1', 'disposed': False}
        body['opening']['balances']['inventory'] = '63/1'
        body['opening']['balances']['capital'] = '-603/1'
        body = m.reports.request(body['opening'], body['events'])
        program = m.from_request(body, 'opening_lot')
        self.equal(m.lower(m.render(program)), program)
        result = m.execute_text(m.render(program))
        self.equal(result, m.reports.calculate(body))
        self.equal(result['execution']['after']['lots']['opening_stock'], body['opening']['lots']['opening_stock'])
        self.assertEqual(result['balance_sheet_recorded']['assets']['inventory'], '63/1')

    def test_explicit_empty_lease_collection(self):
        opening = deepcopy(self.program['request']['opening'])
        opening['leases'] = []
        opening['balances'].update(rou='0/1', lease_liability='0/1', capital='-630/1')
        body = m.reports.request(opening, [])
        program = m.from_request(body, 'empty_leases')
        self.assertIn('leases;\nend_leases;', m.render(program))
        self.equal(m.lower(m.render(program)), program)
        result = m.execute_text(m.render(program))
        self.equal(result, m.reports.calculate(body))
        self.assertEqual(result['status'], 'recorded_prefix')


if __name__ == '__main__':
    unittest.main()
