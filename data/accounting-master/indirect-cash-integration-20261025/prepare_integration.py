"""Create a narrowly adapted additive integration verifier; no build here."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
source = ROOT / 'data/accounting-master/term-authoring-integration-20261025/integrate.py'
text = source.read_text()
replacements = [
    ('Version 4.25', 'Version 4.26'),
    ('Version 4.24', 'Version 4.25'),
    ("'4.25'", "'4.26'"),
    ('manuscript-receivable-terms-20261025', 'manuscript-term-authoring-20261025'),
    ("TARGET = ROOT / 'docs/design/proposal/manuscript-term-authoring-20261025'",
     "TARGET = ROOT / 'docs/design/proposal/manuscript-indirect-cash-20261025'"),
    ('dbbf73db5ef1d2d047e163d418c21b85ef0b993818b99eb7cad87b86b2cb27e5',
     'd35590f4ea484616340fbcaf30eca1b69807f443d3a82f0f75b365819f955f8e'),
    ('A disclosed receivable may have an unidentified population.',
     'Distinguish collecting a claim from assessing whether it is overdue.'),
    ('authoring-addition.tex', 'indirect-addition.tex'),
    ('accdsl-term-authoring-integration-20261025-tex-cache',
     'accdsl-indirect-cash-integration-20261025-tex-cache'),
    ('Term commands retain the meaning of the typed operations.',
     'Explain operating cash from profit under explicit classifications.'),
    ('Malformed syntax, missing or altered imports',
     'This identity alone leaves the nonoperating part of profit'),
    ('This correspondence makes the authoring boundary',
     'Algebraically consistent decompositions can nevertheless'),
    ('Additive matched term-authoring passage; no whole acceptance',
     'Additive conditional indirect-cash explanation; no whole acceptance'),
]
for old, new in replacements:
    assert old in text, old
    text = text.replace(old, new)
anchor = "    if mode == 'prepare':\n"
guard = """        replay = json.loads((ROOT / 'data/accounting-master/declared-indirect-profit-components-20261025/replay-observation.json').read_text())
        assert replay['passed'] is True and replay['cases'] == 20
"""
text = text.replace(anchor, anchor + guard)
anchor = "        print(json.dumps({'prepared': True, 'sources': len(source_hashes)})); return"
snapshot = """        for name in source_hashes:
            saved = HERE / 'baseline-source' / name
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes((SOURCE / name).read_bytes())
        (HERE / 'baseline.pdf').write_bytes((SOURCE / 'accounting-product-proposal.pdf').read_bytes())
"""
text = text.replace(anchor, snapshot + anchor)
anchor = "        assert sha(source) == old_sha, 'predecessor_changed:' + name\n"
text = text.replace(anchor, anchor + "        assert sha(HERE / 'baseline-source' / name) == old_sha, 'snapshot_changed:' + name\n")
target = HERE / 'integrate.py'
assert not target.exists()
target.write_text(text)
print('Prepared additive verifier; candidate creation still requires accepted replay.')
