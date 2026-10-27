"""Bounded integrity/locator/arithmetic checks, not semantic adjudication."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import time
import fitz
import jsonschema
from lxml import html, etree

ROOT=Path(__file__).resolve().parent
started=time.monotonic()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
labels=json.loads((ROOT/'labels-v1.json').read_text())
index=json.loads((ROOT/'occurrence-index-v1.json').read_text())
selection=json.loads((ROOT/'selection.json').read_text())
schema=json.loads((ROOT/'annotation-record.schema.json').read_text())
by_id={r['annotation_id']:r for r in labels}
assert len(by_id)==len(labels)==len(index['occurrences'])
docs={r['document_id']:r for r in selection['records']}
for r in docs.values():
    assert sha(ROOT/r['packet_source'])==r['sha256']
    assert sha(ROOT/r['packet_landing'])==r['metadata']['landing_sha256']
for r in labels:
    jsonschema.validate(r,schema)
    assert r['review_status']=='provisional'
    assert r['original_sha256']==docs[r['document_id']]['sha256']
    for reading in r['readings']:
        for ident in reading['supporting_annotation_ids']:
            assert ident in by_id
            assert by_id[ident]['document_id']==r['document_id']
checks=[]
for occurrence in index['occurrences']:
    r=by_id[occurrence['occurrence_id']]
    loc=occurrence['locator'];path=ROOT/docs[r['document_id']]['packet_source']
    if loc['format']=='pdf':
        page=fitz.open(path)[loc['physical_page_1based']-1]
        box=fitz.Rect(loc['bbox_points'])
        assert page.rect.contains(box)
        assert page.get_textbox(box).strip()==loc['extracted_text']
        assert sha(ROOT/loc['render_path'])==loc['render_sha256']
        if occurrence['kind']=='reported_amount':
            # Ignore known extraction punctuation loss, not context or signs.
            normal=lambda x:re.sub(r'[\s,]','',x).replace('–','-')
            actual=loc['extracted_text']
            if r['annotation_id'] in {'R-revenue','R-ceded','R-reinsurance-result'}:
                # Only these inspected rendered commas have this exact font-map defect.
                assert actual.count('\ufffd')==1
                actual=actual.replace('\ufffd',',')
            assert normal(actual)==normal(r['literal']), r['annotation_id']
    else:
        tree=html.fromstring(path.read_bytes())
        original=path.read_bytes()
        source_span=loc['original_anchor_bytes']
        raw=original[source_span['start_byte']:source_span['end_byte_exclusive']]
        assert hashlib.sha256(raw).hexdigest()==source_span['sha256']
        assert raw.startswith(source_span['opening_tag_utf8'].encode())
        if r['annotation_id']=='A-context':
            assert b'<xbrli:startDate>' in raw and b'<xbrli:endDate>' in raw
        if occurrence['kind']=='reported_amount':
            assert 'contextRef' in loc['anchor_original_attributes']
        node=tree.get_element_by_id(loc['element_id'])
        if loc['relative_xpath']:node=node.xpath(loc['relative_xpath'])[0]
        actual=raw.decode() if loc['capture']=='original_element_bytes' else ''.join(node.itertext()).strip()
        assert actual==r['literal']
    checks.append({'id':r['annotation_id'],'hash_locator_schema':'pass','semantic_adjudication':'pending'})

# Independent, hand-entered expectations from rendered rows/original inline fields.
expected={'A-sales-statement':'124300','A-sales-note':'124300','A-assets':'344085',
          'H-net-interest':'32733','H-interest-expense':'-75898',
          'R-revenue':'60830','R-ceded':'-1666','R-reinsurance-income':'486',
          'R-reinsurance-result':'-1181','M-group-revenue':'407149600',
          'M-parent-revenue':'946607','M-restated-revenue':'372037280'}
for ident,value in expected.items():assert by_id[ident]['readings'][0]['value_exact']==value
assert not by_id['M-parent-interest-dash']['readings']
assert by_id['A-sales-statement']['source']['locator']!=by_id['A-sales-note']['source']['locator']
assert '2024-12-28' in by_id['A-instant']['literal'] and '2024-12-29' not in by_id['A-instant']['literal']
assert by_id['M-group-revenue']['readings'][0]['context']['perimeter']!=by_id['M-parent-revenue']['readings'][0]['context']['perimeter']

apple=html.fromstring((ROOT/docs['apple-2025-q1']['packet_source']).read_bytes())
landing=json.loads((ROOT/docs['apple-2025-q1']['packet_landing']).read_text())
recent=landing['filings']['recent'];ix=recent['accessionNumber'].index('0000320193-25-000008')
assert recent['filingDate'][ix]=='2025-01-31'
assert 97960+26340==124300
assert 108631-75898==32733
assert 407149600+1934090+576==409084266
rounding_difference=(-1666+486)-(-1181)
assert rounding_difference==1
result={'status':'pass_bounded_checks','checked_at':datetime.now(timezone.utc).isoformat(),
        'command':'python3 verify_pilot.py','wall_seconds':time.monotonic()-started,
        'labels':len(labels),'amount_labels':len(expected),'checks':checks,
        'arithmetic':{'Apple_products_plus_services':'97960 + 26340 = 124300 million USD',
          'HSBC_interest_net':'108631 - 75898 = 32733 million USD',
          'Midea_total_revenue':'407149600 + 1934090 + 576 = 409084266 thousand RMB',
          'Munich_Re_rounded_reinsurance':'-1666 + 486 = -1180; reported result -1181; one million EUR display difference, covered by source rounding warning. Do not rewrite source or force exact equality.'},
        'source_time':'Apple filing-date metadata checked; retained-byte historical availability not established; other three publication dates unknown',
        'review_limits':'Source/render author inspection and deterministic checks only; no independent semantic adjudication, tool accuracy or accounting compliance claim.',
        'inputs_sha256':{p.name:sha(p) for p in [ROOT/'labels-v1.json',ROOT/'occurrence-index-v1.json',ROOT/'selection.json']}}
(ROOT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','labels','amount_labels','wall_seconds']}))
