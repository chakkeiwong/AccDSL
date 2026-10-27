from pathlib import Path
H = Path(__file__).resolve().parent
s = (H.parent / "joint-frontier-integration-20261027/integrate.py").read_text()
for old, new in [
    ("manuscript-joint-frontier-v541-20261027", "manuscript-joint-domain-v542-20261027"),
    ("manuscript-joint-policy-v540-20261027", "manuscript-joint-frontier-v541-20261027"),
    ("5c2e0673346966f8e960426821cbc6cf3142044a22b51f29d8bc0d7cb3897c8c", "2bd6d07569d451a8aa0af276af56a5713d1985f18b19849f4af9723471307783"),
    ("cc40dd0d06ca8d2767f244af2b2aafd80874ee8f7a68500b81c269eb178f3937", "39beaf6e83e3b92fac27700c89a39f2e2e517536ab6241170e71c70725abdcbd"),
    ("joint-frontier.tex", "joint-domain.tex"),
    ("simulation/joint-frontier", "simulation/joint-domain"),
    ("t.count('Version 5.40')", "t.count('Version 5.41')"),
    ("t.replace('Version 5.40','Version 5.41')", "t.replace('Version 5.41','Version 5.42')"),
    ("startswith('5.40;')", "startswith('5.41;')"),
    ("['joint-temporal-frontier-20261027']", "['joint-domain-transport-20261027','joint-observation-refinement-20261027']"),
    ("[('joint-temporal-frontier-20261027','attempt-02'),('joint-temporal-frontier-20261027','attempt-03')]", "[('joint-domain-transport-20261027','attempt-01'),('joint-observation-refinement-20261027','attempt-01')]"),
    ("accounting-joint-frontier-integration-20261027.md", "accounting-joint-domain-integration-20261027.md"),
    ("'Version 5.41' in texts[0]", "'Version 5.42' in texts[0]"),
    ("('joint_frontier','Suppose the search stops after checking some','admitting company evidence require further work.',['pending','fixed','refusal','33','Inconsistent','crash'])", "('joint_domain','The fixed-domain result raises a practical question','which economic history continues afterward.',['refined','erasure','2,048','unassessed','bijection','financial'])"),
]:
    assert old in s, old
    s = s.replace(old, new)
target = H / "integrate.py"
assert not target.exists()
target.write_text(s)
print("Prepared bounded integration source for 5.42")
