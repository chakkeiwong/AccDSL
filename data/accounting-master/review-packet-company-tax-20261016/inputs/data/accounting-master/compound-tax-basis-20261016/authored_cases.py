"""Expected issue-date outcomes and refusal cases, before calculator."""
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE=ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'

BASES=[
  dict(id='combined-proceeds-tax-base',gross_proceeds='100',liability='92',equity='8',tax_base='100',rate='1/4',
       expected=dict(dtl='2',equity_after_tax='6',current_tax='0',tax_expense='0',assets='100',liabilities='94',equity_total='6')),
  dict(id='matching-liability-tax-base',gross_proceeds='100',liability='92',equity='8',tax_base='92',rate='1/4',
       expected=dict(dtl='0',equity_after_tax='8',current_tax='0',tax_expense='0',assets='100',liabilities='92',equity_total='8')),
  dict(id='zero-tax-rate',gross_proceeds='100',liability='92',equity='8',tax_base='100',rate='0',
       expected=dict(dtl='0',equity_after_tax='8',current_tax='0',tax_expense='0',assets='100',liabilities='92',equity_total='8')),
  dict(id='different-valid-split',gross_proceeds='100',liability='90',equity='10',tax_base='100',rate='1/5',
       expected=dict(dtl='2',equity_after_tax='8',current_tax='0',tax_expense='0',assets='100',liabilities='92',equity_total='8'))]

ADVERSE=[
 ('missing-tax-base','unresolved','tax_base_missing',dict(tax_base=None)),
 ('missing-rate','unresolved','tax_rate_missing',dict(rate=None)),
 ('missing-equity-allocation','unresolved','equity_component_missing',dict(equity=None)),
 ('negative-tax-base','rejected','invalid_tax_base',dict(tax_base='-1')),
 ('rate-above-profile','unsupported','tax_rate_outside_profile',dict(rate='5/4')),
 ('negative-tax-rate','rejected','invalid_tax_rate',dict(rate='-1/4')),
 ('excess-component-total','rejected','component_total_mismatch',dict(liability='93')),
 ('insufficient-component-total','rejected','component_total_mismatch',dict(liability='90')),
 ('intermediate-tax-base','unsupported','tax_base_outside_subset',dict(tax_base='95')),
 ('negative-equity','rejected','invalid_component',dict(equity='-8')),
 ('decimal-rate','rejected','malformed_rational',dict(rate='0.25')),
 ('unreduced-tax-base','rejected','malformed_rational',dict(tax_base='200/2'))]

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()

def main():
 source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
 cases=dict(wire='CompoundTaxBasis/1',status='issue_date_only',source=dict(path=str(SOURCE.relative_to(ROOT)),sha256=source_hash,anchors=['IAS12.7-8','IAS12.23','IAS12.58','IAS12.61A']),bases=BASES,adverse=[dict(id=n,expected_status=s,expected_code=c,changes=x) for n,s,c,x in ADVERSE],
  synthetic='tax base100 and rate1/4 are explicit alternative jurisdictional premises',scope='no subsequent schedule, current-law or EPS conclusion')
 (OUT/'premises.json').write_text(json.dumps(cases,indent=2)+'\n')
 print(json.dumps(dict(bases=len(BASES),adverse=len(ADVERSE),source_sha256=source_hash)))

if __name__=='__main__':main()
