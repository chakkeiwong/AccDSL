from pathlib import Path
import re
H = Path(__file__).resolve().parent
s = (H.parent / 'coupon-resume-integration-20261027/integrate.py').read_text()
changes = {
    'manuscript-coupon-scope-v547-20261027': 'manuscript-coupon-resume-v548-20261027',
    'manuscript-coupon-resume-v548-20261027': 'manuscript-credit-claim-v549-20261027',
    '85256a6ecf41941fadd638764addd2610ff21aead4ca4511d178935a0f455769': 'c91cfa88237b56a86ad59df541c3330ea7699489ce0e8ccc27a4a0603d249fa3',
    '94e50707fd16d9d43d97e83842dc437536c557e30f2d70ad9e256507607cadf9': 'aa39fdccc65342f3c0caae3e7828f4a77a09abe87ddd162f3e26104f66d6081c',
    '5.47': '5.48', '5.48': '5.49',
    'coupon-resume.tex': 'credit-claim.tex', 'simulation/coupon-resume': 'simulation/credit-claim',
    'simulation/17-continuous-methods.tex': 'simulation/25-interactions.tex',
    'coupon-program-resume-20261027': 'credit-claim-continuity-20261027',
    'accounting-coupon-resume-integration-20261027.md': 'accounting-credit-claim-integration-20261027.md',
}
s = re.sub('|'.join(re.escape(k) for k in sorted(changes, key=len, reverse=True)), lambda m: changes[m[0]], s)
s = s.replace("[('credit-claim-continuity-20261027','attempt-02'),('credit-claim-continuity-20261027','audit-attempt-01')]", "[('credit-claim-continuity-20261027','attempt-01')]")
a = s.index("[('coupon-resume','A selected"); b = s.index(']:', a)
s = s[:a] + "[('credit-claim','Financial closure leaves a separate question about the history of scheduled','the earlier history while leaving forgiveness and later recovery unassessed.',['nominal','57','Twenty-five','prepayment','forgiveness'])]" + s[b+1:]
p = H / 'integrate.py'; assert not p.exists(); p.write_text(s)
print('Prepared successor integration writer')
