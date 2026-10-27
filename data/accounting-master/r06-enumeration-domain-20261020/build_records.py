"""One-time source-bound enumeration record construction."""
import importlib.util
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/'data/accounting-master'

def write(name,value):
    with (U/name).open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2);f.write('\n')

def main():
    assert not (U/'source-ledger.json').exists()
    spec=importlib.util.spec_from_file_location('local_enum',U/'compare.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    network,domains,rows=m.derive()
    write('network.json',network);write('domains.json',domains);write('occurrences.json',rows)
    acquisitions=[]
    for name in ('01-enumerations','02-dimensions','03-xbrl21'):
        acquisitions.append({'id':name,'receipt':m.bind(U/'sources'/f'{name}.receipt.json'),
                             'headers':m.bind(U/'sources'/f'{name}.headers'),
                             'body':m.bind(U/'sources'/f'{name}.body'),
                             'raw_text_view':m.bind(U/'sources'/f'{name}.txt'),
                             'visible_text_view':m.bind(U/'sources'/f'{name}.visible.txt')})
    write('acquisitions.json',acquisitions)
    anchors=[]
    sections=[
        ('enum_identity','01-enumerations',1,36),
        ('enum_concept_domain','01-enumerations',121,146),
        ('enum_representation_validation','01-enumerations',147,164),
        ('enum_dependencies','01-enumerations',165,182),
        ('enum_schema_authority','01-enumerations',183,208),
        ('enum_schema','01-enumerations',209,264),
        ('enum_history_errata','01-enumerations',296,328),
        ('dimensions_target_role','02-dimensions',719,743),
        ('dimensions_domain','02-dimensions',920,942),
        ('dimensions_relationship_usable','02-dimensions',970,1023),
        ('xbrl_effective_arcs','03-xbrl21',1875,1992),
        ('xbrl_equivalence_examples','03-xbrl21',1993,2070),
    ]
    for ident,name,first,last in sections:
        p=U/'sources'/f'{name}.visible.txt'
        anchors.append({'id':ident,'source':m.bind(p),'first_line':first,'last_line':last,
                        'excerpt':'\n'.join(p.read_text().splitlines()[first-1:last])})
    resources=m.load(m.MAP)
    inputs={R/r['retained_path'] for r in resources}
    inputs.update([m.MAP,m.m.COVERAGE,B/'r06-text-semantics-20261020/occurrences.json',
                   B/'r06-text-semantics-20261020/compare.py',B/'r06-text-semantics-20261020/completion.json',
                   B/'r06-numeric-lexical-20261020/compare.py',
                   B/'r06-normative-schema-20261018/sources/02-index.body'])
    for a in acquisitions:
        inputs.update(R/b['path'] for k,b in a.items() if k!='id')
    write('source-ledger.json',{'date':'2026-10-20','new_acquisitions':3,
        'bindings':[m.bind(p) for p in sorted(inputs)],'anchors':anchors,
        'technical_scope':'Enumeration sections 3–6 and appendices; selected Dimensions and XBRL relationship prerequisites.',
        'visible_extraction':'Inline display:none content excluded in separate view; original HTML and raw extraction retained.',
        'normative_scope':'Enumeration Recommendation and linked dependency text; schema appendix expressly non-normative.'})
    A='http://example.com#A';C='http://example.com#B';Z='http://example.com#Z'
    fixtures=[
        {'text':'','expected_errors':[]},
        {'text':A,'expected_errors':[]},
        {'text':A+' '+C,'expected_errors':[]},
        {'text':' \t'+A+'\r\n'+C+'  ','expected_errors':[]},
        {'text':C+' '+A,'expected_errors':['InvalidEnumerationSetOrder']},
        {'text':A+' '+A,'expected_errors':['RepeatedEnumerationSetValue']},
        {'text':Z,'expected_errors':['InvalidEnumerationSetValue']},
        {'text':A.replace('http:','https:'),'expected_errors':['InvalidEnumerationSetValue']},
        {'text':A.replace('#A','#a'),'expected_errors':['InvalidEnumerationSetValue']},
        {'text':A.replace('#A','#%41'),'expected_errors':['InvalidEnumerationSetValue']},
        {'text':A+'\u00a0'+C,'expected_errors':['InvalidEnumerationSetValue']},
        {'text':C+' '+A+' '+A,'expected_errors':['RepeatedEnumerationSetValue','InvalidEnumerationSetOrder']},
    ]
    write('fixtures.json',fixtures)
    r=next(r for r in rows if len(r['members'])==2 and r['declared_head'].endswith('}AssetsAbstract'))
    a,b=r['rules']['members'];prefix='http://fasb.org/us-gaap/2024#'
    controls=[
        {'fact_id':r['fact_id'],'text':b+' '+a,'expected_errors':['InvalidEnumerationSetOrder']},
        {'fact_id':r['fact_id'],'text':a+' '+a,'expected_errors':['RepeatedEnumerationSetValue']},
        {'fact_id':r['fact_id'],'text':prefix+'AssetsAbstract','expected_errors':['InvalidEnumerationSetValue']},
        {'fact_id':r['fact_id'],'text':prefix+'LongTermDebtCurrent','expected_errors':['InvalidEnumerationSetValue']},
        {'fact_id':r['fact_id'],'text':a.replace('http:','https:'),'expected_errors':['InvalidEnumerationSetValue']},
        {'fact_id':r['fact_id'],'text':a.replace('Marketable','marketable'),'expected_errors':['InvalidEnumerationSetValue']},
    ]
    write('altered-controls.json',controls)
    write('network-guard-controls.json',[
        {'id':'prohibited','added_attributes':{'use':'prohibited'}},
        {'id':'priority','added_attributes':{'priority':'1'}},
        {'id':'unusable','added_attributes':{'{http://xbrl.org/2005/xbrldt}usable':'false'}},
        {'id':'target_role','added_attributes':{'{http://xbrl.org/2005/xbrldt}targetRole':'http://example.com/other'}},
        {'id':'unreviewed_attribute','added_attributes':{'{http://example.com}condition':'1'}},
    ])
    base_edges=[(a['source'],a['target']) for a in network['raw_arcs'] if a['source_file'].endswith('import-02-trusted.body')]
    missing=[]
    for r in rows:
        paths=m.graph_witnesses(base_edges,r['declared_head'],False)
        for member in r['members']:
            if member['expanded_name'] not in paths:
                missing.append({'fact_id':r['fact_id'],'member':member['expanded_name']})
    write('source-layer-diagnostic.json',{'role':'explanatory_only',
        'question':'Which actual selected member occurrences require the retained issuer extension arcs?',
        'base_schema_edges':len(base_edges),'combined_edges':len(network['unique_endpoint_edges']),
        'missing_without_issuer_extension':missing,
        'not_concluded':'The base schema alone is not the complete comparator for the issuer filing.'})
    write('source-support-ledger.json',{'classification':'PRIMARY_SPECIFICATION_AND_RETAINED_SOURCE',
        'identity':'source-ledger.json','read_scope':'12 bounded source anchors plus the full 328-line Enumeration Recommendation',
        'allowed':'retained-domain/set-rule results under inspected arc profile',
        'forbidden':['installed DTS correspondence','full XBRL validity','financial validity','general relationship processor']})
    write('claim-support-ledger.json',{'claims':[
        {'claim':'Enumeration set values are unordered sets, but serialized members must be unique and lexicographically ordered.',
         'class':'PRIMARY_TECHNICAL_SUPPORT','anchors':['enum_concept_domain','enum_representation_validation']},
        {'claim':'Declared domains use usable reachable members in the designated role; head membership depends on headUsable.',
         'class':'PRIMARY_TECHNICAL_SUPPORT','anchors':['enum_concept_domain','dimensions_domain','dimensions_relationship_usable']},
        {'claim':'All 718 retained arcs have the simple default profile; equivalent duplication cannot alter endpoint reachability here.',
         'class':'SOURCE_OBSERVATION_AND_LOCAL_ARGUMENT','anchors':['xbrl_effective_arcs'],'evidence':'network.json'},
        {'claim':'All sixteen actual facts and twenty member occurrences pass the selected retained-domain/set rules.',
         'class':'CHECKED_LOCAL_RESULT','evidence':'occurrences.json'},
        {'claim':'A syntactically valid member can fail the specific declared domain; sorting and deduplication must not silently repair source evidence.',
         'class':'AUTHORED_DISCRIMINATOR','evidence':'altered-controls.json'}
    ]})
    write('backward-snowball-ledger.json',{'scope':'Normative dependency trace',
        'leads':[{'source':'Dimensions 1.0 with 2012 errata','status':'acquired; relevant domain/usable/role sections read'},
                 {'source':'XBRL 2.1 with 2013 errata','status':'acquired; effective-relationship rules/examples read'},
                 {'source':'XML Schema 1.0 Second Edition','status':'completed lexical predecessor reused'},
                 {'source':'XML Names/RFC3986','status':'arbitrary URI grammar not implemented; exact actual domain identity and prior ASCII lexical subset suffice for selected inputs'},
                 {'source':'Extensible Enumerations 1.0','status':'not substituted for the 2.0 namespace'}]})
    write('forward-snowball-ledger.json',{'scope':'fixed-version technical inquiry','new_forward_queries':0,
        'status':'Official retained index links this Recommendation; document history and incorporated errata section inspected.',
        'limitation':'No assertion that no later correction or processor difference exists.'})
    write('citation-venue-ledger.json',{'sources':[
        {'title':'Extensible Enumerations 2.0','date':'2020-02-12','status':'Recommendation; normative main text',
         'errata':'Appendix F says no incorporated errata'},
        {'title':'XBRL Dimensions 1.0','date':'2006-09-18 with 2012-01-25 corrections','status':'normative republished HTML'},
        {'title':'XBRL 2.1','date':'2003-12-31 with 2013-02-20 corrections','status':'normative Recommendation'}],
        'citation_metrics':'not applicable to this technical specification inquiry','identity':'acquisitions.json'})
    write('omission-risk-ledger.json',{'risks':[
        {'risk':'Reachability ignores effective arc semantics','response':'All 27 retained resources scanned; 718 matching arcs have no exceptional use/priority/usable/targetRole attributes. Five guards reject scope expansion.'},
        {'risk':'Base taxonomy used without issuer extension','response':'Both embedded schema and issuer links included; source-layer diagnostic preserves affected member occurrences.'},
        {'risk':'Schema lexical pass mistaken for set/domain pass','response':'Independent member, duplicate and order tests; exact source strings retained.'},
        {'risk':'Hidden revision text contaminates extraction','response':'New visible views omit explicit inline-hidden subtrees; HTML and raw text remain intact.'},
        {'risk':'Retained map called installed DTS','response':'No discovery/runtime or full-validity admission; original map flags unchanged.'}
    ]})
    print(json.dumps({'constructed':True,'facts':len(rows),'members':sum(len(r['members']) for r in rows),
                      'anchors':len(anchors),'bindings':len(inputs),'fixtures':len(fixtures),
                      'extension_dependent_member_occurrences':len(missing)}))

if __name__=='__main__':main()
