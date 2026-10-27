"""Prepare record/replay from the dependency-capturing accepted harness."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/insurance-loss-book-20261025/verify.py').read_text()
changes=[('import insurance_loss_book_v1 as bridge','import insurance_fiscal_book_v1 as bridge'),
 ("patterns=['test_insurance_loss_book_v1.py','test_company_book_transition_v1.py',\n              'test_company_method_clock_v1.py','test_company_book_reports_v1.py']",
  "patterns=['test_insurance_fiscal_book_v1.py','test_insurance_loss_book_v1.py',\n              'test_company_book_carry_v1.py','test_declared_company_program_v1.py','test_declared_collection_clock_v1.py']"),
 ('for case in bridge.CASES:','for case in bridge.base.CASES:'),
 ("for row in json.loads((ROOT/(bridge.NATIVE+'input-lock-v2.json')).read_text())['files']:lock(row['path'],row['sha256'])",
  "for name,expected in json.loads((ROOT/'data/accounting-master/insurance-loss-book-20261025/source-lock.json').read_text()).items():lock(name,expected)"),
 ('accounting-insurance-loss-book-20261025.md','accounting-insurance-fiscal-boundary-20261025.md'),
 ("'reports_per_case':2","'native_date_reports_per_case':2,'fiscal_carries_per_case':3"),
 ('Exact retained insurer proposals; no domain/source or fiscal-completeness admission',
  'Exact retained insurer journals across explicit calendar-year carries; no event completeness or source admission'),
 ('insurance-loss-book-20261025/verify.py --record','insurance-fiscal-book-20261025/verify.py --record'),
 ('Two retained InsuranceOrigins/1 cases, two charts and complement variants','Two retained insurer cases, two charts, complement variants and explicit calendar-year carries')]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
text=text.replace("for pattern in patterns:lock(ROOT/'tests'/pattern)",
 "for pattern in patterns:lock(ROOT/'tests'/pattern)\n    for name in ['prepare_verifier.py','discriminator.py','naive-carry.json','attempt-01/insurance_fiscal_book_v1.py','attempt-01/examples.py','attempt-01/probe.log']:lock(HERE/name)")
compile(text,'verify.py','exec');assert not (HERE/'verify.py').exists();(HERE/'verify.py').write_text(text)
print('Prepared fiscal record/replay verifier')
