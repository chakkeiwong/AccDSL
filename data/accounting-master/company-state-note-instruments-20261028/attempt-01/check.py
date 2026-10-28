"""Source population, independent terms and native type-refusal checks."""
import argparse
from copy import deepcopy
from datetime import date,datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import instruments as a
ROOT,H=a.ROOT,Path(__file__).resolve().parent
PLAN='docs/plans/company-state-note-instruments-20261028.md'
BUDGET=dict(max_slots=0,max_formula_nodes=10000,max_integer_assignments=1,max_cells=1,elapsed_ms=5000,solver_timeout_ms=1000,solver_rlimit=1000000)
DEBT='data/accounting-master/company-state-debt-source-20261028/attempt-01/source-to-state.json'
TIMING='data/accounting-master/company-state-source-timing-20261028/attempt-01/source-time-card.json'
DEPENDENCIES='data/accounting-master/company-cases-current-20261028/attempt-01/current-decisions.json'
TARGETS='data/accounting-master/selected-reading-history-20261027/attempt-01/result.json'
EXPECTED=[
 ('The 0.000% 2025 Notes','EUR',1000000000,'2019-11-15','0','2025-11-15','annually',['November 15'],'2020-11-15',0),
 ('The 0.875% 2025 Notes','EUR',1250000000,'2017-05-24','7/800','2025-05-24','annually',['May 24'],'2018-05-24',10937500),
 ('The 2026 Notes','EUR',1400000000,'2014-11-10','13/800','2026-11-10','annually',['November 10'],'2015-11-10',22750000),
 ('The 2027 Notes','EUR',1000000000,'2015-09-17','1/50','2027-09-17','annually',['September 17'],'2016-09-17',20000000),
 ('The 1.375% 2029 Notes','EUR',1250000000,'2017-05-24','11/800','2029-05-24','annually',['May 24'],'2018-05-24',17187500),
 ('The 3.050% 2029 Notes','GBP',750000000,'2015-07-31','61/2000','2029-07-31','semi-annually',['January 31','July 31'],'2016-01-31',22875000),
 ('The 2031 Notes','EUR',1000000000,'2019-11-15','1/200','2031-11-15','annually',['November 15'],'2020-11-15',5000000),
 ('The 2042 Notes','GBP',500000000,'2015-07-31','9/250','2042-07-31','semi-annually',['January 31','July 31'],'2016-01-31',18000000)]
