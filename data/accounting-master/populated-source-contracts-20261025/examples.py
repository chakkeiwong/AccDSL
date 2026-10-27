"""Constructed records with separate economic, availability and ingestion clocks."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'scripts'))
import receivable_source_contract_v1 as source

path = ROOT/'data/accounting-master/declared-collection-state-growth-20261025/examples.py'
spec = importlib.util.spec_from_file_location('populated_receivable_comparator', path)
prior = importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)


def fixture(owner='alpha'):
    program, mapping, native = prior.lifecycle_fixture(owner)
    first = deepcopy(program['commands'][0]); second = deepcopy(first)
    second['event'].update(id='sale.2', date='2027-01-03')
    second['event']['inputs']['claim_id']['value']['value'] = 'invoice/b'
    second['event']['inputs']['consideration']['value']['value'] = '40/1'
    second['event']['inputs']['due']['value']['value'] = '2027-02-28'
    receipt_b = deepcopy(program['commands'][8]); receipt_b['event'].update(id='receipt.B', date='2028-01-11')
    receipt_b['event']['inputs']['claim_id']['value']['value'] = 'invoice/b'
    receipt_b['event']['inputs']['amount']['value']['value'] = '40/1'
    program['commands'] = [first,second,*program['commands'][1:9],receipt_b,*program['commands'][9:]]
    context = {k:program['opening']['context'][k] for k in ['entity','book','currency']}
    context.update(basis='synthetic_declared_sale',unit='currency_unit',calendar='gregorian')
    documents, assertions = {}, []
    def add(identifier, lineage, event, available, ingested, supersedes):
        reading = {k:deepcopy(event['inputs'][k]['value']) for k in ['units','consideration','due']}
        reading.update(claim_id=event['inputs']['claim_id']['value']['value'],
                       customer=event['inputs']['customer']['value']['value'],
                       sale_event=event['id'],issued=event['date'])
        prefix = ('Constructed example — ' + identifier + chr(10)).encode('utf-8')
        content = source.core.canonical(reading); raw = prefix + content + bytes([10])
        digest = sha256(raw).hexdigest()
        documents[digest] = {'content':raw.decode('utf-8'),'origin':'constructed_fixture','available':available,'ingested':ingested}
        assertions.append({'id':identifier,'lineage':lineage,'supersedes':supersedes,'context':deepcopy(context),
                           'span':{'document':digest,'start':len(prefix),'end_exclusive':len(prefix)+len(content),
                                   'sha256':sha256(content).hexdigest()},'reading':reading})
    add('A.original','claim.A',first['event'],'2027-01-02T12:00:00Z','2027-01-02T13:00:00Z',[])
    add('B.original','claim.B',second['event'],'2027-01-03T12:00:00Z','2027-01-03T13:00:00Z',[])
    corrected = deepcopy(first['event']); corrected['inputs']['due']['value']['value'] = '2027-03-31'
    add('A.corrected','claim.A',corrected,'2027-03-15T12:00:00Z','2027-03-16T09:00:00Z',['A.original'])
    return {'profile':source.PROFILE,'template':program,'documents':documents,'assertions':assertions,
            'sale_bindings':{'sale.1':'claim.A','sale.2':'claim.B'},
            'view':{'mode':'latest_available','cutoff':'2027-02-01T00:00:00Z','system_as_of':'2027-04-01T00:00:00Z'},
            'mapping_premise':'Each constructed JSON record is an exact reading of a declared credit sale; no actual company admission'}, mapping, native


def replace_reading(request, index, reading):
    """Author a distinct constructed source version for a negative fixture."""
    row = request['assertions'][index]; old = request['documents'][row['span']['document']]
    prefix = ('Constructed replacement — ' + row['id'] + chr(10)).encode('utf-8')
    selected = source.core.canonical(reading); raw = prefix + selected + bytes([10])
    digest = sha256(raw).hexdigest()
    request['documents'][digest] = {**deepcopy(old),'content':raw.decode('utf-8')}
    row['reading'] = deepcopy(reading)
    row['span'] = {'document':digest,'start':len(prefix),'end_exclusive':len(prefix)+len(selected),'sha256':sha256(selected).hexdigest()}
