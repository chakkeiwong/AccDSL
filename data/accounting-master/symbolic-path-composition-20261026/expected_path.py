"""Independent full-state and guard formulas; no candidate imports."""
from fractions import Fraction as Q

def L(d=None,c=0):return ('linear',tuple(sorted((k,str(Q(v))) for k,v in (d or {}).items() if Q(v))),str(Q(c)))
def V(k,x):return ('literal',k,x)
YES=V('boolean',True)
def cmp(op,d=None,c=0):
 a=L(d,c)
 if a[1]:return (op,a)
 n=Q(a[2]);return V('boolean',n==0 if op=='eq' else n<=0 if op=='le' else n<0)
def cash(i,a1,a2):
 f=a1=='draw';g=a2=='draw'
 return [L(c='11/2'),L(c='11/2'),L({'I1':-1},Q(11,2)+(Q(3,4) if f else 0)),
  L({'I1':-1,'R':1},Q(11,2)+(Q(3,4) if f else 0)),
  L({'I1':-1,'R':1},Q(11,2)-(Q(1,4) if f else 0)),
  L({'I1':-1,'R':1},Q(11,2)-(Q(1,4) if f else 0)),
  L({'I1':-1,'I2':-1,'R':1},Q(11,2)-(Q(1,4) if f else 0)+(Q(3,4) if g else 0))][i]
def state(i,mode,right,a1,a2):
 f=a1=='draw';g=a2=='draw'
 b={'cash':cash(i,a1,a2),'other_assets':L(c='189/2'),'old_debt':L(c=-100),'capital':L(),
    'facility_debt':L(c=-int(f) if i in (2,3) else -int(g) if i==6 else 0),
    'interest_payable':L({'I1':-1}) if i==1 else L({'I2':-1}) if i==5 else L(),
    'income':L({'R':-1}) if i>=3 else L(),
    'interest_expense':L({**({'I1':1} if i>=1 else {}),**({'I2':1} if i>=5 else {})}),
    'fee_expense':L(c=Q(int(f and i>=2)+int(g and i>=6),4))}
 m={k:V('text',v) for k,v in {'mode':mode,'phase':['opening','due1','settled1','receipt2','repaid2','due2','settled2'][i],
   'action1':a1 if i>=2 else 'none','action2':a2 if i>=6 else 'none','source':'synthetic-source-v1','clause':'once-only-v1'}.items()}
 m.update(right=V('boolean',right),used=V('boolean',(f and i>=2) or (g and i>=6)),
   due1=L({'I1':1}) if i>=1 else L(),due2=L({'I2':1}) if i>=5 else L(),
   paid1=L({'I1':1}) if i>=2 else L(),paid2=L({'I2':1}) if i>=6 else L())
 flows=[]
 if i>=2:
  if f:flows += [(a1+'1','facility_draw','financing','facility_draw',L(c=1)),(a1+'1','facility_fee','operating','facility_fee',L(c='-1/4'))]
  flows +=[(a1+'1','interest_payment','operating','interest_payment',L({'I1':-1}))]
 if i>=3:flows +=[('receipt2','operating_receipt','operating','operating_receipt',L({'R':1}))]
 if i>=4:flows +=[('repay2','facility_repayment','financing','facility_repayment',L(c=-int(f)))]
 if i>=6:
  if g:flows +=[(a2+'2','facility_draw','financing','facility_draw',L(c=1)),(a2+'2','facility_fee','operating','facility_fee',L(c='-1/4'))]
  flows +=[(a2+'2','interest_payment','operating','interest_payment',L({'I2':-1}))]
 return {'book':b,'memory':m,'flows':flows}

def nonnegative(form):return cmp('le',{k:-Q(v) for k,v in form[1]},-Q(form[2]))
def guards(i,mode,right,a1,a2):
 key=('accrue1',a1+'1','receipt2','repay2','accrue2',a2+'2')[i]
 pre={k:YES for k in ('phase','dated','mode','source','clause','used_matches_history','payable_matches_history')}
 pre['cash_nonnegative']=nonnegative(cash(i,a1,a2))
 post={k:YES for k in ('phase','used_matches_history','payable_matches_history')}
 post['cash_nonnegative']=nonnegative(cash(i+1,a1,a2))
 if i in (0,4):
  p='I1' if i==0 else 'I2'
  pre['coupon_range']=('all',tuple(sorted([cmp('le',{p:-1},3),cmp('le',{p:1},-6)],key=repr)))
  pre['selected_coupon']=YES
 elif i==2:pre['selected_receipt']=YES
 elif i==3:
  # -L <= cash before repayment; first borrowing L=-1 has not yet repaid.
  pre['repayment_cash']=cmp('le',{'I1':1,'R':-1},-Q(11,2)+(Q(1,4) if a1=='draw' else 0))
 else:
  p='I1' if i==1 else 'I2';action=a1 if i==1 else a2
  pre['amount_due']=YES
  if i==1:
   coefficients={'I1':1};constant=-Q(11,2)
  else:
   coefficients={'I1':1,'I2':1,'R':-1};constant=-Q(11,2)+(Q(1,4) if a1=='draw' else 0)
  if action=='pay':pre['cash_to_pay']=cmp('le',coefficients,constant)
  else:
   pre.update(right=V('boolean',right),unused=V('boolean',i==1 or a1!='draw'),
      strict_trigger=cmp('lt',{p:-1},'11/2'),cash_after_draw=cmp('le',coefficients,constant-Q(3,4)))
 pre['facility_matches_first_order' if i in (2,3) else 'facility_zero']=YES
 return pre,post

def steps(mode,right,a1,a2):
 keys=('accrue1',a1+'1','receipt2','repay2','accrue2',a2+'2');out=[]
 for i,key in enumerate(keys):
  pre,post=guards(i,mode,right,a1,a2)
  out.append({'key':key,'before':state(i,mode,right,a1,a2),'pre':pre,'after':state(i+1,mode,right,a1,a2),'post':post})
 return out