def dump(path,value):path.write_text(json.dumps(value,indent=2)+chr(10))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    checks=[];controls=[];native=[]
    def ck(name,actual,expected):checks.append(dict(name=name,passed=actual==expected,actual=actual,expected=expected))
    card=a.construct();before=deepcopy(card);source=(ROOT/a.TEXT).read_text();ck('source regeneration validates',a.validate(card),True)
    ck('exact eight-series population',[r['source_heading'] for r in card['rows']],[r[0] for r in EXPECTED])
    for r,e in zip(card['rows'],EXPECTED):
        heading,currency,amount,issued,rate,maturity,frequency,monthdays,first,coupon=e;prefix=r['id']
        expected=dict(currency=currency,issue_date=issued,issued_principal=a.fmt(amount),observation_date='2024-10-18',outstanding_principal=a.fmt(amount),annual_rate=a.fmt(rate),maturity_label=maturity,payment_frequency=frequency,payment_month_days=monthdays,first_payment_label=first)
        ck(prefix+'/all independent terms',{k:r[k] for k in expected},expected)
        span=r['source_span'];ck(prefix+'/exact retained quote',source[span['start']:span['end_exclusive']],span['quote'])
        ck(prefix+'/quote hash',sha256(span['quote'].encode()).hexdigest(),span['quote_sha256'])
        ck(prefix+'/physical page',span['physical_page'],63 if len([x for x in EXPECTED[:EXPECTED.index(e)+1]])<=5 else 64)
        for key,quantity,when,value,dims in [('issued_principal','issued_principal',issued,amount,{'currency:'+currency:1}),('outstanding_principal','outstanding_principal','2024-10-18',amount,{'currency:'+currency:1}),('annual_rate','annual_rate','2024-10-18',Q(rate),{'time:year':-1})]:
            obs=r['native_observations'][key];ck(prefix+'/'+key+'/native type',a.temporal.measurement_type(obs['type']),obs['type'])
            ck(prefix+'/'+key+'/date',obs['type']['time'],dict(kind='instant',at=when))
            ck(prefix+'/'+key+'/dimension',obs['type']['value_type']['dimensions'],dims)
            ck(prefix+'/'+key+'/value',[obs['interval']['lower'],obs['interval']['upper']],[a.fmt(value)]*2)
            ck(prefix+'/'+key+'/meaning',obs['type']['quantity'],prefix+'.'+quantity)
        ck(prefix+'/nominal full-year coupon',r['conditional_nominal_annual_coupon']['amount'],a.fmt(coupon))
        ck(prefix+'/coupon annualized dimension',r['conditional_nominal_annual_coupon']['annualized_product_type']['dimensions'],{'currency:'+currency:1,'time:year':-1})
        ck(prefix+'/coupon amount dimension',r['conditional_nominal_annual_coupon']['native_amount_type']['dimensions'],{'currency:'+currency:1})
        ck(prefix+'/unknown mappings',[r[k] for k in ['isin','effective_settlement_dates','reported_carrying_amount','as_of_2024_09_28_outstanding','governing_instrument_instance']],[None]*5)
        ck(prefix+'/no admission',[r['source_admission'],r['accounting_admission']],[False,False])
    ck('qualification span population',[x['id'] for x in card['qualification_spans']],[x[0] for x in a.QUALIFICATIONS])
    for r in card['qualification_spans']:
        sp=r['source_span'];ck(r['id']+'/exact qualification',source[sp['start']:sp['end_exclusive']],sp['quote'])
        ck(r['id']+'/qualification hash',sha256(sp['quote'].encode()).hexdigest(),sp['quote_sha256'])
    ck('no full-debt population',[card['population']['complete_company_term_debt'],card['population']['legal_instrument_ids_complete']],[False,False])
    for field in ['as_of_note9_link','executable_opening','policy_input','probability_model']:ck('no invented '+field,card[field],None)
    for currency,amount in [('EUR',6900000000),('GBP',1250000000)]:
        ck(currency+'/selected principal only',a.fmt(sum(Q(r['outstanding_principal']) for r in card['rows'] if r['currency']==currency)),a.fmt(amount))
    ck('observation gap days',(date(2024,10,18)-date(2024,9,28)).days,20)
    ck('two2025 stated maturities are Saturdays',[date.fromisoformat(card['rows'][i]['maturity_label']).weekday() for i in [0,1]],[5,5])
    deps=json.loads((ROOT/DEPENDENCIES).read_text());targets=json.loads((ROOT/TARGETS).read_text())
    card['preserved_issuer_dependencies']=deepcopy(deps['rows'])
    card['preserved_target_obligations']={k:deepcopy(v['target_obligations']) for k,v in targets['attachments'].items()}
    ck('full15 issuer rows',card['preserved_issuer_dependencies'],deps['rows']);ck('issuer count',len(deps['rows']),15)
    ck('full180 target obligations',sum(len(v) for v in card['preserved_target_obligations'].values()),180)
    ck('all original targets unready',all(x['original_target_ready'] is False for x in deps['rows']),True)
    # The bound source-summary object stays separate from the preserved dependency envelope.
    original=deepcopy(before)
    mutations=[('omitted series',lambda c:c['rows'].pop()),('duplicated series',lambda c:c['rows'].append(deepcopy(c['rows'][0]))),('wrong amount',lambda c:c['rows'][0].update(outstanding_principal='1/1')),('wrong observation date',lambda c:c['rows'][0].update(observation_date='2024-09-28')),('wrong currency',lambda c:c['rows'][0].update(currency='USD')),('false population completion',lambda c:c['population'].update(complete_company_term_debt=True)),('invented ISIN',lambda c:c['rows'][0].update(isin='invented')),('invented settlement date',lambda c:c['rows'][0].update(effective_settlement_dates=['2025-11-17'])),('false source admission',lambda c:c.update(source_admission=True)),('wrong source hash',lambda c:c['source'].update(pdf_sha256='0'*64)),('changed quote',lambda c:c['rows'][0]['source_span'].update(quote='unsupported')),('wrong native currency',lambda c:c['rows'][0]['native_observations']['outstanding_principal']['type']['value_type'].update(dimensions={'currency:USD':1})),('dropped qualifications',lambda c:c['qualification_spans'].clear()),('unsupported Note9 allocation',lambda c:c.update(as_of_note9_link={'amount':'1000000000/1'})),('false maturity observation',lambda c:c['rows'][0]['native_observations']['outstanding_principal']['type'].update(time=dict(kind='instant',at='2025-11-15')))]
    for name,mutate in mutations:
        altered=deepcopy(original);mutate(altered)
        try:a.validate(altered);reason=None
        except ValueError as exc:reason=str(exc)
        ck('reject/'+name,reason,'source_semantic_binding');controls.append(dict(id=name,reason=reason,altered_card_sha256=a.digest(altered)))
    eur=original['rows'][0]['native_observations']['outstanding_principal'];gbp=original['rows'][5]['native_observations']['outstanding_principal']
    issued=original['rows'][0]['native_observations']['issued_principal']
    for name,x,y,reason in [('cross_currency',eur,gbp,'economic_context_mismatch'),('same_currency_wrong_date',eur,issued,'same_time_mismatch')]:
        definition=a.pair_relation(x,y);result=a.temporal.assess(definition,BUDGET)
        ck(name+'/invalid',result['status'],'invalid');ck(name+'/reason',result.get('reason'),reason)
        native.append(dict(id=name,definition=definition,result=result))
    # Equal monetary values can pass scalar equality but never establish series identity.
    other=original['rows'][3]['native_observations']['outstanding_principal']
    definition=a.pair_relation(eur,other);result=a.temporal.assess(definition,BUDGET)
    ck('equal values accepted as scalar relation',result['status'],'conditionally_feasible')
    ck('equal values have distinct source series',original['rows'][0]['id']==original['rows'][3]['id'],False)
    ck('equal values have distinct maturity',original['rows'][0]['maturity_label']==original['rows'][3]['maturity_label'],False)
    native.append(dict(id='equal_amount_different_series',definition=definition,result=result,interpretation='Scalar equality does not establish instrument identity or complete population'))
    debt=json.loads((ROOT/DEBT).read_text());ck('existing Note9 date preserved',debt['as_of'],'2024-09-28')
    ck('existing Note9 currency preserved',debt['unit'],'reported USD million')
    card['aggregate_debt_reference']=dict(path=DEBT,sha256=sha256((ROOT/DEBT).read_bytes()).hexdigest(),as_of=debt['as_of'],unit=debt['unit'],relation=None,reasons=['Different observation date','Different currency','Consolidated aggregate versus issuer-summary subset','Unallocated carrying/hedge adjustments','Unknown intervening transactions and governing series IDs'])
    card['source_timing_reference']=dict(path=TIMING,sha256=sha256((ROOT/TIMING).read_bytes()).hexdigest(),admission=False)
    receipts=[]
    for n in ['4-2','4-19','4-28']:
        p=ROOT/f'docs/design/cases/apple/continuation-20261007/sources/sec-annual-exhibit-{n}-trusted-v1.receipt.json';receipt=json.loads(p.read_text());body=ROOT/receipt['path']
        ck(n+'/retained denied response hash',sha256(body.read_bytes()).hexdigest(),receipt['sha256']);ck(n+'/HTTP refusal',receipt['http_status'],403)
        receipts.append(dict(receipt=str(p.relative_to(ROOT)),sha256=sha256(p.read_bytes()).hexdigest(),http_status=receipt['http_status'],body=receipt['path'],body_sha256=receipt['sha256'],is_contract=False))
    card['prior_access_failures']=receipts
    ck('source adapter remains immutable',original,before)
    paths={Path(__file__),H/'instruments.py',ROOT/PLAN,ROOT/a.PDF,ROOT/a.TEXT,ROOT/DEBT,ROOT/TIMING,ROOT/DEPENDENCIES,ROOT/TARGETS}
    paths.update(Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and Path(x.__file__).resolve().is_relative_to(ROOT))
    paths.update(ROOT/r['receipt'] for r in receipts);paths.update(ROOT/r['body'] for r in receipts)
    hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    renders={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted((H/'rendered').glob('*.png'))};ck('twelve read source renders',len(renders),12)
    # Retain compact checks; full source cards carry exact quotes and dependencies once.
    for row in checks:
        if len(json.dumps(row))>1500:
            row['actual_sha256']=a.digest(row.pop('actual'));row['expected_sha256']=a.digest(row.pop('expected'))
    failed=[x for x in checks if not x['passed']]
    verdict=dict(status='fail' if failed else 'pass',checks=len(checks),series=8,native_observations=24,semantic_controls=len(controls),native_relations=len(native),failed=failed,source_admission=False,complete_company_population=False)
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU-only source, native typing and exact rational checks; no GPU imports',random_seeds='N/A deterministic source mapping',data_version='Retained Apple2024 PDF and text; Exhibit4.1 outstanding2024-10-18',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes=hashes,render_hashes=renders)
    for name,obj in [('verification',verdict),('checks',checks),('source-instruments',card),('native-relations',native),('semantic-controls',controls),('independent-expected-terms',EXPECTED),('run-manifest',manifest)]:dump(out/(name+'.json'),obj)
    for n in ['instruments.py','check.py']:(out/n).write_bytes((H/n).read_bytes())
    print(json.dumps(verdict));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
