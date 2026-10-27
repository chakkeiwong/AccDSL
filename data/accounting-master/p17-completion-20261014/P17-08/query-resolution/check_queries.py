"""Exact interval derivations and bounded integer comparison, no solver/runtime."""
from fractions import Fraction as F
from pathlib import Path
import json,time,hashlib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
def main():
 start=time.perf_counter();c=json.loads((OUT/'query-cases.json').read_text());checks=[]
 def ck(n,a,b=True):checks.append({'name':n,'passed':a==b,'observed':str(a),'expected':str(b)})
 def rnd(x):
  x=F(x);sign=-1 if x<0 else 1;y=abs(x)*100+F(1,2)
  return F(sign*(y.numerator//y.denominator),100)
 def valid(f,v):return f>=0 and v>=0 and F('99.5')<=f+v<F('100.5') and F('4.5')<=F('.05')*(f+v)<F('5.5')
 lo=F('4.975');hi=F('7.035')
 ck('raw_lower_derivation',F('.05')*F('99.5'),lo)
 ck('raw_upper_derivation',F('.07')*F('100.5'),hi)
 ck('raw_min_witness',valid(F('99.5'),F(0)))
 ck('excluded_upper_witness',valid(F(0),F('100.5')),False)
 ck('historic_constraint_lower_redundant',F('.05')*F('99.5')>=F('4.5'))
 ck('historic_constraint_upper_redundant',F('.05')*F('100.5')<=F('5.5'))
 ck('interval_union_overlap',F('.07')*F('99.5'),F('6.965'))
 witnesses=[]
 for cents in range(498,704):
  x=F(cents,100)
  if x<=F('6.965'):v=(x-lo)/F('.02');f=F('99.5')-v
  else:v=x/F('.07');f=F(0)
  ck(f'cent:{cents}:feasible',valid(f,v));ck(f'cent:{cents}:exact_query',F('.05')*f+F('.07')*v,x)
  ck(f'cent:{cents}:rounding',rnd(x),x)
  witnesses.append({'rounded':str(x),'F':str(f),'V':str(v)})
 ck('all_rounded_outputs_witnessed',len(witnesses),c['rounded_query']['expected_distinct_count'])
 ck('included_lower_tie',rnd(lo),F('4.98'));ck('excluded_upper_tie_would_jump',rnd(hi),F('7.04'))
 ck('negative_included_tie',rnd(-lo),F('-4.98'));ck('negative_excluded_tie',rnd(-hi),F('-7.04'))
 ck('open_one_has_rounded_one',rnd(F('.995')),F(1));ck('open_one_witness_inside',F('.995')<1)
 ck('enclosure_left',rnd(F('1.0049')),F(1));ck('enclosure_right',rnd(F('1.0051')),F('1.01'))
 ck('enclosure_cannot_choose_one',rnd(F('1.0049'))!=rnd(F('1.0051')))
 ck('round_each_then_sum',sum(rnd(x) for x in c['round_order']['lines']),F('.02'))
 ck('sum_then_round',rnd(sum(F(x) for x in c['round_order']['lines'])),F('.01'))
 # Integer principal cents: exact interest numerator = 5*total_cents+2*floating_cents.
 # Complete enumeration is finite for THIS changed model, not continuum proof.
 numerators=set();integer_outputs=set();count=0
 for n in range(9950,10050):
  for k in range(n+1):
   z=5*n+2*k;numerators.add(z);integer_outputs.add((z+50)//100);count+=1
 ck('integer_min',F(min(numerators),10000),lo)
 ck('integer_max',F(max(numerators),10000),F('7.0343'))
 ck('integer_attained_witness',valid(F(0),F('100.49')))
 ck('integer_output_image',integer_outputs,set(range(498,704)))
 ck('same_display_does_not_equal_raw_family',F('7.0349')>F(max(numerators),10000) and F('7.0349')<hi)
 ck('real_counterexample_to_integer_domain',valid(F(0),F('7.0349')/F('.07')))
 # Draw the timed states from the previously checked source, not retyped totals alone.
 source=json.loads((ROOT/'data/accounting-master/p17-completion-20261014/P17-07/connected-groups/calculated-schedules.json').read_text())
 for arm in ['timely','late','wrong_pool']:
  for key,i in [('initial_equity',0),('year1_equity',1),('terminal_cash',2)]:
   v=source[arm]['states'][i]['cash' if key=='terminal_cash' else 'equity']
   ck(arm+':'+key,F(v),F(c['sector'][arm][key]))
 ck('two_admitted_terminal_projections_agree',F(c['sector']['timely']['terminal_cash']),F(c['sector']['late']['terminal_cash']))
 ck('two_admitted_interim_outputs_differ',F(c['sector']['timely']['year1_equity'])!=F(c['sector']['late']['year1_equity']))
 ck('invalid_pool_is_not_law_atom','wrong_pool@1' not in c['law']['outcomes'])
 prior=list(map(F,c['law']['prior']));likelihood=list(map(F,c['law']['likelihood']));joint=[p*l for p,l in zip(prior,likelihood)];z=sum(joint)
 ck('prior_sum',sum(prior),F(1));ck('evidence_normalizer',z,F('11/12'))
 post=[x/z for x in joint]
 for i,x in enumerate(post):ck(f'posterior:{i}',x,F(c['law']['posterior'][i]))
 ck('known_plus_unresolved_mass',sum(post),F(1))
 full=post[0]*F(83)+post[1]*F('74.75');ck('authored_interim_mean_if_both_executed',full,F(77))
 ck('successful_only_83_is_wrong_unconditional',F(83)!=full)
 ck('endpoint_records_differ',c['real_model']['expected_image']['upper_attained'],False)
 ck('integer_endpoint_is_attained',c['integer_model']['max_attained'])
 for row in json.loads((OUT/'dependency-manifest.json').read_text())['dependencies']:
  ck('dependency:'+row['path'],hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['sha256'])
 r={'passed':all(x['passed'] for x in checks),'check_count':len(checks),'checks':checks,'integer_assignments':count,'integer_raw_value_count':len(numerators),'role':'Rational derivations and complete finite enumeration for declared integer model; no general solver','wall_seconds':time.perf_counter()-start}
 (OUT/'calculation-checks.json').write_text(json.dumps(r,indent=2)+'\n')
 (OUT/'rounded-witnesses.json').write_text(json.dumps(witnesses,indent=2)+'\n')
 print(json.dumps({'passed':r['passed'],'checks':len(checks),'integer_assignments':count,'wall_seconds':r['wall_seconds'],'failed':[x['name'] for x in checks if not x['passed']]}))
 if not r['passed']:raise SystemExit(1)
if __name__=='__main__':main()
