"""Bounded source-only declared-type interpretations; no upstream execution."""
from collections import Counter
from datetime import date
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import re

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R/'data/accounting-master'
PRIOR = B/'r06-numeric-lexical-20261020'
spec = importlib.util.spec_from_file_location('local_source_binding_helpers', PRIOR/'compare.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
XS = m.XS
load, bind = m.load, m.bind
TERMINALS = {'boolean','duration','date','gMonthDay','string','normalizedString','token'}
BS = chr(92)
PATTERNS = {
    'submissionTypeItemType': '((Other)|([A-Z0-9]+([/A-Z0-9 '+BS+'.'+BS+'-]*[A-Z0-9])?))',
    'fileNumberItemType': '[0-9]{1,3}-[0-9]{1,8}(-.{1,4})?',
    'employerIdItemType': '[0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9][0-9]',
    'internationalNameItemType': '['+BS+'p{L}'+BS+'p{N}].*',
    'enumerationSetItemType': '([A-Za-z][-A-Za-z0-9+-.]*:'+BS+'S+#['+BS+'i-[:]]['+BS+'c-[:]]*( [A-Za-z][-A-Za-z0-9+-.]*:'+BS+'S+#['+BS+'i-[:]]['+BS+'c-[:]]*)*)?',
}
DURATION = re.compile(r'(-)?P(?:([0-9]+)Y)?(?:([0-9]+)M)?(?:([0-9]+)D)?(T(?:([0-9]+)H)?(?:([0-9]+)M)?(?:([0-9]+(?:[.][0-9]+)?)S)?)?')

def normalized(s, terminal):
    if terminal == 'string': return s
    if terminal == 'normalizedString': return s.translate({9:32, 10:32, 13:32})
    return m.collapse(s)

def calendar_member(y, month, day):
    if not 1 <= y <= 9999 or not 1 <= month <= 12: return False
    leap = y % 400 == 0 or (y % 100 != 0 and y % 4 == 0)
    days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    result = 1 <= day <= days[month-1]
    try: date(y, month, day); independent = True
    except ValueError: independent = False
    assert result == independent
    return result

def base_interpretation(s, terminal):
    assert terminal in TERMINALS
    if not isinstance(s, str): return {'status':'not_text','normalized':None,'value':None}
    t = normalized(s, terminal)
    out = {'status':'supported','normalized':t,'value':None}
    if terminal in ('string','normalizedString','token'):
        out['value'] = {'kind':'string','text':t}
    elif terminal == 'boolean':
        if t not in ('true','false','1','0'): out['status']='outside_lexical_space'
        else: out['value']={'kind':'boolean','value':t in ('true','1')}
    elif terminal == 'duration':
        match = DURATION.fullmatch(t)
        if match is None:
            out['status']='outside_lexical_space'
        else:
            sign, y, mo, d, time_group, h, mi, sec = match.groups()
            if all(x is None for x in (y,mo,d,h,mi,sec)) or (time_group is not None and all(x is None for x in (h,mi,sec))):
                out['status']='outside_lexical_space'
            else:
                fields = [m.digits(x) if x is not None else 0 for x in (y,mo,d,h,mi)]
                seconds = Fraction(sec) if sec is not None else Fraction(0)
                out['value']={'kind':'duration_components','sign':-1 if sign else 1,
                    **dict(zip(('years','months','days','hours','minutes'),fields)),
                    'seconds':m.rational(seconds),'canonical_or_equality_normalized':False}
    elif terminal == 'date':
        match = re.fullmatch(r'([0-9]{4})-([0-9]{2})-([0-9]{2})',t)
        if match:
            y, month, day = (m.digits(x) for x in match.groups())
            if not calendar_member(y,month,day): out['status']='outside_lexical_space'
            else: out['value']={'kind':'calendar_date','year':y,'month':month,'day':day,'timezone':None,
                               'meaning':'one_day_interval_on_nontimezoned_timeline'}
        else:
            out['status']='outside_scope'
    else:
        match = re.fullmatch(r'--([0-9]{2})-([0-9]{2})',t)
        if match:
            month, day = (m.digits(x) for x in match.groups())
            if not calendar_member(2000,month,day): out['status']='outside_lexical_space'
            else: out['value']={'kind':'recurring_month_day','month':month,'day':day,'timezone':None,
                               'year_assigned':False}
        else:
            out['status']='outside_scope'
    return out

def pattern_member(local, text):
    if local == 'submissionTypeItemType':
        return text == 'Other' or bool(text) and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/ .-' for c in text) and text[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' and text[-1] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    if local == 'fileNumberItemType':
        return re.fullmatch('[0-9]{1,3}-[0-9]{1,8}(-[^\r\n]{1,4})?',text) is not None
    if local == 'employerIdItemType':
        return re.fullmatch('[0-9]{2}-[0-9]{7}',text) is not None
    if local == 'internationalNameItemType':
        if not text: return False
        if not text[0].isascii(): return None
        return text[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789' and '\r' not in text and '\n' not in text
    if local == 'enumerationSetItemType':
        if not text: return True
        if not text.isascii(): return None
        part = r'[A-Za-z][-A-Za-z0-9+.-]*:[^ \t\r\n]+#[A-Za-z_][A-Za-z0-9_.-]*'
        return re.fullmatch(part+'( '+part+')*',text) is not None
    return None

def type_audit(d, concepts):
    visited, paths = {}, {}
    def visit(name, trail):
        assert name not in trail
        n = d['type_nodes'][name]
        if n['status']=='builtin_reference_only':
            assert name.split('}')[-1] in TERMINALS
            visited[name]={'type':name,'terminal':True,'facets':[]}
            return [name]
        m.checked_anchor(n['anchor'])
        root, scopes = m.schema(n['anchor']['source_path'])
        matches=[e for e in root if e.get('name')==name.split('}')[-1] and e.tag in (XS+'simpleType',XS+'complexType')]
        assert len(matches)==1
        es=[e for e in matches[0].iter() if e.tag in (XS+'extension',XS+'restriction')]
        assert len(es)==1
        e=es[0];children=[{'tag':c.tag,'attributes':dict(c.attrib)} for c in e]
        assert children==n['derivation_children']
        assert e.tag.split('}')[-1]==n['derivation']
        assert len(n['edges'])==1 and n['edges'][0]['role']=='base'
        target=m.expanded(e.attrib['base'],scopes[id(e)])
        assert target==n['edges'][0]['target']
        facets=[c for c in children if c['tag']!=XS+'attributeGroup']
        assert all(c['tag'] in (XS+'enumeration',XS+'minLength',XS+'maxLength',XS+'pattern') for c in facets), 'unsupported facet'
        for c in facets:
            if c['tag']==XS+'pattern': assert c['attributes']['value']==PATTERNS[name.split('}')[-1]]
        visited[name]={'type':name,'terminal':False,'base':target,'derivation':n['derivation'],
                       'facets':facets,'anchor':n['anchor']}
        return [name]+visit(target,trail|{name})
    for name in sorted(concepts):
        c=d['concepts'][name];m.checked_anchor(c['declaration_anchor'])
        root,scopes=m.schema(c['declaration_anchor']['source_path'])
        es=[e for e in root if e.tag==XS+'element' and e.get('name')==name.split('}')[-1]]
        assert len(es)==1 and dict(es[0].attrib)==c['source_attributes']
        assert m.expanded(es[0].attrib['type'],scopes[id(es[0])])==c['declared_type']
        path=visit(c['declared_type'],set())
        assert [path[-1]]==c['type_path']['terminal_references']
        paths[name]=path
    nodes=[visited[k] for k in sorted(visited)]
    return {'concept_paths':paths,'nodes':nodes,'concepts':len(paths),'type_nodes':len(nodes),
            'nodes_with_facets':sum(bool(n['facets']) for n in nodes),'schema_validation':'not_run'}

def facets_interpretation(text, terminal, path, nodes):
    verdicts=[]
    for name in path:
        node=nodes[name];facets=node['facets'];local=name.split('}')[-1]
        enums=[f['attributes']['value'] for f in facets if f['tag']==XS+'enumeration']
        if enums:
            options=[normalized(v,terminal) for v in enums]
            verdicts.append({'type':name,'facet':'enumeration','choices':len(enums),'passed':text in options})
        for f in facets:
            kind=f['tag'].split('}')[-1]
            if kind in ('minLength','maxLength'):
                bound=m.digits(f['attributes']['value'])
                passed=len(text)>=bound if kind=='minLength' else len(text)<=bound
                verdicts.append({'type':name,'facet':kind,'bound':bound,'length':len(text),'passed':passed})
            elif kind=='pattern':
                passed=pattern_member(local,text)
                verdicts.append({'type':name,'facet':'pattern','pattern':f['attributes']['value'],'passed':passed,
                                 'scope':'source_specific_rule_with_explicit_ASCII_name_category_subset'})
    return verdicts

def interpret(row, path, nodes):
    terminal=path[-1].split('}')[-1]
    out={k:row[k] for k in ('fact_id','source_concept','source_context_id','source_unit_id',
          'source_attributes','decoded_text','source_span','packet_candidate_value','portable_candidate_value')}
    base=base_interpretation(row['decoded_text'],terminal)
    facets=facets_interpretation(base['normalized'],terminal,path,nodes) if base['status']=='supported' else []
    status=base['status']
    if any(f['passed'] is False for f in facets): status='facet_mismatch'
    elif any(f['passed'] is None for f in facets): status='facet_outside_scope'
    unchanged=row['portable_candidate_value']=={'tag':'Text','text':row['decoded_text']}
    if not unchanged: status='candidate_text_mismatch'
    residual=[]
    if any(n.endswith('}textBlockItemType') or n.endswith('}xmlNodesItemType') for n in path):
        residual.append('unescaped_XML_nodes_and_XHTML_content_requirements_not_checked')
    if any(n.endswith('}enumerationSetItemType') for n in path):
        residual.append('extensible_enumeration_domain_and_set_semantics_not_checked')
    out.update(type_path=path,terminal=terminal,interpretation=base,facet_checks=facets,status=status,
               nonfacet_semantic_obligations=residual,
               raw_candidate_preserved=unchanged,portable_value_mutated=False,schema_validation='not_run',
               processor_value_admitted=False,financial_admission=False)
    return out

def derive():
    d=load(m.COVERAGE)
    selected=[r for r in d['occurrences'] if r['portable_candidate_value']['tag']=='Text']
    audit=type_audit(d,{r['source_concept'] for r in selected})
    nodes={n['type']:n for n in audit['nodes']}
    data=m.INSTANCE.read_bytes()
    elements={e.get('id'):e for e in m.ET.fromstring(data) if e.get('contextRef') is not None}
    rows=[]
    for r in selected:
        a=r['source_span'];piece=data[a['byte_start']:a['byte_end']]
        assert m.digest(piece)==a['slice_sha256'] and piece.decode()==a['raw_utf8']
        e=elements[r['fact_id']]
        assert e.tag==r['source_concept'] and dict(e.attrib)==r['source_attributes']
        assert e.text==r['decoded_text'] and len(e)==0
        assert r['packet_candidate_value']=={'tag':'UnvalidatedText','text':r['decoded_text']}
        assert r['portable_candidate_value']=={'tag':'Text','text':r['decoded_text']}
        assert r['validation_status']=='not_run' and not r['portable_value_mutated']
        rows.append(interpret(r,audit['concept_paths'][r['source_concept']],nodes))
    return audit,rows

def check():
    audit,rows=derive();assertions=0
    def require(c):
        nonlocal assertions
        assert c
        assertions+=1
    require(audit==load(U/'type-audit.json'));require(rows==load(U/'occurrences.json'))
    require((len(rows),audit['concepts'],audit['type_nodes'],audit['nodes_with_facets'])==(157,112,35,14))
    for row in rows:
        require(row['status']=='supported' and row['raw_candidate_preserved'])
        require(row['schema_validation']=='not_run' and not row['processor_value_admitted'])
    fixtures=load(U/'fixtures.json')
    for f in fixtures:
        result=base_interpretation(f['raw'],f['terminal'])
        require(result['status']==f['expected_status'])
        if 'expected_value' in f: require(result['value']==f['expected_value'])
        if 'expected_normalized' in f: require(result['normalized']==f['expected_normalized'])
    patterns=load(U/'pattern-fixtures.json')
    for f in patterns: require(pattern_member(f['type'],f['text']) is f['expected'])
    source=load(U/'source-ledger.json')
    for b in source['bindings']: require(bind(R/b['path'])==b)
    for a in source['anchors']:
        p=R/a['source']['path'];require(bind(p)==a['source'])
        piece=b''.join(p.read_bytes().splitlines(keepends=True)[a['first_line']-1:a['last_line']])
        require(m.digest(piece)==a['raw_excerpt_sha256'])
        require(bind(R/a['readable']['path'])==a['readable'])
    d=load(m.COVERAGE);originals={r['fact_id']:r for r in d['occurrences']}
    nodes={n['type']:n for n in audit['nodes']}
    controls=load(U/'altered-controls.json')
    for c in controls:
        r=json.loads(json.dumps(originals[c['fact_id']]))
        if 'replacement_text' in c:
            r['decoded_text']=c['replacement_text']
            r['portable_candidate_value']={'tag':'Text','text':c['replacement_text']}
        if c.get('candidate_only'): r['portable_candidate_value']={'tag':'Text','text':'altered'}
        result=interpret(r,audit['concept_paths'][r['source_concept']],nodes)
        require(result['status']==c['expected_status'])
    # A month has different elapsed day counts at distinct calendar anchors.
    require((date(2024,2,1)-date(2024,1,1)).days==31)
    require((date(2024,3,1)-date(2024,2,1)).days==29)
    require(base_interpretation('P1M','duration')['value']['months']==1)
    require(base_interpretation('P30D','duration')['value']['days']==30)
    return {'status':'passed','assertions':assertions,'text_occurrences':len(rows),
            'terminal_counts':dict(Counter(r['terminal'] for r in rows)),
            'concepts':audit['concepts'],'type_nodes':audit['type_nodes'],'nodes_with_facets':audit['nodes_with_facets'],
            'fixtures':len(fixtures),'pattern_fixtures':len(patterns),'altered_controls':len(controls),
            'specification_anchors':len(source['anchors']),'all_narrow_interpretations_supported':True,
            'upstream_executed':False,'schema_validation':'not_run','new_acquisitions':0,'whole_rows_closed':0}
