"""Closed company specification schemas; no service is implemented."""
ACCOUNTS=['cash','inventory','ppe','recovery_asset','investment','dta','dtl','refund_liability','debt','receivable','payable',
 'capital','retained','original_equity','revenue','cogs','selling_expense','wages','depreciation','finance_expense','current_tax','deferred_tax']
PROFIT=['revenue','cogs','selling_expense','wages','depreciation','finance_expense','current_tax','deferred_tax']
GROUP_VALUES=['cash','inventory','ppe','dta','dtl','assets','liabilities','equity','revenue','cogs','selling_expense','wages',
 'depreciation','finance_expense','current_tax','deferred_tax','pretax','profit','nci_profit','parent_profit','nci_equity','parent_equity',
 'operating_receipts','operating_payments','investing_receipts','investing_payments','financing_receipts','financing_payments',
 'interest_paid','tax_paid','net_cash']
Q={'type':'string','pattern':r'^-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?$'}
TXT={'type':'string','minLength':1};DATE={'type':'string','format':'date'};BOOL={'type':'boolean'}
I={'type':'integer','minimum':0};DIGEST={'type':'string','pattern':'^[0-9a-f]{64}$'}
def obj(fields):return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}
def enum(*x):return {'enum':list(x)}
def arr(x):return {'type':'array','items':x}
def maybe(x):return {'anyOf':[x,{'type':'null'}]}
def vector(keys):return obj({k:Q for k in keys})
def sid(kind):return 'accdsl.company-composition.'+kind.lower()+'.v1'
def ref(kind):return obj({'kind':{'const':kind},'schema':{'const':sid(kind)},'digest':DIGEST})
BLOB=obj({'path':TXT,'sha256':DIGEST,'byte_length':I})
FLOW=obj({'entity':enum('P','S'),'activity':enum('operating','investing','financing'),'amount':Q,
 'origin':enum('interest','principal','refund','handling','wages','external_sale','internal','income_tax','nci_purchase')})
JOURNALS=obj({e:vector(ACCOUNTS) for e in ['P','S']})
RETURNS=obj({**{k:Q for k in ['sold_units','expected_units','unit_refund','unit_cost','estimated_handling','estimated_deterioration','recovery','refund','inventory']},'settled':BOOL})
COMPOUND=obj({'phase':enum('matured','ended'),**{k:Q for k in ['debt','debt_cash_basis','original_equity','prior_interest_expensed']},'due_date':DATE})
LOT=obj({'lot_id':TXT,'invoice_id':TXT,**{k:Q for k in ['original_cost','internal_price','sold_fraction']},'transferred':BOOL,'settled':BOOL})
OWNERSHIP=obj({'date':DATE,**{k:Q for k in ['old_fraction','new_fraction','consideration','nci_before','carrying_reduction','parent_equity_debit','subsidiary_profit_before']}})
FACTS={'date':DATE,'currency':{'const':'USD'},'basis':{'const':'historical_EU_IFRS_conditional'},'entities':{'const':['P','S']},
 'parent':{'const':'P'},'subsidiary':{'const':'S'},'parent_fraction':Q,'control_start':DATE,'control_end_exclusive':DATE,
 'same_policies':BOOL,'same_calendar':BOOL,'noninvestment_entity':BOOL,'separate_investment_policy':{'const':'cost'},
 'tax_rate':Q,'tax_recovery_supported':BOOL,'outside_basis_timing_control':BOOL,'outside_basis_no_foreseeable_reversal':BOOL,
 'books':JOURNALS,'returns':RETURNS,'compound':COMPOUND,'lot':LOT,'return_inventory':Q,'ownership_purchase':maybe(OWNERSHIP),'tax_closes':arr(DATE)}
