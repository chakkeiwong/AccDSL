"""Bind the official delivery chain and inspected EU technical passages once."""
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
S = U / 'sources'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bind = lambda p: {'path':str(p.relative_to(R)), 'sha256':sha(p)}
FILES = [('efrag-update59','html'),('eu-2026-338','pdf'),('eu-eli','html'),
         ('eu-cellar','body'),('eu-cellar-rdf','xml'),('eu-english-rdf','xml'),
         ('eu-adopted','pdf'),('eu-pdf-manifestation','xml'),('eu-regulation','pdf')]
SPANS = [
 ('identity_and_publication',1,10),('article1_insertion',113,122),
 ('article2_application',156,160),('article3_entry_into_force',162,170),
 ('B30_business_assessment',2009,2014),('B31_B32_examples',2019,2034),
 ('B33_B36_evidence',2036,2066),('B37_group',2069,2072),
 ('B38_asset_groups',2075,2083),('B39_B40_other_assets',2090,2100),
 ('B41_prospective_assessment_change',2102,2109),
 ('C1_effective_date',3469,3470),('C2_C3_transition',3475,3482),
 ('C4_C6_interim_transition',3484,3501),('IAS7_amendment_scope',4782,4784),
 ('IAS7_18_indirect',4886,4897),('IAS7_20_reconciliation',4899,4912),
 ('IAS7_31_32_separate_flows',4916,4926),('IAS7_33A_34A',4930,4936),
 ('IAS7_34B_34C',4938,4949),('IAS7_34D_35',4951,4962),
 ('IAS7_46_47_components',4969,4976),('IAS7_64_application',4991,4993)]

def main():
    assert not (U/'source-record.json').exists()
    requests=[]
    for name,suffix in FILES:
        meta=S/(name+'.request.json'); value=json.loads(meta.read_text())
        body=S/(name+'.'+suffix)
        assert body.stat().st_size == value['bytes']
        requests.append({'id':name,**value,'request_record':bind(meta),
                         'body':bind(body),'response_headers':bind(S/(name+'.headers'))})
    text=S/'eu-regulation.txt';lines=text.read_text().split('\n')
    anchors=[{'id':name,'start_line':a,'end_line':b,
              'physical_page':1+'\n'.join(lines[:a-1]).count('\f'),
              'quote':'\n'.join(lines[a-1:b])} for name,a,b in SPANS]
    data={'scope':'EU2026/338 Articles1-3 and selected IFRS18/IAS7 annex passages',
          'requests':requests,'regulation':bind(S/'eu-regulation.pdf'),'text':bind(text),
          'pdf_pages':105,'anchors':anchors,
          'announcement_text':bind(S/'efrag-update59.txt'),
          'announcement_anchor':{'start_line':84,'end_line':89,
             'quote':'\n'.join((S/'efrag-update59.txt').read_text().split('\n')[83:89])},
          'publication_date':'2026-02-16','act_date':'2026-02-13',
          'derived_entry_into_force':str(date(2026,2,16)+timedelta(days=20)),
          'mandatory_first_year_start_on_or_after':'2027-01-01',
          'early_application_permitted':True,'selected_EU_technical_source_inspected':True,
          'full_annex_comparison_performed':False,'issuer_2027_classification_admitted':False,
          'historical_vintage_admissions':0,'empirical_execution':False}
    with (U/'source-record.json').open('x') as f:
        json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps({'requests':len(requests),'EU_anchors':len(anchors),'pdf_pages':105,
                      'entry_into_force':data['derived_entry_into_force']}))

if __name__=='__main__':main()
