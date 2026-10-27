"""One-time construction from retained sources; standard library only."""
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'data/accounting-master'
S = B / 'r06-unitless-semantics-20261019/sources'

def write(name, value):
    with (U/name).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=True)
        f.write('\n')

class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('p','div','h4','h5','dt','dd','li','pre','br'):
            self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('p','div','h4','h5','dt','dd','li','pre'):
            self.parts.append('\n')
    def handle_data(self, data):
        self.parts.append(data)

def main():
    assert not (U/'source-ledger.json').exists(), 'one-time construction'
    spec = importlib.util.spec_from_file_location('local_numeric', U/'compare.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    audit, rows = m.derive()
    sections = [
        ('decimal', '02-dated.body', 1058, 1112, 'Part 2 sections 3.2.3–3.2.3.4'),
        ('integer', '02-dated.body', 2482, 2512, 'Part 2 sections 3.3.13–3.3.13.4'),
        ('whitespace', '02-dated.body', 4263, 4312, 'Part 2 section 4.3.6'),
        ('decimal_builtin', '02-dated.body', 5214, 5236, 'Part 2 Appendix A decimal declaration'),
        ('integer_builtin', '02-dated.body', 5700, 5708, 'Part 2 Appendix A integer declaration'),
        ('nil', '03-structures.body', 1402, 1455, 'Part 1 section 3.3.4'),
    ]
    anchors = []
    (U/'reading').mkdir(exist_ok=False)
    for name, filename, first, last, scope in sections:
        p = S/filename
        excerpt = b''.join(p.read_bytes().splitlines(keepends=True)[first-1:last])
        parser = Text()
        parser.feed(excerpt.decode())
        readable = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip()) + '\n'
        target = U/'reading'/f'{name}.txt'
        with target.open('x', encoding='utf-8') as f: f.write(readable)
        anchors.append({'id':name, 'source':m.bind(p), 'first_line':first, 'last_line':last,
                        'raw_excerpt_sha256':m.digest(excerpt), 'readable':m.bind(target), 'scope':scope})
    d = m.load(m.COVERAGE)
    concept_names = audit['concept_paths'].keys()
    sources = {m.COVERAGE, m.INSTANCE, S/'02-dated.body', S/'03-structures.body'}
    sources.update(R/d['concepts'][n]['declaration_anchor']['source_path'] for n in concept_names)
    sources.update(R/n['anchor']['source_path'] for n in audit['nodes'] if not n['terminal'])
    write('source-ledger.json', {
        'date':'2026-10-20', 'new_acquisitions':0, 'bindings':[m.bind(p) for p in sorted(sources)],
        'anchors':anchors, 'specification':'XML Schema 1.0 Second Edition, 28 October 2004',
        'source_urls':['https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/',
                       'https://www.w3.org/TR/2004/REC-xmlschema-1-20041028/'],
        'source_role':'retained primary specifications plus retained instance and schema bytes',
        'scope':'Narrow lexical/value interpretation; no full validator or original data mutation.'
    })
    write('type-audit.json', audit)
    write('occurrences.json', rows)
    fixtures = []
    positives = [
        ('0','decimal',0,1), ('-0','decimal',0,1), ('+0','decimal',0,1),
        ('-00.00','decimal',0,1), ('2.0','decimal',2,1), ('2.00','decimal',2,1),
        ('+0012.3400','decimal',617,50), ('.5','decimal',1,2), ('5.','decimal',5,1),
        ('-.5','decimal',-1,2), ('+5.','decimal',5,1), ('0.0001','decimal',1,10000),
        (' \t\r\n+0012.3400\t ','decimal',617,50),
        ('12345678901234567890','decimal',12345678901234567890,1),
        ('0','integer',0,1), ('-000','integer',0,1), ('+0012','integer',12,1),
        ('\t-42\r\n','integer',-42,1), ('12345678901234567890','integer',12345678901234567890,1),
    ]
    for text, terminal, n, den in positives:
        fixtures.append({'id':f'positive-{len(fixtures)+1}', 'raw':text, 'terminal':terminal,
                         'expected_status':'member','expected_rational':{'n':str(n),'d':str(den)}})
    invalid_both = ['', ' ', '\t\r\n', '+', '-', '.', '+.', '-.', '1e3', '1E+3', 'NaN', 'INF',
                    '-INF', '1_000', '1,000', '1 2', '1\t2', '--1', '+-1', '1..2', '1x2',
                    'x5', '5x', '１２', '١٢', '\u00a01\u00a0', '\v1', '\f1', '1\u200b',
                    '\u22121', '0x10']
    for terminal in ('decimal','integer'):
        for text in invalid_both:
            fixtures.append({'id':f'negative-{len(fixtures)+1}','raw':text,'terminal':terminal,
                             'expected_status':'outside_lexical_space','expected_rational':None})
        fixtures.append({'id':f'nontext-{terminal}','raw':None,'terminal':terminal,
                         'expected_status':'not_text','expected_rational':None})
    for text in ('1.0','1.','0.0','.5'):
        fixtures.append({'id':f'integer-point-{len(fixtures)+1}','raw':text,'terminal':'integer',
                         'expected_status':'outside_lexical_space','expected_rational':None})
    write('fixtures.json', fixtures)
    original = next(r for r in d['occurrences'] if r['fact_id']=='f-191')
    nil_attrs = dict(original['source_attributes']); nil_attrs[m.XSI+'nil']='false'
    nil_span = dict(original['source_span']); nil_span['content_utf8']=' '
    controls = [
        {'id':'wrong_rational','fact_id':'f-53','row_changes':{'portable_candidate_value':{'tag':'Decimal','rational':{'n':'1','d':'1'}}},'expected_status':'requires_repair'},
        {'id':'exponent','fact_id':'f-53','row_changes':{'decoded_text':'2628553e6'},'expected_status':'requires_repair'},
        {'id':'unicode_digits','fact_id':'f-53','row_changes':{'decoded_text':'１２'},'expected_status':'requires_repair'},
        {'id':'nbsp','fact_id':'f-53','row_changes':{'decoded_text':'\u00a02628553000000\u00a0'},'expected_status':'requires_repair'},
        {'id':'nil_false','fact_id':'f-191','row_changes':{'source_attributes':nil_attrs},'expected_status':'nil_condition_failed'},
        {'id':'nil_nonempty','fact_id':'f-191','row_changes':{'source_span':nil_span,'decoded_text':' '},'expected_status':'nil_condition_failed'},
        {'id':'not_nillable','fact_id':'f-191','declaration_changes':{'nillable':'false'},'expected_status':'nil_condition_failed'},
        {'id':'nil_fixed','fact_id':'f-191','declaration_changes':{'fixed':'0'},'expected_status':'nil_condition_failed'},
        {'id':'nil_as_zero','fact_id':'f-191','row_changes':{'portable_candidate_value':{'tag':'Decimal','rational':{'n':'0','d':'1'}}},'expected_status':'requires_repair'},
    ]
    write('altered-controls.json', controls)
    write('source-support-ledger.json', {
        'classification':'PRIMARY_SPECIFICATION_AND_RETAINED_SOURCE',
        'source_identity':'source-ledger.json', 'read_scope':[x['scope'] for x in anchors],
        'allowed':'selected lexical/value relations and retained path/nil conditions',
        'forbidden':['full XSD/XBRL validity','installed processor correspondence','financial meaning or accuracy']
    })
    write('claim-support-ledger.json', {'claims':[
        {'id':'grammar','class':'SOURCE_RULE_WITH_LOCAL_FORMALIZATION','anchors':['decimal','integer','whitespace','decimal_builtin','integer_builtin'],
         'claim':'ASCII decimal/integer grammars after fixed XML whitespace collapse define the selected narrow parser.'},
        {'id':'values','class':'CHECKED_LOCAL_RESULT','evidence':['type-audit.json','occurrences.json'],
         'claim':'961 selected exact values agree; 958 decimal terminals and three integer terminals.'},
        {'id':'nil','class':'SOURCE_RULE_AND_OBSERVATION','anchors':['nil'],'evidence':'occurrences.json',
         'claim':'Two empty nil elements have nillable declarations without fixed value constraints; they are not zero.'},
        {'id':'precision','class':'SOURCE_RULE','anchors':['decimal'],
         'claim':'2.0 and 2.00 denote the same decimal value; lexical scale does not set financial precision.'}
    ]})
    write('backward-snowball-ledger.json', {'scope':'Bounded specification dependency trace, not a new literature survey',
        'leads':[{'lead':'Part 2 decimal/integer built-in definitions','disposition':'read in retained Appendix A'},
                 {'lead':'Part 1 element validity for nil','disposition':'relevant 3.3.4 retained section read'},
                 {'lead':'full XML/XBRL validity and numeric attribute semantics','disposition':'outside this narrow inquiry; no admission'}]})
    write('forward-snowball-ledger.json', {'scope':'No forward literature search required for the selected historical specification',
        'new_queries':0, 'reason':'The question fixes XML Schema 1.0 Second Edition; later editions would change the comparator.',
        'future_lead':'Actual chosen processor/build and full-validation evidence remain separate held work.'})
    write('citation-venue-ledger.json', {'source':'W3C XML Schema 1.0 Second Edition Parts 1 and 2',
        'publication_status':'W3C Recommendation dated 28 October 2004',
        'authority_scope':'retained historical specification; not current processor certification',
        'citation_anchors':'source-ledger.json', 'retraction_status':'N/A specification; supersession is not runtime correspondence'})
    write('omission-risk-ledger.json', {'risks':[
        {'risk':'Hidden custom restriction','response':'All 263 selected concept paths, 13 nodes and actual restriction children checked; unsupported facets would stop the narrow claim.'},
        {'risk':'Numeric parser too permissive','response':'ASCII grammar, XML-only whitespace, positive/negative fixtures and exact independent Decimal tuple cross-check.'},
        {'risk':'Nil treated as numeric zero','response':'Two separate records; no parser invocation; altered zero/fixed/nonempty/nillable cases rejected.'},
        {'risk':'Metadata precision or units inferred from syntax','response':'No decimals scaling, currency inference or precision admission.'},
        {'risk':'Local proof read as installed validation','response':'All validation flags remain not_run and processor/runtime/financial admission remain false.'}
    ]})
    print(json.dumps({'constructed':True,'occurrences':len(rows),'type_nodes':audit['type_nodes'],
                      'specification_anchors':len(anchors),'source_bindings':len(sources),
                      'fixtures':len(fixtures),'altered_controls':len(controls)}))

if __name__ == '__main__':
    main()
