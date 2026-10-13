"""Necessary compatibility conditions, not a synthetic whole-company history."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
if (UNIT/'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
    (UNIT/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((UNIT/'baseline.json').read_text());checks={}
for path,digest in b['dependencies'].items():checks['source:'+path]=sha(ROOT/path)==digest
asset=json.loads((ROOT/'data/accounting-master/apple-assets-20261008/asset-history.json').read_text())
annual=json.loads((ROOT/'data/accounting-master/apple-statement-network-20261013/statement-readings.json').read_text())
row={r['id']:r for r in annual['rows']}
def amount(key):return int(row[key]['value'])
def change(key):return amount('balance.'+key)-int(row['balance.'+key]['opening']['value'])
histories=[]
for h in asset['histories']:
    signed=defaultdict(int)
    for j in h['journals']:
        checks[h['id']+':balanced:'+j['event']]=sum(p['debit']-p['credit'] for p in j['postings'])==0
        for p in j['postings']:signed[p['account']]+=p['debit']-p['credit']
    derived={'net_ppe':signed['ppe_cost']+signed['accumulated_depreciation'],
      'cash':signed['cash'],'assets':signed['ppe_cost']+signed['accumulated_depreciation']+signed['cash'],
      'liabilities':-signed['capital_payable'],'profit':-signed['depreciation_expense']-signed['retirement_loss'],
      'equity':-signed['depreciation_expense']-signed['retirement_loss'],'investing_cash':signed['cash']}
    for k,v in derived.items():checks[h['id']+':effects:'+k]=v==h['statement_effects'][k]
    # Under the inherited isolated subsystem, all expense is noncash;
    # acquisition payments are investing. Operating cash is therefore zero.
    derived.update({'oci':0,'operating_cash':0,'financing_cash':0,
                    'indirect_depreciation':h['expense'],'indirect_retirement_addback':h['retired_carrying_loss'],
                    'cash_flow_change':derived['cash']})
    checks[h['id']+':indirect_cash']=derived['profit']+derived['indirect_depreciation']+derived['indirect_retirement_addback']==0
    histories.append({'id':h['id'],'signed_account_movements':dict(signed),'effects':derived,
        'scope':h['scope'],'assumptions':asset['assumptions']})
p1,p2=[h['effects'] for h in histories]
delta={k:p2[k]-p1[k] for k in p1}
checks['expected_delta']=delta=={'net_ppe':0,'cash':0,'assets':0,'liabilities':1000,'profit':-1000,'equity':-1000,'investing_cash':0,'oci':0,'operating_cash':0,'financing_cash':0,'indirect_depreciation':0,'indirect_retirement_addback':1000,'cash_flow_change':0}
checks['delta_balance']=delta['assets']==delta['liabilities']+delta['equity']

# These subtraction residuals are obligations for an unconstructed remainder.
# They are NEVER journal entries or proof of an admissible completion.
target={'net_ppe':change('ppe'),'cash':change('cash'),'assets':change('assets'),
 'liabilities':change('liabilities'),'profit':amount('operations.net_income'),
 'equity':change('equity'),'investing_cash':amount('cash_flow.investing'),
 'oci':amount('comprehensive.oci'),'operating_cash':amount('cash_flow.operating'),
 'financing_cash':amount('cash_flow.financing'),'cash_flow_change':amount('cash_flow.change')}
requirements=[]
for h in histories:
    rest={k:target[k]-h['effects'][k] for k in target}
    checks[h['id']+':remaining_balance']=rest['assets']==rest['liabilities']+rest['equity']
    checks[h['id']+':remaining_cash_population']=rest['cash']-rest['cash_flow_change']==772
    checks[h['id']+':remaining_cash_flow']=rest['operating_cash']+rest['investing_cash']+rest['financing_cash']==rest['cash_flow_change']
    requirements.append({'branch':h['id'],'required_complement_effects':rest,'status':'necessary aggregate conditions only; admissible complement not constructed'})
r1,r2=[r['required_complement_effects'] for r in requirements]
fixed_combinations=[]
for h in histories:
    joined={k:h['effects'][k]+r1[k] for k in target}
    residual={k:joined[k]-target[k] for k in target}
    fixed_combinations.append({'branch':h['id'],'complement':'H1 necessary aggregate vector, not a journal history',
        'joined':joined,'residual_to_observed':residual,'all_observed_totals_match':all(v==0 for v in residual.values()),
        'identity_still_balances':joined['assets']==joined['liabilities']+joined['equity']})
checks['h1_algebraic_identity']=fixed_combinations[0]['all_observed_totals_match']
checks['h2_same_remainder_rejected']=not fixed_combinations[1]['all_observed_totals_match']
checks['h2_balance_alone_misses_failure']=fixed_combinations[1]['identity_still_balances']
checks['branch_remainder_difference']={k:r2[k]-r1[k] for k in target}=={k:-delta[k] for k in target}
checks['annual_target_values']=target=={'net_ppe':1965,'cash':-22,'assets':12397,'liabilities':17593,'profit':93736,'equity':-5196,'investing_cash':2935,'oci':4280,'operating_cash':118254,'financing_cash':-121983,'cash_flow_change':-794}
observed_adjustment=amount('cash_flow.other_adjustments')
other_requirements={h['id']:observed_adjustment-h['effects']['indirect_retirement_addback'] for h in histories}
checks['conditional_other_adjustments']=other_requirements=={'H1':-2630,'H2':-3630}
save('compatibility.json',{'claimed_target':'Two local PP&E witnesses extend to the same annual Apple reported statements with one identical remaining history',
 'computed':'Exact journal-derived effect differences and necessary reported-total complements under inherited isolated-subsystem assumptions',
 'verdict':'wrong relative to the same-remainder claim; H2 changes liabilities/profit/equity by 1000 with the remainder fixed',
 'histories':histories,'H2_minus_H1':delta,'reported_targets':target,'necessary_complements':requirements,'fixed_remainder_test':fixed_combinations,
 'cash_population_limit':'The company balance-sheet cash change is -22, while cash-flow cash changes -794. The complement must preserve their 772 difference; no offsetting cash transaction is invented.',
 'conditional_cash_classification':{'assumption':'Retirement is an expensed noncash loss with no proceeds; addback belongs to reported broad Other adjustment only under an explicit mapping hypothesis.',
  'reported_other_adjustment':observed_adjustment,'required_remaining_other':other_requirements,'status':'conditional necessary allocation; source does not identify this classification or these losses'},
 'unknowns':['Whether either local witness has any whole-company admissible completion.','Which published liability class contains the hypothetical capital payable.','Which expense class and tax consequences correspond to the hypothetical retirement loss.','Whether other components can supply the required opposite branch difference without violating detailed rows/notes.','Actual dates, asset cohorts, leases, settlement and future operations.'],
 'nonconclusions':['H1 aggregate subtraction is not an actual history or proof of existence.','H2 failure with a fixed remainder does not reject H2 with a different admissible remainder.','No probabilities, performance ranking or company-wide forecast is generated.','The inherited 8200 depreciation is an illustrative displayed-centre input, not an exact undisclosed Apple amount.']})
missing=[
 ('capital_payable','balance.payables / balance.other_liabilities_current / balance.other_liabilities_noncurrent','Determine a disjoint supported liability mapping and settlement/opening history; no residual assigned to a reported class.'),
 ('retirement_loss','operations.products_cost / operations.services_cost / operating expenses / other_income','Determine actual recognition and expense placement; all these reported row totals are fixed.'),
 ('taxes','operations.tax / balance.other_assets_noncurrent / liabilities / cash_flow.income_tax_paid','The isolated examples omit tax; a full completion must explain expense, tax bases and payments jointly.'),
 ('noncash_addback','cash_flow.other_adjustments','A noncash loss adds back conditionally, but the reported net Other row does not identify its composition.'),
 ('subsequent_settlement','cash_flow.operating / cash_flow.investing / cash_flow.financing and dated liability rows','Annual hypothetical payables are not observed December amounts or dated cash demands.'),
 ('asset_memory','PP&E Note 5 and conditional future depreciation','Cohort lives, residual values, remaining carrying amounts and impairment are needed before forecasting.')]
save('missing-bindings.json',{'bindings':[{'component':a,'affected_records':b,'required_evidence':c} for a,b,c in missing],
 'continuation':'Expected fixed-remainder rejection triggers a coupled completion model. Keep unsupported completion as unknown rather than manufacture a balancing transaction.'})
failed=[k for k,v in checks.items() if not v]
save('source-arithmetic-checks.json',{'passed':sum(checks.values()),'failed':failed,'checks':checks,'interpretation':'Checks PASS that the same-remainder candidate FAILS; no full-history promotion.'})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'same_remainder':'rejected','whole_history_completion':'not established','necessary_complements':requirements}))
raise SystemExit(bool(failed))
