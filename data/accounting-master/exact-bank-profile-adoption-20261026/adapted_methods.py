"""Pinned native capital/loss methods with exact UTC-day projection only."""
from checker import native as n, exact
from datetime import date,timedelta
need=n.need;day=n.day;capital=n.capital;loss=n.loss;unique=n.unique;FinancialRefusal=n.FinancialRefusal;Refusal=n.Refusal
def utc_day(value):return date.fromordinal(int(exact(value)//86400)+1)

def expected_capital(self,br):
 b=self.body(br);ctx=b['context_ref'];v=b['view_ref'];s=self.state(b['state_ref'],v)
 need(s['context_ref']==ctx,'context_mismatch')
 need(b['assessment_date']==s['as_of_date'],'assessment_date_mismatch')
 end=day(b['period_end_exclusive']);start=day(b['period_start'])
 need(start<end and day(b['assessment_date'])==end-timedelta(days=1),'assessment_period_mismatch')
 need(start>=date(2026,1,1) and end<=date(2026,4,1),'scenario_window_mismatch')
 need(day(b['assessment_date'])<=utc_day(self.body(v)['decision_at']),'assessment_after_decision')
 rule=self.body(b['rule_ref'])
 need(rule==self.body(self.alias['rules']),'rule_package_mismatch')
 names=['applicability_ref','eligibility_ref','exposure_ref','allowance_ref','deduction_ref']
 records={k:self.body(b[k]) for k in names}
 need(all(x['context_ref']==ctx for x in records.values()),'context_mismatch')
 self.information(br,v)
 average=None
 if b['average_ref']:
  a=self.body(b['average_ref']);need(a['context_ref']==ctx,'context_mismatch')
  need(a['measure_kind']=='regulatory_average_total_assets','average_kind_mismatch')
  need((a['period_start'],a['period_end_exclusive'])==(b['period_start'],b['period_end_exclusive']),'average_period_mismatch')
  average=a['amount']
 try:
  amounts,ratios=capital(s['balances'],records['applicability_ref']['exclusions'],records['eligibility_ref']['conditions'],{k:records['exposure_ref'][k] for k in ('reserve_venue','loan_class')},records['allowance_ref']['all_eligible_aacl'],records['deduction_ref']['goodwill_without_dtl'],average)
 except FinancialRefusal as e:raise Refusal(str(e))
 # Independent dependency map, separate from authored packet construction.
 groups={'book_equity':['state_ref'],'gross_loans':['state_ref'],'allowance':['state_ref'],'goodwill':['state_ref']}
 risk=['state_ref','rule_ref','applicability_ref','exposure_ref','deduction_ref']
 core=['state_ref','rule_ref','applicability_ref','eligibility_ref','deduction_ref']
 for k in ('cap_base','cap'):groups[k]=risk
 for k in ('admitted_allowance','excess_allowance','rwa','tier2'):groups[k]=risk+['allowance_ref']
 for k in ('cet1','tier1'):groups[k]=core
 groups['total_capital']=risk+core+['allowance_ref']
 groups['leverage_denominator']=['state_ref','rule_ref','applicability_ref','deduction_ref']+(['average_ref'] if b['average_ref'] else [])
 for k,m in amounts.items():m['dependency_refs']=unique([v]+[b[x] for x in groups[k]])
 for k,n,d in [('cet1_ratio','cet1','rwa'),('tier1_ratio','tier1','rwa'),('total_ratio','total_capital','rwa'),('leverage_ratio','tier1','leverage_denominator')]:ratios[k]['dependency_refs']=unique(amounts[n]['dependency_refs']+amounts[d]['dependency_refs'])
 return dict(basis_ref=br,amounts=amounts,ratios=ratios,distribution_permission='unresolved_not_assessed',minimum_ratio_verdict='not_assessed',accounting_effect='none')

def expected_loss(self,qr):
 query=self.body(qr);v=query['view_ref'];measure=self.body(query['measure_ref']);law=self.body(measure['law_ref']);vintage=self.body(law['vintage_ref']);condition=self.body(query['condition_ref'])
 need(law['context_ref']==query['context_ref'],'context_mismatch');self.information(qr,v)
 need(law['dependence']=='joint_cells_no_factorization','factorized_law')
 need(all(c['default_date'] is None or day(law['origin_date'])<=day(c['default_date'])<day(law['horizon_end_exclusive']) for c in law['cells']),'joint_cell_date_mismatch')
 origin=day(query['origin_date']);start=day(query['default_window_start']);end=day(query['default_window_end_exclusive'])
 need(day(law['origin_date'])<=origin<=start<end<=day(law['horizon_end_exclusive']),'loss_window_mismatch')
 need(day(vintage['as_of_date'])<=origin<=utc_day(self.body(v)['decision_at']),'vintage_origin_mismatch')
 need(day(self.body(vintage['evidence_ref'])['measurement_asof'])<=day(vintage['as_of_date']),'vintage_evidence_mismatch')
 if vintage['supersedes_ref']:
  old=self.body(vintage['supersedes_ref']);need(day(old['as_of_date'])<day(vintage['as_of_date']),'vintage_order_mismatch')
 if condition['kind']=='all':need(condition['survived_through'] is None and condition['evidence_ref'] is None,'condition_shape_mismatch');through=None
 else:
  need(condition['survived_through'] is not None and condition['evidence_ref'] is not None,'condition_shape_mismatch')
  through=condition['survived_through'];need(day(law['origin_date'])<=day(through)<=origin,'condition_date_mismatch')
  need(day(self.body(condition['evidence_ref'])['measurement_asof'])==day(through),'condition_evidence_date_mismatch')
 # A later vintage can retain a complete original history partition, including
 # past cells of zero mass. The query's default window selects future defaults.
 try:out=loss(law['cells'],measure['candidates'],measure['mode'],through,query['default_window_start'],query['default_window_end_exclusive'])
 except FinancialRefusal as e:raise Refusal(str(e))
 return dict(query_ref=qr,**out,dependency_refs=[qr])
