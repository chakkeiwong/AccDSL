"""Finite documentary checks only; preserves all frozen portable Values."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
DECLARATIONS = ROOT/'data/accounting-master/unitless-type-evidence-20261018/declarations.json'
IDS = ['f-57','f-59','f-13','f-14','f-934','f-935','f-1127']

def sha(b): return hashlib.sha256(b).hexdigest()
def bind(p): return {'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())}
def read(name): return json.loads((UNIT/name).read_text())

class Plain(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.parts=[]
    def handle_data(self,t): self.parts.append(t)

def plain(html):
    p=Plain();p.feed(html);p.close()
    return re.sub(r'\s+',' ',' '.join(p.parts)).strip()

def replace_xml_space(s):
    return s.translate({9:32,10:32,13:32})

def collapse_xml_space(s):
    return ' '.join(x for x in replace_xml_space(s).split(' ') if x)

def classify(s,kind):
    if kind=='normalizedString':
        # Tested examples contain XML-legal character data; no XML Char
        # validity, context, attributes or full schema constraint checked here.
        return {'normalized':replace_xml_space(s),'selected_membership':True,'value_family':'string'}
    t=collapse_xml_space(s)
    if kind=='cik':
        ok=len(t)==10 and all('0'<=c<='9' for c in t)
        return {'normalized':t,'selected_membership':ok,'value_family':'restricted token string'}
    if kind=='sequence':
        ok=bool(t) and '1'<=t[0]<='9' and all('0'<=c<='9' for c in t)
        return {'normalized':t,'selected_membership':ok,'value_family':'restricted token string'}
    if kind=='gYear':
        # Only the actually observed positive four-digit timezone-absent form.
        # Other valid forms are deliberately not implemented or rejected here.
        if len(t)==4 and all('0'<=c<='9' for c in t):
            return {'normalized':t,'selected_membership':t!='0000','value_family':'Gregorian calendar year','timezone':None}
        return {'normalized':t,'selected_membership':None,'value_family':'Gregorian calendar year','reason':'outside selected four-digit positive timezone-absent subset'}
    raise ValueError('unsupported selected kind')

def rows():
    d=json.loads(DECLARATIONS.read_text()); assert [r['fact_id'] for r in d['rows']]==IDS
    kinds={'f-57':'gYear','f-59':'cik','f-13':'normalizedString','f-14':'normalizedString',
           'f-934':'gYear','f-935':'gYear','f-1127':'sequence'}
    result=[]
    for r in d['rows']:
        kind=kinds[r['fact_id']]
        terminal=r['chain'][-1]['base'].rsplit('}',1)[1]
        assert terminal=={'gYear':'gYear','cik':'token','sequence':'token','normalizedString':'normalizedString'}[kind]
        facets=[f for x in r['chain'] for f in x['facets']]
        expected=('[0-9]'*10 if kind=='cik' else '[1-9][0-9]*') if kind in ('cik','sequence') else None
        assert facets==([{'kind':'pattern','attributes':{'value':expected}}] if expected else [])
        result.append({'fact_id':r['fact_id'],'concept':r['source_concept'],'initial_character_data':r['original_token'],
                       'kind':kind,'terminal_type':terminal,'pattern':expected,**classify(r['original_token'],kind),
                       'declared_type':r['declared_type'],'declaration_source':r['declaration_anchor']['source'],
                       'chain_source':bind(DECLARATIONS),'full_validity':None,'portable_Value':'Unknown',
                       'financial_admission':False,'normalization_status':'source-defined documentary calculation, not observed PSVI'})
    return result

def examples():
    # Expectations are hand-authored independently of the implementation.
    return [
      {'id':'replace_keeps_spaces','kind':'normalizedString','input':'  00\t42\r\n ','normalized':'  00 42   ','membership':True},
      {'id':'collapse_cik','kind':'cik','input':' \t0000320193\r\n','normalized':'0000320193','membership':True},
      {'id':'cik_leading_zeros','kind':'cik','input':'0000320193','normalized':'0000320193','membership':True},
      {'id':'cik_integer_loss','kind':'cik','input':'320193','normalized':'320193','membership':False},
      {'id':'cik_extra_prefix','kind':'cik','input':'x0000320193','normalized':'x0000320193','membership':False},
      {'id':'cik_extra_suffix','kind':'cik','input':'0000320193x','normalized':'0000320193x','membership':False},
      {'id':'cik_internal_space','kind':'cik','input':'00003 20193','normalized':'00003 20193','membership':False},
      {'id':'cik_nbsp_not_collapsed','kind':'cik','input':'\u00a00000320193\u00a0','normalized':'\u00a00000320193\u00a0','membership':False},
      {'id':'cik_nonascii_digits','kind':'cik','input':'００００３２０１９３','normalized':'００００３２０１９３','membership':False},
      {'id':'sequence_valid','kind':'sequence','input':' \t42\n','normalized':'42','membership':True},
      {'id':'sequence_leading_zero','kind':'sequence','input':'042','normalized':'042','membership':False},
      {'id':'sequence_zero','kind':'sequence','input':'0','normalized':'0','membership':False},
      {'id':'sequence_plus','kind':'sequence','input':'+42','normalized':'+42','membership':False},
      {'id':'sequence_empty','kind':'sequence','input':' \t ','normalized':'','membership':False},
      {'id':'normalized_leading_zeros','kind':'normalizedString','input':'00408','normalized':'00408','membership':True},
      {'id':'normalized_nbsp_preserved','kind':'normalizedString','input':'\u00a0 42 \u00a0','normalized':'\u00a0 42 \u00a0','membership':True},
      {'id':'year_observed','kind':'gYear','input':'2024','normalized':'2024','membership':True},
      {'id':'year_whitespace','kind':'gYear','input':'\t2062\n','normalized':'2062','membership':True},
      {'id':'year_zero_xsd10','kind':'gYear','input':'0000','normalized':'0000','membership':False},
      {'id':'year_timezone_unimplemented','kind':'gYear','input':'2024Z','normalized':'2024Z','membership':None},
      {'id':'year_negative_unimplemented','kind':'gYear','input':'-0001','normalized':'-0001','membership':None},
      {'id':'year_long_unimplemented','kind':'gYear','input':'10000','normalized':'10000','membership':None},
    ]

def check():
    expected_rows=rows(); assert read('interpretations.json')['rows']==expected_rows
    assert len(expected_rows)==7 and all(r['selected_membership'] is True for r in expected_rows)
    fixtures=read('examples.json'); assert fixtures==examples()
    checked=0
    for x in fixtures:
        got=classify(x['input'],x['kind'])
        assert got['normalized']==x['normalized'], x['id'];checked+=1
        assert got['selected_membership'] is x['membership'], x['id'];checked+=1
    assert str(int('0000320193'))=='320193'
    assert '00408'!='408' and int('00408')==int('408');checked+=2
    nbsp='\u00a00000320193\u00a0'
    assert ' '.join(nbsp.split())=='0000320193' and collapse_xml_space(nbsp)==nbsp;checked+=1
    assert collapse_xml_space('a\u00a0b')=='a\u00a0b';checked+=1
    # Mutation tests target conclusions, not a claim to full XSD validation.
    rejections=[]
    for field,bad in [('portable_Value','Int'),('full_validity',True),('financial_admission',True)]:
        altered=json.loads(json.dumps(expected_rows));altered[0][field]=bad
        assert altered!=rows();rejections.append(field)
    for kind,token in [('cik','00003201930'),('cik','x0000320193'),('sequence','042'),('sequence','42x'),('gYear','0000')]:
        assert classify(token,kind)['selected_membership'] is False;rejections.append(kind+':'+token)
    ledger=read('source-ledger.json')
    for a in ledger['acquisitions']:
        for key in ('body','headers'):
            b=a[key];assert bind(ROOT/b['path'])==b
    assert len(ledger['acquisitions'])==3
    assert (UNIT/'sources/01-datatypes.body').read_bytes()==(UNIT/'sources/02-dated.body').read_bytes()
    passages=read('passages.json')
    for r in passages:
        source=(ROOT/r['source']['path']).read_bytes(); assert sha(source)==r['source']['sha256']
        raw=source[r['byte_start']:r['byte_end_exclusive']]; assert sha(raw)==r['slice_sha256']
        assert plain(raw.decode())==r['text'];checked+=2
    text_by_id={r['id']:r['text'] for r in passages}
    assert 'implicitly anchors all regular expressions at the head and tail' in text_by_id['regex']
    assert '0000' in text_by_id['year-zero'] and 'not a valid lexical representation' in text_by_id['year-zero']
    assert 'initial value' in text_by_id['normalization-stage'] and 'normalized value' in text_by_id['normalization-stage']
    assert 'value="replace"' in text_by_id['builtin-normalizedString']
    assert 'value="collapse"' in text_by_id['builtin-token']
    assert 'fixed="true" value="collapse"' in text_by_id['builtin-gYear']
    return {'status':'finite documentary semantics checked','facts':7,'examples':len(fixtures),
            'explicit_assertions':checked,'source_passages':len(passages),'acquisitions':3,
            'illustrative_rejections':rejections,'outside_subset_not_rejected':3,
            'frozen_Values_changed':0,'full_validity_admissions':0,'whole_rows_closed':0}
