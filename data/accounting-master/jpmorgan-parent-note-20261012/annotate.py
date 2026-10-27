"""Bind selected parent-only rows and check displayed-number bridges."""
import hashlib
import json
import re
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
START = time.monotonic()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def match_once(text, phrase):
    expression = r"\s+".join(re.escape(token) for token in phrase.split())
    found = list(re.finditer(expression, text))
    if len(found) != 1:
        raise ValueError(f"Expected one source span, found {len(found)}: {phrase[:90]}")
    m = found[0]
    return {"start": m.start(), "end": m.end(), "quote": m.group(), "span_sha256": hashlib.sha256(m.group().encode()).hexdigest()}


def main():
    assert not (OUT / "source-ledger.json").exists(), "Preserve checked source ledger"
    manifest = json.loads((OUT / "source-manifest.json").read_text())
    checks = []

    def ck(name, value):
        checks.append({"check": name, "passed": bool(value)})

    ck("source PDF preserved", sha(ROOT / manifest["source_pdf"]) == manifest["source_pdf_sha256"])
    ck("candidate PDF preserved", sha(ROOT / manifest["candidate_pdf"]) == manifest["candidate_pdf_sha256"])
    pages = {}
    for page in manifest["pages"]:
        n = page["pdf_page"]
        ck(f"reading page {n}", sha(ROOT / page["reading"]) == page["reading_sha256"])
        ck(f"layout page {n}", sha(ROOT / page["layout"]) == page["layout_sha256"])
        ck(f"render page {n}", sha(ROOT / page["render"]) == page["render_sha256"])
        pages[n] = (ROOT / page["reading"]).read_text()
    ck("note identity", "Note 33 – Parent Company" in pages[312] and "Parent Company-only" in pages[312])
    ck("table units and periods", "(in millions)" in pages[312] and "(in millions)" in pages[313] and all(y in pages[312] and y in pages[313] for y in ["2025", "2024", "2023"]))
    ck("footnotes a through e", all(f"({letter})" in pages[313] for letter in "abcde"))

    # The amounts below are literal displayed US$ millions, not unrounded facts.
    specs = [
        ("income.dividends.bank", 312, "Bank and bank holding company $ 50,000 $ 37,000 $ 61,000", [50000, 37000, 61000]),
        ("income.equity_undistributed", 312, "Equity in undistributed net income of subsidiaries 21,163 35,781 1,867", [21163, 35781, 1867]),
        ("income.total", 312, "Total income 53,036 40,207 63,563", [53036, 40207, 63563]),
        ("income.expense", 312, "Total expense 18,973 18,781 17,403", [18973, 18781, 17403]),
        ("income.pretax", 312, "Income before income tax benefit and undistributed net income of subsidiaries 34,063 21,426 46,160", [34063, 21426, 46160]),
        ("income.tax_benefit", 312, "Income tax benefit 1,822 1,264 1,525", [1822, 1264, 1525]),
        ("income.net", 312, "Net income $ 57,048 $ 58,471 $ 49,552", [57048, 58471, 49552]),
        ("balance.cash", 312, "Cash and due from banks $ 39 $ 38", [39, 38]),
        ("balance.bank_deposits", 312, "Deposits with banking subsidiaries(b) 9,751 9,762", [9751, 9762]),
        ("balance.trading_intercompany", 312, "Trading assets - intercompany 14,885 43,214", [14885, 43214]),
        ("balance.investments_bank", 312, "Bank and bank holding company 669,449 603,044", [669449, 603044]),
        ("balance.assets", 312, "Total assets $ 710,044 $ 669,614", [710044, 669614]),
        ("balance.intercompany_payables", 312, "Borrowings from, and payables to, subsidiaries and affiliates $ 79,317 $ 72,881", [79317, 72881]),
        ("balance.long_term_debt", 312, "Long-term debt(c)(d) 254,633 239,626", [254633, 239626]),
        ("balance.liabilities", 312, "Total liabilities(d) 347,606 324,856", [347606, 324856]),
        ("balance.equity", 312, "Total stockholders’ equity 362,438 344,758", [362438, 344758]),
        ("cashflow.subsidiary_income", 313, "Less: Net income of subsidiaries and affiliates 71,163 72,781 62,868", [71163, 72781, 62868]),
        ("cashflow.parent_loss", 313, "Parent company net loss (14,115) (14,310) (13,316)", [-14115, -14310, -13316]),
        ("cashflow.dividends", 313, "Cash dividends from subsidiaries and affiliates 50,000 37,000 61,000", [50000, 37000, 61000]),
        ("cashflow.other_operating", 313, "Other operating adjustments 8,583 (44,671) 9,412", [8583, -44671, 9412]),
        ("cashflow.operating", 313, "Net cash provided by/(used in) operating activities 44,468 (21,981) 57,096", [44468, -21981, 57096]),
        ("cashflow.investing", 313, "Net cash provided by/(used in) investing activities 34 21 (24,975)", [34, 21, -24975]),
        ("cashflow.financing", 313, "Net cash provided by/(used in) financing activities (44,512) 21,914 (32,122)", [-44512, 21914, -32122]),
        ("cashflow.change", 313, "Net increase/(decrease) in cash and due from banks and deposits with banking subsidiaries (10) (46) (1)", [-10, -46, -1]),
        ("cashflow.opening", 313, "Cash and due from banks and deposits with banking subsidiaries at the beginning of the year 9,800 9,846 9,847", [9800, 9846, 9847]),
        ("cashflow.closing", 313, "Cash and due from banks and deposits with banking subsidiaries at the end of the year(b) $ 9,790 $ 9,800 $ 9,846", [9790, 9800, 9846]),
        ("cashflow.interest_paid", 313, "Cash interest paid $ 12,399 $ 14,851 $ 13,742", [12399, 14851, 13742]),
    ]
    rows = []
    for key, page, phrase, values in specs:
        span = match_once(pages[page], phrase)
        row = {"id": key, "pdf_page": page, "printed_page": page - 2, "source_text": next(r["reading"] for r in manifest["pages"] if r["pdf_page"] == page), "values_usd_millions": dict(zip(["2025", "2024", "2023"][:len(values)], values)), **span}
        rows.append(row)
        ck("source row " + key, pages[page][span["start"]:span["end"]] == span["quote"] and hashlib.sha256(span["quote"].encode()).hexdigest() == span["span_sha256"])
    qualifiers = [
        ("cash includes time deposits", 313, "includes intercompany time deposits of $8.0 billion as of December 31, 2025, 2024 and 2023"),
        ("maturity schedule", 313, "long-term debt that contractually matures in 2026 through 2030 totaled $14.3 billion, $20.3 billion, $36.4 billion, $22.4 billion, and $23.6 billion, respectively"),
        ("parent guarantee cross reference", 313, "Refer to Notes 20 and 28 for information regarding the Parent Company’s guarantees of its subsidiaries’ obligations"),
        ("reimbursement tax qualification", 313, "includes taxes paid on behalf of certain of its subsidiaries that are subsequently reimbursed"),
        ("bank transfer restriction", 21, "JPMorgan Chase Bank, N.A. is subject to regulatory restrictions and requirements relating to the dividends that it can pay to the Parent Company"),
        ("IHC transfer restriction", 21, "the IHC is prohibited from paying dividends or extending credit to the Parent Company if certain capital or liquidity thresholds are breached"),
        ("net proceeds routing", 21, "The Parent Company must contribute to the IHC substantially all the net proceeds that it receives from securities issuances"),
    ]
    notes = []
    for label, page, phrase in qualifiers:
        span = match_once(pages[page], phrase)
        notes.append({"id": label, "pdf_page": page, "printed_page": page - 2, "source_text": next(r["reading"] for r in manifest["pages"] if r["pdf_page"] == page), **span})
        ck("qualifier " + label, pages[page][span["start"]:span["end"]] == span["quote"])

    V = {row["id"]: list(row["values_usd_millions"].values()) for row in rows}
    for i, year in enumerate(["2025", "2024", "2023"]):
        ck(year + " income before tax", V["income.total"][i] - V["income.expense"][i] == V["income.pretax"][i])
        ck(year + " reported net income", V["income.pretax"][i] + V["income.tax_benefit"][i] + V["income.equity_undistributed"][i] == V["income.net"][i])
        ck(year + " parent net loss bridge", V["income.net"][i] - V["cashflow.subsidiary_income"][i] == V["cashflow.parent_loss"][i])
        ck(year + " operating cash bridge", V["cashflow.parent_loss"][i] + V["cashflow.dividends"][i] + V["cashflow.other_operating"][i] == V["cashflow.operating"][i])
        ck(year + " change in cash bridge", V["cashflow.operating"][i] + V["cashflow.investing"][i] + V["cashflow.financing"][i] == V["cashflow.change"][i])
        ck(year + " closing cash bridge", V["cashflow.opening"][i] + V["cashflow.change"][i] == V["cashflow.closing"][i])
    ck("2025 balance cash matches cash flow", V["balance.cash"][0] + V["balance.bank_deposits"][0] == V["cashflow.closing"][0])
    ck("2024 balance cash matches cash flow", V["balance.cash"][1] + V["balance.bank_deposits"][1] == V["cashflow.closing"][1])
    ck("2025 income source split", V["cashflow.dividends"][0] + V["income.equity_undistributed"][0] == V["cashflow.subsidiary_income"][0])
    ck("2024 income source split", V["cashflow.dividends"][1] + V["income.equity_undistributed"][1] == V["cashflow.subsidiary_income"][1])
    ck("2023 split has one-million displayed residual", V["cashflow.subsidiary_income"][2] - V["cashflow.dividends"][2] - V["income.equity_undistributed"][2] == 1)
    ck("2025 assets equal liabilities plus equity", V["balance.assets"][0] == V["balance.liabilities"][0] + V["balance.equity"][0])
    ck("2024 assets equal liabilities plus equity", V["balance.assets"][1] == V["balance.liabilities"][1] + V["balance.equity"][1])
    ck("2025 cash is smaller than parent assets", V["cashflow.closing"][0] < V["balance.assets"][0])

    failed = [r["check"] for r in checks if not r["passed"]]
    if failed:
        print(json.dumps({"failed": failed}))
        raise SystemExit(1)
    ledger = {"source_manifest": str((OUT / "source-manifest.json").relative_to(ROOT)), "unit": "US$ millions as displayed; parent-only Note 33, years ended 2023–2025 and balance dates 2024–2025", "selected_rows": rows, "qualifiers": notes, "interpretation_boundary": "Reported parent-only accounting statements; no forward payment capacity, free transfer, current ASC or historical-byte admission"}
    (OUT / "source-ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
    (OUT / "checks.json").write_text(json.dumps({"checks": checks, "passed": len(checks), "failed": 0, "wall_seconds": time.monotonic() - START}, indent=2) + "\n")
    print(json.dumps({"rows": len(rows), "qualifiers": len(notes), "checks": len(checks), "failed": 0}))


if __name__ == "__main__":
    main()
