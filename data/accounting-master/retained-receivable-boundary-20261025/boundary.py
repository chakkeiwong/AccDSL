"""Finite comparison of retained observations with identified-claim inputs."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys
import fitz
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[3]
PRIOR=ROOT/'data/accounting-master/real-company-input-readiness-20261024'
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(PRIOR))
import readiness
import receivable_source_contract_v1 as contract

PROFILE='RetainedReceivableBoundary/1'
ROW_IDS={'balance.receivables','balance.vendor_receivables','cash_flow.receivables','cash_flow.vendor_receivables'}
EXTRA_FIELDS=['source_document','source_span','source_timing','revision_relation','legal_context',
              'opening_population','settlements','recognition_approval','inventory_cost','assessment_policy','vendor_method']
NOTE_SOURCES={
    'annual':('docs/design/cases/apple/annual-2024.pdf','ec74758cd767465362c641cf2fd5d8fedd477aed2bf7f62117e67610435dcb88'),
    'interim':('docs/design/cases/apple/interim-2025q1.html','2f7629f0733f75b3155dd52f7ae6a8724468e3cde1a9ce32fbce96d98f1ec27e')}

def sha(p):return sha256(p.read_bytes()).hexdigest()
def ensure(ok,message):
    if not ok:raise ValueError(message)

def notes_for(versions):
    notes=[]
    for version in sorted(versions):
        name,expected=NOTE_SOURCES[version];path=ROOT/name
        ensure(sha(path)==expected,'note source bytes')
        if version=='annual':
            with fitz.open(path) as document:full=document[40].get_text()
            start=full.index('Accounts Receivable');end=full.index('Apple Inc.',start)
            locator={'pdf_page':41,'printed_page':38,'section':'Accounts Receivable'}
        else:
            full=BeautifulSoup(path.read_text(),'html.parser').get_text(' ',strip=True)
            start=full.index('Accounts Receivable');end=full.index('Note 5',start)
            locator={'section':'Accounts Receivable','next_section':'Note 5','normalized_text_start':start}
        passage=full[start:end].strip()
        ensure('Vendor Non-Trade Receivables' in passage and 'Trade Receivables' in passage,'note anchors')
        notes.append({'id':version+'.receivable-note','source':name,'source_sha256':expected,
            'locator':locator,'extracted_text':passage,'extracted_text_sha256':sha256(passage.encode()).hexdigest(),
            'interpretation_status':'author_reading_not_accounting_admission'})
    return notes

def source_row(packet,observation):
    record=observation['record'];b=record['body']
    evidence=readiness.record(packet,b['reading_file_ref'])['body']['blob']
    location=packet['blobs'][evidence['digest']]
    path=ROOT/location['path'];raw=path.read_bytes()
    ensure(len(raw)==evidence['byte_length']==location['byte_length'],'reading length')
    ensure(sha256(raw).hexdigest()==evidence['digest'],'reading bytes')
    value=json.loads(raw)
    for part in b['pointer'].strip('/').split('/'):
        value=value[int(part)] if isinstance(value,list) else value[part]
    # Comparison pointers resolve the original nested reading, not a new fact.
    rows=json.loads(raw)['rows']
    parent=next(r for r in rows if r['id']==b['row_id'].removeprefix('opening.'))
    ensure(value['literal']==b['literal'],'reading literal')
    ensure(Fraction(value['value'])==Fraction(int(b['value']['amount']['n']),int(b['value']['amount']['d'])),'reading amount')
    ensure(parent['precision']==b['precision'],'reading precision')
    context=observation['context']
    expected_period=value.get('date',value.get('period'))
    ensure(context=={'issuer':'Apple','perimeter':parent['entity'],'basis':parent['basis'],
        'period':expected_period,'unit':parent['unit'],'measurement_kind':parent['measurement_kind']},'reading context')
    source=readiness.record(packet,b['source_ref'])
    blob=source['body']['original_blob'];original=packet['blobs'][blob['digest']]
    path=ROOT/original['path'];ensure(sha(path)==blob['digest'],'original source bytes')
    ensure(path.stat().st_size==blob['byte_length']==original['byte_length'],'original source length')
    ensure(parent['source_sha256']==blob['digest'],'original reading source')
    return {'reading_path':location['path'],'pointer':b['pointer'],'entry':deepcopy(value),
            'label':parent['label'],'source_path':original['path'],'source_sha256':blob['digest'],
            'pdf_page':parent.get('pdf_page'),'printed_page':parent.get('printed_page'),
            'source_version':source}

def evaluate(request):
    ensure(type(request) is dict and set(request)=={'profile','readiness_request','target_sha256'},'boundary request')
    ensure(request['profile']==PROFILE,'boundary profile')
    ensure(request['target_sha256']==sha(ROOT/'scripts/receivable_source_contract_v1.py'),'target identity')
    ensure(request['readiness_request']['target']==readiness.OPS,'retained comparator')
    base=readiness.evaluate(request['readiness_request']);packet=readiness.load_packet()
    observations=[]
    for group,rows in base['known_evidence'].items():
        for row in rows:
            if row['record']['body']['row_id'].removeprefix('opening.') in ROW_IDS:
                observations.append({'group':group,'observation':deepcopy(row),'original':source_row(packet,row)})
    mapping=[]
    reasons={
        'claim_id':'No identified claim population in these retained readings or inspected receivable notes.',
        'customer':'Concentration percentages do not identify each claim counterparty.',
        'sale_event':'A period statistic or closing balance does not identify a sale event.',
        'issued':'Statement and fiscal dates are not claim issuance dates.',
        'units':'Receivable captions contain no delivered units per claim.',
        'consideration':'Net displayed receivables and cash-flow adjustments are not exact gross sale consideration.',
        'due':'No individual contractual due dates are supplied by the selected material.',
        'source_document':'Original PDF/HTML and reading-file bytes are retained and hash-bound.',
        'source_span':'PDF boxes/HTML reading anchors differ from this constructed-JSON byte-span profile.',
        'source_timing':'Exact byte publication, ingestion and review clocks remain unknown.',
        'revision_relation':'Annual and interim sources retain no supersession link; dates alone do not imply revision.',
        'legal_context':'Consolidated issuer context is known; ownership and allocation to legal books are unresolved.',
        'opening_population':'Aggregate opening receivables cannot satisfy an empty identified-claim opening or identify its members.',
        'settlements':'Changes in operating assets and liabilities are not identified gross customer receipts.',
        'recognition_approval':'No selected transaction facts or method approval are supplied by a displayed caption.',
        'inventory_cost':'No per-sale inventory units or homogeneous cost mapping is supplied.',
        'assessment_policy':'The synthetic strict-after-due-date policy is not established by these disclosures.',
        'vendor_method':'Disclosed vendor component-sale gains reduce products cost of sales on final-product sale; the lifecycle posts sale revenue immediately.'}
    for field in [*contract.READING_FIELDS,*EXTRA_FIELDS]:
        status='supported' if field=='source_document' else 'unsupported' if field in ['source_span','vendor_method'] else 'unresolved'
        mapping.append({'field':field,'status':status,'reason':reasons[field]})
    dependencies=[deepcopy(d) for d in base['dependencies'] if d['id'] in ['claims','context','information','opening','inventory','behavior']]
    versions={r['original']['source_version']['body']['version'] for r in observations}
    notes=notes_for(versions)
    for row in mapping:
        row['observation_refs']=[deepcopy(r['observation']['ref']) for r in observations]
        row['note_refs']=[n['id'] for n in notes]
    return {'profile':PROFILE,'request_sha256':readiness.digest(request),'request':deepcopy(request),
        'status':'partial_source_representation','executed':False,'source_admission':False,
        'accounting_admission':False,'historical_execution_established':False,
        'executable_program':None,'claims':None,'observations':observations,'field_mapping':mapping,
        'dependencies':dependencies,'notes':notes,'preserved_package':deepcopy(base['preserved_package']),
        'readiness_result_sha256':readiness.digest(base),
        'decision':'This selected claim-execution mapping is unsupported; no conclusion of whole-company infeasibility.',
        'next':'Represent aggregate measurements and unknown claim populations without inventing a decomposition.'}

def fixture(view='combined'):
    return {'profile':PROFILE,'readiness_request':readiness.fixture(view=view),
            'target_sha256':sha(ROOT/'scripts/receivable_source_contract_v1.py')}

def verify(request,result):
    try:return readiness.canonical(evaluate(request))==readiness.canonical(result)
    except Exception:return False
