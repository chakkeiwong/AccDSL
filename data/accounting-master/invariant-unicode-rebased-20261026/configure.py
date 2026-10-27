from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE.parent/'invariant-unicode-integration-20261026/integrate.py').read_text()
pairs=[
('Preserved Version 5.12 nested invariant source correction','Preserved Version 5.13 correction on concurrent literature baseline'),
("SOURCE = ROOT / 'docs/design/proposal/manuscript-complete-claims-20261026'","SOURCE = ROOT / 'docs/design/proposal/manuscript-literature-methods-v512-20261026'"),
("TARGET = ROOT / 'docs/design/proposal/manuscript-invariant-unicode-20261026'","TARGET = ROOT / 'docs/design/proposal/manuscript-invariant-unicode-v513-20261026'"),
('05ff78c88e9b3c1a1ec3cc87bc5d0df6b718ca1fd8a206c0003b65928e4b2a90','87da6f2a6bd7c56ea7718202047b9722b3de0b4e22e7f3aa4638d0a7fcb64622'),
("old='Version 5.11 (proposal candidate)'","old='Version 5.12 (proposal candidate)'"),
("return text.replace(old,'Version 5.12 (proposal candidate)')","return text.replace(old,'Version 5.13 (proposal candidate)')"),
('assert len(sources) == 222','assert len(sources) == 234'),
("'candidate':'5.12'","'candidate':'5.13'"),
("assert 'Version 5.12' in doc[0].get_text()","assert 'Version 5.13' in doc[0].get_text()"),
("version='5.12'","version='5.13'")]
for old,new in pairs:
    assert old in text,old
    text=text.replace(old,new)
assert not (HERE/'integrate.py').exists()
(HERE/'integrate.py').write_text(text)
print('Configured combined Version 5.13 preserving literature Version 5.12')
