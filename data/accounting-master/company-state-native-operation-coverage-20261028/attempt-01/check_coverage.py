"""Source-reviewed dependency inventory and bounded native guard controls."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'data/accounting-master/company-state-population-admission-20261028'))
import admission
rel=admission.rel
import operations
PLAN='docs/plans/company-state-native-operation-coverage-20261028.md'
INPUT='data/accounting-master/company-operation-path-20261023/example.json'
HERE='data/accounting-master/company-state-native-operation-coverage-20261028'

# This is a source-inspected registry, not automatic dependency extraction.
SPEC=[
('purchase',['payload.units','payload.claim_id','inventory.unit_cost','inventory_units','claims'],['fresh_claim_id','nonnegative_units'],['inventory','payables'],['inventory_units','claims'],['actual_goods_title','supplier_identity']),
('delivery',['payload.units','payload.unit_price','payload.control_transferred','payload.claim_id','inventory.unit_cost','inventory_units','claims'],['fresh_claim_id','control_transferred','inventory_sufficient'],['receivables','revenue','cost_of_sales','inventory'],['inventory_units','claims'],['legal_control_evidence','customer_identity']),
('supplier_payment',['payload.allocations','claims.ledger','claims.outstanding','cash'],['no_duplicate_allocation','recognised_claim','correct_ledger','no_over_settlement','cash_available'],['payables','cash'],['claims.settled','claims.outstanding','operating_flows'],['payment_authority','bank_finality']),
('collection',['payload.allocations','claims.ledger','claims.outstanding'],['no_duplicate_allocation','recognised_claim','correct_ledger','no_over_settlement'],['cash','receivables'],['claims.settled','claims.outstanding','operating_flows'],['actual_receipt','counterparty']),
('facility_draw',['loan.principal','facility.id','facility.limit','facility.reserved','facility.eligible','facility_drawn'],['known_eligible','principal_within_headroom'],['cash','debt'],['facility_drawn','financing_flows'],['actual_facility_right','lender_funding']),
('facility_interest',['loan.principal','loan.annual_rate','loan.day_count','loan.interest_cash_class','facility_draw.at','facility_repayment.at','cash'],['bridge_dates','cash_available'],['interest','cash'],['operating_flows'],['fees','variable_coupon_terms']),
('facility_repayment',['loan.principal','facility_drawn','cash'],['no_undrawn_repayment','cash_available'],['debt','cash'],['facility_drawn','financing_flows'],['prepayment_terms','redraw_rights']),
('payroll',['payload.amount','cash'],['nonnegative_amount','cash_available'],['payroll','cash'],['operating_flows'],['employee_population','payroll_accruals']),
('plant_addition',['payload.asset_id','payload.cost','payload.life','payload.in_service','operation.at','period','assets','cash'],['fresh_asset_id','positive_life','service_not_before_acquisition','supported_service_timing','cash_available'],['plant_cost','cash'],['assets','investing_flows','plant_additions'],['legal_title','location','disposal_rules']),
('depreciation',['assets.cost','assets.life','assets.accumulated','assets.in_service','period.start','depreciation_method'],['service_eligibility','remaining_cost_cap'],['depreciation','accum_depreciation'],['assets.accumulated'],['impairment','residual_values','midyear_proration']),
('interest',['debt.principal','debt.fixed_rate','debt.floating_rate','debt.floating_share','debt.coupon_years','cash'],['annual_coupon_only','share_domain','cash_available'],['interest','cash'],['operating_flows'],['term_structure','reset_calendar','covenants']),
('tax',['revenue','temporary_expense_accounts','tax.rate','tax.method','cash'],['nonnegative_pretax_income','tax_rate_domain','cash_available'],['tax','cash'],['operating_flows'],['loss_carryforwards','tax_basis_differences','deferred_tax']),
('dividend',['payload.amount','cash','retained'],['nonnegative_amount','cash_available'],['retained','cash'],['dividends','financing_flows'],['legal_distributability','board_authority','shareholder_rights']),
('close',['all_temporary_accounts','retained','opening_balances','flows','dividends'],['final_operation','balance_identity','indirect_cfo_identity','equity_bridge'],['all_temporary_accounts','retained'],['income','profit','annual_report','closing_memory'],['regulatory_reporting','historical_source_admission'])
]

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    path=json.loads((ROOT/INPUT).read_text());sp=path['initial_year']['source']['path'];source=(ROOT/sp).read_bytes()
    checks=[];controls={}
    def check(n,a,b):checks.append(dict(name=n,passed=a==b,actual=a,expected=b))
    def op(p,kind):return next(o for o in p['initial_year']['operations'] if o['kind']==kind)
    def execute(p):return admission.inspect(p,source,rel.native.digest(p))
    native_kinds={x['properties']['kind']['const'] for x in operations.schema()['properties']['operations']['items']['oneOf']}
    registry=[dict(kind=k,reads=reads,guards=guards,accounts_written=accounts,memory_or_reports_written=memory,
                   unresolved_scope=unknown,inspection='native source reviewed; scoped exact controls separately listed')
              for k,reads,guards,accounts,memory,unknown in SPEC]
    check('exact native kind coverage',sorted(r['kind'] for r in registry),sorted(native_kinds))
    check('fourteen unique kinds',len(registry),14)
    check('all kinds have explicit dependencies',all(r['reads'] and r['guards'] and r['accounts_written'] and r['unresolved_scope'] for r in registry),True)
    baseline=execute(path);check('baseline native complete',baseline['native_result']['status'],'complete_conditional')
    applied=[j for y in baseline['native_result']['years'] for j in y['run']['journals']]
    check('all kinds actually in baseline',sorted({j['kind'] for j in applied}),sorted(native_kinds))
    mutations=[
      ('ineligible facility',lambda p:p['initial_year']['facility'].update(eligible=False),'funding_failure','known_ineligible_facility'),
      ('reserved facility headroom',lambda p:p['initial_year']['facility'].update(reserved='20/1'),'funding_failure','facility_headroom'),
      ('payroll cash shortage',lambda p:op(p,'payroll')['payload'].update(amount='1000000/1'),'funding_failure','cash_shortfall'),
      ('dividend cash shortage',lambda p:op(p,'dividend')['payload'].update(amount='1000000/1'),'funding_failure','cash_shortfall'),
      ('interest cash shortage',lambda p:p['initial_year']['debt'].update(fixed_rate='100/1',floating_rate='100/1'),'funding_failure','cash_shortfall'),
      ('facility interest cash shortage',lambda p:p['initial_year']['loan'].update(annual_rate='100/1'),'funding_failure','cash_shortfall'),
      ('loan fee unsupported',lambda p:p['initial_year']['loan'].update(fee='1/1'),'unsupported','loan_fee'),
      ('tax rate outside domain',lambda p:p['initial_year']['tax'].update(rate='2/1'),'invalid','fraction_domain'),
      ('unknown tax rate',lambda p:p['initial_year']['tax'].update(rate='unknown'),'unresolved',None),
      ('close not final',lambda p:p['initial_year']['operations'].append(dict(id='after-close',kind='dividend',at='2025-12-31T23:00:00Z',payload=dict(amount='0/1'))),'invalid','annual_dependencies'),
    ]
    def loss(p):
        for o in p['initial_year']['operations']:
            if o['kind']=='delivery':o['payload']['unit_price']='1/1'
            if o['kind']=='collection':
                for a in o['payload']['allocations']:
                    if a['claim_id'].startswith('sales-ar'):a['amount']='5/1'
        p['initial_year']['loan']['principal']='10/1'
    # Income loss may meet an earlier funding veto. Preserve the actual native
    # outcome rather than assuming the loss-tax branch is reachable.
    for name,mutate,status,reason in mutations:
        p=deepcopy(path);mutate(p);r=execute(p);n=r['native_result'];run=n['years'][-1]['run'] if n.get('years') else n
        check(name+' status',run['status'],status)
        if reason is not None:check(name+' reason',run.get('reason'),reason)
        else:check(name+' unresolved obligations',bool(run.get('obligations')),True)
        check(name+' native full result preserved',n,rel.native.wire(rel.native.execute(p,source)))
        check(name+' no false full company admission',r['full_company_constructor'],False)
        controls[name]=r
    # No unsupported method is inferred merely because baseline execution passed.
    inventory=dict(profile='NativeCompanyOperationDependencyInventory/1',
        scope='Source-inspected CompanyOperationsDraft/1 and its current native annual path only',
        operations=registry,global_requirements=[
          'closed schema, canonical nonnegative rational inputs and source/opening/context identities',
          'full calendar year, chronological operations, single-operation cardinality and annual-tail dates',
          'opening ledger balance, homogeneous inventory cost, claim totals and asset totals',
          'debt/facility controls and supported method constants',
          'nonnegative intermediate cash, balanced journal and claim/asset control totals after each applied event'],
        reporting_dependencies=['opening balances','annual income accumulated before close','classified cash flows','all dated journals','closing balances'],
        carry_dependencies=['consecutive periods','facility identity','complete prior run','claim lifetime carry','asset service/life/accumulation','conditional origin chain'],
        limitations=['guard inventory is source-reviewed, not a generic static extractor',
          'not every guard is independently exercised in this continuation',
          'no actual source, actor, legal or standards admission',
          'other profiles and sectors remain separate responsibilities'])
    failed=[c for c in checks if not c['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),failed=failed,kinds=len(registry),controls=len(controls))
    files={Path(__file__),Path(admission.__file__),ROOT/PLAN,ROOT/INPUT,ROOT/sp}
    for m in list(sys.modules.values())+[rel.native,rel.native.reports,rel.native.annual_path]:
        f=getattr(m,'__file__',None)
        if f and Path(f).is_file() and Path(f).resolve().is_relative_to(ROOT):files.add(Path(f).resolve())
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=sys.version,
        cpu_gpu='CPU-only source inspection and exact native execution; no accelerator imports',random_seeds='N/A deterministic',
        data_version='Original full path and native schema/executor',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
        plan_file=PLAN,result_file=HERE+'/result.md',source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    for name,x in [('inventory',inventory),('baseline',baseline),('controls',controls),('checks',checks),('verification',v),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(x,indent=2)+chr(10))
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
