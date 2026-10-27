"""Bind the retained coverage resolver to the accepted fiscal successor."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
assert not (HERE/'verify_continuity.py').exists()
text=(ROOT/'data/accounting-master/source-history-reassessment-20261025/verify_continuity.py').read_text()
changes=[('retained-population-integration-20261025','fiscal-timeline-integration-20261025'),
         ('manuscript-retained-population-20261025','manuscript-fiscal-timeline-20261025'),
         ('9e068d276e5a7dfc29df05209ac86bcd3a28f9df760dc73959da511ff2c2599c','2c9e72249cbc28aadcb6ded520165b6ee86bcbff88adc634afc05740ee9ac8f9'),
         ("'candidate':'4.37'","'candidate':'4.39'")]
for old,new in changes:
    assert old in text,old
    text=text.replace(old,new)
compile(text,'verify_continuity.py','exec');(HERE/'verify_continuity.py').write_text(text)
