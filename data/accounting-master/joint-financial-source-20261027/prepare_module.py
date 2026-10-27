"""Create a separately identified source selector; preserve the fixed-head baseline."""
from pathlib import Path
H = Path(__file__).resolve().parent
s = (H.parent / "two-decision-source-views-20261027/joint.py").read_text()
changes = [
    ("JointTwoDecisionSourceViews/1", "JointRevisableFinancialSourceViews/1"),
    (" financial=[r for r in old['registry'].values() if r.get('slot')=='financial_family']" + chr(10) + " need(len(financial)==1 and financial[0]['disposition']=='assertion' and financial[0]['supersedes'] is None,'fixed_single_financial_head')" + chr(10), ""),
    ("joint_same_clock_source_views_no_policy_binding", "joint_revisable_financial_source_views_no_policy_binding"),
    ("scope='joint_revisable_financial_source_views_no_policy_binding')", "scope='joint_revisable_financial_source_views_no_policy_binding',financial_policy_binding='not_assessed_source_selection_only')"),
    ("'method_identity','scope','status'", "'method_identity','scope','financial_policy_binding','status'"),
    ("need(result['scope']=='joint_revisable_financial_source_views_no_policy_binding','joint_scope')", "need(result['scope']=='joint_revisable_financial_source_views_no_policy_binding','joint_scope');need(result['financial_policy_binding']=='not_assessed_source_selection_only','no_policy_binding')"),
]
for old, new in changes:
    assert old in s, old
    s = s.replace(old, new)
target = H / "joint.py"
assert not target.exists()
target.write_text(s)
print("Created separately identified financial-source selector")
