"""Independent prior-equity expression expectations from frozen symbolic cases."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json
H=Path(__file__).resolve().parent
SAVED=json.loads((H.parent/'acquisition-symbolic-20261027/attempt-01/cases.json').read_text())
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def prior(id):return next(x for x in SAVED if x['id']==id)
def bind(b):b['expected_payload_sha256']=digest(b['payload']);return b
def fixture(id='proportional/equity',classification='fvtpl',treatment='none'):
    old=prior(id);bp=old['request']['payload'];source=dict(text='Synthetic prior20% equity,classification and separate-treatment premise; not source admission',subject=['P','S'],actor='manager',available_at='2025-01-01T00:00:00Z');sid=digest(source)
    desc=lambda symbol,kind,zero:dict(symbol=symbol,kind=kind,currency='USD',unit='currency_unit',at='2025-07-01T00:00:00Z',basis='Unknown amount at acquisition before the current fair-value update',evidence_sha256=sid,zero_stipulated=zero)
    return bind(dict(profile='ConditionalPriorEquityExpressions/1',payload=dict(base_request=deepcopy(old['request']),base_result_sha256=digest(old['result']),source_lock_sha256=sha256((H/'predecessor-lock.json').read_bytes()).hexdigest(),prior=dict(kind=bp['prior_interest']['kind'],fraction='1/5',classification=classification,equity_eligible=True,irrevocable_election=classification=='equity_fvoci',hedging='none_stipulated',oci_treatment=treatment,separate_transactions='none_stipulated',separate_books='unresolved',evidence_sha256=sid),carrying=desc('C','prior_carrying_before_update',False),cumulative_oci=desc('PriorOCI','prior_cumulative_oci',classification=='fvtpl'),source=source),expected_payload_sha256=''))
def resupport(b):
    p=b['payload'];sid=digest(p['source']);p['prior']['evidence_sha256']=sid;p['carrying']['evidence_sha256']=sid;p['cumulative_oci']['evidence_sha256']=sid;return bind(b)
def expected(id,classification,treatment):
    old=prior(id)['result'];ex=deepcopy(old['expressions'])
    e=lambda c:dict(constant='0/1',coefficients=c)
    gain={'C':'-1/1','P':'1/1'};total={'C':'-1/1','P':'1/1','PriorOCI':'1/1'}
    ex.update(prior_remeasurement=e(gain),prior_parent_profit_before_tax=e(gain if classification=='fvtpl' else {}),prior_parent_oci_before_tax=e(gain if classification=='equity_fvoci' else {}),prior_oci_recycling_to_profit=e({}),prior_transfer_to_retained=e(total if treatment=='transfer_within_equity' else {}),prior_oci_reserve_after=e(total if treatment=='retain_reserve' else {}),prior_nci_effect=e({}),prior_remeasurement_cash=e({}))
    dependencies=sorted(set(old['dependencies']+['unmeasured:C','prior_tax_method','separate_books_method','complete_worksheet_and_report']+([] if classification=='fvtpl' else ['unmeasured:PriorOCI'])))
    return ex,dependencies
