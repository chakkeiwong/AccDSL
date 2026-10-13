"""Exact conditional acquisition-asset checks; no production accounting engine."""
import hashlib
import json
from pathlib import Path

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
if (UNIT/'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((UNIT/'baseline.json').read_text())
pages=json.loads((UNIT/'source-pages.json').read_text())
checks={'source_identity':sha(ROOT/base['source'])==base['source_sha256']}
for p in pages['pages']:
    checks[f"text:{p['pdf_page']}"]=sha(ROOT/p['text'])==p['sha256']
    if 'image' in p:
        checks[f"image:{p['pdf_page']}"]=sha(ROOT/p['image'])==p['image_sha256']
anchors=[
    (29,'AppendixA','directly attributable to the portfolio of insurance contracts'),
    (10,'28A','using a systematic and rational method'),
    (10,'28B','recognise such an asset for each related group'),
    (10,'28C','shall derecognise an asset for insurance acquisition cash flows'),
    (10,'28E','if facts and circumstances indicate the asset may be impaired'),
    (10,'28F','to the extent that the impairment conditions no longer exist or have improved'),
    (11,'32(a)','a risk adjustment for non-financial risk'),
    (11,'35','Such amounts relate to future insurance contracts'),
    (19,'79','include any assets for insurance acquisition cash flows'),
    (37,'B35A','insurance acquisition cash flows directly attributable to a group'),
    (38,'B35A(a)(ii)','expected to arise from renewals'),
    (38,'B35B','reflect any changes in assumptions'),
    (38,'B35C','derecognise the portion of an asset'),
    (38,'B35D(a)','does not exceed the expected net cash inflow for the related group'),
    (38,'B35D(b)(ii)','has not already been recognised as an impairment loss applying (a)'),
]
for n,a,t in anchors:
    checks[f'anchor:{a}']=t in ' '.join((UNIT/f'source-pages/page-{n}.txt').read_text().split())

def assess(cost,whole,renewals):
    # This local rule is restricted to the positive, disjoint inputs in the note.
    first=max(cost-whole,0)
    second=max(cost-renewals-first,0)
    return {'cost':cost,'whole_group_inflow':whole,'renewal_inflow':renewals,
            'first_loss':first,'additional_renewal_loss':second,
            'total_loss':first+second,'asset':cost-first-second}

initial={'G1':assess(40,35,25),'G2':assess(20,25,10)}
checks['G1_expected']=(initial['G1']['first_loss'],initial['G1']['additional_renewal_loss'],initial['G1']['asset'])==(5,10,25)
checks['G2_expected']=(initial['G2']['first_loss'],initial['G2']['additional_renewal_loss'],initial['G2']['asset'])==(0,10,10)
checks['initial_totals']=sum(x['total_loss'] for x in initial.values())==25 and sum(x['asset'] for x in initial.values())==35
raw_renewal_loss=sum(x['cost']-x['renewal_inflow'] for x in initial.values())
first_loss=sum(x['first_loss'] for x in initial.values())
checks['overlap_error_rejected']=first_loss+raw_renewal_loss==30!=25 and first_loss==5
checks['initial_subset_consistency']=all(0<x['renewal_inflow']<=x['whole_group_inflow'] for x in initial.values())
checks['other_contract_contributions']=[x['whole_group_inflow']-x['renewal_inflow'] for x in initial.values()]==[10,15]
improved={'G1':assess(40,45,35),'G2':assess(20,30,15)}
reversals={g:initial[g]['total_loss']-improved[g]['total_loss'] for g in initial}
checks['improved_losses']=[x['total_loss'] for x in improved.values()]==[5,5]
checks['reversals_by_group']=reversals=={'G1':10,'G2':5}
checks['improved_assets']=[x['asset'] for x in improved.values()]==[35,15]
checks['improved_group_and_subset_limits']=all(x['asset']<=min(x['cost'],x['whole_group_inflow'],x['renewal_inflow']) for x in improved.values())
checks['other_contracts_unchanged']=[x['whole_group_inflow']-x['renewal_inflow'] for x in improved.values()]==[10,15]
checks['reversal_does_not_exceed_prior_loss']=all(0<=reversals[g]<=initial[g]['total_loss'] for g in initial)
cash=100-60
checks['cash_and_equity_bridge']=cash==40 and cash+35==75 and cash+50==90
journals={'first_test':{'debit_expense':5,'credit_assets':{'G1':5,'G2':0}},
          'renewal_test':{'debit_expense':20,'credit_assets':{'G1':10,'G2':10}},
          'reversal':{'credit_profit':15,'debit_assets':{'G1':10,'G2':5}}}
checks['impairment_entry_balanced']=all(j['debit_expense']==sum(j['credit_assets'].values()) for j in [journals['first_test'],journals['renewal_test']])
checks['impairment_entries_match_group_losses']=all(journals['first_test']['credit_assets'][g]+journals['renewal_test']['credit_assets'][g]==initial[g]['total_loss'] for g in initial)
checks['reversal_entry_balanced']=journals['reversal']['credit_profit']==sum(journals['reversal']['debit_assets'].values()) and journals['reversal']['debit_assets']==reversals
fully_recovered={'G1':assess(40,55,45),'G2':assess(20,40,25)}
checks['full_recovery_ceiling']=sum(x['asset'] for x in fully_recovered.values())==60 and sum(x['asset'] for x in fully_recovered.values())-50==10
boundary=assess(20,20,20)
checks['equality_boundary']=boundary['total_loss']==0 and boundary['asset']==20
zero_renewals=assess(20,25,0)
checks['zero_recovery_boundary']=zero_renewals['total_loss']==20 and zero_renewals['asset']==0
record={'scope':'Authored deterministic example with separate origination cohorts and no prior impairment; real allocation/actuarial inputs not established',
        'source_sha256':base['source_sha256'],'anchors':anchors,
        'initial':initial,'improved':improved,'reversals':reversals,'journals':journals,
        'illustrative_slice':{'initial_cash_equity':100,'cash_after_paid_acquisition':40,'asset_before_impairment':60,'asset_after_impairment':35,'equity_after_impairment':75,'asset_after_reversal':50,'equity_after_reversal':90,'cash_at_both_measurement_dates':40},
        'rejected_double_count':{'loss':30,'correct_loss':25,'error':5},'fully_recovered':fully_recovered,
        'checks':checks,'passed':sum(checks.values()),'failed':[k for k,v in checks.items() if not v]}
(UNIT/'source-calculation-checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['passed','failed','reversals','rejected_double_count']}))
raise SystemExit(bool(record['failed']))
