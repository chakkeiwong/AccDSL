"""Exact authored interaction cases; not the production company runtime."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib, json, platform, sys, time

start = time.monotonic()
base = Path(__file__).resolve().parent
rows = []
def encode(value):
    if isinstance(value, F): return str(value)
    if isinstance(value, dict): return {str(k): encode(v) for k,v in value.items()}
    if isinstance(value, (list, tuple)): return [encode(v) for v in value]
    return value
def check(name, actual, expected, meaning):
    passed = actual == expected
    rows.append(dict(id=name, actual=encode(actual), expected=encode(expected), passed=passed, meaning=meaning))
    assert passed, (name, actual, expected)

# I1. Equal current reports, a correction of a contract note, and actor knowledge.
# Currency units at one date; both loans have face 100 and observed coupon 5.
# A declared +2 percentage-point reset makes the floating coupon 7.
types = ('fixed', 'floating')
interest = {'fixed': F(5), 'floating': F(7)}
opening_cash = F(6)
# An immediately effective hedge costs 1 and caps the floating coupon at 5.
# A fixed loan receives no cash-flow benefit. No fair-price claim about the hedge.
def cash_after(kind, hedge):
    payment = F(5) if kind == 'floating' and hedge else interest[kind]
    return opening_cash - F(hedge) - payment

def policies(reveals_type):
    signals = types if reveals_type else ('unknown',)
    return [dict(zip(signals, actions)) for actions in product((0,1), repeat=len(signals))]
def results(policy, reveals_type):
    return {kind: cash_after(kind, policy[kind if reveals_type else 'unknown']) for kind in types}

check('I1_equal_observed_reports', [(100,5),(100,5)], [(100,5)]*2,
      'Current balance/coupon do not distinguish the persistent terms.')
check('I1_shock_separates_types', [cash_after(k,0) for k in types], [F(1),F(-1)],
      'The declared reset exposes a difference hidden by reported amounts.')
informed = {'fixed':0, 'floating':1}
check('I1_type_conditioned_cash', results(informed,True), {'fixed':F(1),'floating':F(0)},
      'The informed policy avoids a shortfall and preserves cash in the fixed type.')
uninformed_safe = [p for p in policies(False) if all(c>=0 for c in results(p,False).values())]
check('I1_uninformed_safe_policy', uninformed_safe, [{'unknown':1}],
      'Without the notice, hedge in both types is the only robustly safe admitted policy.')
check('I1_uninformed_safe_cash', results(uninformed_safe[0],False), {'fixed':F(0),'floating':F(0)},
      'Losing actor information changes attainable type-conditional outcomes.')
check('I1_anticipative_policy_rejected', informed in policies(False), False,
      'A simulator may know type without revealing it to management.')
old_evidence = {'revision':'v1', 'admitted_types':('fixed',)}
corrected_evidence = {'revision':'v2', 'admitted_types':types}
old_range = sorted({cash_after(k,0) for k in old_evidence['admitted_types']})
new_range = sorted({cash_after(k,0) for k in corrected_evidence['admitted_types']})
check('I1_correction_reopens_history', [old_range,new_range], [[F(1)],[F(-1),F(1)]],
      'Withdrawal of an unsupported fixed-rate classification can enlarge the family.')
check('I1_old_result_not_reusable', old_range==new_range, False,
      'A cached range for a superseded evidence family is wrong for the corrected family.')
def certificate(evidence, reveals_type):
    return (evidence['revision'],evidence['admitted_types'],reveals_type,'reset+2pp','terminal_cash','hedge0or1')
check('I1_revision_invalidates_certificate',certificate(old_evidence,False)==certificate(corrected_evidence,False),False,
      'Evidence revisions are among the dependencies of a sharing certificate.')
check('I1_information_invalidates_certificate',certificate(corrected_evidence,False)==certificate(corrected_evidence,True),False,
      'Actor information is a separate dependency even when the reports are unchanged.')

# I2. Rate reset -> coupon -> liquidity covenant -> restricted financing -> dilution.
# Opening cash 16, loan face 100, coupon fixed 5 or floating 7 after reset;
# operating cash payment 6. Covenant tests cash >=5 AFTER these payments,
# BEFORE financing. Breach blocks new borrowing but permits an equity cure.
# Required closing cash is 8. Maximum candidate debt face is 5.
# Exogenous conditional lender inputs: Q(solvent)=4/5, recovery=2, gross rf=21/20.
# Equity cure fee is 1, economic pre-issue equity value20, old share count100.
# Fractional common shares allowed; legal requirements and endogenous price
# feedback are deliberately outside this one-period conditional stress.
def financing_path(kind):
    pre_financing = F(16) - interest[kind] - F(6)
    breach = pre_financing < F(5)
    need = F(8) - pre_financing
    face, p, recovery, rf = F(5),F(4,5),F(2),F(21,20)
    debt_proceeds = (p*face+(1-p)*recovery)/rf
    if not breach and debt_proceeds >= need:
        issue_face = face * need/debt_proceeds
        # Same quoted per-face price, used only as a declared conditional input.
        return dict(cash_before=pre_financing, breach=False, debt_allowed=True,
                    funding_need=need, max_debt_proceeds=debt_proceeds,
                    issue_face=issue_face, debt_cash=need, equity_gross=F(0),
                    fee=F(0),new_fraction=F(0),new_shares=F(0),
                    closing_cash=pre_financing+need)
    fee, pre_value, old_shares = F(1),F(20),F(100)
    gross=need+fee
    post_value=pre_value+gross-fee
    price=(pre_value-fee)/old_shares
    new_shares=gross/price
    return dict(cash_before=pre_financing,breach=breach,debt_allowed=not breach,
                funding_need=need,max_debt_proceeds=debt_proceeds,issue_face=F(0),
                debt_cash=F(0),equity_gross=gross,fee=fee,
                new_fraction=gross/post_value,new_shares=new_shares,
                post_value=post_value,old_value=(1-gross/post_value)*post_value,
                closing_cash=pre_financing+gross-fee)
paths={kind:financing_path(kind) for kind in types}
fixed,floating=paths['fixed'],paths['floating']
check('I2_coupon_to_covenant',[fixed['cash_before'],floating['cash_before']],[F(5),F(3)],
      'Cash is tested after interest and operations, before any permitted cure.')
# The fixed type meets the threshold; the reset triggers the floating breach.
check('I2_covenant_blocks_debt',[fixed['debt_allowed'],floating['debt_allowed']],[True,False],
      'A financing policy cannot use debt barred by the stated covenant.')
check('I2_price_below_face',fixed['max_debt_proceeds'],F(88,21),
      'Expected payment22/5 discounted at21/20 gives proceeds88/21, not face5.')
check('I2_floating_face_plug_fails',floating['max_debt_proceeds']>=floating['funding_need'],False,
      'Even an improper borrowing override would not fill the five-unit floating gap.')
check('I2_gross_equity_includes_fee',[fixed['equity_gross'],floating['equity_gross']],[F(0),F(6)],
      'Gross subscriptions must fund the cash shortfall and issuance fee.')
check('I2_closing_cash',[fixed['closing_cash'],floating['closing_cash']],[F(8),F(8)],
      'Permitted debt in the fixed type and equity in the floating type restore cash8.')
check('I2_dilution_differs',[fixed['new_fraction'],floating['new_fraction']],[F(0),F(6,25)],
      'Matching closing cash does not make the ownership outcomes equivalent.')
check('I2_old_value_fee',floating['old_value'],F(19),
      'Under this fair-price convention the incumbents bear the one-unit issue cost.')
check('I2_share_fraction',[p['new_shares']/(100+p['new_shares']) for p in paths.values()],
      [F(0),F(6,25)],'Share-count and value allocations agree exactly.')
check('I2_end_cash_cannot_retroactively_erase_breach',
      [floating['closing_cash']>=5,floating['breach']],[True,True],
      'A permitted subsequent cure does not change the earlier breach event.')
check('I2_ignored_fee_leaves_shortfall',floating['cash_before']+floating['funding_need']-1,F(7),
      'Treating the required net cash as a gross subscription leaves cash below8.')
check('I2_ownership_merge_wrong',fixed['closing_cash']==floating['closing_cash'] and fixed['new_fraction']!=floating['new_fraction'],True,
      'An output request including ownership rejects a merge based only on closing cash.')

check('I2_fixed_issue_face',fixed['issue_face'],F(315,88),
      'The admitted quoted per-face price funds exactly3 with face315/88.')

# I3. A fixed type is independent of a fair observed signal in each admitted law.
# Maximizing separately after seeing the signal creates a new dependent law.
static_costs=[sum((F(int(x==theta),2) for x in (0,1)),F()) for theta in (0,1)]
nested_cost=sum((F(max(int(x==theta) for theta in (0,1)),2) for x in (0,1)),F())
check('I3_static_worst_value',max(static_costs),F(1,2),'One prior is selected for the full path before the unrelated signal.')
check('I3_nested_worst_value',nested_cost,F(1),'History-wise choice of the type produces perfect dependence on the signal.')
check('I3_new_law_not_admitted',[(x,x,F(1,2)) for x in (0,1)] in [[(x,t,F(1,2)) for x in (0,1)] for t in (0,1)],False,
      'Allowing pasted conditional laws changes the declared family, even when every point was already in its union of supports.')
# Conditional CVaR at alpha=1/2 within a three-point equiprobable atom, losses0,1,2.
# The original six equiprobable-state CVaR envelope has each Q mass <=1/3.
# It can put1/6 on loss2, zero on other points in its atom, and5/18 each
# on the other three states, yielding conditional expectation2.
conditional_cvar=min(t+2*sum((max(F(x)-t,F()) for x in (0,1,2)),F())/3 for t in map(F,(0,1,2)))
q=[F(0),F(0),F(1,6),F(5,18),F(5,18),F(5,18)]
check('I3_cvar_envelope_feasible',[sum(q),max(q)<=F(1,3)],[F(1),True],
      'The exhibited law belongs to the original six-state alpha1/2 CVaR envelope.')
check('I3_conditional_risk_discrepancy',[conditional_cvar,sum((q[i]*i for i in range(3)),F())/sum(q[:3])],[F(5,3),F(2)],
      'Conditional CVaR under the reference law differs from conditioning the original unconditional risk envelope.')

result=dict(status='PASS',date='2026-10-26',count=len(rows),checks=rows,paths=encode(paths),
            scope='Exact authored finite interaction oracles, not production runtime, issuer calibration or equilibrium pricing.')
(base/'interaction-results.json').write_text(json.dumps(result,indent=2)+'\n')
(base/'interaction-manifest.json').write_text(json.dumps(dict(command='python3 data/accounting-master/literature-closure-20261026/interaction_cases.py',
 environment=sys.version,platform=platform.platform(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 git_commit='Unavailable: unusable project .git; source SHA256 used',cpu_gpu='CPU-only standard-library; no GPU/ML libraries',
 data='Declared synthetic exact models in script',seeds='N/A: exhaustive finite and rational arithmetic',
 wall_seconds=time.monotonic()-start,plan='docs/plans/accounting-literature-closure-20261026.md',
 result='data/accounting-master/literature-closure-20261026/interaction-results.json'),indent=2)+'\n')
print(json.dumps(dict(status='PASS',interaction_checks=len(rows))))
