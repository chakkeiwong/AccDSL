"""Compose existing fiscal and indirect reports under explicit fixture policies."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import declared_indirect_cash_v2 as bridge

PIN='5b8a9c2d74a834a7d5cc7abaa82c80a61da9459cc8fcb349ba04645017aef3e9'


def fixture(chart='named',case='loss-service-finance'):
    assert sha256(Path(bridge.__file__).read_bytes()).hexdigest()==PIN
    folder=ROOT/'data/accounting-master/insurance-fiscal-book-20261025'
    accepted=json.loads((folder/'acceptance-manifest.json').read_text())
    for name,expected in accepted['artifacts'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    index=json.loads((folder/'evidence.json').read_text())
    name=chart+'.'+case+'.complement'
    row=next(r for r in index['cases'] if r['name']==name)
    p=ROOT/row['path'];assert sha256(p.read_bytes()).hexdigest()==row['sha256']
    return json.loads(p.read_text())


def policy(row,year,variant='split'):
    assert year in [2025,2026,2027] and variant in ['split','all_noncash']
    source=row['result']['program'];roles=row['request']['base_request']['roles']
    methods={}
    indices=[] if year==2025 else [1,2,3] if year==2026 else [4,5,6]
    for index in indices:
        entry=source['registry']['entries']['insurance.'+str(index)]
        part=(index-1)%3;account_map={};profit={}
        if part!=2:
            account_map[roles['liability']]='noncash_profit' if part==0 or variant=='all_noncash' else 'working_capital'
        for posting in entry['method']['monetary']['definition']['postings']:
            role=posting['account']
            if role in ['finance_expense','revenue','loss_reversal','claims_expense']:
                profit[roles[role]]='operating'
        methods[entry['method_sha256']]={'accounts':account_map,'profit_accounts':profit,
            'premise':'Supplied illustrative '+variant+' explanation for native insurer method '+str(index)+
                '; reconciliation does not admit or uniquely determine accounting classification.'}
    return {'profile':bridge.POLICY,'context':deepcopy(source['opening']['context']),'methods':methods}


def exchange(row,year,variant='split'):
    q=bridge.request(row['result']['program'],row['result']['execution'],
                     'insurance.fiscal.close.'+str(year),policy(row,year,variant))
    result=bridge.report(q);assert result['status']=='explained_provisional',result
    p={2025:'0/1',2026:'-5/1',2027:'10/1'}[year]
    cash={2025:'0/1',2026:'-50/1',2027:'-45/1'}[year]
    working={2025:'0/1',2026:'-55/1',2027:'-50/1'}[year] if variant=='split' else '0/1'
    noncash=({2025:'0/1',2026:'10/1',2027:'-5/1'} if variant=='split' else
             {2025:'0/1',2026:'-45/1',2027:'-55/1'})[year]
    expected={'profit':p,'working_capital':working,'noncash_profit':noncash,
        'nonoperating_profit_adjustment':'0/1','indirect_operating_cash':cash}
    assert result['items']==expected and result['direct_operating_cash']==cash
    assert all(result[k] is False for k in bridge.FLAGS)
    trace=row['result']['execution']['trace']
    selected=next(r for r in trace if r['command']['kind']=='carry' and r['command']['id']==q['report_id'])
    assert result['financial_report']==selected['result']['report']
    assert result['opening_sha256']==bridge.core.digest(selected['request']['report_request']['opening'])
    assert result['closing_sha256']==bridge.core.digest(selected['request']['report_request']['closing'])
    events=[r for r in trace if r['command']['kind']=='event' and r['command']['event']['date'].startswith(str(year))]
    assert [r['event_id'] for r in result['events']]==[r['command']['event']['id'] for r in events]
    for item,event in zip(result['events'],events):
        gross=event['result']['transition']['monetary']['diagnostics']['postings']
        assert len(item['gross_postings'])==len(gross)
        for actual,original in zip(item['gross_postings'],gross):
            assert actual['posting_id']==original['id']
            assert actual['debit_change']==original['binding']['value']
    assert len(result['events'])==(0 if year==2025 else 3)
    return {'request':q,'result':result,'expected':expected,
            'fiscal_request_sha256':bridge.core.digest(row['request']),
            'fiscal_result_sha256':bridge.core.digest(row['result']),
            'preserved_loss_origins':deepcopy(row['result']['loss_origins'])}


if __name__=='__main__':
    row=fixture()
    results=[exchange(row,year) for year in [2025,2026,2027]]
    print(json.dumps({'passed':True,'annual_items':[r['result']['items'] for r in results]}))
