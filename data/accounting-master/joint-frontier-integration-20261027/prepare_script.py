"""Adapt the established bounded document integration to the checked frontier."""
from pathlib import Path
H = Path(__file__).resolve().parent
old = H.parent / "joint-policy-integration-20261027/integrate.py"
text = old.read_text()
replacements = [
    ("manuscript-policy-refinement-v539-20261027", "manuscript-joint-policy-v540-20261027"),
    ("manuscript-joint-policy-v540-20261027'\nPDFS", "manuscript-joint-frontier-v541-20261027'\nPDFS"),
    ("26b999910aeda9f934ffe75f8ec5d96b2c64cb1956655e2483c3c87971015318", "5c2e0673346966f8e960426821cbc6cf3142044a22b51f29d8bc0d7cb3897c8c"),
    ("5f5a5fb6b1a6711e0b8e9582fee3a5b303ce4f897d4a19d321c6c1ed2ddb4d55", "cc40dd0d06ca8d2767f244af2b2aafd80874ee8f7a68500b81c269eb178f3937"),
    ("joint-stage.tex", "joint-frontier.tex"),
    ("simulation/joint-stage", "simulation/joint-frontier"),
    ("t.count('Version 5.39')", "t.count('Version 5.40')"),
    ("t.replace('Version 5.39','Version 5.40')", "t.replace('Version 5.40','Version 5.41')"),
    ("startswith('5.39;')", "startswith('5.40;')"),
    ("['two-decision-source-views-20261027','joint-stage-policy-20261027']", "['joint-temporal-frontier-20261027']"),
    ("[('two-decision-source-views-20261027','attempt-01'),('joint-stage-policy-20261027','attempt-01')]", "[('joint-temporal-frontier-20261027','attempt-02'),('joint-temporal-frontier-20261027','attempt-03')]"),
    ("accounting-joint-policy-integration-20261027.md", "accounting-joint-frontier-integration-20261027.md"),
    ("'Version 5.40' in texts[0]", "'Version 5.41' in texts[0]"),
    ("('joint','A manager can make the first payment before receiving a correction','admitting actual actor information remain separate tasks.',['Cartesian','15','12','unresolved','correction','second'])", "('joint_frontier','Suppose the search stops after checking some','admitting company evidence require further work.',['pending','fixed','refusal','33','Inconsistent','crash'])"),
]
for before, after in replacements:
    assert before in text, before
    text = text.replace(before, after)
target = H / "integrate.py"
assert not target.exists()
target.write_text(text)
print("Created bounded 5.41 integration script")
