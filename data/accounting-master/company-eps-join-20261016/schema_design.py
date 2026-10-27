"""Closed record shapes; semantic validity is checked separately."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

OUT = Path(__file__).resolve().parent
EPS_SCHEMA = json.loads((OUT.parent / "continuation-integrity-eps-20261016/ordered-eps/record-schemas.json").read_text())
PREMISES = json.loads((OUT / "premises.json").read_text())
Q = {"type":"string", "pattern":"^(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?$"}
TEXT = {"type":"string", "minLength":1}
HASH = {"type":"string", "pattern":"^[0-9a-f]{64}$"}
DATE = {"type":"string", "format":"date"}


def obj(fields):
    return {"type":"object", "properties":fields,"required":list(fields),"additionalProperties":False}


def enum(*values):
    return {"enum":list(values)}


def arr(item):
    return {"type":"array", "items":item}


def nullable(schema):
    return {"anyOf":[schema,{"type":"null"}]}


QUANTITIES = {"ordinary_opening_shares","proceeds","coupon","principal","period_rate","conversion_shares",
              "rate","initial_liability_tax_base","initial_equity_fiscal_allocation"}
DATES = {"issue_date","maturity_date","report_start","report_end_exclusive"}


def premise_shape(node, key=""):
    if isinstance(node, dict):
        return obj({k:premise_shape(v,k) for k,v in node.items()})
    if isinstance(node, bool):
        return nullable({"type":"boolean"})
    return Q if key in QUANTITIES else DATE if key in DATES else TEXT


SUPPORT = obj(dict(path=TEXT,sha256=HASH,anchor=TEXT))
REQUEST = obj(dict(wire=enum("CompanyEPSJoin/1"),operation=enum("report"),world=TEXT,
    base_packet=SUPPORT,premises=premise_shape(PREMISES),eps=EPS_SCHEMA["$defs"]["Request"]))
BOOK_KEYS = ["cash","inventory","ppe","recovery_asset","investment","dta","dtl","refund_liability","debt","receivable","payable",
    "capital","retained","original_equity","revenue","cogs","selling_expense","wages","depreciation","finance_expense","current_tax","deferred_tax",
    "new_debt","new_conversion_equity"]
BOOKS = obj({owner:obj({key:Q for key in BOOK_KEYS}) for owner in ("P","S")})
FINANCIAL_KEYS = ["group_profit","parent_profit","nci_profit","cash","assets","liabilities","equity","parent_equity","nci_equity",
    "current_tax","deferred_tax","pretax","parent_legal_cash","parent_legal_profit","parent_legal_equity",
    "operating_receipts","operating_payments","investing_receipts","investing_payments","financing_receipts","financing_payments",
    "interest_paid","tax_paid","net_cash","actual_ending_shares","basic_numerator","basic_denominator",
    "potential_numerator_increment","potential_share_increment","basic_eps"]
COMPANY = obj(dict(world=enum("conversion","redemption"), financials=obj({key:Q for key in FINANCIAL_KEYS}),
    closing_books=BOOKS,timeline=arr(obj(dict(id=TEXT,date=DATE,journal=BOOKS,new_debt_after=Q,parent_cash=Q))),
    flows=arr(obj(dict(entity=enum("P","S"),activity=enum("operating","investing","financing"),amount=Q,origin=TEXT,date=DATE))),
    daily_shares=arr(obj(dict(date=DATE,actual=Q,potential=Q))),issue_debt=Q,issue_equity=Q,liability_after_coupon=Q,external_equity_additions=Q))
RESULT = obj(dict(wire=enum("CompanyEPSJoin/1"),request_sha256=HASH,
    status=enum("conditional_complete","unresolved","unsupported","rejected","blocked"),
    company=nullable(COMPANY),eps=nullable(EPS_SCHEMA["$defs"]["Result"]),issues=arr(TEXT),
    mutations={"type":"array","maxItems":0},acceptance=enum("conditional_documentary_only")))
SCHEMA = {"$schema":"https://json-schema.org/draft/2020-12/schema","$defs":{"Request":REQUEST,"Result":RESULT},
          "oneOf":[{"$ref":"#/$defs/Request"},{"$ref":"#/$defs/Result"}]}
REQUEST_VALIDATOR = Draft202012Validator(REQUEST,format_checker=FormatChecker())
RESULT_VALIDATOR = Draft202012Validator(RESULT,format_checker=FormatChecker())


if __name__ == "__main__":
    (OUT/"record-schemas.json").write_text(json.dumps(SCHEMA,indent=2)+"\n")
