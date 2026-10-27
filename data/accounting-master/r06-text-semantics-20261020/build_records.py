"""One-time retained-source and authored-fixture construction."""
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/'data/accounting-master'
S=B/'r06-unitless-semantics-20261019/sources'

def write(name,value):
    with (U/name).open('x',encoding='utf-8') as f:
        json.dump(value,f,indent=2,ensure_ascii=True);f.write('\n')

class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('p','div','h4','h5','dt','dd','li','pre','br','tr'):self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('p','div','h4','h5','dt','dd','li','pre','tr'):self.parts.append('\n')
    def handle_data(self,data):self.parts.append(data)

def main():
    assert not (U/'source-ledger.json').exists(),'one-time construction'
    spec=importlib.util.spec_from_file_location('local_text',U/'compare.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    audit,rows=m.derive()
    sections=[
        ('string_boolean',1005,1057,'3.2.1–2'),
        ('duration',1341,1425,'3.2.6 lexical and partial-order rules'),
        ('date',1652,1736,'3.2.9'),
        ('date_components',1514,1543,'3.2.7.1'),
        ('gMonthDay',1818,1856,'3.2.12'),
        ('string_derived',2201,2253,'3.3.1–2'),
        ('length',3731,3760,'4.3.1'),
        ('minLength',3859,3886,'4.3.2'),
        ('maxLength',3981,4005,'4.3.3'),
        ('enumeration',4174,4215,'4.3.5'),
        ('whitespace',4263,4312,'4.3.6'),
        ('builtins_string_boolean',5136,5172,'Appendix A string/boolean'),
        ('builtins_string_derived',5537,5555,'Appendix A normalizedString/token'),
        ('calendar',6370,6421,'Appendix D.1'),
        ('calendar_arithmetic',6549,6562,'Appendix E Gregorian month arithmetic'),
        ('pattern_membership',6620,6673,'Appendix F whole-string regular expressions'),
        ('pattern_subtraction',6806,6855,'Appendix F character groups/subtraction'),
        ('pattern_categories',6932,6979,'Appendix F escapes/categories'),
        ('pattern_names',7010,7025,'Appendix F name classes/wildcard'),
    ]
    (U/'reading').mkdir(exist_ok=False)
    p=S/'02-dated.body';anchors=[]
    for name,first,last,scope in sections:
        piece=b''.join(p.read_bytes().splitlines(keepends=True)[first-1:last])
        parser=Text();parser.feed(piece.decode())
        readable='\n'.join(x.strip() for x in ''.join(parser.parts).splitlines() if x.strip())+'\n'
        q=U/'reading'/f'{name}.txt'
        with q.open('x',encoding='utf-8') as f:f.write(readable)
        anchors.append({'id':name,'source':m.bind(p),'first_line':first,'last_line':last,
                        'raw_excerpt_sha256':m.m.digest(piece),'readable':m.bind(q),'scope':scope})
    d=m.load(m.m.COVERAGE)
    sources={m.m.COVERAGE,m.m.INSTANCE,p,m.PRIOR/'compare.py',m.PRIOR/'completion.json'}
    sources.update(R/d['concepts'][n]['declaration_anchor']['source_path'] for n in audit['concept_paths'])
    sources.update(R/n['anchor']['source_path'] for n in audit['nodes'] if not n['terminal'])
    write('source-ledger.json',{'date':'2026-10-20','new_acquisitions':0,
        'specification':'XML Schema 1.0 Second Edition, 28 October 2004',
        'source_url':'https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/',
        'bindings':[m.bind(p) for p in sorted(sources)],'anchors':anchors,
        'scope':'Retained declared value-space and facet interpretation, with explicit nonfacet obligations.'})
    write('type-audit.json',audit);write('occurrences.json',rows)
    fixtures=[]
    def f(raw,terminal,status='supported',value=None,norm=None):
        entry={'id':f'fixture-{len(fixtures)+1}','raw':raw,'terminal':terminal,'expected_status':status}
        if value is not None:entry['expected_value']=value
        if norm is not None:entry['expected_normalized']=norm
        fixtures.append(entry)
    for text,value in [('true',True),('1',True),('false',False),('0',False),(' \tfalse\r\n',False)]:
        f(text,'boolean',value={'kind':'boolean','value':value})
    for text in ('TRUE','False','yes','2','00','','\u00a0false','f alse'):
        f(text,'boolean','outside_lexical_space')
    for text in ('P1Y','P12M','P0D','-P1Y2M3DT4H5M6.25S','PT0.5S','P1YT0H','P0001Y',' P2D\t'):
        f(text,'duration')
    for text in ('P','PT','P1YT','+P1Y','P-1Y','P1.5Y','PT.5S','PT1.S','P1W','P1D1Y','P1Y1Y','P١Y','P1D T1H','p1y'):
        f(text,'duration','outside_lexical_space')
    f('P1M','duration',value={'kind':'duration_components','sign':1,'years':0,'months':1,'days':0,'hours':0,'minutes':0,
                            'seconds':{'n':'0','d':'1'},'canonical_or_equality_normalized':False})
    f('-P1Y2M3DT4H5M6.25S','duration',value={'kind':'duration_components','sign':-1,'years':1,'months':2,'days':3,'hours':4,'minutes':5,
                                         'seconds':{'n':'25','d':'4'},'canonical_or_equality_normalized':False})
    for text in ('2024-09-28','2024-02-29','2000-02-29','1900-02-28',' 2024-09-28\t'):
        f(text,'date')
    for text in ('2023-02-29','1900-02-29','0000-01-01','2024-04-31','2024-13-01','2024-00-01','2024-01-00'):
        f(text,'date','outside_lexical_space')
    for text in ('2024-09-28Z','-0001-01-01','10000-01-01','2024-09-28+08:00'):
        f(text,'date','outside_scope')
    f('2024-09-28','date',value={'kind':'calendar_date','year':2024,'month':9,'day':28,'timezone':None,
                               'meaning':'one_day_interval_on_nontimezoned_timeline'})
    for text in ('--09-28','--02-29',' --12-31\t'):f(text,'gMonthDay')
    for text in ('--02-30','--04-31','--13-01','--00-10'):f(text,'gMonthDay','outside_lexical_space')
    for text in ('--09-28Z','--09-28+08:00'):f(text,'gMonthDay','outside_scope')
    f('--02-29','gMonthDay',value={'kind':'recurring_month_day','month':2,'day':29,'timezone':None,'year_assigned':False})
    for terminal,expected in [('string',' \tA\r\n B  '),('normalizedString','  A   B  '),('token','A B')]:
        f(' \tA\r\n B  ',terminal,value={'kind':'string','text':expected},norm=expected)
    for terminal in ('string','normalizedString','token'):
        f('\u00a0A\u00a0',terminal,value={'kind':'string','text':'\u00a0A\u00a0'},norm='\u00a0A\u00a0')
    f('0000320193','token',value={'kind':'string','text':'0000320193'})
    write('fixtures.json',fixtures)
    patterns=[]
    groups={
        'submissionTypeItemType':[('10-K',True),('10-K/A',True),('Other',True),('a10-K',False),(' 10-K',False),('10-K ',False),('10_K',False)],
        'fileNumberItemType':[('001-36743',True),('1-12345678-ab',True),('1234-1',False),('1-123456789',False),('x001-36743',False),('1-1-\n',False)],
        'employerIdItemType':[('94-2404110',True),('９４-2404110',False),('94-240411',False),('x94-2404110',False)],
        'internationalNameItemType':[('Ernst & Young LLP',True),('San Jose, California',True),('1abc',True),('_abc',False),('',False),('A\nB',False),('École',None)],
        'enumerationSetItemType':[('',True),('http://example.com#Name',True),('urn:abc#_Name1 http://x#Second-Name',True),('1urn:abc#Name',False),
                                   ('http://x#1Name',False),('http://x#Name  http://x#Other',False),('http://x#Name ',False),('http://x#名',None)]
    }
    for typ,examples in groups.items():
        for text,expected in examples:patterns.append({'type':typ,'text':text,'expected':expected})
    write('pattern-fixtures.json',patterns)
    # Select actual facts by their declared restrictions, rather than assuming ids.
    def fact_for(local):
        return next(r['fact_id'] for r in rows if r['type_path'][0].endswith('}'+local))
    controls=[]
    cases=[
        ('f-56','TRUE','outside_lexical_space'),('f-390','P1YT','outside_lexical_space'),
        ('f-4','2023-02-29','outside_lexical_space'),('f-3','--02-30','outside_lexical_space'),
        (fact_for('fiscalPeriodItemType'),'FYX','facet_mismatch'),
        (fact_for('securityTitleItemType'),'','facet_mismatch'),
        (fact_for('tradingSymbolItemType'),'A'*26,'facet_mismatch'),
        (fact_for('employerIdItemType'),'94-240411','facet_mismatch'),
        (fact_for('internationalNameItemType'),'_notALetter','facet_mismatch'),
        (fact_for('enumerationSetItemType'),'http://x#1Bad','facet_mismatch'),
        (fact_for('trueItemType'),'false','facet_mismatch'),
        (fact_for('yesNoItemType'),'yes','facet_mismatch'),
    ]
    for fact,text,status in cases:
        controls.append({'id':f'altered-{len(controls)+1}','fact_id':fact,'replacement_text':text,'expected_status':status})
    controls.append({'id':'candidate-only','fact_id':'f-56','candidate_only':True,'expected_status':'candidate_text_mismatch'})
    write('altered-controls.json',controls)
    write('source-support-ledger.json',{'classification':'PRIMARY_SPECIFICATION_AND_RETAINED_DECLARATIONS',
        'identity':'source-ledger.json','technical_read':[s[3] for s in sections],
        'allowed':'Bounded declared base values, source-specific facets and explicit omitted nonfacet duties',
        'forbidden':['full schema validity','XBRL enumeration-domain or XHTML validity','processor validation','financial inference']})
    write('claim-support-ledger.json',{'claims':[
        {'id':'text_tags','class':'CHECKED_SOURCE_COMPARISON','evidence':'occurrences.json',
         'claim':'157 UnvalidatedText packet values and Text portable values preserve identical source text; tags do not identify the schema value space.'},
        {'id':'boolean','class':'PRIMARY_TECHNICAL_SUPPORT','anchors':['string_boolean'],'claim':'false and 0 denote false; nonempty-string truthiness is not the mapping.'},
        {'id':'duration','class':'PRIMARY_TECHNICAL_SUPPORT_AND_ILLUSTRATION','anchors':['duration','calendar_arithmetic'],
         'claim':'Calendar duration components do not supply a universal fixed-day conversion; month/day ordering is partial.'},
        {'id':'calendar','class':'PRIMARY_TECHNICAL_SUPPORT','anchors':['date','date_components','gMonthDay','calendar'],
         'claim':'The selected unzoned date is a one-day interval; gMonthDay is recurring and has no assigned year.'},
        {'id':'facets','class':'PROJECT_FORMALIZATION','evidence':'type-audit.json','anchors':['length','enumeration','pattern_membership','pattern_names'],
         'claim':'Fourteen custom restricted nodes are checked through explicit supported rules, retaining unknown general Unicode scope.'},
        {'id':'nonfacet','class':'RETAINED_SCHEMA_DOCUMENTATION','evidence':'type-audit.json',
         'claim':'56 text-block occurrences retain unvalidated XML/XHTML obligations and 16 enumeration-set occurrences retain domain/set obligations.'}
    ]})
    write('backward-snowball-ledger.json',{'scope':'Specification dependency trace, not a new literature survey',
        'dependencies':[{'source':'Part 2 dateTime and Appendices D/E','status':'relevant Gregorian prerequisites read'},
                        {'source':'Appendix F','status':'whole-string, class, category and name escape rules read'},
                        {'source':'DTR XML/XHTML and enumeration specification','status':'nonfacet obligations recorded; full semantic validation excluded'}]})
    write('forward-snowball-ledger.json',{'scope':'Historical fixed-edition inquiry','new_queries':0,
        'reason':'Later specification/processor versions are separate comparators; no current-version or runtime claim.',
        'open':'Actual installed parser and validator behavior remain held and unobserved.'})
    write('citation-venue-ledger.json',{'source':'W3C XML Schema 1.0 Second Edition Part 2','date':'2004-10-28',
        'publication_status':'W3C Recommendation','citation_count':'not applicable','venue_metric':'not applicable',
        'retraction_status':'N/A specification; later edition correspondence not claimed','identity':'source-ledger.json'})
    write('omission-risk-ledger.json',{'risks':[
        {'risk':'Text means string','response':'Separate raw portable text from declared boolean/calendar/duration/string interpretation.'},
        {'risk':'Terminal-only validation misses facets','response':'35 nodes and actual restriction children checked, with 14 restricted nodes.'},
        {'risk':'No facets means no semantic duties','response':'56 XML/XHTML and 16 enumeration-set occurrence duties remain explicitly unvalidated.'},
        {'risk':'Duration tuple implies days or total ordering','response':'No scalar conversion or canonical equality rule; two calendar anchors illustrate differing month lengths.'},
        {'risk':'Timezone/subset or Unicode scope loss','response':'Unsupported date/name forms return outside_scope/unknown; they are not declared invalid.'},
        {'risk':'Full XML character validity','response':'Retained source XML parsing is a prerequisite, not an implementation of the full character production for arbitrary fixtures.'}
    ]})
    print(json.dumps({'constructed':True,'occurrences':len(rows),'concepts':audit['concepts'],
                      'type_nodes':audit['type_nodes'],'anchors':len(anchors),'bindings':len(sources),
                      'fixtures':len(fixtures),'pattern_fixtures':len(patterns),'altered_controls':len(controls)}))

if __name__=='__main__':main()
