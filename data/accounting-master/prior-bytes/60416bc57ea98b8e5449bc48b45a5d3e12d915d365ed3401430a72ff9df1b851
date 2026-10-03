#!/usr/bin/env python3
"""Generate the closed structural IR schema and the complete debt package.

Semantic validations are specified in core-contract.md, not inferred from JSON
Schema success. This is a specification generator, not a compiler.
"""
import json
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; SPEC=ROOT/'docs/design/spec'; FIX=ROOT/'docs/design/fixtures'
S={'type':'string'}; B={'type':'boolean'}; N={'type':'integer','minimum':0}
def ref(n):return {'$ref':'#/$defs/'+n}
def arr(t):return {'type':'array','items':t}
def enum(*values):return {'enum':list(values)}
def nullable(t):return {'anyOf':[t,{'type':'null'}]}
def obj(**fields):return dict(type='object',properties=fields,required=list(fields),additionalProperties=False)
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def main():
    defs={}
    defs['Rational']=obj(n={'type':'string','pattern':'^-?(0|[1-9][0-9]*)$'},d={'type':'string','pattern':'^[1-9][0-9]*$'})
    defs['Model']=obj(id=S,language_version=S,declarations=arr(S),package_lock=arr(S),scope=S)
    defs['Time']=obj(kind=enum('instant','interval'),start=S,end_exclusive=nullable(S),calendar=S)
    defs['Dimension']=obj(axis=S,member=S)
    defs['Context']=obj(id=S,entity=S,perimeter=S,concept=S,basis=S,measurement=S,time=ref('Time'),unit=S,currency=nullable(S),taxonomy_version=nullable(S),dimensions=arr(ref('Dimension')))
    defs['SourceSpan']=obj(id=S,document=S,locator=S,literal=S,extraction=S)
    defs['Document']=obj(id=S,sha256=S,uri=S,filing_id=S,available=S,availability_policy=S,ingested=S)
    defs['Domain']=obj(kind=enum('exact','interval','finite','missing'),lower=nullable(ref('Rational')),upper=nullable(ref('Rational')),lower_closed=B,upper_closed=B,values=arr(S),missing_reason=nullable(enum('notDisclosed','notApplicable','unreadable','withheld','unresolvedMeaning')),display=nullable(S),rounding_rule=nullable(S))
    defs['Observation']=obj(id=S,context=S,domain=ref('Domain'),source_spans=arr(S),reading=S,review_decision=S,supersedes=arr(S),revision_group=S)
    defs['Narrative']=obj(id=S,source_spans=arr(S),actor=S,predicate=S,object=S,scope=S,modality=enum('asserted','conditional','permitted','required','management_forecast'),quantifier=enum('all','some','none','qualitative','numeric'),qualification=S,condition=nullable(S),affected_observations=arr(S),translation=nullable(S),review=S)
    defs['CoverageUnit']=obj(id=S,document=S,locator=S,parent=nullable(S),kind=enum('page','text','table','note','reference','exhibit'),disposition=enum('structured','narrative','policy','context','duplicate','unresolved'),target_refs=arr(S),reason=S)
    defs['Mapping']=obj(id=S,source_concepts=arr(S),target_concept=S,relation=enum('equivalent','component','broader','reclassification','measurement_transform'),applicability=S,transform=nullable(S),partition=nullable(S),source_refs=arr(S),review=S)
    defs['Partition']=obj(id=S,population=S,axis=S,members=arr(S),disjoint_proof=S,exhaustive_proof=S,residual_member=nullable(S),context=S)
    defs['Entity']=obj(id=S,functional_currency=S)
    defs['Control']=obj(id=S,parent=S,child=S,valid=ref('Time'),ownership=ref('Rational'),control_conclusion=enum('controlled','not_controlled','unresolved'),basis=S,evidence=arr(S),adjustment_book=S)
    defs['Book']=obj(id=S,entity=S,basis=S,package=S,currency=S)
    defs['Account']=obj(id=S,book=S,role=enum('Asset','ContraAsset','Liability','Equity','Income','Expense','OCI'),report_concept=S)
    defs['Symbol']=obj(id=S,type=S,context=nullable(S),domain=ref('Domain'),uncertainty_kind=enum('ExtractionReading','HistoricalFact','AccountingElection','MeasurementEstimate','BehaviourPolicy','FutureInnovation'),scope=S,dependencies=arr(S),admission=S,provenance=arr(S))
    defs['Choice']=obj(id=S,members=arr(S),scope=S,uncertainty_kind=S,dependencies=arr(S),admission=S,provenance=arr(S))
    defs['Expression']=obj(id=S,op=enum('literal','ref','add','subtract','multiply','divide','negate','not','and','or','eq','ne','lt','le','gt','ge','call','field','array','record'),type=S,context=nullable(S),args=arr(S),rational=nullable(ref('Rational')),text=nullable(S),target=nullable(S),field_names=arr(S))
    defs['Constraint']=obj(id=S,expression=S,kind=enum('evidence','accounting_identity','contract','assumption','choice'),scope=S,source_refs=arr(S))
    defs['Assumption']=obj(id=S,expression=S,scope=S,rationale=S,provenance=enum('Analyst','EmpiricalEstimate','ImportedModel','ScenarioDesign'),source_refs=arr(S),valid=ref('Time'),information_cutoff=S,role=enum('Baseline','Hypothesis','Convenience','ReviewedDefault'))
    defs['Alternative']=obj(id=S,parent=S,scope=S,author=S,created_at=S,constraints=arr(S),choice_group=nullable(S),reason=S,evidence=arr(S),opposing_evidence=arr(S))
    defs['FieldBinding']=obj(name=S,expression=S)
    defs['Contract']=obj(id=S,type=S,book=S,fields=arr(ref('FieldBinding')),package=S,source_refs=arr(S))
    defs['Posting']=obj(account=S,side=enum('Debit','Credit'),amount=ref('Rational'),currency=S,original_quantity=nullable(ref('Rational')),original_unit=nullable(S),movement=S,counterparty=nullable(S),lot=nullable(S),valuation=nullable(S))
    defs['Balance']=obj(account=S,signed_amount=ref('Rational'))
    defs['State']=obj(id=S,date=S,book=S,balances=arr(ref('Balance')),contracts=arr(S),measurements=arr(S),dependencies=arr(S))
    defs['Event']=obj(id=S,time=S,phase=S,owner=S,operation=S,payload=arr(ref('FieldBinding')),dependencies=arr(S),information_view=S,source_refs=arr(S))
    defs['Rule']=obj(id=S,package=S,event_type=S,operation=S,guard=S,overrides=arr(S),bindings=arr(ref('FieldBinding')),requirements=arr(S),posting_expressions=arr(ref('FieldBinding')),state_transition=S)
    defs['Package']=obj(id=S,version=S,digest=S,basis=S,effective=ref('Time'),operations=arr(S),extension_points=arr(S),dependencies=arr(S),authority=arr(S),review_status=enum('illustrative','source_checked','domain_reviewed'),implementation=nullable(S))
    defs['Measurement']=obj(id=S,value_expression=S,basis=S,date=S,information_view=S,method=S,numerical_status=enum('exact','approximate','failed'),error=nullable(ref('Rational')),provenance=arr(S))
    defs['Journal']=obj(id=S,event=S,book=S,date=S,accrual_period=nullable(ref('Time')),postings=arr(ref('Posting')),rule=S,measurements=arr(S),assumptions=arr(S),precondition_hash=S,explanation=S)
    defs['Scenario']=obj(id=S,kind=enum('ExogenousStress','ObservationalConditioning','StructuralIntervention'),drivers=arr(ref('FieldBinding')),probability_model=nullable(S),observed_event=nullable(S),structural_model=nullable(S),replaced_equations=arr(S),visibility=enum('announced','current_and_past'))
    defs['InformationView']=obj(id=S,date=S,observer=S,role=S,evidence_view=S,committed_prefix=S,scenario_inputs=arr(S),forecast_model=nullable(S),future_realisation_access=enum(False))
    defs['ReviewDecision']=obj(id=S,reading_ids=arr(S),action=enum('Propose','Accept','AcceptAlternative','Reject','Supersede'),reviewer=S,date=S,reason=S,evidence=arr(S),prior_view=S,new_view=S,invalidated_descendants=arr(S))
    defs['EvidenceView']=obj(id=S,cutoff=S,system_as_of=nullable(S),mode=enum('Original','LatestAvailable','ExplicitSelection','Harmonised'),documents=arr(S),observations=arr(S),decisions=arr(S),conflict_sets=arr(arr(S)),transforms=arr(S))
    defs['ModelScope']=obj(id=S,templates=arr(S),slot_limits=arr(ref('FieldBinding')),resolution=S,calendars=arr(S),choices=arr(S),exclusions=arr(S),obligations=arr(S))
    defs['HistoryFamily']=obj(id=S,scope=S,evidence_view=S,opening_state=S,symbols=arr(S),choices=arr(S),constraints=arr(S),alternatives=arr(S),feasibility=enum('Feasible','Infeasible','Unknown'),coverage=enum('ExactWithinScope','PartialSearch','Approximate'),completed_cells=N,unresolved_cells=N,witnesses=arr(S),solver_results=arr(S))
    defs['ProbabilityModel']=obj(id=S,kind=enum('finite','continuous','credal'),measure=S,hypotheses=arr(S),weights=arr(ref('Rational')),parameterisation=nullable(S),density=nullable(S),likelihood_blocks=arr(S),information_cutoff=S,method=S,provenance=arr(S))
    defs['ReportMapping']=obj(id=S,book=S,basis=S,rows=arr(ref('FieldBinding')),closing_policy=S,cash_flow_policy=S,required_operations=arr(S))
    defs['ResultCell']=obj(id=S,context=S,history_condition=S,scenario=S,path=S,kind=enum('Exact','Symbolic','Samples','CertifiedBounds','ExploredRange','Unresolved'),value=nullable(ref('Rational')),expression=nullable(S),lower=nullable(ref('Rational')),upper=nullable(ref('Rational')),lower_attained=nullable(B),upper_attained=nullable(B),sample_ref=nullable(S),certificate=nullable(S),reason=nullable(S),dependencies=arr(S))
    defs['BranchResult']=obj(id=S,condition=S,scenario=S,path=S,status=enum('Complete','EconomicDefault','Unsupported','NumericalFailure','SolverUnknown','Cancelled'),mass=nullable(ref('Rational')),cells=arr(S),last_committed_state=S,diagnostics=arr(S))
    defs['Run']=obj(id=S,model=S,evidence_view=S,initial_state=S,horizon=ref('Time'),conditions=arr(S),scenarios=arr(S),probability_model=nullable(S),information_policy=S,package_lock=arr(S),solver=S,budgets=arr(ref('FieldBinding')),numeric_policy=S,stream_scheme=S,seed=S,reports=arr(S),environment=S,branches=arr(S))
    defs['Diagnostic']=obj(id=S,code=S,message=S,source_refs=arr(S),entity=nullable(S),period=nullable(ref('Time')),dependency_path=arr(S),retryable=B,capability=nullable(S))
    plurals={'Entity':'entities','HistoryFamily':'historyFamilies'}
    fields={plurals.get(n,n[0].lower()+n[1:]+'s'):arr(ref(n)) for n in defs if n not in ['Rational','Time','Dimension','Domain','FieldBinding','Balance']}
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'accdsl:core-ir:0.1',
            'title':'AccDSL closed structural IR; see core-contract.md for semantic constraints',**obj(schema_version=enum('0.1'),**fields),'$defs':defs}
    write(SPEC/'core-ir.schema.json',schema)
    package=dict(id='DemoDebt@1',status='illustrative executable-method specification; no standard compliance',
        registry={
            'synthetic-note-7':dict(document='synthetic disclosure NS.debt variant Acme',locator='debt and interest paragraph',literal='Debt 100; interest 5; fixed/floating split not disclosed',entity='Acme',perimeter='Acme-only',basis='DemoDebt@1',concept='debt_principal',currency='USD',instant='2025-12-31',precision='Exact',amount=dict(n='100',d='1'),accepted_reading='demo-review-1'),
            'after-2025-close':dict(book='Local',date='2025-12-31',signed_balances=dict(Cash='95',Debt='-100',Retained='5',InterestExpense='0'),contracts=['loans'],unpaid_interest='0'),
            'DemoDebt.statements.v1':dict(balance_sheet=dict(cash='Cash',debt='-Debt',equity='-Retained-current_temporary_total'),income='interest expense movements excluding closing',comprehensive_income='profit; OCI zero',cash_flow='interest cash settlement operating',equity='opening equity + profit; no dividends',closing='debit Retained / credit InterestExpense for expense balance; omit current profit from equity after closing')},
        symbol_admission=dict(alpha=dict(kind='HistoricalFact',domain='[0,1]',evidence='synthetic-note-7',reason='Composition undisclosed',probability=None)),
        currency=dict(USD=dict(scale=2,posting_rounding='half_even')),
        DebtMix=dict(fields=dict(principal='Money<book.currency>, >=0',fixed_fraction='Real [0,1]',fixed_rate='Rate<annual_simple> >=0',initial_floating_rate='Rate<annual_simple> >=0'),
            additional_terms=dict(maturity='2027-12-31',fees='0',currency='USD',pay_date='2026-12-31',accrual_period=['2026-01-01','2027-01-01'],year_fraction='1',default_rule='halt settlement with unpaid obligation; no hidden credit facility'),
            state=['principal','fixed_principal','floating_principal','current_floating_rate','unpaid_interest','status'],
            initialization='F=alpha*principal; V=(1-alpha)*principal; current_floating_rate=initial_floating_rate; unpaid_interest=0; status=performing',
            operations=[
                dict(name='reset',phase='market',precondition='date=2026-01-01; driver available',payload=['market_rate'],effect='current_floating_rate=market_rate',postings='none; explicit non-recognition operation'),
                dict(name='accrue_and_pay',phase='settlement',precondition='principal>=0 and cash>=rounded_interest',payload=['F','V','fixed_rate','current_floating_rate','year_fraction'],amount='roundMoney((F*fixed_rate+V*current_floating_rate)*year_fraction,2,half_even)',postings=['Dr InterestExpense amount','Cr Cash amount'],effect='interest obligation accrued and settled atomically'),
                dict(name='close',phase='closing',precondition='all required period operations committed',payload=['InterestExpense balance'],postings=['Dr Retained expense','Cr InterestExpense expense'],effect='temporary account zero')]),
        request=dict(model='BorrowingExample@1',evidence_view='synthetic-2025-exact',initial_state='after-2025-close',horizon=['2026-01-01','2027-01-01'],conditions=['allFixed','allFloating'],scenarios=['rateShock'],mode='conditional',weight_model=None,reports=['balance_sheet','income','comprehensive_income','cash_flow','equity','journals']),
        expected=dict(allFixed=dict(interest='5',cash='90',debt='100',profit='-5',equity='-10'),allFloating=dict(interest='7',cash='88',debt='100',profit='-7',equity='-12'),parent=dict(interest='7-2*alpha',bounds=['5','7'],measure=None)))
    write(FIX/'demo-debt-package.json',package)
    # Complete structural envelope with a source-to-expression fixture. This does
    # not purport to lower the whole program; the document specifies all node kinds.
    envelope={k:[] for k in fields};envelope['schema_version']='0.1'
    envelope['expressions']=[dict(id='literal.principal',op='literal',type='Money<USD>',context=None,args=[],rational=dict(n='100',d='1'),text=None,target=None,field_names=[]),
        dict(id='symbol.alpha.ref',op='ref',type='Real',context=None,args=[],rational=None,text=None,target='alpha',field_names=[])]
    envelope['symbols']=[dict(id='alpha',type='Real',context=None,domain=dict(kind='interval',lower=dict(n='0',d='1'),upper=dict(n='1',d='1'),lower_closed=True,upper_closed=True,values=[],missing_reason=None,display=None,rounding_rule=None),uncertainty_kind='HistoricalFact',scope='BorrowingExample@1',dependencies=[],admission='demo-review-1',provenance=['synthetic-note-7'])]
    write(FIX/'core-ir-structure.json',envelope)
    # Author-entered complete lowering for the demonstration. This is the
    # expected compiler output, not evidence that a production compiler exists.
    demo={k:[] for k in fields};demo['schema_version']='0.1'
    def q(n,d=1):return dict(n=str(n),d=str(d))
    def tm(start,end=None):return dict(kind='instant' if end is None else 'interval',start=start,end_exclusive=end,calendar='DemoCalendar@1')
    def expr(id,op,type,args=(),rational=None,target=None,text=None,context=None):
        demo['expressions'].append(dict(id=id,op=op,type=type,context=context,args=list(args),rational=rational,text=text,target=target,field_names=[]));return id
    demo['entities']=[dict(id='Acme',functional_currency='USD')]
    demo['books']=[dict(id='Local',entity='Acme',basis='DemoDebt@1',package='DemoDebt@1',currency='USD')]
    demo['accounts']=[dict(id=a,book='Local',role=role,report_concept=concept) for a,role,concept in [('Cash','Asset','cash'),('Debt','Liability','debt'),('InterestExpense','Expense','interest'),('Retained','Equity','retained')]]
    literal=package['registry']['synthetic-note-7']['literal'];docsha=hashlib.sha256(literal.encode()).hexdigest()
    demo['documents']=[dict(id='synthetic-note-document',sha256=docsha,uri='fixture:demo-debt-package.json#registry/synthetic-note-7',filing_id='synthetic-2025',available='2026-01-01T00:00:00Z',availability_policy='exact_synthetic_timestamp',ingested='2026-01-01T00:00:00Z')]
    demo['sourceSpans']=[dict(id='synthetic-note-7',document='synthetic-note-document',locator='fixture:registry/synthetic-note-7/literal',literal=literal,extraction='authored-fixture@1')]
    demo['contexts']=[dict(id='debt-context',entity='Acme',perimeter='Acme-only',concept='debt_principal',basis='DemoDebt@1',measurement='principal',time=tm('2025-12-31'),unit='USD',currency='USD',taxonomy_version=None,dimensions=[])]
    domain=dict(kind='exact',lower=q(100),upper=q(100),lower_closed=True,upper_closed=True,values=[],missing_reason=None,display='100 USD',rounding_rule='exact_authored_fixture')
    demo['observations']=[dict(id='debt',context='debt-context',domain=domain,source_spans=['synthetic-note-7'],reading='fixture:synthetic-note-7/exact-reading',review_decision='demo-review-1',supersedes=[],revision_group='synthetic-v1')]
    demo['reviewDecisions']=[dict(id='demo-review-1',reading_ids=['fixture:synthetic-note-7/exact-reading'],action='Accept',reviewer='synthetic-fixture-author',date='2026-01-01T00:00:00Z',reason='Exact authored disclosure and context, not extracted from a real issuer',evidence=['synthetic-note-7'],prior_view='fixture:empty-view',new_view='synthetic-2025-exact',invalidated_descendants=[])]
    demo['evidenceViews']=[dict(id='synthetic-2025-exact',cutoff='2026-01-01T00:00:00Z',system_as_of=None,mode='ExplicitSelection',documents=['synthetic-note-document'],observations=['debt'],decisions=['demo-review-1'],conflict_sets=[],transforms=[])]
    demo['symbols']=deep_symbols=json.loads(json.dumps(envelope['symbols']))
    deep_symbols[0]['admission']='demo-review-1'
    expr('debt.value','call','Money<USD>',target='builtin:value@1',args=['debt.ref'],context='debt-context')
    expr('debt.ref','ref','Observation<Money<USD>>',target='debt',context='debt-context')
    expr('alpha.ref','ref','Real',target='alpha')
    expr('rate.fixed','literal','Rate<annual_simple>',rational=q(1,20))
    expr('rate.stress','literal','Rate<annual_simple>',rational=q(7,100))
    expr('rate.driver','call','Driver<Rate<annual_simple>>',args=['rate.stress'],target='builtin:constant@1')
    expr('zero','literal','Real',rational=q(0));expr('one','literal','Real',rational=q(1))
    expr('slot.one','literal','Int',rational=q(1))
    expr('is.fixed','eq','Bool',args=['alpha.ref','one']);expr('is.floating','eq','Bool',args=['alpha.ref','zero'])
    demo['constraints']=[dict(id='condition.fixed',expression='is.fixed',kind='assumption',scope='allFixed',source_refs=[]),dict(id='condition.floating',expression='is.floating',kind='assumption',scope='allFloating',source_refs=[])]
    demo['assumptions']=[dict(id='admission.'+name,expression=e,scope=name,rationale='Named endpoint condition for comparison, not inferred from disclosure',provenance='ScenarioDesign',source_refs=[],valid=tm('2026-01-01','2027-01-01'),information_cutoff='2026-01-01T00:00:00Z',role='Hypothesis') for name,e in [('allFixed','is.fixed'),('allFloating','is.floating')]]
    demo['assumptions'] += [dict(id='admission.'+scope,expression=e,scope=scope,rationale=reason,provenance='ScenarioDesign',source_refs=[],valid=tm('2026-01-01','2027-01-01'),information_cutoff='2026-01-01T00:00:00Z',role='Hypothesis') for scope,e,reason in [
        ('rateShock','rate.driver','Illustrative constant 7% annual simple stress; not an estimated future rate'),
        ('loans','rate.fixed','Both initial component rates are assumed to be 5%; the aggregate disclosure alone does not identify them')]]
    demo['alternatives']=[dict(id=name,parent='BorrowingFamily',scope='BorrowingScope',author='synthetic-fixture-author',created_at='2026-01-01T00:00:00Z',constraints=[con],choice_group=None,reason='Named endpoint view; not exhaustive alternatives',evidence=['synthetic-note-7'],opposing_evidence=[]) for name,con in [('allFixed','condition.fixed'),('allFloating','condition.floating')]]
    demo['contracts']=[dict(id='loans',type='DemoDebt@1/DebtMix',book='Local',fields=[dict(name=n,expression=e) for n,e in [('principal','debt.value'),('fixed_fraction','alpha.ref'),('fixed_rate','rate.fixed'),('initial_floating_rate','rate.fixed')]],package='DemoDebt@1',source_refs=['synthetic-note-7'])]
    demo['states']=[dict(id='after-2025-close',date='2025-12-31',book='Local',balances=[dict(account=a,signed_amount=q(n)) for a,n in [('Cash',95),('Debt',-100),('Retained',5),('InterestExpense',0)]],contracts=['loans'],measurements=[],dependencies=['synthetic-2025-exact'])]
    pkgsha=hashlib.sha256((FIX/'demo-debt-package.json').read_bytes()).hexdigest()
    demo['packages']=[dict(id='DemoDebt@1',version='1',digest=pkgsha,basis='DemoDebt',effective=tm('2025-01-01','2028-01-01'),operations=['DemoDebt@1/reset','DemoDebt@1/accrue_and_pay','DemoDebt@1/close','DemoDebt@1/statements'],extension_points=[],dependencies=['builtin:Core0@1','DemoCalendar@1'],authority=['fixture:demo-debt-package.json'],review_status='illustrative',implementation=None)]
    demo['modelScopes']=[dict(id='BorrowingScope',templates=['DemoDebt@1/DebtMix'],slot_limits=[dict(name='debt_contracts',expression='slot.one')],resolution='one fixed/floating aggregate, annual simple accrual, maturity after horizon',calendars=['DemoCalendar@1'],choices=[],exclusions=['fees','foreign_currency','embedded_options'],obligations=[])]
    demo['historyFamilies']=[dict(id='BorrowingFamily',scope='BorrowingScope',evidence_view='synthetic-2025-exact',opening_state='after-2025-close',symbols=['alpha'],choices=[],constraints=[],alternatives=['allFixed','allFloating'],feasibility='Feasible',coverage='ExactWithinScope',completed_cells=1,unresolved_cells=0,witnesses=['fixture:alpha=0','fixture:alpha=1'],solver_results=['fixture:borrowings.json#exact'])]
    demo['scenarios']=[dict(id='rateShock',kind='ExogenousStress',drivers=[dict(name='market_rate',expression='rate.driver')],probability_model=None,observed_event=None,structural_model=None,replaced_equations=[],visibility='announced')]
    expr('report.mapping','literal','SourceRef',text='DemoDebt.statements.v1')
    demo['reportMappings']=[dict(id='statements',book='Local',basis='DemoDebt@1',rows=[dict(name='package_mapping',expression='report.mapping')],closing_policy='DemoDebt@1/close',cash_flow_policy='DemoDebt@1/interest_operating',required_operations=['DemoDebt@1/accrue_and_pay'])]
    demo['models']=[dict(id='BorrowingExample@1',language_version='Core0.1',declarations=['Acme','Local','Cash','Debt','InterestExpense','Retained','debt','alpha','loans','allFixed','allFloating','rateShock','statements','after-2025-close'],package_lock=['DemoDebt@1'],scope='BorrowingScope')]
    write(FIX/'core-ir-demo.json',demo)
    print('Wrote closed structural schema, complete demonstration dependency package and structural IR fixture.')

if __name__=='__main__':main()
