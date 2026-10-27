"""Read-only source binding and record replay."""
from datetime import date,timedelta
import hashlib
import json
import os
from pathlib import Path
import runpy
import xml.etree.ElementTree as ET

U=Path(__file__).resolve().parent
R=U.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())

def check():
    assert os.environ['CUDA_VISIBLE_DEVICES']=='-1'
    predecessor=runpy.run_path(str(R/'data/accounting-master/r05-interim-assets-20261023/verify.py'))
    predecessor['check']()
    data=load(U/'source-record.json')
    for key in ('regulation','text','announcement_text'):
        assert sha(R/data[key]['path'])==data[key]['sha256']
    assert (R/data['regulation']['path']).read_bytes().startswith(b'%PDF-')
    assert len(data['requests'])==9
    statuses={200:0,202:0,404:0}
    for request in data['requests']:
        for key in ('request_record','body','response_headers'):
            assert sha(R/request[key]['path'])==request[key]['sha256']
        assert (R/request['body']['path']).stat().st_size==request['bytes']
        statuses[request['http_code']]+=1
    assert statuses=={200:5,202:2,404:2}
    lines=(R/data['text']['path']).read_text().split('\n')
    for anchor in data['anchors']:
        assert '\n'.join(lines[anchor['start_line']-1:anchor['end_line']])==anchor['quote']
    a=data['announcement_anchor']; lines=(R/data['announcement_text']['path']).read_text().split('\n')
    assert '\n'.join(lines[a['start_line']-1:a['end_line']])==a['quote']
    assert str(date.fromisoformat(data['publication_date'])+timedelta(days=20))==data['derived_entry_into_force']=='2026-03-08'
    # Inspect the delivery link relationships, not just plausible identifiers.
    rdf='{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
    root=ET.fromstring((U/'sources/eu-pdf-manifestation.xml').read_bytes())
    item='http://publications.europa.eu/resource/cellar/ebfd6845-0ad9-11f1-8870-01aa75ed71a1.0006.01/DOC_1'
    assert any(e.tag.endswith('}manifestation_has_item') and e.attrib.get(rdf+'resource')==item for e in root.iter())
    assert data['requests'][-1]['requested_url']==item.replace('http:','https:',1)
    assert data['issuer_2027_classification_admitted'] is False
    assert data['historical_vintage_admissions']==0 and data['empirical_execution'] is False
    checks={'requests':9,'official_EU_pages':105,'EU_anchors':len(data['anchors']),
            'technical_source_gap_resolved':True,'issuer_policy_admissions':0,
            'historical_vintage_admissions':0,'whole_rows_closed':0,'readiness':'not_ready'}
    if (U/'completion.json').exists():
        complete=load(U/'completion.json');assert complete['checks']==checks
        for name,digest in complete['bindings'].items():assert sha(R/name)==digest,name
    return checks

if __name__=='__main__':print(json.dumps({'status':'read-only checks passed',**check()}))
