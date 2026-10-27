"""Deterministic teaching-example checks; no empirical or engine-validity claim."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json, math
checks=[]
def eq(name, actual, expected):
    assert actual == expected, (name, actual, expected)
    checks.append({'name':name,'actual':str(actual),'expected':str(expected),'passed':True})
def approx(name,actual,expected,tol):
    assert abs(actual-expected)<=tol,(name,actual,expected)
    checks.append({'name':name,'actual':actual,'expected':expected,'tolerance':tol,'passed':True})
# Shared rate family, dependence, threshold, exact uniform reference.
for a in [F(0),F(1,5),F(3,10),F(2,5),F(1)]:
    interest=5+2*a; cash=95-interest
    eq('rate cash/interest conservation '+str(a),cash+interest,F(95))
eq('rate lower interest',5+2*F(1,5),F(27,5));eq('rate upper interest',5+2*F(2,5),F(29,5))
eq('cash boundary',90-2*F(3,10),F(447,5))
eq('uniform mean',(F(88)+90)/2,F(89));eq('uniform variance',F(4,12),F(1,3))
eq('uniform breach',1-F(3,10),F(7,10));eq('conditional breached mean',(F(88)+F(447,5))/2,F(887,10))
eq('four-point grid breach',F(sum(F(2*i-1,8)>F(3,10) for i in range(1,5)),4),F(3,4))
# Positive-recovery debt convention.
face=F(100);r=F(1,20);p=F(1,10);recovery=F(40)
payoff=(1-p)*face+p*recovery;proceeds=payoff/(1+r)
eq('creditor expected payoff',payoff,F(94));eq('consistent proceeds',proceeds,F(1880,21))
eq('consistent yield',face/proceeds-1,F(11,94))
y_bad=F(11,90);proceeds_bad=face/(1+y_bad)
eq('inconsistent convention proceeds',proceeds_bad,F(9000,101));eq('inconsistent break-even residual',payoff-(1+r)*proceeds_bad,F(44,101))
eq('net issuance target with fixed fee',(F(100)+2)/F(9,10),F(340,3))
# Whole operating company, historical journal bridges and four stresses.
profit=120-70-25-5-10;cash=40+130-50-25-5-20;ar=30+120-130;inv=50+60-70;ppe=80+20-10;ap=40+60-50;equity=60+profit
eq('historical profit',profit,10);eq('historical cash',cash,70);eq('historical balance',cash+ar+inv+ppe,ap+100+equity)
for c,f in product((0,1),repeat=2):
    loss=2+18*c;interest=5+2*f;closing_cash=cash-50+(ar-loss)-interest;closing_eq=equity-loss-interest
    eq('stress cash '+str((c,f)),closing_cash,33-18*c-2*f)
    eq('stress equity '+str((c,f)),closing_eq,63-18*c-2*f)
    eq('stress balance '+str((c,f)),closing_cash+inv+ppe,100+closing_eq)
eq('worst facility restores liquidity',13+1,14);eq('worst facility balance',14+40+90,101+43)
# Dated refinancing and fees.
eq('five-day cash without funding',12+18-10-30-2,-12)
eq('pre-maturity bridge need',32-(12-10),30)
eq('bridge only cash',2+30-1,31)
eq('full sale bridge principal',32-2-15+1,16)
eq('full sale final cash H1',18-(16+1),1)
eq('full sale term face H2',(F(17)+2)/F(9,10),F(190,9))
eq('half sale bridge principal',32-2-F(15,2)+1,F(47,2))
for need,face_expected,threshold in [(F(13,2),F(85,9),F(17,80)),(F(49,2),F(265,9),F(53,80))]:
    eq('term face need '+str(need),(need+2)/F(9,10),face_expected)
    eq('term price threshold '+str(need),(need+2)/40,threshold)
eq('low-price net capacity',40*F(3,5)-2,22)
eq('priority remainder',25-17,8)
# Ordinary and preferred equity, conversion and incentives.
eq('simple fair issue old value',F(100)*F(1200,120),F(1000))
eq('simple discounted old value',F(100)*F(1160,120),F(2900,3))
eq('recapitalization value',600+20-80,540)
new=F(60)/F(27,5);eq('fair recap shares',new,F(100,9));eq('fair recap price',600/(100+new),F(27,5))
eq('discounted recap old value',F(600)*F(100,120),F(500));eq('fee recap old value',F(600)*F(100,122),F(30000,61))
eq('authorization cash',15*3-6,39);eq('authorization shortfall',80-(20+39),21);eq('authorization price',(F(60)+6)/15,F(22,5))
pref=lambda v:max(min(F(90),v),F(1,5)*v)
part=lambda v:min(F(90),v)+F(1,5)*max(v-90,0)
for v,expected in [(50,50),(300,90),(600,120)]:
    eq('nonparticipating preference '+str(v),pref(v),F(expected));eq('preference conservation '+str(v),pref(v)+(v-pref(v)),F(v))
eq('participating 300',part(300),F(132));eq('participating 600',part(600),F(192))
eq('preference conversion threshold',F(90)/F(1,5),F(450));eq('debt conversion threshold',F(80)*116/16,F(580))
eq('senior-claim risky residual',(F(0)+max(500-250,0))/2,F(125))
eq('net equity event cash',30*4-10*6,60);eq('net equity event units',30-10,20)
# Learning and nonanticipativity.
for q,loss in [(F(9,10),3),(F(1,2),7)]: eq('signal expected loss '+str(q),12-10*q,F(loss))
eq('signal value q=.9',10*F(9,10)-5,F(4))
p=F(19,20);q=F(9,10);eq('contrary signal posterior',p*(1-q)/(p*(1-q)+(1-p)*q),F(19,28))
eq('two independent signals posterior',q*q/(q*q+(1-q)**2),F(81,82))
eq('switch threshold q=.9',20*q-10,F(8))
eq('persistent type worst total',max(sum(x) for x in [(0,10),(10,0)]),10)
eq('invalid pasted worst total',max(0,10)+max(10,0),20)
# Analytic approximation/reference probabilities (not stochastic experiments).
eq('rare loss mean',F(1,1000)*1000,F(1));eq('rare loss variance',F(1,1000)*1000**2-1,F(999))
eq('importance tail weight',F(1,1000)/F(1,10),F(1,100))
eq('importance non-tail weight',F(999,1000)/F(9,10),F(111,100))
eq('importance weighted mean',F(1,10)*10,F(1));eq('importance weighted variance',F(1,10)*100-1,F(9))
approx('no narrow event probability',.98**100,.133,.0005);approx('no rare loss probability',.999**100,.905,.0005)
eq('sampled minimum',90-2*F(9,10),F(441,5));eq('outer minimum',90-2*F(11,10),F(439,5))
eq('conditional residual minimizer',F(1),F(1));eq('single-draw derivative root',F(2,4),F(1,2))
eq('single-draw residual at optimizer',F(1,2)-1,F(-1,2));eq('KKT boundary multiplier',2*(0+1),2)
# Projection, collateral, entity and currency constraints.
eq('AR collections and writeoffs',30+40-20,50);eq('AR inferred writeoffs',30+40-20-48,2)
eq('coupled worst funding at d=.1 r=.02',50*F(1,10)+50*F(1,50),F(6))
eq('LP bound attaining witness',2*10+0,20);eq('nonlinear interval maximum',F(1,2)*(1-F(1,2)),F(1,4))
eq('parent limited transfer shortfall',20-(5+10),5);eq('group post-transfer cash',5+30-20,15)
eq('second collateral recovery',min(30,50-40),10)
eq('pari passu conservation',50*F(40,70)+50*F(30,70),F(50))
eq('borrowing-base capacity',F(4,5)*(100-20),64);eq('borrowing-base deficiency',70-F(4,5)*80,6)
eq('currency conversion baseline',10*8,80);eq('currency conversion stress',10*12,120)
eq('guarantee induced parent gap',4-(5-(6-4)),1)
# Teaching tax law and contractual memory.
def tax_step(losses,income):
    return F(1,4)*max(income-losses,0),max(losses-max(income,0),0)+max(-income,0)
tax,loss=tax_step(40,30);eq('loss-pool first tax',tax,0);eq('loss-pool first balance',loss,10)
tax2,loss2=tax_step(loss,30);eq('loss-pool second tax',tax2,5);eq('loss-pool second balance',loss2,0)
eq('negative income adds losses once',tax_step(40,-10)[1],50);eq('no-loss tax over two years',2*tax_step(0,30)[0],15)
eq('limited-loss tax',(30-min(40,F(1,2)*30))*F(1,4),F(15,4))
eq('fee then interest remaining',5-(6-2),1);eq('refinancing option saving',110-102,8)
# Two-state endogenous debt benchmark.
def price(face,assets=(60,140)):
    return sum(F(min(face,a)) for a in assets)/2
for face,p_expected in [(0,0),(60,60),(100,80),(140,100),(200,100)]:eq('two-state price '+str(face),price(face),F(p_expected))
eq('finite debt gross fee target',price(110),85);eq('finite debt fee equity',100-price(110),15)
prop_gross=F(80)/F(19,20);prop_face=2*(prop_gross-30)
eq('proportional fee gross',prop_gross,F(1600,19));eq('proportional fee face',prop_face,F(2060,19));eq('proportional fee proceeds',price(prop_face)*F(19,20),80)
eq('default-cost price',(F(50)+110)/2,80);eq('expected bankruptcy loss',(F(10)+0)/2,5)
eq('asset substitution creditor',price(80,(0,180)),40);eq('asset substitution equity',90-price(80,(0,180)),50)
eq('committed risky funding',price(160,(0,180)),80);eq('committed risky equity',90-price(160,(0,180)),10)
eq('new equity fraction',F(80,100),F(4,5));eq('old equity low state',F(1,5)*60,12);eq('old equity high state',F(1,5)*140,28)
eq('unknown-asset low price',price(100,(40,140)),70);eq('robust face low price',price(120,(40,140)),80);eq('robust face high price',price(120,(60,140)),90)
# Probability-metric reduction and discontinuous guard.
weights=[F(1,4),F(1,2),F(1,4)];states=[F(0),F(1),F(2)];mapping=[F(0),F(0),F(2)]
eq('reduced mass at zero',weights[0]+weights[1],F(3,4))
eq('reduction transport cost',sum(w*abs(x-y) for w,x,y in zip(weights,states,mapping)),F(1,2))
eq('original scenario mean',sum(w*x for w,x in zip(weights,states)),1)
eq('reduced scenario mean',sum(w*y for w,y in zip(weights,mapping)),F(1,2))
eta=F(1,1000);eq('small-distance threshold example transport',F(1,2)*2*eta,eta)
eq('original threshold probability',sum(F(1,2) for x in [1-eta,1+eta] if x>1),F(1,2))
eq('reduced threshold probability',int(1-eta>1),0)
# Additional cash, decision and derivative examples from the core chapters.
eq('overlapping report subtraction',120-50,70)
eq('currency quote increase on foreign principal',50*F(1,5),10)
eq('uninformed plan A mean',(F(10)+0)/2,5)
eq('perfect-information plan mean',(F(10)+6)/2,8)
eq('perfect-information net payoff',8-1,7)
eq('swap incremental net cash cost',(100-60)*F(1,50),F(4,5))
eq('half-year rate exposure',100*F(1,50)*F(1,2),1)
fixed_face=F(21)/F(98,100)
eq('yield feedback fixed point',20*(1+F(1,20)+F(1,1000)*fixed_face),fixed_face)
eq('senior/junior recovery over-allocation',F(7,10)*(60+50),77)
eq('net refinance shortfall',100-(90-2),12)
eq('effective-interest accretion',90*(1+(F(100,90)-1)),100)
eq('issue price shock capped shortfall',90-(15*5-10),25)
eq('small preference conversion threshold',F(30)/F(1,4),120)
eq('issue and repurchase net cash',20*10-10*12,80)
eq('half-year weighted shares',(100+120)/2,110)
eq('small gross issue shares',(F(40)-10+5)/5,7)
eq('residual unit rescaling optimum',F(2,20002),F(1,10001))
for rho in [F(1),F(10),F(1000)]:
 a=-1/(1+rho);eq('finite penalty derivative '+str(rho),2*(a+1)+2*rho*a,0);eq('finite penalty remains infeasible '+str(rho),a<0,True)
result={'status':'pass','checks':checks,'count':len(checks),'scope':'Exact deterministic teaching examples and specified probability identities; no simulation engine, empirical forecast, method-ranking or neural-training validation.'}
Path(__file__).with_name('arithmetic.json').write_text(json.dumps(result,indent=2)+chr(10))
print(json.dumps({'status':'pass','checks':len(checks),'artifact':str(Path(__file__).with_name('arithmetic.json'))}))
