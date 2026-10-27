from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'coupon-continuation-integration-20261027/integrate.py').read_text()
changes={
 'manuscript-viability-v545-20261027':'manuscript-coupon-continuation-v546-20261027',
 'manuscript-coupon-continuation-v546-20261027':'manuscript-coupon-scope-v547-20261027',
 'c441c3d2307e82c2c4ced5f25cad1c1216daf00df42496ebec6ccca220a7a7a6':'526c347b98545f7865211f5b510b0429b4d9761a097ac5bdfc5f02e139797e93',
 '61cac1727c12ca519620ccd7feffd0bcf358b43e8892bf4681d3604d74c93cde':'5db0146d165d1e2124be8cf9fa091c4bf6fe7b08fd95db81e752c7f135864b89',
 'Version 5.45':'Version 5.46','Version 5.46':'Version 5.47',
 "startswith('5.45;')":"startswith('5.46;')",
 'simulation/coupon-continuation':'simulation/coupon-scope',
 "'coupon-continuation.tex'":"'coupon-scope.tex'",
 'accounting-coupon-continuation-integration-20261027.md':'accounting-coupon-scope-integration-20261027.md',
 "['refused-payment-reporting-20261027','coupon-carry-20261027','coupon-partial-settlement-20261027']":"['coupon-schedule-invariant-20261027','coupon-continuation-scope-20261027']",
 "[('refused-payment-reporting-20261027','attempt-02'),('coupon-carry-20261027','attempt-01'),('coupon-partial-settlement-20261027','attempt-01')]":"[('coupon-schedule-invariant-20261027','attempt-01'),('coupon-continuation-scope-20261027','attempt-01')]",
 "[('coupon-continuation','The refused second payment leaves a complete financial state to report.','without inventing its recovery.',['85/16','43/8','refusal','partial2','January','year-end'])]":"[('coupon-scope','The residual claim is a property of the cash-only payment rule','discarding prior flows.',['induction','January','midperiod','identities','64','65'])]",
}
for k in changes:assert k in s,k
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
assert not (H/'integrate.py').exists();(H/'integrate.py').write_text(s)
print('Prepared version 5.47 integration writer')
