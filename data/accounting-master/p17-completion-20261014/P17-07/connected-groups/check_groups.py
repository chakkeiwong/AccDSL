"""Exact component and independent journal comparisons; documentary only."""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import json,time
OUT=Path(__file__).resolve().parent
def main():
 start=time.perf_counter();c=json.loads((OUT/'group-cases.json').read_text());checks=[];schedules={}
 def ck(n,a,b=True): checks.append({'name':n,'passed':a==b,'observed':str(a),'expected':str(b)})
 rate=F(c['rate']);q=F(c['R']['q']);capital=F(c['opening_cash_equity'])
 for g in ['A','B']:
  x=c[g];pv=sum(F(v)/(1+rate)**(i+1) for i,v in enumerate(x['claims']))
  ck(g+':claim_pv',pv,F(x['claim_pv']))
  ck(g+':initial_csm',max(F(x['premium'])-pv-F(x['ra']),0),F(x['csm']))
  ck(g+':initial_loss',max(pv+F(x['ra'])-F(x['premium']),0),F(x['loss']))
 ck('R:recovery_pv',sum(F(v)/(1+rate)**(i+1) for i,v in enumerate(c['R']['recoveries'])),F(c['R']['claim_pv']))
 ck('R:base_cost_csm',F(c['R']['premium'])-F(c['R']['claim_pv'])-F(c['R']['ra']),F(c['R']['base_cost_csm']))
 ck('timely_condition',c['timing']['timely_treaty_entered']<=c['timing']['issued_recognition'])
 ck('late_fails_original_loss_condition',c['timing']['late_treaty_entered']>c['timing']['issued_recognition'])
 ck('original_groups_must_remain_separate',c['admission']['separate_profitability'] and not c['admission']['pricing_law_exception'])
 for mode in ['timely','late','wrong_pool']:
  b=defaultdict(F,{'Cash':capital,'Capital':-capital});events=[];rows=[]
  def post(name,lines):
   ck(mode+':'+name+':journal',sum((F(v) for _,v in lines),F(0)),F(0))
   for a,v in lines:b[a]+=F(v)
   ck(mode+':'+name+':trial_balance',sum(b.values()),F(0))
   events.append({'event':name,'lines':[(a,str(v)) for a,v in lines]})
  def equity():return -b['Capital']-sum(v for a,v in b.items() if a.startswith('PL:'))
  def state(t):
   r={'t':t,'cash':b['Cash'],'A_LRC':-b['A_LRC'],'B_LRC':-b['B_LRC'],'R_ARC':b['R_ARC'],'equity':equity(),'A_LIC':-b['A_LIC'],'B_LIC':-b['B_LIC'],'R_incurred':b['R_incurred']}
   ck(mode+f':t{t}:balance',r['cash']+r['R_ARC']+r['R_incurred'],r['A_LRC']+r['B_LRC']+r['A_LIC']+r['B_LIC']+r['equity'])
   if mode=='timely':
    for k,v in c['expected']['timely'][t].items(): ck(mode+f':t{t}:'+k,r[k],F(v))
   else:ck(mode+f':t{t}:expected_equity',r['equity'],F(c['expected'][mode+'_equity'][t]))
   rows.append(r);return r
  if mode=='wrong_pool':
   pvA=F(200);raA=F(20);csmA=F(0);pvB=raB=F(0);loss=F(0)
   post('pooled-premium',[('Cash',F(220)),('A_LRC',-F(220))])
  else:
   pvA=F(80);raA=F(10);csmA=F(30);pvB=F(120);raB=F(10);loss=F(30)
   post('recognise-B-onerous',[('PL:issued_loss',loss),('B_LRC',-loss)])
   post('premiums',[('Cash',F(220)),('A_LRC',-F(120)),('B_LRC',-F(100))])
  pvR=F(60);raR=F(5);csmR=F(5);lr=F(0)
  if mode=='timely':
   lr=q*loss;csmR+=lr
   post('initial-loss-recovery',[('R_ARC',lr),('PL:R_initial_income',-lr)])
  post('reinsurance-premium',[('R_ARC',F(70)),('Cash',-F(70))])
  state(0);totals=[];ratio=F(3,13)
  ck(mode+':initial_R_components',pvR+raR+csmR,b['R_ARC'])
  for i in [0,1]:
   year=i+1;units=2-i;before=equity()
   claimA=F(c['A']['claims'][i]);claimB=F(c['B']['claims'][i]);recovery=F(c['R']['recoveries'][i])
   if mode=='wrong_pool':claimA+=claimB;claimB=F(0)
   finA=(pvA+csmA)*rate;finB=pvB*rate;finR=(pvR+csmR)*rate
   pvA*=1+rate;csmA*=1+rate;pvB*=1+rate;pvR*=1+rate;csmR*=1+rate
   lc_fin=ratio*finB if mode!='wrong_pool' else F(0);loss+=lc_fin
   lr_fin=q*lc_fin if mode=='timely' else F(0);lr+=lr_fin
   post(f'y{year}-finance-A',[('PL:A_finance',finA),('A_LRC',-finA)])
   post(f'y{year}-finance-B',[('PL:B_finance',finB),('B_LRC',-finB)])
   post(f'y{year}-finance-R',[('R_ARC',finR),('PL:R_finance',-finR)])
   ck(mode+f':y{year}:B_lc_finance_ratio',loss,ratio*(pvB+raB) if mode!='wrong_pool' else F(0))
   if mode=='timely':ck(f'y{year}:R_lrc_after_finance',lr,q*loss)
   relA=raA/units;relB=raB/units;relR=raR/units;releaseA=csmA/units;releaseR=csmR/units
   serviceA=claimA+relA+releaseA;serviceB=claimB+relB
   lc_release=ratio*serviceB if mode!='wrong_pool' else F(0)
   lr_release=q*lc_release if mode=='timely' else F(0)
   R_release=recovery+relR+releaseR
   premium_allocation=R_release-lr_release
   post(f'y{year}-service-A',[('A_LRC',serviceA),('PL:A_revenue',-serviceA)])
   post(f'y{year}-service-B',[('B_LRC',serviceB),('PL:B_revenue',-(serviceB-lc_release)),('PL:B_loss_reversal',-lc_release)])
   post(f'y{year}-service-R',[('PL:R_premium_allocation',premium_allocation),('PL:R_loss_recovery_reversal',lr_release),('R_ARC',-R_release)])
   post(f'y{year}-claims-incurred',[('PL:A_claims',claimA),('A_LIC',-claimA),('PL:B_claims',claimB),('B_LIC',-claimB)])
   post(f'y{year}-recovery-incurred',[('R_incurred',recovery),('PL:R_claim_recovery',-recovery)])
   # This intermediate state proves claims/recoveries survive before cash settlement.
   ck(mode+f':y{year}:gross_incurred_before_settlement',-b['A_LIC']-b['B_LIC'],claimA+claimB)
   ck(mode+f':y{year}:held_incurred_before_settlement',b['R_incurred'],recovery)
   post(f'y{year}-claims-paid',[('A_LIC',claimA),('B_LIC',claimB),('Cash',-claimA-claimB)])
   post(f'y{year}-recovery-collected',[('Cash',recovery),('R_incurred',-recovery)])
   pvA-=claimA;raA-=relA;csmA-=releaseA;pvB-=claimB;raB-=relB
   pvR-=recovery;raR-=relR;csmR-=releaseR;loss-=lc_release;lr-=lr_release
   ck(mode+f':y{year}:A_components',pvA+raA+csmA,-b['A_LRC'])
   ck(mode+f':y{year}:B_components',pvB+raB,-b['B_LRC'])
   ck(mode+f':y{year}:R_components',pvR+raR+csmR,b['R_ARC'])
   ck(mode+f':y{year}:no_unpaid_balances',b['A_LIC']+b['B_LIC']+b['R_incurred'],F(0))
   if mode=='timely':
    ck(f'y{year}:B_lc',loss,F(c['expected']['timely_B_lc'][year]));ck(f'y{year}:R_lrc',lr,F(c['expected']['timely_R_lrc'][year]))
   if mode in ['timely','late']:ck(mode+f':y{year}:profit',equity()-before,F(c['expected'][mode+'_period_profit'][year]))
   r=state(year);r.update({'A_pv':pvA,'A_ra':raA,'A_csm':csmA,'B_pv':pvB,'B_ra':raB,'B_lc':loss,'R_pv':pvR,'R_ra':raR,'R_csm':csmR,'R_lrc':lr})
   totals.append({'year':year,'finance_A':finA,'finance_B':finB,'finance_R':finR,'B_lc_finance':lc_fin,'B_lc_release':lc_release,'R_lrc_finance':lr_fin,'R_lrc_release':lr_release,'revenue_A':serviceA,'revenue_B':serviceB-lc_release,'R_premium_allocation':premium_allocation,'R_claim_recovery':recovery,'issued_claims':claimA+claimB,'profit':equity()-before})
  ck(mode+':terminal_cash_identity',b['Cash'],capital+F(220)-F(70)-sum(F(x) for x in c['A']['claims']+c['B']['claims'])+sum(F(x) for x in c['R']['recoveries']))
  ck(mode+':components_expire',sum([pvA,raA,csmA,pvB,raB,pvR,raR,csmR,loss,lr]),F(0))
  schedules[mode]={'states':rows,'periods':totals,'journals':events}
 # Wrong treatments remain balanced yet fail the target's component/timing checks.
 ck('pooling_final_cash_cannot_detect_error',schedules['wrong_pool']['states'][-1]['cash'],schedules['timely']['states'][-1]['cash'])
 ck('pooling_opening_equity_error',schedules['wrong_pool']['states'][0]['equity']-schedules['timely']['states'][0]['equity'],F(15))
 ck('pooling_interim_equity_error',schedules['wrong_pool']['states'][1]['equity']-schedules['timely']['states'][1]['equity'],F('8.25'))
 ck('late_original_loss_not_recovered',schedules['late']['states'][0]['equity'],F(70))
 ck('late_final_same_cash_does_not_authorise_initial_income',schedules['late']['states'][-1]['equity'],F('88.3'))
 ck('ignore_LC_finance_exhausts_too_early',F(30)-F(3,13)*(F(71)+F('77.6'))<0)
 ck('double_component_balanced_but_wrong',F(250)+F(85)+F(15)-F(120)-F(130),F(100))
 ck('year_end_recovery_cap',F('213/26'),q*F('213/13'))
 result={'passed':all(x['passed'] for x in checks),'check_count':len(checks),'checks':checks,'role':'Exact documentary group/journal/statement arithmetic; not actuarial estimation or runtime','wall_seconds':time.perf_counter()-start}
 (OUT/'calculation-checks.json').write_text(json.dumps(result,indent=2)+'\n')
 (OUT/'calculated-schedules.json').write_text(json.dumps(schedules,indent=2,default=str)+'\n')
 print(json.dumps({'passed':result['passed'],'checks':len(checks),'failed':[x['name'] for x in checks if not x['passed']],'period_profit':{m:[str(x['profit']) for x in d['periods']] for m,d in schedules.items()}}))
 if not result['passed']:raise SystemExit(1)
if __name__=='__main__':main()
