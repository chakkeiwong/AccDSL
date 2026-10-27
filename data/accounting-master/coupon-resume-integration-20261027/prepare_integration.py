from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'coupon-scope-integration-20261027/integrate.py').read_text()
changes={
 'manuscript-coupon-continuation-v546-20261027':'manuscript-coupon-scope-v547-20261027',
 'manuscript-coupon-scope-v547-20261027':'manuscript-coupon-resume-v548-20261027',
 '526c347b98545f7865211f5b510b0429b4d9761a097ac5bdfc5f02e139797e93':'85256a6ecf41941fadd638764addd2610ff21aead4ca4511d178935a0f455769',
 '5db0146d165d1e2124be8cf9fa091c4bf6fe7b08fd95db81e752c7f135864b89':'94e50707fd16d9d43d97e83842dc437536c557e30f2d70ad9e256507607cadf9',
 'Version 5.46':'Version 5.47','Version 5.47':'Version 5.48',
 "startswith('5.46;')":"startswith('5.47;')",
 'simulation/coupon-scope':'simulation/coupon-resume',
 "'coupon-scope.tex'":"'coupon-resume.tex'",
 'accounting-coupon-scope-integration-20261027.md':'accounting-coupon-resume-integration-20261027.md',
 "['coupon-schedule-invariant-20261027','coupon-continuation-scope-20261027']":"['coupon-program-resume-20261027']",
 "[('coupon-schedule-invariant-20261027','attempt-01'),('coupon-continuation-scope-20261027','attempt-01')]":"[('coupon-program-resume-20261027','attempt-02'),('coupon-program-resume-20261027','audit-attempt-01')]",
 "[('coupon-scope','The residual claim is a property of the cash-only payment rule','discarding prior flows.',['induction','January','midperiod','identities','64','65'])]":"[('coupon-resume','A selected same-period runner now extends the checked coupon prefix','erasing the company’s earlier history.',['checkpoint','cursor','82,883','82,882','registry','64'])]",
}
for k in changes:assert k in s,k
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
assert not (H/'integrate.py').exists();(H/'integrate.py').write_text(s)
print('Prepared version 5.48 integration writer')
