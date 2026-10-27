"""Create the successor integration writer from the preserved bounded template."""
from pathlib import Path
import re
H=Path(__file__).resolve().parent
s=(H.parent/'viability-integration-20261027/integrate.py').read_text()
changes={
 'manuscript-actor-existence-v544-20261027':'manuscript-viability-v545-20261027',
 'manuscript-viability-v545-20261027':'manuscript-coupon-continuation-v546-20261027',
 '6b7cccb558f66077f161663657a417cb4422fb7be39a3f9a65fff8b370ab505b':'c441c3d2307e82c2c4ced5f25cad1c1216daf00df42496ebec6ccca220a7a7a6',
 '5283b054c62cb522904b978fc7cfa801674acab11acf2b9ef3ec28df6c0200b6':'61cac1727c12ca519620ccd7feffd0bcf358b43e8892bf4681d3604d74c93cde',
 'Version 5.44':'Version 5.45','Version 5.45':'Version 5.46',
 "startswith('5.44;')":"startswith('5.45;')",
 'simulation/viability':'simulation/coupon-continuation',
 "'viability.tex'":"'coupon-continuation.tex'",
 'accounting-viability-integration-20261027.md':'accounting-coupon-continuation-integration-20261027.md',
 "['policy-failure-diagnosis-20261027','financing-viability-boundary-20261027']":"['refused-payment-reporting-20261027','coupon-carry-20261027','coupon-partial-settlement-20261027']",
 "[('policy-failure-diagnosis-20261027','attempt-01'),('financing-viability-boundary-20261027','attempt-01')]":"[('refused-payment-reporting-20261027','attempt-02'),('coupon-carry-20261027','attempt-01'),('coupon-partial-settlement-20261027','attempt-01')]",
 "[('viability','The receipt-6 contradiction contains an economic impossibility','rather than remove it from later statements.',['receipt','continuous','committed','obligation','49','45'])]":"[('coupon-continuation','The refused second payment leaves a complete financial state to report.','without inventing its recovery.',['85/16','43/8','refusal','partial2','January','year-end'])]",
}
for key in changes: assert key in s,key
s=re.sub('|'.join(re.escape(k) for k in sorted(changes,key=len,reverse=True)),lambda m:changes[m[0]],s)
s=s.replace('Protected acquisition design integration','Protected coupon continuation integration')
assert not (H/'integrate.py').exists()
(H/'integrate.py').write_text(s)
print('Prepared version 5.46 integration writer')
