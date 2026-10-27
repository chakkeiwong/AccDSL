"""P11 bounded adapter discovery and captured exchanges, never mock promotion."""
from __future__ import annotations
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'docs/design/fixtures/p11'
TIMEOUT = 30
LEDGER_ORDER = ('beancount', 'ledger', 'hledger')
STATES = {'Passed','Failed','Unavailable','NotAttempted'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(command, timeout=TIMEOUT):
    start = time.monotonic()
    environment = dict(os.environ, CUDA_VISIBLE_DEVICES='-1', PYTHONDONTWRITEBYTECODE='1',
                       HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    try:
        result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True,
                                text=True, timeout=timeout, check=False)
        return {'command':list(command),'exit_code':result.returncode,'stdout':result.stdout,
                'stderr':result.stderr,'elapsed_seconds':time.monotonic()-start,'timeout':False}
    except subprocess.TimeoutExpired as exc:
        decode = lambda v: v.decode(errors='replace') if isinstance(v,bytes) else (v or '')
        return {'command':list(command),'exit_code':None,'stdout':decode(exc.stdout),
                'stderr':decode(exc.stderr),'elapsed_seconds':time.monotonic()-start,'timeout':True}
    except OSError as exc:
        return {'command':list(command),'exit_code':None,'stdout':'','stderr':str(exc),
                'elapsed_seconds':time.monotonic()-start,'timeout':False}


def probe_python(module, distribution):
    spec = importlib.util.find_spec(module)
    try:
        version = importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        version = None
    record = {'name':module,'distribution':distribution,'location':spec.origin if spec else None,
              'version':version,'status':'Unavailable','probe':None,'reason':'module absent in recorded interpreter'}
    if spec is not None:
        record['probe'] = capture([sys.executable,'-B','-c',
            f'import {module}; import importlib.metadata as m; print(m.version({distribution!r}))'])
        p = record['probe']
        record['status'] = 'Available' if (p['exit_code']==0 and not p['timeout'] and version and
                                          p['stdout'].strip()==version) else 'Failed'
        record['reason'] = 'version/import probe only' if record['status']=='Available' else 'version/import probe failed'
    return record


def probe_executable(name):
    found = shutil.which(name)
    row = {'name':name,'location':str(Path(found).resolve()) if found else None,
           'version':None,'status':'Unavailable','reason':'executable absent from captured PATH','probe':None}
    if found:
        row['probe'] = capture([row['location'],'--version'])
        p = row['probe']
        if p['exit_code']==0 and not p['timeout'] and p['stdout'].strip():
            row.update(status='Available',version=p['stdout'].splitlines()[0],reason='version probe only')
        else:
            row.update(status='Failed',reason='version probe failed')
    return row


def select_ledger(candidates):
    by_name = {c['name']:c for c in candidates}
    if len(candidates) != len(LEDGER_ORDER) or set(by_name) != set(LEDGER_ORDER):
        raise ValueError('all deterministic ledger candidates required')
    return next((name for name in LEDGER_ORDER if by_name[name]['status']=='Available'
                 and by_name[name]['version'] and by_name[name]['location']), None)


def source_evidence(repository):
    records = json.loads((ROOT/'docs/design/research/tools.json').read_text())['records']
    rows = [r for r in records if r['repository']==repository]
    if not rows:
        return {'repository':repository,'retained_sources':[],'licence':'not inspected'}
    r = rows[0]
    return {'repository':repository,'url':r['url'],'licence':r['github_license_detection'],
            'runtime_pin':False,'retained_sources':[{'path':p,'sha256':sha(ROOT/p),
                'matches_inspected_hash':sha(ROOT/p)==r['sha256'][p]} for p in r['local_files']]}


def request_record(family, engine, filenames, conventions, repository):
    failed_probe = engine and engine['status']=='Failed'
    return {'family':family,'status':'Failed' if failed_probe else 'Unavailable',
            'reason':engine['reason'] if engine else 'no selected local engine',
            'engine':engine,'source_evidence':source_evidence(repository),
            'inputs':[{'path':str((FIXTURES/name).relative_to(ROOT)), 'sha256':sha(FIXTURES/name),
                       'bytes':(FIXTURES/name).read_text()} for name in filenames],
            'conventions':conventions,'execution':None,'normalized_output':None,
            'diagnostics':[], 'evidence_class':'discovery_only',
            'limitations':['Synthetic bounded input; no real-filing completeness or accounting-validity claim.']}


def decode_exchange(execution):
    if execution['timeout']:
        raise ValueError('exchange timeout (limit is not a capability or performance verdict)')
    if execution['exit_code'] != 0:
        raise ValueError('exchange process failed')
    value = json.loads(execution['stdout'])
    if not isinstance(value,dict) or value.get('executed') is not True or 'result' not in value:
        raise ValueError('missing actual execution payload')
    return value


def validate_output(family, result):
    """Bounded semantic checks, independent of a worker's success flag."""
    from decimal import Decimal
    if not isinstance(result, dict):
        raise ValueError('normalized output must be an object')
    if family == 'QuantLib':
        pv = Decimal(str(result['present_value']))
        error = abs(pv - 100)
        if (not pv.is_finite() or error > Decimal('1e-10') or
                Decimal(str(result['absolute_error'])) != error or
                result['year_fraction'] != 1 or result['currency'] != 'USD' or
                result.get('evaluation_date') != '2025-12-31' or
                result.get('payment_date') != '2026-12-31' or
                result['evaluation_date_restored'] is not True):
            raise ValueError('valuation semantics mismatch')
    elif family == 'Arelle':
        if result.get('diagnostics') != []:
            raise ValueError('XBRL loader diagnostics require repair')
        facts = result['facts']
        if len(facts) != 3 or [f['value'] for f in facts] != ['95', '96', None]:
            raise ValueError('fact preservation mismatch')
        for index, fact in enumerate(facts):
            if (fact['id'] != f'f{index+1}' or fact['qname'] != '{urn:accdsl:p11}Cash' or
                    fact['entity'] != ['urn:synthetic', 'Acme'] or fact['context'] != 'c1' or
                    fact['period_end'] != '2026-01-01T00:00:00' or fact['dimensions'] or
                    fact['unit'] != 'USD' or fact['decimals'] != '0' or
                    fact['nil'] != (index == 2)):
                raise ValueError('XBRL context or unit preservation mismatch')
    elif family == 'ledger':
        expected = {'Assets:Cash':90, 'Liabilities:Debt':-100,
                    'Equity:Retained':10, 'Expenses:Interest':0}
        balances = {k:Decimal(v) for k,v in result['balances'].items()}
        if balances != expected or result['errors']:
            raise ValueError('ledger balance mismatch')
        tx = result['transactions']
        if [t['date'] for t in tx] != ['2025-12-31', '2026-12-31', '2026-12-31']:
            raise ValueError('ledger dates mismatch')
        expected_postings = [
            {'Assets:Cash':95, 'Liabilities:Debt':-100, 'Equity:Retained':5},
            {'Expenses:Interest':5, 'Assets:Cash':-5},
            {'Equity:Retained':5, 'Expenses:Interest':-5}]
        for transaction, wanted in zip(tx, expected_postings):
            postings = transaction['postings']
            if (len(postings) != len(wanted) or any(p['currency'] != 'USD' for p in postings) or
                    {p['account']:Decimal(p['amount']) for p in postings} != wanted):
                raise ValueError('ledger postings mismatch')
    elif family == 'Docling':
        if (result.get('status') != 'success' or not result.get('document') or
                result.get('table_cells') != [['Account','USD'],['Cash','90'],['Debt','100']]):
            raise ValueError('document table semantics mismatch')
    else:
        raise ValueError('no reviewed output validator for this adapter')


def run_exchange(row, backend):
    engine = row['engine']
    if not engine or engine['status'] != 'Available':
        return
    row['execution'] = capture([sys.executable,'-B',str(Path(__file__).resolve()),'--exchange',backend,
                                engine['version'],engine['location']])
    row['evidence_class'] = 'upstream_execution_attempt'
    try:
        response = decode_exchange(row['execution'])
        if response['version'] != engine['version'] or response['location'] != engine['location']:
            raise ValueError('engine version/location drift')
        validate_output(row['family'], response['result'])
        row['normalized_output'] = response['result']
        row['status'] = 'Passed'
        row['reason'] = 'captured upstream execution and bounded semantic assertions passed'
    except (ValueError,KeyError,TypeError,ArithmeticError) as exc:
        row['status'] = 'Failed'
        row['reason'] = str(exc)


def collect():
    inventory = [probe_python(m,d) for m,d in [('arelle','arelle-release'),('QuantLib','QuantLib'),
                                             ('docling','docling'),('beancount','beancount')]]
    inventory += [probe_executable(n) for n in ('ledger','hledger','actus')]
    by_name = {r['name']:r for r in inventory}
    ledger_candidates = [by_name[n] for n in LEDGER_ORDER]
    selected = select_ledger(ledger_candidates)
    rows = [request_record('Arelle',by_name['arelle'],['facts.xbrl','demo.xsd','xbrl-local.xsd'],
                {'currency':'USD','period':'instant 2025-12-31','calendar':'Gregorian',
                 'decimals':'0','dimensions':[],'nil':'missing','duplicates':'preserve each','scale':'no inline transform in XML fixture'},'Arelle/Arelle'),
            request_record('ACTUS',by_name['actus'],['loan.json'],
                {'currency':'USD','day_count':'Actual/365','calendar':'NC','business_day':'NOS',
                 'rate':'annual_simple','payoff_sign':'borrower negative for payments'},'actusfrf/actus-service'),
            request_record('QuantLib',by_name['QuantLib'],['valuation.json'],
                {'currency':'USD','day_count':'Actual365Fixed','calendar':'NullCalendar','business_day':'Unadjusted',
                 'rate':'annual_effective','tolerance_usd':'1e-10'},'lballabio/QuantLib'),
            request_record('Docling',by_name['docling'],['table.html'],
                {'currency':'USD as literal header only','calendar':'N/A document layout',
                 'page':'HTML has no physical pagination; PDF/page-bounds exchange remains unsupported',
                 'assets':'HTML backend only; CPU; no download'},'docling-project/docling'),
            request_record('ledger',by_name[selected] if selected else None,['journal.beancount','journal.ledger'],
                {'currency':'USD','calendar':'Gregorian dates; no adjustments','sign':'debit positive, credit negative',
                 'rounding':'explicit exact cent postings','symbolic':'unsupported'},'beancount/beancount')]
    for row, backend in zip(rows,('arelle','actus','QuantLib','docling',selected)):
        if backend=='actus' and row['engine']['status']=='Available':
            row.update(status='NotAttempted',reason='No reviewed local ACTUS wire protocol/version mapping; no service provisioned')
        elif backend in ('ledger','hledger'):
            row.update(status='NotAttempted',reason='CLI backend discovered; its output translator requires version-specific validation')
        elif backend:
            run_exchange(row,backend)
    # A broken/timeout probe is not evidence that the tool is absent. Keep all
    # candidate records and do not select another backend after an exchange.
    if selected is None and any(c['status']=='Failed' for c in ledger_candidates):
        rows[-1].update(status='Failed',reason='No ledger selected; one or more candidate probes failed',
                        diagnostics=[{'candidate':c['name'],'reason':c['reason']}
                                     for c in ledger_candidates if c['status']=='Failed'])
    return {'inventory':inventory,'ledger_selection':{'order':list(LEDGER_ORDER),
             'candidates':ledger_candidates,'selected_backend':selected,'fallback_after_failure':False},
            'adapters':rows,'discovery_scope':{'interpreter':sys.executable,'PATH':os.environ.get('PATH',''),
             'local_engine_candidates':['vendor/actus-service.jar','vendor/actus/actus-service.jar'],
             'local_candidate_exists':[(ROOT/p).exists() for p in ['vendor/actus-service.jar','vendor/actus/actus-service.jar']],
             'network_access':'none; no engine or asset download','installs':'none'}}


def validate_record(row):
    if row['status'] not in STATES:
        raise ValueError('unknown status')
    for item in row['inputs']:
        if hashlib.sha256(item['bytes'].encode()).hexdigest()!=item['sha256'] or sha(ROOT/item['path'])!=item['sha256']:
            raise ValueError('input hash mismatch')
    if row['status']=='Passed':
        engine, execution = row['engine'], row['execution']
        if not engine or not engine['version'] or not engine['location'] or not execution:
            raise ValueError('Passed without version/location/execution')
        result = decode_exchange(execution)
        if result['version']!=engine['version'] or result['location']!=engine['location']:
            raise ValueError('version drift')
        if row['normalized_output']!=result['result'] or row['evidence_class']!='upstream_execution_attempt':
            raise ValueError('uncaptured normalized result')
        validate_output(row['family'], result['result'])
    elif row['status']=='Unavailable' and (row['execution'] or row['normalized_output'] is not None):
        raise ValueError('Unavailable cannot claim an exchange')
    return True


def exchange(backend, version, location):
    """Isolated upstream calls. stdout contains the complete exchange JSON."""
    distribution = {'QuantLib':'QuantLib','beancount':'beancount','arelle':'arelle-release','docling':'docling'}[backend]
    actual_version = importlib.metadata.version(distribution)
    actual_location = importlib.util.find_spec(backend).origin
    if (version,location)!=(actual_version,actual_location):
        raise ValueError('engine pin drift')
    if backend=='QuantLib':
        import QuantLib as ql
        request = json.loads((FIXTURES/'valuation.json').read_text())
        settings = ql.Settings.instance()
        before = settings.evaluationDate
        try:
            date = ql.DateParser.parseISO(request['evaluation_date'])
            end = ql.DateParser.parseISO(request['payment_date'])
            settings.evaluationDate = date
            day_count = ql.Actual365Fixed()
            yf = day_count.yearFraction(date,end)
            curve = ql.FlatForward(date,float(request['yield']),day_count,ql.Compounded,ql.Annual)
            pv = float(request['amount'])*curve.discount(end)
            if yf!=1 or abs(pv-100)>float(request['absolute_tolerance_usd']):
                raise ValueError('QuantLib reference mismatch')
            from decimal import Decimal
            result = {'present_value':pv,'absolute_error':str(abs(Decimal(str(pv))-100)),
                      'year_fraction':yf,'currency':request['currency'],
                      'evaluation_date':request['evaluation_date'],'payment_date':request['payment_date']}
        finally:
            settings.evaluationDate = before
        if settings.evaluationDate!=before:
            raise ValueError('evaluation date leaked')
        result['evaluation_date_restored'] = True
    elif backend=='beancount':
        from beancount import loader
        from beancount.core import data
        entries, errors, _ = loader.load_file(str(FIXTURES/'journal.beancount'))
        if errors:
            raise ValueError(repr(errors))
        transactions = []
        balances = {}
        for e in entries:
            if isinstance(e,data.Transaction):
                postings=[]
                for p in e.postings:
                    if p.units.currency!='USD': raise ValueError('currency mismatch')
                    postings.append({'account':p.account,'amount':str(p.units.number),'currency':p.units.currency})
                    balances[p.account]=balances.get(p.account,0)+p.units.number
                transactions.append({'date':e.date.isoformat(),'postings':postings})
        if {k:str(v) for k,v in balances.items()} != {'Assets:Cash':'90','Liabilities:Debt':'-100',
                                                            'Equity:Retained':'10','Expenses:Interest':'0'}:
            raise ValueError('ledger balance mismatch')
        result={'transactions':transactions,'balances':{k:str(v) for k,v in balances.items()},'errors':[]}
    elif backend=='arelle':
        from arelle import Cntlr
        cntlr=Cntlr.Cntlr(logFileName='logToBuffer',disable_persistent_config=True)
        cntlr.webCache.workOffline=True
        model=cntlr.modelManager.load(str(FIXTURES/'facts.xbrl'))
        try:
            facts=[{'id':f.id,'qname':f.qname.clarkNotation,'context':f.contextID,
                    'entity':list(f.context.entityIdentifier),'period_end':f.context.instantDatetime.isoformat(),
                    'dimensions':{str(k):str(v) for k,v in f.context.qnameDims.items()},'unit':f.unitID,
                    'decimals':f.decimals,'nil':f.isNil,'value':None if f.isNil else f.value} for f in model.facts]
            if len(facts)!=3 or [f['value'] for f in facts]!=['95','96',None]:
                raise ValueError('fact preservation mismatch')
            result={'facts':facts,'diagnostics':list(model.errors),'inline_scale_checked':False}
        finally:
            model.close(); cntlr.close()
    else:
        from docling.datamodel.base_models import InputFormat
        from docling.document_converter import DocumentConverter
        conversion=DocumentConverter(allowed_formats=[InputFormat.HTML]).convert(FIXTURES/'table.html')
        tables = conversion.document.tables
        cells = [[cell.text for cell in row] for row in tables[0].data.grid] if tables else []
        result={'document':conversion.document.export_to_dict(),'status':conversion.status.value,
                'physical_page_bounds':None, 'table_cells':cells}
        if cells != [['Account','USD'],['Cash','90'],['Debt','100']]:
            raise ValueError('missing table content')
    print(json.dumps({'executed':True,'version':actual_version,'location':actual_location,'result':result}))


if __name__=='__main__':
    if len(sys.argv)!=5 or sys.argv[1]!='--exchange':
        raise SystemExit('internal --exchange BACKEND VERSION LOCATION only')
    exchange(*sys.argv[2:])
