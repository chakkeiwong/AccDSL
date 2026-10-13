"""Check scoped group incorporation, journal transitions and source identities."""
import hashlib
import json
from pathlib import Path

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
if (UNIT/'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((UNIT/'baseline.json').read_text());pages=json.loads((UNIT/'source-pages.json').read_text())
checks={'source_identity':sha(ROOT/b['source'])==b['source_sha256']}
for p in pages['pages']:
    checks[f"text:{p['pdf_page']}"]=sha(ROOT/p['text'])==p['sha256']
    checks[f"image:{p['pdf_page']}"]=sha(ROOT/p['image'])==p['image_sha256']
for label,rel in pages['carried_anchors'].items():
    p=ROOT/rel;source_manifest=json.loads((p.parent.parent/'source-pages.json').read_text())
    item=next(x for x in source_manifest['pages'] if x['text']==rel)
    checks['carried:'+label]=source_manifest['source_sha256']==b['source_sha256'] and sha(p)==item['sha256']
anchors=[(9,'25','earliest of the following'),(9,'25a','the beginning of the coverage period'),
         (12,'38','results in no income or expenses'),(12,'38ci','any asset for insurance acquisition cash flows applying paragraph 28C'),
         (12,'40','the contractual service margin of the group at that date'),
         (20,'83','Insurance revenue shall depict the provision of services'),
         (53,'B123ai','changes resulting from cash inflows from premiums received'),
         (53,'B123A','cash flows other than insurance acquisition cash flows'),
         (54,'B125','recognise the same amount as insurance service expenses')]
for n,a,t in anchors:checks['anchor:'+a]=t in ' '.join((UNIT/f'source-pages/page-{n}.txt').read_text().split())
prior=json.loads((ROOT/'data/accounting-master/insurance-acquisition-recoverability-20261013/source-calculation-checks.json').read_text())
checks['prior_checked']=not prior['failed']
given={'G1':{'acquisition_asset':35,'premium':100,'claims_expenses_pv':50,'risk_adjustment':5},
       'G2':{'acquisition_asset':15,'premium':60,'claims_expenses_pv':25,'risk_adjustment':5}}
groups={}
for g,x in given.items():
    f=x['claims_expenses_pv']+x['risk_adjustment']-x['premium'];c=-f-x['acquisition_asset'];l=f+c
    after_f=f+x['premium'];after_l=after_f+c
    groups[g]={**x,'fcf_before_receipt':f,'csm':c,'signed_group_balance_before_receipt':l,'fcf_after_receipt':after_f,'liability_after_receipt':after_l}
    checks[g+':prior_input_consistency']=x['acquisition_asset']==prior['improved'][g]['asset'] and -f==prior['improved'][g]['whole_group_inflow']
    checks[g+':nononerous_and_no_initial_gain']=c>0 and l==-x['acquisition_asset']
    checks[g+':receipt_only']=after_f-f==x['premium'] and after_l-l==x['premium']
checks['expected_components']=[(x['fcf_before_receipt'],x['csm'],x['signed_group_balance_before_receipt'],x['liability_after_receipt']) for x in groups.values()]==[(-45,10,-35,65),(-30,15,-15,45)]
# Apply independently stated journal lines with debit-positive signs.
initial={'cash':40,'acq_G1':35,'acq_G2':15,'group_G1':0,'group_G2':0,'equity':-90}
journals=[{'group_G1':35,'group_G2':15,'acq_G1':-35,'acq_G2':-15},
          {'cash':160,'group_G1':-100,'group_G2':-60}]
states=[dict(initial)]
for i,journal in enumerate(journals):
    checks[f'journal:{i}:balanced']=sum(journal.values())==0
    state=dict(states[-1])
    for account,amount in journal.items():state[account]+=amount
    states.append(state)
    checks[f'state:{i}:balanced']=sum(state.values())==0
checks['recognition_state']=states[1]=={'cash':40,'acq_G1':0,'acq_G2':0,'group_G1':35,'group_G2':15,'equity':-90}
checks['receipt_state']=states[2]=={'cash':200,'acq_G1':0,'acq_G2':0,'group_G1':-65,'group_G2':-45,'equity':-90}
checks['journal_matches_measurement']=all(-states[2]['group_'+g]==groups[g]['liability_after_receipt'] for g in groups)
checks['no_acquisition_asset_left']=states[1]['acq_G1']==states[1]['acq_G2']==states[2]['acq_G1']==states[2]['acq_G2']==0
wrong_csm=sum(-x['fcf_before_receipt'] for x in groups.values());correct_csm=sum(x['csm'] for x in groups.values())
checks['omission_overstates_csm']=wrong_csm-correct_csm==50 and (wrong_csm,correct_csm)==(75,25)
wrong_liability=sum(x['fcf_after_receipt'] for x in groups.values())+wrong_csm
checks['balanced_wrong_path']=wrong_liability==160 and 200+50-wrong_liability==90
checks['correct_path_with_stale_asset_rejected']=200+50-sum(x['liability_after_receipt'] for x in groups.values())==140!=90
checks['zero_acquisition_boundary']=all(x['fcf_before_receipt']+(-x['fcf_before_receipt']-0)==0 for x in groups.values())
record={'scope':'Exact authored recognition and immediate premium-receipt bridge; valuation/recognition facts supplied, no service elapsed',
        'source_sha256':b['source_sha256'],'anchors':anchors,'groups':groups,'journal_sign':'debits positive, credits negative','journals':journals,'states':states,
        'rejected_paths':{'csm_without_acquisition':wrong_csm,'correct_csm':correct_csm,'both_errors_liability':wrong_liability,'both_errors_equity':90,'stale_asset_with_correct_liability_equity':140},
        'checks':checks,'passed':sum(checks.values()),'failed':[k for k,v in checks.items() if not v]}
(UNIT/'source-calculation-checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'passed':record['passed'],'failed':record['failed'],'csm_total':correct_csm,'final_cash':states[-1]['cash'],'final_equity':-states[-1]['equity']}))
raise SystemExit(bool(record['failed']))
