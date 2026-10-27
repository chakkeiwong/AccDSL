"""Reuse read-only continuity algorithm for the current protected release."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
assert not (HERE/'verify_continuity.py').exists()
text=(ROOT/'data/accounting-master/simulator-post-sector-reassessment-20261025/verify_continuity.py').read_text()
for a,b in [
 ('credit-linked-book-integration-20261025','retained-population-integration-20261025'),
 ('manuscript-credit-linked-book-20261025','manuscript-retained-population-20261025'),
 ('8b37990bbc97416916ae9874156ecdb4e2a286ba6d6d7cfe70e26c3fd221a878','9e068d276e5a7dfc29df05209ac86bcd3a28f9df760dc73959da511ff2c2599c'),
 ("'candidate':'4.32'","'candidate':'4.37'")]:
    assert a in text,a;text=text.replace(a,b)
(HERE/'verify_continuity.py').write_text(text)