PARAMETERS={
 'compound.redeem':obj({'amount':Q,'original_rights_unchanged':maybe(BOOL)}),
 'returns.settle':obj({**{k:Q for k in ['actual_units','unit_handling','unit_deterioration','refund_cash','handling_cash','inventory_nrv']},'all_rights_closed':BOOL,'handling_is_selling_cost':maybe(BOOL)}),
 'payroll.pay':obj({'amount':Q,'service_received':maybe(BOOL),'tax_deductible':maybe(BOOL)}),
 'ppe.depreciate':obj({'amount':Q,'systematic_basis':maybe(BOOL),'tax_matches_book':maybe(BOOL)}),
 'inventory.transfer':obj({'seller':enum('P','S'),'buyer':enum('P','S'),'lot_id':TXT,'invoice_id':TXT,'seller_amount':Q,'buyer_amount':Q,'cost':Q,'counterparty_confirmed':maybe(BOOL)}),
 'inventory.sell':obj({'entity':enum('P','S'),'lot_id':TXT,'fraction':Q,'proceeds':Q,'performance_complete':maybe(BOOL)}),
 'intercompany.pay':obj({'payer':enum('P','S'),'payee':enum('P','S'),'invoice_id':TXT,'payer_amount':Q,'payee_amount':Q}),
 'tax.close':obj({'period_start':DATE,'period_end_exclusive':DATE,'rate':maybe(Q),'rate_enacted':maybe(BOOL),'recovery_supported':maybe(BOOL),
  'temporary_difference_inventory_complete':maybe(BOOL),'return_tax_timing':enum('refund_and_recovered_stock_on_settlement','unknown'),
  'outside_basis_timing_control':maybe(BOOL),'outside_basis_no_foreseeable_reversal':maybe(BOOL)}),
 'ownership.purchase':obj({'new_parent_fraction':Q,'consideration':Q,'control_retained':maybe(BOOL),'same_rights_per_share':maybe(BOOL)})}
def schemas():
 s={'State':obj({**FACTS,'sequence':I,'flows':arr(obj({**FLOW['properties'],'date':DATE}))}),
 'Event':{'oneOf':[obj({'method':{'const':k},'date':DATE,'currency':{'const':'USD'},'parameters':v}) for k,v in PARAMETERS.items()]},
 'SchemaLock':obj({'schema':BLOB,'contract':BLOB}),
 'SourceSupport':obj({'pdf':BLOB,'text':BLOB,'reading':BLOB,'anchors':arr(TXT),'status':{'const':'historical_conditional_not_current_admission'}}),
 'Profile':obj({'name':{'const':'CompanyComposition/1'},'lock':ref('SchemaLock'),'source':ref('SourceSupport'),'execution':{'const':'documentary_only'},'sector':{'const':'nonfinancial_corporate'},'interest_cash_policy':{'const':'operating'}}),
 'View':obj({'profile':ref('Profile'),'revision':I,'information_mode':{'const':'archival_synthetic'}}),
 'Basis':obj({'opening':ref('State'),'event':ref('Event'),'view':ref('View'),'profile':ref('Profile'),'event_identity':TXT}),
 'Authorization':obj({'basis':ref('Basis'),'posting_permitted':{'const':True},'facts':{'const':'supplied_synthetic'}}),
 'Proposal':obj({'basis':ref('Basis'),'authorization':ref('Authorization'),'closing':ref('State'),'journals':JOURNALS,'cash':arr(FLOW)}),
 'Receipt':obj({'request':ref('Request'),'proposal':ref('Proposal'),'opening':ref('State'),'closing':ref('State'),'generation':I}),
 'Report':obj({'opening':ref('State'),'closing':ref('State'),'start':DATE,'end':DATE,'group':vector(GROUP_VALUES),
  'legal':obj({e:vector(['cash','profit','equity','taxable_income']) for e in ['P','S']}),'scope':{'const':'joined_finite_company_conditional'}})}
 args={'authorize':obj({'basis':ref('Basis')}),'propose':obj({'basis':ref('Basis'),'authorization':ref('Authorization')}),
 'commit':obj({'proposal':ref('Proposal')}),'report':obj({'opening':ref('State'),'closing':ref('State'),'start':DATE,'end':DATE})}
 s['Request']={'oneOf':[obj({'identity':TXT,'operation':{'const':op},'profile':ref('Profile'),'view':ref('View'),'head':ref('State'),'arguments':a}) for op,a in args.items()]}
 output={'oneOf':[ref(k) for k in ['Authorization','Proposal','Receipt','Report']]}
 s['Result']=obj({'request':ref('Request'),'status':enum('completed','replayed','rejected','partial','unsupported'),
  'diagnostic':maybe(TXT),'outputs':arr(output)})
 return {'$schema':'https://json-schema.org/draft/2020-12/schema','$defs':s,'schema_ids':{k:sid(k) for k in s}}
