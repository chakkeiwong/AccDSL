"""Validate retained anchors and exact conditional reinsurance arithmetic."""
import datetime
import hashlib
import json
from fractions import Fraction
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
base = json.loads((UNIT / 'baseline.json').read_text())
pages = json.loads((UNIT / 'source-pages.json').read_text())
checks = {'source_identity':sha(ROOT / base['source']) == base['source_sha256']}
for p in pages['pages']:
    checks[f"text:{p['pdf_page']}"] = sha(ROOT/p['text']) == p['sha256']
    if 'image' in p:
        checks[f"image:{p['pdf_page']}"] = sha(ROOT/p['image']) == p['image_sha256']
anchors = [
    (16,'62','shall recognise a group of reinsurance contracts held'),
    (16,'63','the effect of any risk of non-performance'),
    (16,'64','the amount of risk being transferred'),
    (16,'65','a net cost or net gain on purchasing the reinsurance'),
    (17,'66B','a loss-recovery component of the asset for remaining coverage'),
    (17,'68','Reinsurance contracts held cannot be onerous'),
    (19,'75','when, and only when, the underlying insurance contract(s) is or are extinguished'),
    (19,'78','present separately in the statement of financial position'),
    (52,'B119C','entered into before or at the same time'),
    (52,'B119E','a systematic and rational method of allocation'),
    (53,'B119F','shall not exceed the portion'),
    (61,'C20A','without the need to meet the condition set out in paragraph B119C'),
    (61,'C20A','the loss component of the liability for remaining coverage'),
    (61,'C20A','the percentage of claims for the underlying insurance contracts'),
]
for n,a,t in anchors:
    checks[f'anchor:{a}:{n}'] = t in ' '.join((UNIT/f'source-pages/page-{n}.txt').read_text().split())
# C4 is carried from the inspected previous unit, bound to the same source PDF.
prior = ROOT/'data/accounting-master/insurance-transition-balances-20261013'
prior_pages = json.loads((prior/'source-pages.json').read_text())
item = next(p for p in prior_pages['pages'] if p['pdf_page']==57)
checks['C4_carried_source'] = prior_pages['source_sha256']==base['source_sha256'] and sha(ROOT/item['text'])==item['sha256']
checks['C4_equity'] = 'recognise any resulting net difference in equity' in ' '.join((ROOT/item['text']).read_text().split())

K, q, issued = 20, Fraction(3,5), 120
R = K*q
checks['component_expected'] = R == 12
checks['issued_liability_retained'] = issued == 120 and K == 20
checks['component_is_not_gross_quota'] = R != issued*q == 72
old_asset, new_asset = 45, 50  # Explicit independent authored inputs, not R outputs.
old_issued, new_issued, other_assets = 220,230,500
old_equity, new_equity = other_assets+old_asset-old_issued, other_assets+new_asset-new_issued
checks['conditional_bridge'] = (old_equity,new_equity) == (325,320)
checks['conditional_equity_components'] = new_equity-old_equity == (new_asset-old_asset)-(new_issued-old_issued) == -5
checks['asset_component_not_added_twice'] = other_assets+new_asset+R-new_issued == 332 != new_equity
checks['double_count_error'] = (other_assets+new_asset+R-new_issued)-new_equity == 12
checks['illustrative_entry_balances'] = new_asset == old_asset+5
for pct, expected in [(0,0),(1,20)]:
    checks[f'recovery_boundary:{pct}'] = K*pct == expected
cap = 14*q
checks['later_cap_exact'] = cap == Fraction(42,5)
checks['stale_component_violates_cap'] = R > cap
# The source provides a bound here. Do not compute a unique later asset/P&L.
later = {'underlying_loss_component':14,'recovery_fraction':'3/5','component_upper_bound':'42/5 (8.4)',
         'component_exact_value':None,'full_asset':None,'profit_movement':None,'role':'veto bound only'}
checks['bound_not_upgraded_to_measurement'] = all(later[x] is None for x in ['component_exact_value','full_asset','profit_movement'])
underlying_date=datetime.date(2020,7,1);treaty_date=datetime.date(2020,10,1);transition_date=datetime.date(2022,1,1)
checks['ordinary_timing_condition_fails'] = not treaty_date<=underlying_date
checks['both_precede_transition'] = underlying_date<treaty_date<transition_date
result={'scope':'Authored conditional transition component; total asset supplied separately; no runtime implementation',
        'source_sha256':base['source_sha256'],'anchors':anchors,
        'inputs':{'issued_liability':issued,'underlying_loss_component':K,'expected_recovery_fraction':'3/5','old_reinsurance_asset':old_asset,'new_reinsurance_asset_assumed_already_includes_component':new_asset},
        'derived':{'loss_recovery_component':int(R),'old_total_assets':545,'new_total_assets':550,'old_equity':old_equity,'new_equity':new_equity},
        'timing':{'underlying_recognition':str(underlying_date),'treaty_entered':str(treaty_date),'transition':str(transition_date),'C20A_B119C_exception_applies_only_to_transition_component':True,'other_conditions':'assumed, not established by dates'},
        'later_diagnostic':later,'checks':checks,'passed':sum(checks.values()),'failed':[k for k,v in checks.items() if not v]}
(UNIT/'source-calculation-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['passed','failed','derived']}))
raise SystemExit(bool(result['failed']))
