"""Finite source-to-OIM dimension inquiry; not an XBRL/OIM validator."""
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, timedelta
import importlib.util
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/'data/accounting-master'
spec=importlib.util.spec_from_file_location('oim_local_helpers',B/'r06-numeric-lexical-20261020/compare.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
load,bind=m.load,m.bind
X='{http://www.xbrl.org/2003/instance}'
L='{http://www.xbrl.org/2003/linkbase}'
D='{http://xbrl.org/2006/xbrldi}'
XML='{http://www.w3.org/XML/1998/namespace}'
XL='{http://www.w3.org/1999/xlink}'
XS=m.XS
O='{https://xbrl.org/2021}'
COVER=B/'native-concept-type-coverage-20261018/coverage.json'
PERIODS=B/'r06-context-periods-20261020/contexts.json'
UNITS=B/'r06-unit-measures-20261020/units.json'
TYPES=B/'r06-unit-measures-20261020/facts.json'
OLD=B/'r06-duplicate-facts-20261020/duplicate-facts.json'
DIMS=B/'r06-dimensional-facts-20261020/dimensional-facts.json'
TYPED=B/'r06-typed-domain-dates-20261020/declarations.json'
INPUTS=[m.INSTANCE,COVER,PERIODS,UNITS,TYPES,OLD,DIMS,TYPED,
 B/'r06-typed-domain-dates-20261020/occurrences.json',
 B/'r06-numeric-lexical-20261020/occurrences.json',
 B/'r06-text-semantics-20261020/occurrences.json',
 B/'r06-calculations11-source-20261020/prerequisites.json',
 B/'r06-numeric-lexical-20261020/compare.py']


def token(x):return json.dumps(x,sort_keys=True,separators=(',',':'))

def boundary(text,role):
    value=m.collapse(text)
    assert re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',value),'outside finite date profile'
    d=date.fromisoformat(value)
    if role in ('endDate','instant'):d+=timedelta(days=1)
    return d.isoformat()+'T00:00:00'

def text_class(path):
    builtins=set(path)
    if XS+'token' in builtins:builtins.add(XS+'normalizedString')
    if XS+'normalizedString' in builtins:builtins.add(XS+'string')
    excluded=any(n in (XS+'language',XS+'Name',XS+'NCName',XS+'ID',XS+'IDREF',XS+'ENTITY') or
        (n.startswith('{http://www.xbrl.org/dtr/type/') and n.split('}')[-1] in
         ('domainItemType','noLangTokenItemType','noLangStringItemType')) for n in path)
    return XS+'string' in builtins and not excluded

def language_value(is_text,lang):
    return m.collapse(lang).lower() if is_text and lang and m.collapse(lang) else None

def unit_value(numerators,denominators):
    if numerators==[X+'pure'] and not denominators:return None
    return {'numerators':sorted(numerators),'denominators':sorted(denominators)}

def ancestry(name,nodes):
    out=[]
    while True:
        assert name not in out,'type cycle'
        out.append(name);n=nodes[name]
        if n['status']=='builtin_reference_only':break
        assert len(n['edges'])==1 and n['edges'][0]['role']=='base'
        name=n['edges'][0]['target']
    return out

def shape_scan(root):
    allnodes=list(root.iter());parent={id(c):p for p in allnodes for c in p}
    contexts=[e for e in root if e.tag==X+'context']
    dimensions=[e for e in allnodes if e.tag in (D+'explicitMember',D+'typedMember')]
    containers=[e for e in allnodes if e.tag in (X+'segment',X+'scenario')]
    facts=[e for e in allnodes if 'contextRef' in e.attrib]
    return {
      'elements':len(allnodes),'direct_facts':sum(parent.get(id(e)) is root for e in facts),
      'all_contextRef_elements':len(facts),'contexts':len(contexts),
      'unexpected_root_children':[e.tag for e in root if not e.get('contextRef') and e.tag not in
        (X+'context',X+'unit',L+'schemaRef',L+'roleRef',L+'arcroleRef',L+'linkbaseRef',L+'footnoteLink')],
      'non_dimensional_children':[c.tag for e in containers for c in e if c.tag not in (D+'explicitMember',D+'typedMember')],
      'non_whitespace_container_text':sum(bool((e.text or '').strip()) or any((c.tail or '').strip() for c in e) for e in containers),
      'dimension_containers':dict(Counter(parent[id(e)].tag for e in dimensions)),
      'segment_count':sum(e.tag==X+'segment' for e in containers),
      'scenario_count':sum(e.tag==X+'scenario' for e in containers),
      'explicit_members':sum(e.tag==D+'explicitMember' for e in dimensions),
      'typed_members':sum(e.tag==D+'typedMember' for e in dimensions),
      'footnote_resources':sum(e.tag==L+'footnote' for e in allnodes),
      'literal_xbrli_footnote_elements':sum(e.tag==X+'footnote' for e in allnodes),
      'footnote_links':sum(e.tag==L+'footnoteLink' for e in allnodes),
      'footnote_arcs':sum(e.tag==L+'footnoteArc' for e in allnodes),
      'linkbase_refs':sum(e.tag==L+'linkbaseRef' for e in allnodes),
      'role_refs':sum(e.tag==L+'roleRef' for e in allnodes),
      'arcrole_refs':sum(e.tag==L+'arcroleRef' for e in allnodes),
      'nonroot_xml_base':sum(XML+'base' in e.attrib for e in allnodes if e is not root),
      'root_xml_base':root.get(XML+'base'),
      'precision_attributes':sum('precision' in e.attrib for e in facts),
      'zero_precision':sum(e.get('precision','').strip() in ('0','+0','-0') for e in facts),
      'language_declarations':dict(Counter(e.get(XML+'lang') for e in allnodes if XML+'lang' in e.attrib)),
      'nonstandard_footnote_roles':[e.get(XL+'role') for e in allnodes if e.tag==L+'footnote' and
         e.get(XL+'role') not in (None,'http://www.xbrl.org/2003/role/footnote')]}

def derive():
    cover=load(COVER);root,ns=m.schema(str(m.INSTANCE.relative_to(R)))
    inventory=shape_scan(root)
    assert inventory['all_contextRef_elements']==inventory['direct_facts']==1127
    assert not inventory['unexpected_root_children']
    assert not inventory['non_dimensional_children'] and not inventory['non_whitespace_container_text']
    assert set(inventory['dimension_containers'])=={X+'segment'}
    for k in ('scenario_count','footnote_resources','literal_xbrli_footnote_elements','footnote_links','footnote_arcs',
              'linkbase_refs','role_refs','arcrole_refs','nonroot_xml_base','precision_attributes'):
        assert inventory[k]==0,k
    nodes=cover['type_nodes'];type_rows=[]
    for name,c in sorted(cover['concepts'].items()):
        m.checked_anchor(c['declaration_anchor'])
        sr,ss=m.schema(c['declaration_anchor']['source_path'])
        declarations=[e for e in sr if e.tag==XS+'element' and e.get('name')==name.split('}')[-1]]
        assert len(declarations)==1
        d=declarations[0]
        assert m.expanded(d.get('substitutionGroup'),ss[id(d)])==X+'item'
        assert m.expanded(d.get('type'),ss[id(d)])==c['declared_type']
        path=ancestry(c['declared_type'],nodes)
        assert X+'fractionItemType' not in path
        type_rows.append({'concept':name,'path':path,'text':text_class(path),'substitutionGroup':X+'item'})
    for name,node in nodes.items():
        if node['status']!='builtin_reference_only':
            m.checked_anchor(node['anchor'])
            sr,ss=m.schema(node['anchor']['source_path'])
            defs=[e for e in sr if e.get('name')==name.split('}')[-1]]
            assert len(defs)==1
            assert not any(e.tag==XS+'complexContent' for e in defs[0].iter())
            ds=[e for e in defs[0].iter() if e.tag in (XS+'extension',XS+'restriction')]
            assert len(ds)==1 and m.expanded(ds[0].get('base'),ss[id(ds[0])])==node['edges'][0]['target']
    typed=load(TYPED)
    assert typed['domain_type']==XS+'date'
    for key in ('axis','domain'):
        attrs=typed[key+'_attributes'];assert attrs['name']==typed[key].split('}')[-1]
    periods={c['context_id']:c for c in load(PERIODS)}
    prior_dims={c['context_id']:c for c in load(DIMS)['contexts']}
    contexts={};context_rows=[]
    for c in root.findall(X+'context'):
        ident=c.find(X+'entity/'+X+'identifier');period=c.find(X+'period');dims={}
        assert ident is not None and not list(ident)
        assert ident.text==m.collapse(ident.text) and ident.get('scheme')==m.collapse(ident.get('scheme'))
        if not (ident.text=='NA' and ident.get('scheme')=='https://xbrl.org/2021/entities'):
            dims[O+'entity']={'scheme':ident.get('scheme'),'identifier':ident.text}
        p=list(period)
        if len(p)==1 and p[0].tag==X+'instant':
            b=boundary(p[0].text,'instant');interval=[b,b]
            assert b==periods[c.get('id')]['interpretation']['instant']['implied_boundary']
        else:
            assert [e.tag for e in p]==[X+'startDate',X+'endDate']
            interval=[boundary(p[0].text,'startDate'),boundary(p[1].text,'endDate')]
            assert interval==[periods[c.get('id')]['interpretation'][k]['implied_boundary'] for k in ('start','end')]
        dims[O+'period']={'interval':interval,'timezone':'absent_not_inferred'}
        reported=[]
        for e in c.iter():
            if e.tag not in (D+'explicitMember',D+'typedMember'):continue
            axis=m.expanded(e.get('dimension'),ns[id(e)]);assert axis not in dims
            if e.tag==D+'explicitMember':
                value={'datatype':XS+'QName','value':m.expanded(m.collapse(e.text),ns[id(e)])}
            else:
                assert axis==typed['axis'] and len(e)==1 and e[0].tag==typed['domain'] and not list(e[0])
                assert not e[0].attrib and date.fromisoformat(e[0].text).isoformat()==e[0].text
                value={'datatype':XS+'date','value':e[0].text,'timezone':'absent_not_inferred'}
            dims[axis]=value;reported.append(axis)
        assert set(reported)=={d['axis_qname'] for d in prior_dims[c.get('id')]['dimensions']}
        contexts[c.get('id')]=dims
        context_rows.append({'context_id':c.get('id'),'dimensions':dims,'reported_axes':reported,'defaults_inserted':False})
    prior_units={u['unit_id']:u for u in load(UNITS)};units={};unit_rows=[]
    for u in root.findall(X+'unit'):
        div=u.find(X+'divide')
        if div is None:n=u.findall(X+'measure');d=[]
        else:n=div.findall(X+'unitNumerator/'+X+'measure');d=div.findall(X+'unitDenominator/'+X+'measure')
        numer=[m.expanded(m.collapse(e.text),ns[id(e)]) for e in n]
        denom=[m.expanded(m.collapse(e.text),ns[id(e)]) for e in d]
        assert {'numerator':dict(Counter(numer)),'denominator':dict(Counter(denom))}==prior_units[u.get('id')]['interpretation']['product_signature']
        units[u.get('id')]=unit_value(numer,denom)
        unit_rows.append({'unit_id':u.get('id'),'unit_dimension':units[u.get('id')]})
    class_by_concept={r['concept']:r for r in type_rows}
    oldtypes={r['fact_id']:r for r in load(TYPES)}
    coverage={r['fact_id']:r for r in cover['occurrences']}
    fact_rows=[];groups=defaultdict(list);inherited=root.get(XML+'lang')
    ids=[e.get('id') for e in root.iter() if e.get('id') is not None]
    assert len(ids)==len(set(ids))
    for position,e in enumerate(root,1):
        if not e.get('contextRef'):continue
        fid=e.get('id');assert re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]*',fid)
        assert e.tag==coverage[fid]['source_concept']
        assert coverage[fid]['source_span']['element_path']==f'/1/{position}'
        assert not list(e),'nested fact content outside finite source profile'
        dims=deepcopy(contexts[e.get('contextRef')]);dims[O+'concept']=e.tag
        cls=class_by_concept[e.tag];path=cls['path']
        numeric=path[-1] in (XS+'decimal',XS+'integer',XS+'float',XS+'double')
        assert numeric==oldtypes[fid]['numeric']
        assert bool(e.get('unitRef'))==numeric
        if numeric and units[e.get('unitRef')] is not None:dims[O+'unit']=units[e.get('unitRef')]
        effective=e.get(XML+'lang',inherited);lang=language_value(cls['text'],effective)
        if lang is not None:dims[O+'language']=lang
        nil=e.get(m.XSI+'nil') in ('true','1')
        dec=None if nil or not numeric else e.get('decimals')
        assert dec is None or dec=='INF' or re.fullmatch(r'[+-]?[0-9]+',dec)
        row={'fact_id':fid,'source_path':f'/1/{position}','dimensions':dims,'numeric':numeric,'text':cls['text'],
             'effective_xml_language':effective,'language_equality_value':lang,'nil':nil,
             'decimals':None if dec is None else ('infinity' if dec=='INF' else int(dec)),
             'value_source':{'occurrence':fid,'type':coverage[fid]['portable_candidate_value']['tag']},
             'full_oim_value_validation':'not_run','links':[]}
        groups[token(dims)].append(fid);fact_rows.append(row)
    assert len(fact_rows)==len(coverage)==1127 and {r['fact_id'] for r in fact_rows}==set(coverage)
    classes=[{'members':members,'duplicate':len(members)>1} for members in groups.values()]
    oldpart={tuple(sorted(c['members'])) for c in load(OLD)['classes']}
    newpart={tuple(sorted(c['members'])) for c in classes}
    counts={'facts':len(fact_rows),'concepts':len(type_rows),'type_nodes':len(nodes),
      'contexts':len(context_rows),'units':len(unit_rows),'text_facts':sum(f['text'] for f in fact_rows),
      'numeric_facts':sum(f['numeric'] for f in fact_rows),'language_facts':sum(f['language_equality_value'] is not None for f in fact_rows),
      'pure_unit_omissions':sum(f['numeric'] and O+'unit' not in f['dimensions'] for f in fact_rows),
      'nil_facts':sum(f['nil'] for f in fact_rows),'classes':len(classes),'duplicate_classes':sum(c['duplicate'] for c in classes),
      'duplicate_occurrences':sum(len(c['members']) for c in classes if c['duplicate']),
      'duplicate_pairs':sum(len(c['members'])*(len(c['members'])-1)//2 for c in classes),
      'old_only_classes':len(oldpart-newpart),'new_only_classes':len(newpart-oldpart),
      'note_facts':0,'generated_fact_ids':0}
    duties=[]
    names=['dimension-only containers','single container','simple typed dimension','no tuples','no fraction ancestry',
      'standard footnote resource roles','no zero precision','no instance linkbaseRef',
      'roleRef/arcroleRef discoverability','no unlinked footnotes','no non-root xml:base','typed legacy/derivation restrictions']
    for i,name in enumerate(names,1):
        duties.append({'section':f'2.1.{i}','duty':name,'status':'supported_for_retained_instance',
          'basis':'No applicable resources/references occur; no general processor implemented' if i in (6,9,10) else 'Exact source structure and used declaration paths',
          'general_validation':False})
    return {'inventory':inventory,'compatibility':duties,'types':type_rows,'contexts':context_rows,'units':unit_rows,
      'facts':fact_rows,'classes':classes,'counts':counts,'partition_equal':oldpart==newpart,
      'old_only_classes':sorted(oldpart-newpart),'new_only_classes':sorted(newpart-oldpart),
      'value_mapping_scope':'dimensions and IDs complete within finite profile; values remain separately bound source candidates',
      'full_schema_validation':'not_run','installed_correspondence':'not_checked','actual_calc11':'not_run'}


def fixtures():
    results=[]
    def expect(name,actual,expected):
        assert actual==expected,name
        results.append({'name':name,'actual':actual,'expected':expected,'passed':True})
    expect('string text',text_class([XS+'string']),True)
    expect('token inherits string',text_class([XS+'token']),True)
    for t in ('language','Name','NCName','ID','IDREF','ENTITY'):
        expect('excluded xs '+t,text_class([XS+t,XS+'token',XS+'string']),False)
    for t in ('domainItemType','noLangTokenItemType','noLangStringItemType'):
        expect('excluded DTR '+t,text_class(['{http://www.xbrl.org/dtr/type/2020-01-21}'+t,XS+'string']),False)
    expect('boolean nontext',text_class([XS+'boolean']),False)
    expect('language equality',language_value(True,' EN-us '),'en-us')
    expect('language cleared',language_value(True,''),None)
    expect('nontext language absent',language_value(False,'en-US'),None)
    expect('different text languages',language_value(True,'fr')==language_value(True,'en'),False)
    expect('pure absent',unit_value([X+'pure'],[]),None)
    expect('double pure retained',unit_value([X+'pure',X+'pure'],[]) is None,False)
    expect('unit multiplicity',unit_value(['a','a'],[])==unit_value(['a'],[]),False)
    expect('unit order immaterial',unit_value(['b','a'],[])==unit_value(['a','b'],[]),True)
    expect('numerator versus denominator',unit_value(['a'],['b'])==unit_value(['b'],['a']),False)
    expect('leap end',boundary('2024-02-29','endDate'),'2024-03-01T00:00:00')
    expect('leap start',boundary('2024-02-29','startDate'),'2024-02-29T00:00:00')
    expect('year instant',boundary('2024-12-31','instant'),'2025-01-01T00:00:00')
    for text in ('2024-02-30','2024-01-01Z','2024-01-01T00:00:00'):
        try:boundary(text,'instant')
        except (AssertionError,ValueError):rejected=True
        else:rejected=False
        expect('finite period rejects '+text,rejected,True)
    base=ET.fromstring(f'<xbrl xmlns="{X[1:-1]}"><context id="c"><entity><segment /></entity></context><item contextRef="c" id="f" /></xbrl>')
    r=deepcopy(base);r[-1].set(XML+'base','x');expect('nonroot base',shape_scan(r)['nonroot_xml_base'],1)
    r=deepcopy(base);r.set(XML+'base','x');expect('root base permitted',shape_scan(r)['nonroot_xml_base'],0)
    r=deepcopy(base);ET.SubElement(r,L+'linkbaseRef');expect('direct linkbase',shape_scan(r)['linkbase_refs'],1)
    r=deepcopy(base);ET.SubElement(r,L+'roleRef');expect('role reference duty',shape_scan(r)['role_refs'],1)
    r=deepcopy(base);ET.SubElement(r,L+'arcroleRef');expect('arcrole reference duty',shape_scan(r)['arcrole_refs'],1)
    r=deepcopy(base);r[-1].set('precision','0');expect('zero precision',shape_scan(r)['zero_precision'],1)
    r=deepcopy(base);ET.SubElement(r[0][0][0],X+'unexpected');expect('qualifier rejected',len(shape_scan(r)['non_dimensional_children']),1)
    r=deepcopy(base);ET.SubElement(r,L+'footnote',{XL+'role':'urn:other'});expect('nonstandard note role',shape_scan(r)['nonstandard_footnote_roles'],['urn:other'])
    r=deepcopy(base);n=r[-1];r.remove(n);ET.SubElement(r,'{urn:test}Tuple').append(n);expect('nested item detected',shape_scan(r)['direct_facts'],0)
    d={'concept':'c','entity':'e','period':['a','b']}
    expect('value excluded from identity',token(d)==token(deepcopy(d)),True)
    dd=deepcopy(d);dd['axis']='default';expect('default insertion changes identity',token(d)==token(dd),False)
    expect('typed date differs from QName',token({'datatype':XS+'date','value':'2024-01-01'})==token({'datatype':XS+'QName','value':'2024-01-01'}),False)
    return results


def check():
    checks=0
    def ck(value,label):
        nonlocal checks
        assert value,label;checks+=1
    ledger=load(U/'source-ledger.json')
    for item in ledger['bindings']:ck(bind(R/item['path'])==item,item['path'])
    for anchor in ledger['anchors']:
        raw=(R/anchor['source_path']).read_bytes()
        ck(m.digest(raw)==anchor['source_sha256'],'source hash')
        ck(raw[anchor['byte_start']:anchor['byte_end']].decode()==anchor['text'],'anchor')
    actual=derive();ck(actual==load(U/'mapping.json'),'regenerated mapping')
    f=fixtures();ck(f==load(U/'fixtures.json'),'fixtures replay')
    ck(actual['partition_equal'],'actual partition correspondence')
    ck(len(actual['compatibility'])==12,'all twelve compatibility constraints')
    for row in actual['facts']:
        ck((O+'language' in row['dimensions'])==row['text'],'actual text-language classification')
        ck(not row['nil'] or row['decimals'] is None,'nil decimals absent')
    return {'assertions':checks,'fixtures':len(f),'source_anchors':len(ledger['anchors']),
      'input_bindings':len(ledger['bindings']),**actual['counts'],'compatibility_constraints':12,
      'partition_equal':actual['partition_equal'],'full_validation':'not_run','actual_report_calc11':'not_run',
      'upstream_executed':False,'financial_admission':False,'whole_rows_closed':0}
