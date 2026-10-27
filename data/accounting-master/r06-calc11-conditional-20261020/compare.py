"""Conditional local interval arithmetic; no upstream processor execution."""
from collections import Counter,defaultdict
from decimal import Decimal,localcontext
from fractions import Fraction
from itertools import combinations
import importlib.util
import json
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2];B=R/'data/accounting-master'
def imported(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ref=imported('conditional_math',B/'r06-calculations11-source-20261020/compare.py')
alignment=imported('conditional_alignment',B/'r06-calc11-alignment-20261020/compare.py')
load,bind=ref.load,ref.bind
MAP=B/'r06-oim-mapping-20261020/mapping.json'
ALIGN=B/'r06-calc11-alignment-20261020/alignment.json'
LEX=B/'r06-numeric-lexical-20261020/occurrences.json'
CALC=B/'r06-calculation-bindings-20261020/calculation-bindings.json'
MODES=('round-to-nearest','truncation')

def decimal_iv(f,mode):
 v,d=f['value'],f['decimals'];v=Decimal(v.numerator)/Decimal(v.denominator)
 if d=='INF':return (v,v,True,True)
 q=Decimal(10)**(-d)
 if mode=='round-to-nearest':return (v-q/2,v+q/2,True,True)
 # Excess digits are rejected before arithmetic; this gives the truncated
 # value explicitly for fixtures too.
 v=(v/q).to_integral_value(rounding='ROUND_DOWN')*q
 return (v,v+q,True,False) if v>0 else ((v-q,v,False,True) if v<0 else (-q,q,False,False))

def meet(intervals):
 if not intervals:return None
 lo=max(i[0] for i in intervals);hi=min(i[1] for i in intervals)
 lc=all(i[2] for i in intervals if i[0]==lo);hc=all(i[3] for i in intervals if i[1]==hi)
 return None if lo>hi or (lo==hi and not(lc and hc)) else (lo,hi,lc,hc)

def dpoint(fs,mode):
 if all(f['value'] is None for f in fs):return ('all_nil_ignored',None)
 if any(f['value'] is None for f in fs):return ('inconsistent_duplicates',None)
 ivs=[decimal_iv(f,mode) for f in fs]
 for a,b in combinations(range(len(fs)),2):
  if (fs[a]['decimals']==fs[b]['decimals'] and fs[a]['value']!=fs[b]['value']) or meet([ivs[a],ivs[b]]) is None:
   return ('inconsistent_duplicates',None)
 for f in fs:
  if f['decimals']!='INF':
   v=Decimal(f['value'].numerator)/Decimal(f['value'].denominator);q=Decimal(10)**(-f['decimals'])
   if v%q:return ('excess_digits',None)
 return ('supported_under_contextual_reading',meet(ivs))

def dbinding(total,contributors,mode):
 if all(f['value'] is None for f in total):return {'status':'nonbinding_no_total'}
 parts=[(fs,w) for fs,w in contributors if any(f['value'] is not None for f in fs)]
 if not parts:return {'status':'nonbinding_no_contribution'}
 ps=[dpoint(total,mode)]+[dpoint(fs,mode) for fs,w in parts]
 if any(p[0]=='inconsistent_duplicates' for p in ps):return {'status':'inconsistent_duplicates'}
 if any(p[0]=='excess_digits' for p in ps):return {'status':'excess_digits'}
 terms=[]
 for (_,iv),(_,w) in zip(ps[1:],parts):
  w=Decimal(w.numerator)/Decimal(w.denominator)
  lo,hi,lc,hc=iv
  terms.append((lo*w,hi*w,lc,hc) if w>0 else (hi*w,lo*w,hc,lc))
 computed=(sum(t[0] for t in terms),sum(t[1] for t in terms),all(t[2] for t in terms),all(t[3] for t in terms))
 shared=meet([ps[0][1],computed])
 def rational(iv):
  return None if iv is None else (Fraction(iv[0]),Fraction(iv[1]),iv[2],iv[3])
 return {'status':'consistent' if shared is not None else 'inconsistent_calculation',
   'reported_interval':rational(ps[0][1]),'calculated_interval':rational(computed),'shared':rational(shared)}

def derive():
 prior=load(CALC);net=prior['network'];mapped=load(MAP);joins=load(ALIGN)
 assert alignment.derive()==joins
 lex={x['fact_id']:x for x in load(LEX)}
 facts={}
 for f in mapped['facts']:
  if not f['numeric']:continue
  l=lex[f['fact_id']]
  if f['nil']:
   assert l['portable_candidate_value']['tag']=='Nil';v=None;d=None
  else:
   v=Fraction(l['lexical']['rational']['n'])/Fraction(l['lexical']['rational']['d'])
   assert v==Fraction(Decimal(l['decoded_text']))
   assert len(str(abs(v.numerator)))+len(str(v.denominator))<60
   d='INF' if f['decimals']=='infinity' else f['decimals']
   assert d=='INF' or abs(d)<30
  facts[f['fact_id']]=ref.fact(v,d)
 points={p['id']:p for p in joins['data_points'] if p['numeric']}
 pfs={i:[facts[fid] for fid in p['members']] for i,p in points.items()}
 arcs={a['id']:a for a in net['raw_arcs'] if a['id'] in set(net['effective_arc_ids'])}
 result_modes={};point_results={};agreement=0
 with localcontext() as ctx:
  ctx.prec=120
  for mode in MODES:
   prs=[]
   for i,fs in pfs.items():
    rp=ref.point(fs,mode);dp=dpoint(fs,mode)
    assert rp['status']==dp[0]
    if rp['interval'] is not None:assert rp['interval']==(Fraction(dp[1][0]),Fraction(dp[1][1]),dp[1][2],dp[1][3])
    agreement+=1
    prs.append({'data_point':i,'members':points[i]['members'],'result':ref.serial(rp),
      'duplicate_pairs_checked':len(fs)*(len(fs)-1)//2})
   point_results[mode]=prs;rows=[]
   for c in joins['candidates']['equal']:
    total=pfs[c['total_point']];parts=[];detail=[]
    for term in c['contributors']:
     a=arcs[term['arc']];p=points[term['point']];t=points[c['total_point']]
     assert p['concept']==a['target_qname'] and t['concept']==a['source_qname']
     assert p['dimensions_without_concept']==t['dimensions_without_concept']
     w=Fraction(a['weight']['n'])/Fraction(a['weight']['d'])
     assert w and len(str(abs(w.numerator)))+len(str(w.denominator))<30
     parts.append((pfs[term['point']],w));detail.append({**term,'members':p['members'],'weight':a['weight']})
    r=ref.binding(total,parts,mode);d=dbinding(total,parts,mode)
    assert r['status']==d['status'],(c['role'],c['total_point'],r,d)
    for field in ('reported_interval','calculated_interval','shared'):
     if field in r:assert r[field]==d[field],field
    agreement+=1
    rows.append({'role':c['role'],'total_point':c['total_point'],'total_members':c['total_members'],
     'contributors':detail,'unreported_edges':c['arcs_without_reported_contributor'],
     'result':ref.serial(r),'independent_Decimal_agreement':True})
   result_modes[mode]=rows
 comparisons=[];lookup={mode:{(x['role'],x['total_point']):x for x in rows} for mode,rows in result_modes.items()}
 for bridge in joins['old_candidate_bridge']:
  key=(bridge['role'],bridge['data_point'])
  comparisons.append({**bridge,'conditional_status':{mode:lookup[mode][key]['result']['status'] for mode in MODES}})
 changes=[]
 for key,n in lookup[MODES[0]].items():
  t=lookup[MODES[1]][key]
  if n['result']['status']!=t['result']['status']:
   changes.append({'role':key[0],'data_point':key[1],'total_members':n['total_members'],
     'nearest':n['result']['status'],'truncation':t['result']['status']})
 counts={'total_candidates_per_mode':len(result_modes[MODES[0]]),'numeric_points_per_mode':len(points),
   'numeric_occurrences':len(facts),'independent_arithmetic_agreements':agreement,
   'candidate_statuses':{mode:dict(Counter(x['result']['status'] for x in rows)) for mode,rows in result_modes.items()},
   'point_statuses':{mode:dict(Counter(x['result']['status'] for x in rows)) for mode,rows in point_results.items()},
   'mode_status_differences':len(changes),
   'old_bound_statuses':{mode:dict(Counter(x['conditional_status'][mode] for x in comparisons if x['old_binds'])) for mode in MODES},
   'old_bound_occurrences':sum(x['old_binds'] for x in comparisons),
   'unreported_edges_in_bound':{mode:sum(len(x['unreported_edges']) for x in rows if not x['result']['status'].startswith('nonbinding')) for mode,rows in result_modes.items()}}
 return {'counts':counts,'point_results':point_results,'candidate_results':result_modes,'old_comparison':comparisons,
  'mode_status_changes':changes,'alignment':'conditional_equal_nonconcept_dimensions','duplicate_interpretation':'contextual_OIM6.2',
  'issuer_rounding_policy_selected':False,'full_conformance':'not_admitted','upstream_executed':False}

def fixtures():
 rows=[];F=ref.fact
 for mode in MODES:
  for name,total,parts in [
   ('duplicate_unequal',[F(1,0),F(3,0)],[([F(1,0)],Fraction(1))]),
   ('closed_open_touch',[F(2,'INF')],[([F(1,0)],Fraction(1))]),
   ('negative_weight',[F(-2,'INF')],[([F(1,0)],Fraction(-1))]),
   ('mixed_nil',[F(1,0),F(None,None)],[([F(1,0)],Fraction(1))]),
   ('no_contributor',[F(1,0)],[]),
   ('no_total',[F(None,None)],[([F(1,0)],Fraction(1))]),
   ('excess_digits',[F('1.1',0)],[([F(1,0)],Fraction(1))]),
   ('same_precision_first',[F('1.1',0),F(3,0)],[([F(1,0)],Fraction(1))]),
   ('coarse_fine',[F(5500,-2)],[([F(5000,-3),F(5500,-2)],Fraction(1))]),
   ('exact_sum',[F(3,'INF')],[([F(1,'INF')],Fraction(1)),([F(2,'INF')],Fraction(1))])]:
   with localcontext() as ctx:
    ctx.prec=120;r=ref.binding(total,parts,mode);d=dbinding(total,parts,mode)
   assert r['status']==d['status']
   for key in ('reported_interval','calculated_interval','shared'):
    if key in r:assert r[key]==d[key]
   rows.append({'mode':mode,'name':name,'result':ref.serial(r),'independent_Decimal_agreement':True})
 return rows

def check():
 ledger=load(U/'source-ledger.json');count=0
 for b in ledger['bindings']:assert bind(R/b['path'])==b;count+=1
 for a in ledger['anchors']:
  p=R/a['source']['path'];assert bind(p)==a['source'];count+=1
  assert chr(10).join(p.read_text().splitlines()[a['first_line']-1:a['last_line']])==a['excerpt'];count+=1
 r=derive();assert r==load(U/'conditional-calculations.json');count+=1
 f=fixtures();assert f==load(U/'fixtures.json');count+=len(f)+1
 for mode in MODES:
  assert sum(r['counts']['candidate_statuses'][mode].values())==223;count+=1
  assert sum(r['counts']['point_statuses'][mode].values())==879;count+=1
 return {'assertions':count,'fixtures':len(f),'source_anchors':len(ledger['anchors']),
  'input_bindings':len(ledger['bindings']),**r['counts'],'conformance_admitted':False,
  'upstream_executed':False,'whole_rows_closed':0}
