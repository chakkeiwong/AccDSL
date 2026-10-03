"""Regression checks for evidence revocation, period identity and source slots."""
import tempfile
import unittest
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from bs4 import BeautifulSoup

from scripts import acquire_financial_report_corpus as corpus
from scripts.resolve_financial_report_sources import classify_link, link_title
from scripts.verify_financial_report_corpus import verify


class CorpusRegressionTests(unittest.TestCase):
    def test_corrupted_hash_named_original_is_not_silently_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder)
            doc = {'issuer_id': 'example', 'document_id': 'example-2025-annual'}
            corpus.save_bytes(data, doc, b'original version', '.pdf')
            path, _ = corpus.save_bytes(data, doc, b'new version', '.pdf')
            path.write_bytes(b'corrupted version')
            with self.assertRaises(ValueError):
                corpus.save_bytes(data, doc, b'new version', '.pdf')

    def test_curl_partial_200_is_not_an_acquired_body(self):
        response = SimpleNamespace(returncode=28, stdout=b'200\nhttps://example.com/report.pdf\napplication/pdf\n', stderr=b'Timeout')
        with patch.object(corpus.subprocess, 'run', return_value=response) as run:
            result = corpus.safe_fetch('https://example.com/report.pdf', retries=0, client='curl')
        self.assertEqual(result['status'], 'network_error')
        self.assertNotIn('body', result)
        self.assertNotIn('http_status', result)
        self.assertIn('--max-time', run.call_args.args[0])

    def test_curl_denial_is_retained_without_retries(self):
        def denied(command, **kwargs):
            Path(command[command.index('--output') + 1]).write_bytes(b'Access denied')
            Path(command[command.index('--dump-header') + 1]).write_text('HTTP/1.1 403 Forbidden\n')
            return SimpleNamespace(returncode=0, stdout=b'403\nhttps://example.com/report.pdf\ntext/html\n', stderr=b'')
        with patch.object(corpus.subprocess, 'run', side_effect=denied) as run:
            result = corpus.safe_fetch('https://example.com/report.pdf', retries=1, client='curl')
        self.assertEqual(result['http_status'], 403)
        self.assertEqual(result['body'], b'Access denied')
        self.assertEqual(run.call_count, 1)

    def test_integrity_verifier_detects_original_and_text_tampering(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = root / 'corpus'
            data.mkdir()
            panel = {'coverage_window': {'start_year': 2025, 'end_year': 2025, 'minimum_complete_years_per_issuer': 1},
                     'issuers': [{'issuer_id': 'example', 'standard_family': 'ifrs_oriented'}]}
            (root / 'panel.json').write_text(json.dumps(panel))
            rows, records = [], []
            for cls in ['annual', 'interim_h1']:
                doc_id = f'example-2025-{cls}'
                content = ('Financial statements prepared in accordance with IFRS. ' + cls).encode()
                digest = hashlib.sha256(content).hexdigest()
                original = data / f'{cls}.html'
                original.write_bytes(content)
                extracted = data / f'extracted-{digest}.txt'
                extracted.write_bytes(content)
                path = str(original.relative_to(root))
                checks = {key: {'status': 'matched'} for key in ['issuer', 'period_year', 'report_class', 'statements', 'notes']}
                checks['accounting_basis'] = {'status': 'verified', 'evidence': [{'quote': content.decode()}]}
                record = {'document_id': doc_id, 'local_path': path, 'extracted_text_path': str(extracted.relative_to(root)),
                          'sha256': digest, 'status': 'acquired_verified', 'qa_version': 'test',
                          'source_url': 'https://example.com/' + cls, 'checks': checks}
                records.append(record)
                rows.append({key: record[key] for key in ['document_id', 'local_path', 'sha256', 'status', 'extracted_text_path', 'source_url', 'qa_version']})
            coverage = {'panel': 'panel.json', 'rows': rows, 'expected_documents': 2, 'verified_documents': 2,
                        'per_issuer': {'example': {'complete_years': [2025], 'longest_consecutive_complete_years': 1}},
                        'acceptance': {'status': 'source_corpus_ready'}}
            for name, value in [('coverage.json', coverage), ('source-evidence.json', {'qa_version': 'test', 'documents': {r['document_id']: r for r in records}}),
                                ('source-access.json', []), ('resolved-sources.json', {})]:
                (data / name).write_text(json.dumps(value))
            (data / 'acquisition-results.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in records))
            self.assertEqual(verify(root, data)['status'], 'pass')
            recorded_hash = rows[0]['sha256']
            rows[0]['sha256'] = '0' * 64
            (data / 'coverage.json').write_text(json.dumps(coverage))
            self.assertIn('coverage_field_disagrees_with_ledger', [i['issue'] for i in verify(root, data)['issues']])
            rows[0]['sha256'] = recorded_hash
            (data / 'coverage.json').write_text(json.dumps(coverage))
            original.write_text('changed original')
            extracted.write_text('changed extraction')
            result = verify(root, data)
            self.assertEqual(result['status'], 'fail')
            self.assertEqual(sum(i['issue'] == 'hash_mismatch' for i in result['issues']), 2)
            self.assertIn('basis_quote_not_in_retained_text', [i['issue'] for i in result['issues']])

    def test_old_archive_download_uses_nearest_title(self):
        soup = BeautifulSoup('<mr-e-text><p>Annual report (Group) 2018<br><a href="group.pdf">Download (PDF)</a></p><p>Annual report (Company) 2018<br><a href="company.pdf">Download (PDF)</a></p></mr-e-text>', 'html.parser')
        group, company = soup.find_all('a')
        self.assertEqual(classify_link('munich_re', link_title('munich_re', group), group['href']), (2018, 'annual'))
        self.assertIsNone(classify_link('munich_re', link_title('munich_re', company), company['href']))

    def test_ping_an_mirror_title_identifies_year_and_interim(self):
        url = 'https://doc.irasia.com/listco/hk/pingan/interim/ir217643-c101.pdf'
        self.assertEqual(classify_link('ping_an', '二零一九年中期报告', url), (2019, 'interim_h1'))
        self.assertIsNone(classify_link('ping_an', '二零一九年业绩公告', url))

    def test_revalidation_revokes_same_original(self):
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder)
            common = {"document_id": "x", "local_path": "original.pdf", "qa_version": corpus.QA_VERSION}
            corpus.append_results(data, [
                {**common, "status": "acquired_verified", "attempted_at": "1"},
                {**common, "status": "invalid", "attempted_at": "2", "mode": "revalidate"},
            ])
            self.assertEqual(corpus.latest_results(data)["x"]["status"], "invalid")

    def test_network_failure_preserves_verified_original(self):
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder)
            corpus.append_results(data, [
                {"document_id": "x", "local_path": "original.pdf", "qa_version": corpus.QA_VERSION, "status": "acquired_verified", "attempted_at": "1"},
                {"document_id": "x", "status": "network_error", "attempted_at": "2"},
            ])
            self.assertEqual(corpus.latest_results(data)["x"]["status"], "acquired_verified")

    def test_failed_version_preserves_independent_verified_version(self):
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder)
            common = {"document_id": "x", "qa_version": corpus.QA_VERSION}
            corpus.append_results(data, [
                {**common, "local_path": "a.pdf", "status": "acquired_verified", "attempted_at": "1"},
                {**common, "local_path": "b.pdf", "status": "invalid", "attempted_at": "2"},
            ])
            self.assertEqual(corpus.latest_results(data)["x"]["local_path"], "a.pdf")

    def test_stale_qa_requires_revalidation(self):
        with tempfile.TemporaryDirectory() as folder:
            data = Path(folder)
            corpus.append_results(data, [{"document_id": "x", "local_path": "a.pdf", "status": "acquired_verified", "qa_version": "1"}])
            self.assertEqual(corpus.latest_results(data)["x"]["status"], "needs_revalidation")

    def test_half_year_is_not_annual(self):
        self.assertEqual(classify_link("midea", "2022 H1 年度报告", "https://www.midea.com.cn/a.pdf"), (2022, "interim_h1"))
        self.assertEqual(classify_link("midea", "2024 H1 半年度报告", "https://www.midea.com.cn/a.pdf"), (2024, "interim_h1"))
        doc = {"issuer_id": "midea", "period_year": 2024, "report_class": "annual"}
        self.assertEqual(corpus.period_identity(doc, "美的集团 2024 年半年度报告")["status"], "mismatch")

    def test_comparative_year_does_not_establish_report_year(self):
        doc = {"issuer_id": "hsbc", "period_year": 2023, "report_class": "annual"}
        self.assertEqual(corpus.period_identity(doc, "Annual Report and Accounts 2024 with 2023 comparative figures")["status"], "mismatch")

    def test_apple_fiscal_year_crosses_calendar_year(self):
        doc = {"issuer_id": "apple", "period_year": 2025, "report_class": "q1"}
        self.assertEqual(corpus.period_identity(doc, "For the quarterly period ended December 28, 2024")["status"], "matched")
        doc["period_year"] = 2024
        self.assertEqual(corpus.period_identity(doc, "For the quarterly period ended December 28, 2024")["status"], "mismatch")

    def test_incidental_ifrs_reference_is_not_preparation_basis(self):
        doc = {"standard_family": "ifrs_oriented"}
        self.assertEqual(corpus.basis_check(doc, "Capital ratios comply with regulation including IFRS 9 transition arrangements.")["status"], "missing")
        self.assertEqual(corpus.basis_check(doc, "These financial statements have been prepared in accordance with IFRS Accounting Standards.")["status"], "verified")

    def test_negated_basis_requires_an_affirmative_anchor(self):
        doc = {"standard_family": "ifrs_oriented"}
        self.assertEqual(corpus.basis_check(doc, "The financial statements have not been prepared in accordance with IFRS.")["status"], "missing")
        self.assertEqual(corpus.basis_check(doc, "This interim financial report has been prepared in accordance with International Accounting Standard (IAS) 34.")["status"], "verified")
        doc = {'standard_family': 'asbe_candidates'}
        self.assertEqual(corpus.basis_check(doc, '本财务报表未按照企业会计准则编制。')['status'], 'missing')
        self.assertEqual(corpus.basis_check(doc, '本中期简要财务报表根据中国财政部颁布的《企业会计准则第32号——中期财务报告》列报。')['status'], 'verified')

    def test_munich_re_issue_number_cover_overrides_comparatives(self):
        doc = {"issuer_id": "munich_re", "period_year": 2021, "report_class": "interim_h1"}
        text = "Half-Year Financial Report\nMunich Re\n2/2021\fRefer to Annual Report 2020"
        self.assertEqual(corpus.period_identity(doc, text)["status"], "matched")
        doc["period_year"] = 2020
        self.assertEqual(corpus.period_identity(doc, text)["status"], "mismatch")

    def test_two_column_sec_cover_preserves_own_period(self):
        doc = {"issuer_id": "jpmorgan", "period_year": 2018, "report_class": "q1"}
        self.assertEqual(corpus.period_identity(doc, "For the quarterly period ended Commission file March 31, 2018 number 1-5805")["status"], "matched")
        doc["report_class"] = "q2"
        self.assertEqual(corpus.period_identity(doc, "For the quarterly period ended Commission file March 31, 2018 number 1-5805")["status"], "mismatch")

    def test_hidden_ixbrl_metadata_does_not_displace_cover(self):
        raw = b'<html><ix:header><ix:hidden>old dates</ix:hidden><xbrli:context>metadata</xbrli:context></ix:header><p>Actual report</p></html>'
        self.assertEqual(corpus.clean_text(raw, "text/html", ".html"), "Actual report")

    def test_hidden_converted_html_keeps_visible_body(self):
        raw = b'<html><DIV STYLE="DISPLAY:NONE"><span>metadata</span><br>more</DIV><p>Visible cover</p></html>'
        self.assertEqual(corpus.clean_text(raw, "text/html", ".html"), "Visible cover")

    def test_local_file_url_is_never_fetched(self):
        result = corpus.safe_fetch("file:///etc/passwd")
        self.assertEqual(result["attempts"], 0)
        self.assertNotIn("body", result)


if __name__ == "__main__":
    unittest.main()
