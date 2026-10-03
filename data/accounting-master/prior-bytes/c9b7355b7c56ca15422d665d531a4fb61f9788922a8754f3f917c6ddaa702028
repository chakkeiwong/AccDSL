"""Deterministic real-input checks for the bounded Apple P02 case.

The tests deliberately exercise the retained annual PDF/text and interim HTML
through the reusable case adapter.  Expected identities below are stated from
the filing rows themselves; they are not copied from a generated case result.
"""
from __future__ import annotations

import copy
from fractions import Fraction
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from scripts import apple_case_v1 as case


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/accounting-master/deliverables/P02"
CASE_PATH = OUT / "case.json"
ANNUAL_TEXT = ROOT / "docs/design/cases/apple/annual-2024.txt"
INTERIM_HTML = ROOT / "docs/design/cases/apple/interim-2025q1.html"


class AccountingP02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case_data = json.loads(CASE_PATH.read_text())
        cls.by_id = {o["id"]: o for o in cls.case_data["observations"]}
        cls.annual = case.Document("annual", case.APPLE + "annual-2024.pdf",
                                   case.APPLE + "annual-2024.txt", pdf=True)
        cls.interim = case.Document("interim", case.APPLE + "interim-2025q1.html",
                                    case.APPLE + "interim-2025q1.txt")
        cls.reader = case.InlineReader(cls.interim)
        cls.official = case.Document("annual-2024-official",
            case.NEW + "annual-2024-official.html", case.NEW + "annual-2024-official.txt")

    def reader_with_raw(self, raw):
        reader = copy.copy(self.reader)
        reader.raw = raw
        reader.soup = BeautifulSoup(raw, "html.parser")
        reader.ids = {e["id"]: e for e in reader.soup.find_all(id=True)}
        reader.facts = reader.soup.find_all("ix:nonfraction")
        return reader

    def test_fresh_pdf_rows_and_independent_arithmetic(self):
        fresh = subprocess.run(["pdftotext", "-layout", str(ROOT / case.APPLE / "annual-2024.pdf"), "-"],
                               capture_output=True, check=True, timeout=30).stdout.decode()
        self.assertEqual(fresh, ANNUAL_TEXT.read_text())

        def page(n):
            found = [p for p in fresh.split("\f")
                     if re.search(r"Apple Inc\. \| 2024 Form 10-K \| " + str(n) + r"\s*$", p)]
            self.assertEqual(len(found), 1)
            return found[0]

        def values(text, label, count):
            rows = re.findall(r"(?m)^[ \t]*" + re.escape(label) + r"[ \t]{2,}([^\n]+)", text)
            self.assertEqual(len(rows), 1, label)
            tokens = re.findall(r"\(?\d[\d,]*\)?|—", rows[0])
            self.assertEqual(len(tokens), count)
            return [Fraction(0) if t == "—" else
                    Fraction(t.replace(",", "").replace("(", "-").replace(")", "")) for t in tokens]

        for col, day in enumerate(["2024-09-28", "2023-09-30"]):
            debt = [values(page(43).split("To manage interest rate risk")[0], label, 2)[col] for label in [
                "Total term debt principal", "Unamortized premium/(discount) and issuance costs, net",
                "Hedge accounting fair value adjustments", "Total term debt"]]
            self.assertEqual(sum(debt[:3]), debt[3])
            for key, val in zip(["principal", "discount", "hedge", "carrying"], debt):
                self.assertEqual(val * 1000000, Fraction(self.by_id[f"annual.debt.{day}.{key}"]["value_usd"]))
            balance = page(31)
            current = balance.split("Current liabilities:")[1].split("Non-current liabilities:")[0]
            noncurrent = balance.split("Non-current liabilities:")[1]
            self.assertEqual(values(current, "Term debt", 2)[col] +
                             values(noncurrent, "Term debt", 2)[col], debt[3])
            self.assertEqual(values(balance, "Total liabilities", 2)[col] +
                             values(balance, "Total shareholders’ equity", 2)[col],
                             values(balance, "Total assets", 2)[col])
            ppe = [values(page(39), label, 2)[col] for label in [
                "Gross property, plant and equipment", "Accumulated depreciation", "Total property, plant and equipment, net"]]
            self.assertEqual(ppe[0] + ppe[1], ppe[2])
            self.assertEqual(ppe[2], values(balance, "Property, plant and equipment, net", 2)[col])
            for key, val in zip(["gross", "depreciation", "net"], ppe):
                self.assertEqual(val * 1000000, Fraction(self.by_id[f"annual.ppe.{day}.{key}"]["value_usd"]))
        for col, year in enumerate([2024, 2023, 2022]):
            revenue = values(page(29), "Total net sales", 3)[col]
            products = [values(page(35), label, 3)[col] for label in [
                "iPhone", "Mac", "iPad", "Wearables, Home and Accessories", "Services (1)"]]
            geographic = [values(page(47).split(label + ":")[1].split("Operating income")[0],
                                 "Net sales", 3)[col] for label in
                          ["Americas", "Europe", "Greater China", "Japan", "Rest of Asia Pacific"]]
            self.assertEqual(sum(products), revenue)
            self.assertEqual(sum(geographic), revenue)
            for partition, amounts in [("product", products), ("segment", geographic)]:
                for i, val in enumerate(amounts):
                    self.assertEqual(val * 1000000, Fraction(self.by_id[f"annual.{partition}.{year}.{i}"]["value_usd"]))
            flows = [values(page(33), label, 3)[col] for label in [
                "Cash, cash equivalents, and restricted cash and cash equivalents, beginning balances",
                "Cash generated by operating activities", "Cash generated by/(used in) investing activities",
                "Cash used in financing activities",
                "Cash, cash equivalents, and restricted cash and cash equivalents, ending balances"]]
            self.assertEqual(sum(flows[:4]), flows[4])
            for key, val in zip(["opening", "operating", "investing", "financing", "closing"], flows):
                self.assertEqual(val * 1000000, Fraction(self.by_id[f"annual.cf.{year}.{key}"]["value_usd"]))

    def test_independent_html_contexts_values_and_bridges(self):
        # Independently parse all selected interim readings, including repeated
        # facts. No InlineReader extraction or generated expected totals here.
        soup = BeautifulSoup(INTERIM_HTML.read_text(), "html.parser")
        for oid, obs in self.by_id.items():
            if not oid.startswith("interim."):
                continue
            for reading in obs["source_readings"]:
                fact = soup.find(id=reading["fact_id"])
                ctx = soup.find(id=fact["contextref"])
                unit = soup.find(id=fact["unitref"])
                self.assertEqual(fact["name"], obs["concept"])
                self.assertEqual(ctx.find("xbrli:identifier").get_text(), obs["context"]["entity"])
                self.assertEqual(unit.find("xbrli:measure").get_text(), "iso4217:USD")
                period = {e.name.split(":")[1].replace("date", ""): e.get_text()
                          for e in ctx.find("xbrli:period").find_all(recursive=False)}
                self.assertEqual(period, obs["context"]["period"])
                dims = {e["dimension"]: e.get_text() for e in ctx.find_all("xbrldi:explicitmember")}
                self.assertEqual(dims, obs["context"]["dimensions"])
                literal = fact.get_text(strip=True).replace(",", "")
                val = Fraction(0 if literal in ("—", "–") else literal) * Fraction(10)**int(fact.get("scale", 0))
                val *= -1 if fact.get("sign") == "-" else 1
                self.assertEqual(val, Fraction(obs["value_usd"]))
        get = lambda oid: Fraction(self.by_id[oid]["value_usd"])
        self.assertEqual(get("interim.bs.2024-12-28.debt_current") / 1000000, 10848)
        self.assertEqual(get("interim.bs.2024-12-28.debt_noncurrent") / 1000000, 83956)
        self.assertEqual(10848 + 83956, 94804)
        for end in ["2024-12-28", "2023-12-30"]:
            for partition in ["product", "segment"]:
                self.assertEqual(sum(get(f"interim.{partition}.{end}.{i}") for i in range(5)), get("interim.revenue." + end))
            self.assertEqual(sum(get(f"interim.cf.{end}.{k}") for k in ["opening", "operating", "investing", "financing"]),
                             get(f"interim.cf.{end}.closing"))

    def test_substantive_indenture_and_exhibit_contents(self):
        text = (ROOT / case.NEW / "registration-2021.txt").read_text()
        # Locate operative numbered section headings independently of adapter regex.
        normalized = text.replace("\xa0", " ")
        start = normalized.index("Section 501.\nEvents of\nDefault\n.")
        end = normalized.index("Section 502.\nAcceleration of Maturity; Rescission and Annulment\n.", start)
        self.assertGreater(start, text.index("Exhibit 4.1\nApple Inc."))
        agreement = self.case_data["external"]["agreement_interpretation"]
        support = agreement["support"][-1]
        self.assertEqual((support["start"], support["end"]), (start, end))
        self.assertIn("30 days", support["quote"])
        self.assertIn("series", support["quote"].lower())
        self.assertIn("series", agreement["missing"])
        e = next(x for x in self.case_data["external"]["partIII_and_package_obligations"]
                 if x["id"] == "annual.exhibit.4.1.in_pdf")
        self.assertGreater(e["support"]["start"], e["index_support"]["end"])
        self.assertIn("DESCRIPTION OF THE REGISTRANT’S SECURITIES", e["support"]["quote"])
        self.assertGreater(len(e["support"]["quote"]), 10000)

    def test_note_membership_complete_span_and_extraction_identity(self):
        notes = self.case_data["notes"]
        case.validate_note_links(notes, self.case_data["observations"])
        raw = INTERIM_HTML.read_text()
        headings = [m for m in re.finditer(r">Note (\d+) &#8211; <ix:nonNumeric", raw)]
        self.assertEqual([int(m[1]) for m in headings], list(range(1, 11)))
        for note in notes:
            self.assertTrue(note["unresolved_meaning"])
            self.assertFalse(note["semantic_completion"])
            if note["id"].startswith("interim."):
                boundary = note["raw_note_boundary"]
                self.assertEqual(boundary["start"], headings[note["number"]-1].start())
                for evidence in note["linked_quantity_evidence"]:
                    s = evidence["source"]
                    self.assertEqual(raw[s["start"]:s["end"]], s["quote"])
                    self.assertLessEqual(s["end"], boundary["end"])
        linked_note = next(n for n in notes if n["id"].startswith("interim.") and n["linked_quantities"])
        for mutation in ["end", "extraction", "assignment"]:
            altered = copy.deepcopy(notes)
            note = next(n for n in altered if n["id"] == linked_note["id"])
            link = note["linked_quantity_evidence"][0]
            if mutation == "end":
                note["raw_note_boundary"]["end"] = link["source"]["end"] - 1
            elif mutation == "extraction":
                note["raw_note_boundary"]["path"] = case.APPLE + "interim-2025q1.txt"
            else:
                other = next(n for n in altered if n["id"] == "interim.note.3")
                note["raw_note_boundary"] = other["raw_note_boundary"]
            with self.subTest(mutation=mutation), self.assertRaisesRegex(case.CaseError, "note source span/extraction mismatch"):
                case.validate_note_links(altered, self.case_data["observations"])

    def test_issuer_statement_dates_columns_and_ambiguity(self):
        for label, occurrence, expected in [("Total assets", 0, [364980, 352583]),
                                          ("Term debt", 0, [10912, 9822]),
                                          ("Term debt", 1, [85750, 95281]),
                                          ("Total net sales", 0, [391035, 383285, 394328])]:
            for column, value in enumerate(expected):
                anchor, literal = case.rendered_row_match(self.official, label, occurrence, column)
                self.assertEqual(Fraction(literal.replace(",", "")), value)
                self.assertEqual(self.official.text[anchor["start"]:anchor["end"]], literal)
        for column in [-1, 2]:
            with self.assertRaisesRegex(case.CaseError, "issuer period/column mismatch"):
                case.rendered_row_match(self.official, "Total assets", column=column)
        for mutation, message in [("dates", "issuer period/column mismatch"), ("row", "ambiguous issuer row")]:
            doc = copy.copy(self.official)
            doc.text = doc.text.replace("September 28,", "September 27,") if mutation == "dates" else doc.text.replace("\nTotal assets\n", "\nTotal assets\nTotal assets\n")
            with self.subTest(mutation=mutation), self.assertRaisesRegex(case.CaseError, message):
                case.rendered_row_match(doc, "Total assets")
        # Alter the issuer cell in an in-memory source; comparison must reject it.
        original = case.rendered_row_match
        def altered(doc, label, occurrence=0, column=0):
            if label == "Total assets":
                doc = copy.copy(doc)
                anchor, _ = original(doc, label, occurrence, column)
                doc.text = doc.text[:anchor["start"]] + "364,981" + doc.text[anchor["end"]:]
            return original(doc, label, occurrence, column)
        with patch.object(case, "rendered_row_match", side_effect=altered), self.assertRaisesRegex(case.CaseError, "issuer/annual selected value mismatch"):
            case.build_case()

    def test_missing_and_reordered_note_headings(self):
        for doc, count in [(self.annual, 13), (self.interim, 10)]:
            for mutation in ["missing", "reordered"]:
                altered = copy.copy(doc)
                if mutation == "missing":
                    altered.text = re.sub(r"(?m)^(\s*)Note 2\s*[–-]", r"\1Removed 2 –", altered.text, count=1)
                else:
                    altered.text = altered.text.replace("Note 1 –", "Note X –", 1).replace("Note 2 –", "Note 1 –", 1).replace("Note X –", "Note 2 –", 1)
                with self.subTest(doc=doc.identity, mutation=mutation), self.assertRaisesRegex(case.CaseError, "missing, duplicate or reordered notes"):
                    case.discover_notes(altered, count)

    def test_raw_note_boundaries_and_duplicate_ids_reject(self):
        raw = INTERIM_HTML.read_text()
        variants = [
            (raw.replace(">Note 2 &#8211;", ">Note 1 &#8211;", 1), "missing, duplicate or reordered raw note headings"),
            (raw.replace(">Note 2 &#8211;", ">Removed 2 &#8211;", 1), "missing, duplicate or reordered raw note headings"),
            (re.sub(r"Item 2\.(?:&#160;)+Management", "Removed Management", raw), "raw final note boundary missing"),
        ]
        with tempfile.TemporaryDirectory(prefix="p02-raw-notes-") as directory:
            root = Path(directory)
            for content, message in variants:
                (root / "interim.html").write_text(content)
                with patch.object(case, "ROOT", root):
                    doc = case.Document("interim", "interim.html", "interim.html")
                    with self.assertRaisesRegex(case.CaseError, message):
                        case.raw_note_ranges(doc)
            fid = self.by_id["interim.bs.2024-12-28.assets"]["source_readings"][0]["fact_id"]
            (root / "interim.html").write_text(raw + '<div id="' + fid + '"></div>')
            with patch.object(case, "ROOT", root):
                doc = case.Document("interim", "interim.html", "interim.html")
                with self.assertRaisesRegex(case.CaseError, "duplicate HTML/XBRL id"):
                    case.InlineReader(doc)

    def test_inline_repeated_readings_and_dimension_mutations(self):
        obs = self.by_id["interim.bs.2024-12-28.assets"]
        source = obs["source_readings"][0]
        fact = copy.copy(self.reader.ids[source["fact_id"]])
        fact["id"] = "p02_duplicate_reading"
        fact.string = "999"
        reader = self.reader_with_raw(self.reader.raw + str(fact))
        with self.assertRaisesRegex(case.CaseError, "conflicting repeated readings"):
            reader.select(obs["concept"], obs["context"], obs["measurement"], "conflict")
        ctx = copy.copy(next(x for x in self.reader.ids.values() if x.name == "xbrli:context" and x.find("xbrldi:explicitmember")))
        member = ctx.find("xbrldi:explicitmember")
        member.insert_after(copy.copy(member))
        with self.assertRaisesRegex(case.CaseError, "duplicate/missing dimension"):
            self.reader.parse_context(ctx)
        reader = self.reader_with_raw(self.reader.raw)
        fact = reader.ids[source["fact_id"]]
        fact["id"] = "missing-fact-id"
        with self.assertRaisesRegex(case.CaseError, "raw ID anchor missing/ambiguous"):
            reader.parse(fact)
        reader = self.reader_with_raw(self.reader.raw.replace("iso4217:USD", "iso4217:EUR"))
        with self.assertRaisesRegex(case.CaseError, "unsupported currency/unit"):
            reader.parse(reader.ids[source["fact_id"]])
        raw_fact = source["fact"]["quote"]
        for change, message in [(raw_fact.replace('scale="6"', 'scale="3"'), "wrong presentation scale/precision"),
                                (raw_fact.replace('scale="6"', 'sign="-" scale="6"'), "rendered/tagged sign mismatch")]:
            reader = self.reader_with_raw(self.reader.raw.replace(raw_fact, change))
            with self.assertRaisesRegex(case.CaseError, message):
                reader.select(obs["concept"], obs["context"], obs["measurement"], "mutated")
        for key, value in [("entity", "0000000001"), ("period", {"instant": "2024-12-27"})]:
            ctx = copy.deepcopy(obs["context"])
            ctx[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(case.CaseError, "missing required fact/context"):
                self.reader.select(obs["concept"], ctx, obs["measurement"], "wrong-context")

    def test_context_and_measurement_rejection_reasons(self):
        assets = self.by_id["annual.bs.2024-09-28.assets"]
        liabilities = self.by_id["annual.bs.2024-09-28.liabilities"]
        equity = self.by_id["annual.bs.2024-09-28.equity"]
        for key, value in [("entity", "0000000001"), ("currency", "EUR"),
                           ("period", {"instant": "2024-09-27"}), ("perimeter", "standalone")]:
            mutated = copy.deepcopy(equity)
            mutated["context"][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(case.CaseError, "entity/currency/perimeter/basis/period/dimensions mismatch"):
                case.reconcile("bad", "balance", [liabilities, mutated], assets)
        parts = [self.by_id[f"annual.product.2024.{i}"] for i in range(5)]
        geography = [self.by_id[f"annual.segment.2024.{i}"] for i in range(5)]
        with self.assertRaisesRegex(case.CaseError, "overlapping or wrong partitions"):
            case.reconcile("bad", "partition", parts + geography, self.by_id["annual.revenue.2024"], partition="product")
        operands = [self.by_id[f"interim.bs.2024-12-28.debt_{s}"] for s in ["current", "noncurrent"]]
        for oid in ["interim.debt.2024-12-28.fair_value", "interim.notional.2024-12-28"]:
            # Equalize dimensional context to isolate measurement rejection;
            # original dimensional mismatch is independently rejected above.
            target = copy.deepcopy(self.by_id[oid])
            target["context"] = copy.deepcopy(operands[0]["context"])
            with self.assertRaisesRegex(case.CaseError, "measurement substitution"):
                case.reconcile("bad", "rounded_debt", operands, target)
        opening = copy.deepcopy(self.by_id["annual.cf.2024.opening"])
        opening["context"]["period"]["instant"] = "2023-09-29"
        flows = [self.by_id[f"annual.cf.2024.{k}"] for k in ["operating", "investing", "financing"]]
        with self.assertRaisesRegex(case.CaseError, "stock/flow date mismatch"):
            case.reconcile("bad", "cash_flow", [opening] + flows, self.by_id["annual.cf.2024.closing"])

    def test_exact_rounding_endpoints_with_valid_synthetic_sources(self):
        # This is a numerical unit fixture, explicitly separate from Apple
        # source validation. All fixture literals and anchors are consistent.
        with tempfile.TemporaryDirectory(prefix="p02-rounding-") as directory:
            root = Path(directory)
            (root / "numbers.txt").write_text("1\n2\n1.5\n")
            with patch.object(case, "ROOT", root):
                doc = case.Document("synthetic", "numbers.txt", "numbers.txt")
                ctx = case.context({"instant": "2024-12-28"})
                def obs(oid, n, concept):
                    start, end = {Fraction(1): (0, 1), Fraction(2): (2, 3), Fraction(3, 2): (4, 7)}[n]
                    anchor = doc.anchor(start, end)
                    return case.observation(oid, concept, n * 1000000, anchor["quote"], 6, 1000000,
                        ctx, "carrying_amount", [{"cell": anchor}])
                current = obs("current", 1, "us-gaap:LongTermDebtCurrent")
                noncurrent = obs("noncurrent", 2, "us-gaap:LongTermDebtNoncurrent")
                target = obs("target", 2, "us-gaap:LongTermDebt")
                self.assertEqual(case.validate_anchors([current, noncurrent, target]), 3)
                self.assertTrue(case.reconcile("compatible", "rounded_debt", [current, noncurrent], target)["rounding_compatible"])
                endpoint = obs("endpoint", Fraction(3, 2), "us-gaap:LongTermDebt")
                bridge = case.reconcile("endpoint", "rounded_debt", [current, noncurrent], endpoint)
                self.assertEqual(bridge["lhs_interval_usd"][0], bridge["rhs_interval_usd"][1])
                self.assertTrue(bridge["rounding_compatible"])
                target = obs("target", 1, "us-gaap:LongTermDebt")
                case.validate_value(target)
                case.validate_anchors(target)
                with self.assertRaisesRegex(case.CaseError, "incompatible rounding intervals"):
                    case.reconcile("incompatible", "rounded_debt", [current, noncurrent], target)
        self.assertEqual(case.interval(Fraction(948, 10), Fraction(1, 10)), ["379/4", "1897/20"])
        self.assertTrue(case.compatible([0, Fraction(1, 2)], [Fraction(1, 2), 1]))
        self.assertFalse(case.compatible([0, Fraction(1, 2)], [Fraction(1, 2) + Fraction(1, 10**12), 1]))
        self.assertEqual(case.interval_sum([{"rounding_interval_usd": ["1", "2"]}], [-1]), (-2, -1))

    def test_publication_cutoffs_conflicts_and_metadata_tampering(self):
        records = self.case_data["filing_availability"]
        view = case.version_view(records, "2024-11-01", scope="filing_identity")
        self.assertEqual(view["eligible"], ["annual"])
        self.assertEqual(next(r["availability"] for r in view["versions"] if r["id"] == "proxy"), "later")
        self.assertEqual(case.version_view(records, "2099-12-31")["eligible"], [])
        versions = [{"id": "v1", "filing_date": "2024-11-01", "retained_byte_publication_date": "2024-11-01", "value": 1},
                    {"id": "v2", "filing_date": "2024-11-02", "retained_byte_publication_date": "2024-11-02", "value": 2}]
        before = copy.deepcopy(versions)
        result = case.version_view(versions, "2024-11-03")
        self.assertEqual(result["eligible"], ["v1", "v2"])
        self.assertEqual(result["resolution"], "retain_all_no_automatic_supersession")
        self.assertEqual(versions, before)
        for mutation in ["filing", "column", "entity"]:
            candidate = copy.deepcopy(self.case_data)
            if mutation == "filing":
                candidate["filing_availability"][2]["filing_date"] = "2024-10-01"
            elif mutation == "column":
                candidate["observations"][0]["source_readings"][0]["column_index"] = 1
            else:
                candidate["observations"][0]["context"]["entity"] = "0000000001"
            with self.subTest(mutation=mutation), self.assertRaisesRegex(case.CaseError, "case differs from source-derived rebuild"):
                case.validate_case(candidate)

    def test_real_inputs_build_and_independent_annual_arithmetic(self):
        built = case.build_case()
        self.assertEqual(len(built["notes"]), 23)
        self.assertEqual(built["coverage"]["annual_notes"], 13)
        self.assertEqual(built["coverage"]["interim_notes"], 10)
        self.assertEqual(built["acceptance"]["empirical_forecast_validity"],
                         "not evaluated; no forecast generated")

        annual = ANNUAL_TEXT.read_text()
        debt_row = re.search(
            r"Total term debt principal.*?97,341.*?\n.*?"
            r"Unamortized premium/\(discount\) and issuance costs, net.*?\(321\).*?\n.*?"
            r"Hedge accounting fair value adjustments.*?\(358\).*?\n.*?"
            r"Total term debt\s+96,662",
            annual,
            re.S,
        )
        self.assertIsNotNone(debt_row)
        # Independent displayed-million arithmetic from the retained PDF text.
        self.assertEqual(Fraction(97341) - Fraction(321) - Fraction(358),
                         Fraction(96662))
        self.assertEqual(
            Fraction(10912) + Fraction(85750),
            Fraction(96662),
        )
        self.assertIn("30,737", annual)
        self.assertIn("29,965", annual)

        # The independent retained HTML contains the actual tagged facts used
        # by the interim reader, including the rounded narrative debt fact.
        interim = INTERIM_HTML.read_text()
        self.assertIn('name="us-gaap:LongTermDebt"', interim)
        self.assertIn('>94.8</ix:nonFraction>', interim)

    def test_cli_check_rebuilds_case_from_sources(self):
        result = subprocess.run(
            ["python3", "-B", "scripts/apple_case_v1.py", "--check",
             "--output-dir", "data/accounting-master/deliverables/P02"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["notes"], 23)
        self.assertGreater(report["anchors"], 500)

    def test_note_inventory_and_boundary_mutations_are_rejected(self):
        annual = case.Document("annual", case.APPLE + "annual-2024.pdf",
                               case.APPLE + "annual-2024.txt", pdf=True)
        self.assertEqual(len(case.discover_notes(annual, 13)), 13)
        duplicate = case.Document("annual", case.APPLE + "annual-2024.pdf",
                                  case.APPLE + "annual-2024.txt", pdf=True)
        duplicate.text = duplicate.text.replace("Note 2 –", "Note 1 –", 1)
        with self.assertRaisesRegex(case.CaseError, "missing, duplicate or reordered notes"):
            case.discover_notes(duplicate, 13)
        broken_boundary = case.Document("annual", case.APPLE + "annual-2024.pdf",
                                        case.APPLE + "annual-2024.txt", pdf=True)
        broken_boundary.text = broken_boundary.text.replace(
            "Report of Independent Registered", "Report marker removed")
        with self.assertRaisesRegex(case.CaseError, "final note boundary missing"):
            case.discover_notes(broken_boundary, 13)

    def test_anchor_quote_hash_and_metadata_revalidation_reject_mutations(self):
        mutated = copy.deepcopy(self.case_data)
        anchor = mutated["notes"][0]["anchor"]
        anchor["quote"] = anchor["quote"] + " altered"
        with self.assertRaisesRegex(case.CaseError, "broken source quotation/offset"):
            case.validate_anchors(mutated)

        mutated = copy.deepcopy(self.case_data)
        anchor = mutated["notes"][0]["anchor"]
        anchor["extraction_sha256"] = "0" * 64
        with self.assertRaisesRegex(case.CaseError, "anchor source hash mismatch"):
            case.validate_anchors(mutated)

        mutated = copy.deepcopy(self.case_data)
        mutated["observations"][0]["displayed_literal"] = "1"
        with self.assertRaisesRegex(case.CaseError, "case differs from source-derived rebuild"):
            case.validate_case(mutated)

    def test_context_scale_sign_and_measurement_substitutions_reject(self):
        assets = copy.deepcopy(self.by_id["annual.bs.2024-09-28.assets"])
        liabilities = copy.deepcopy(self.by_id["annual.bs.2024-09-28.liabilities"])
        equity = copy.deepcopy(self.by_id["annual.bs.2024-09-28.equity"])

        wrong_scale = copy.deepcopy(assets)
        wrong_scale["scale"] = 9
        with self.assertRaisesRegex(case.CaseError, "literal/scale/value mismatch"):
            case.validate_value(wrong_scale)

        wrong_sign = copy.deepcopy(assets)
        wrong_sign["value_usd"] = "-364980000000"
        wrong_sign["rounding_interval_usd"] = case.interval(wrong_sign["value_usd"], wrong_sign["presentation_quantum_usd"])
        with self.assertRaisesRegex(case.CaseError, "annual cell/value mismatch"):
            case.validate_value(wrong_sign)

        wrong_perimeter = copy.deepcopy(equity)
        wrong_perimeter["context"]["perimeter"] = "standalone"
        with self.assertRaisesRegex(case.CaseError, "entity/currency/perimeter/basis/period/dimensions mismatch"):
            case.reconcile("bad.perimeter", "balance",
                           [liabilities, wrong_perimeter], assets)

        fair_value = copy.deepcopy(self.by_id["interim.debt.2024-12-28.fair_value"])
        current = copy.deepcopy(self.by_id["interim.bs.2024-12-28.debt_current"])
        noncurrent = copy.deepcopy(self.by_id["interim.bs.2024-12-28.debt_noncurrent"])
        with self.assertRaisesRegex(case.CaseError, "entity/currency/perimeter/basis/period/dimensions mismatch"):
            case.reconcile("bad.measurement", "rounded_debt",
                           [current, noncurrent], fair_value)

    def test_cash_perimeter_and_revenue_axis_substitutions_reject(self):
        opening = copy.deepcopy(self.by_id["annual.cf.2024.opening"])
        closing = copy.deepcopy(self.by_id["annual.cf.2024.closing"])
        flows = [copy.deepcopy(self.by_id[f"annual.cf.2024.{k}"])
                 for k in ("operating", "investing", "financing")]
        balance_sheet_cash = copy.deepcopy(self.by_id["annual.bs.2023-09-30.cash"])
        # 30,737 is the cash-flow opening balance; 29,965 is the prior
        # balance-sheet cash-only figure.  The latter has the wrong perimeter.
        self.assertEqual(Fraction(opening["displayed_literal"].replace(",", "")),
                         Fraction(30737))
        self.assertEqual(Fraction(balance_sheet_cash["displayed_literal"].replace(",", "")),
                         Fraction(29965))
        with self.assertRaisesRegex(case.CaseError, "cash perimeter mismatch"):
            case.reconcile("bad.cash.perimeter", "cash_flow",
                           [balance_sheet_cash] + flows, closing)

        product = [copy.deepcopy(self.by_id[f"annual.product.2024.{i}"])
                   for i in range(5)]
        product_total = copy.deepcopy(self.by_id["annual.revenue.2024"])
        self.assertEqual(case.reconcile("ok.product", "partition", product,
                                        product_total, partition="product")["status"],
                         "pass")
        product[0]["context"]["dimensions"] = {
            "us-gaap:StatementBusinessSegmentsAxis": "aapl:AmericasSegmentMember"
        }
        with self.assertRaisesRegex(case.CaseError, "partition axis/member/concept mismatch"):
            case.reconcile("bad.product.axis", "partition", product,
                           product_total, partition="product")

    def test_inline_fact_context_and_unit_ids_are_required(self):
        interim = case.Document("interim", case.APPLE + "interim-2025q1.html",
                                case.APPLE + "interim-2025q1.txt")
        reader = case.InlineReader(interim)
        fact = copy.copy(reader.facts[0])
        fact["contextref"] = "missing-context"
        with self.assertRaisesRegex(case.CaseError, "broken xbrli:context reference"):
            reader.parse(fact)
        fact = copy.copy(reader.facts[0])
        fact["unitref"] = "missing-unit"
        with self.assertRaisesRegex(case.CaseError, "broken xbrli:unit reference"):
            reader.parse(fact)

    def test_rounding_compatibility_and_incompatibility_are_distinct(self):
        current = copy.deepcopy(self.by_id["interim.bs.2024-12-28.debt_current"])
        noncurrent = copy.deepcopy(self.by_id["interim.bs.2024-12-28.debt_noncurrent"])
        rounded = copy.deepcopy(self.by_id["interim.debt.2024-12-28.rounded"])
        passing = case.reconcile("ok.rounded", "rounded_debt",
                                 [current, noncurrent], rounded)
        self.assertTrue(passing["rounding_compatible"])
        self.assertFalse(passing["displayed_identity"])

        incompatible = copy.deepcopy(rounded)
        incompatible["displayed_literal"] = "95.1"
        incompatible["value_usd"] = "95100000000"
        incompatible["rounding_interval_usd"] = case.interval(
            Fraction("95100000000"), Fraction("100000000"))
        source = incompatible["source_readings"][0]["fact"]
        source["quote"] = source["quote"].replace(">94.8<", ">95.1<")
        # Source corruption is rejected separately from the valid synthetic
        # incompatible-interval fixture above.
        with self.assertRaisesRegex(case.CaseError, "broken source quotation/offset"):
            case.reconcile("bad.rounded", "rounded_debt",
                           [current, noncurrent], incompatible)

    def test_external_obligations_and_unidentified_histories_remain_explicit(self):
        external = self.case_data["external"]
        self.assertTrue(external["partIII_and_package_obligations"])
        self.assertTrue(any("proxy" in x.get("target", "").lower()
                            for x in external["partIII_and_package_obligations"]))
        self.assertTrue(any(x.get("contents_status") ==
                            "internal_target_missing_in_retained_html"
                            for x in external["exhibit_inventory"]))
        views = case.version_view(self.case_data["filing_availability"],
                                  "2024-11-01", scope="retained_bytes")
        self.assertEqual({x["availability"] for x in views["versions"]},
                         {"unknown"})
        self.assertEqual(
            {x["status"] for x in self.case_data["unidentified_histories"]},
            {"not_identified"},
        )
        self.assertEqual(
            self.case_data["representation_comparison"]["whole_document_equivalence"],
            False,
        )


if __name__ == "__main__":
    unittest.main()
