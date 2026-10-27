"""Exact retained-network enumeration checks, not an installed XBRL validator."""
from collections import Counter, defaultdict, deque
import importlib.util
import json
from pathlib import Path
from urllib.parse import urljoin, urldefrag

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/'data/accounting-master'
spec=importlib.util.spec_from_file_location('local_text_semantics',B/'r06-text-semantics-20261020/compare.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
m=t.m
load,bind=m.load,m.bind
XS=m.XS
XL='{http://www.w3.org/1999/xlink}'
LINK='{http://www.xbrl.org/2003/linkbase}'
XBRLI='{http://www.xbrl.org/2003/instance}'
ENUM='{http://xbrl.org/2020/extensible-enumerations-2.0}'
XML='{http://www.w3.org/XML/1998/namespace}'
ROLE='http://fasb.org/us-gaap/role/eedm/ExtensibleEnumerationLists'
ARCROLE='http://xbrl.org/int/dim/arcrole/domain-member'
MAP=B/'native-offline-resolution-20261018/resource-map.json'

def require_simple_arc(attrs):
    permitted={XL+'arcrole',XL+'from',XL+'to',XL+'type','order'}
    assert set(attrs)<=permitted, 'effective arc or other attribute requires separate source handling'
    assert attrs[XL+'arcrole']==ARCROLE and attrs.get(XL+'type')=='arc'

def graph_witnesses(edges,head,head_usable=False):
    adjacency=defaultdict(set)
    for a,b in edges:adjacency[a].add(b)
    seen={head};queue=deque([head]);paths={head:[]}
    while queue:
        a=queue.popleft()
        for b in sorted(adjacency[a]):
            if b not in seen:
                seen.add(b);paths[b]=paths[a]+[[a,b]];queue.append(b)
    if not head_usable:paths.pop(head)
    return paths

def set_rules(raw,allowed):
    normalized=m.collapse(raw)
    tokens=normalized.split(' ') if normalized else []
    errors=[]
    if any(x not in allowed for x in tokens):errors.append('InvalidEnumerationSetValue')
    if len(set(tokens))!=len(tokens):errors.append('RepeatedEnumerationSetValue')
    if tokens!=sorted(tokens):errors.append('InvalidEnumerationSetOrder')
    return {'normalized':normalized,'members':tokens,'errors':errors,'passes_selected_rules':not errors}

def build_network():
    resources=load(MAP);roots={};ids={};declarations={};namespaces={}
    for r in resources:
        p=R/r['retained_path'];data=p.read_bytes()
        assert m.digest(data)==r['expected_blob']['digest'] and len(data)==r['expected_blob']['byte_length']
        root,scopes=m.schema(r['retained_path'])
        assert not any(XML+'base' in e.attrib for e in root.iter()), 'XML Base outside reviewed network scope'
        roots[r['logical_uri']]=(r,root,scopes)
        if root.tag==XS+'schema':
            ns=root.attrib['targetNamespace']
            for e in root:
                if e.tag==XS+'element':
                    expanded='{'+ns+'}'+e.attrib['name']
                    assert expanded not in declarations
                    declarations[expanded]={'attributes':dict(e.attrib),'source':r['retained_path'],
                                             'namespace_scope':scopes[id(e)]}
                    if e.get('id'):
                        key=(r['logical_uri'],e.attrib['id']);assert key not in ids
                        ids[key]=expanded
    def locator(uri,element):
        base,fragment=urldefrag(urljoin(uri,element.attrib[XL+'href']))
        assert fragment and (base,fragment) in ids, ('unresolved locator',base,fragment)
        return ids[(base,fragment)]
    arcs=[];links=[];role_links=0
    for uri,(r,root,scopes) in roots.items():
        for index,e in enumerate(root.iter(LINK+'definitionLink')):
            if e.get(XL+'role')!=ROLE:continue
            role_links+=1
            labels=defaultdict(list)
            for child in e:
                if child.tag==LINK+'loc':labels[child.attrib[XL+'label']].append(locator(uri,child))
            assert all(len(v)==1 for v in labels.values()), 'multiple locator bindings outside reviewed profile'
            count=0
            for child_index,a in enumerate(e):
                if a.tag!=LINK+'definitionArc':continue
                assert a.attrib[XL+'arcrole']==ARCROLE
                require_simple_arc(a.attrib)
                source=labels[a.attrib[XL+'from']][0];target=labels[a.attrib[XL+'to']][0]
                for n in (source,target):
                    declaration=declarations[n]
                    assert m.expanded(declaration['attributes']['substitutionGroup'],declaration['namespace_scope'])==XBRLI+'item'
                arcs.append({'source':source,'target':target,'order':a.get('order','1'),
                             'source_file':r['retained_path'],'definition_link_index':index,
                             'child_index':child_index,'attributes':dict(a.attrib)})
                count+=1
            links.append({'source_file':r['retained_path'],'definition_link_index':index,'role':ROLE,'arcs':count})
    edges=sorted({(a['source'],a['target']) for a in arcs})
    # All selected arcs are optional, priority zero, usable, same-role; merging
    # any equivalent duplicates changes no endpoint reachability.
    adjacency=defaultdict(set)
    for a,b in edges:adjacency[a].add(b)
    active,done=set(),set()
    def acyclic(n):
        assert n not in active, 'directed cycle'
        if n in done:return
        active.add(n)
        for child in adjacency[n]:acyclic(child)
        active.remove(n);done.add(n)
    for n in list(adjacency):acyclic(n)
    public={'retained_resources':len(resources),'matching_links':links,'raw_arcs':arcs,
            'unique_endpoint_edges':[list(x) for x in edges],'role':ROLE,'arcrole':ARCROLE,
            'special_arc_attributes_present':False,'xml_base_present':False,'directed_cycle':False,
            'all_endpoint_substitution_groups':'direct_xbrli_item',
            'effective_profile':'optional_priority_zero_usable_same_role',
            'installed_DTS_equivalence':'not_checked'}
    return public,declarations,edges

def derive():
    network,declarations,edges=build_network()
    d=load(m.COVERAGE)
    selected=[r for r in d['occurrences'] if d['concepts'][r['source_concept']]['declared_type']==ENUM+'enumerationSetItemType']
    previous={r['fact_id']:r for r in load(B/'r06-text-semantics-20261020/occurrences.json')}
    rows=[];domains={}
    for r in selected:
        assert previous[r['fact_id']]['status']=='supported'
        c=d['concepts'][r['source_concept']];m.checked_anchor(c['declaration_anchor'])
        decl=declarations[r['source_concept']];attrs=decl['attributes']
        assert attrs==c['source_attributes']
        head=m.expanded(attrs[ENUM+'domain'],decl['namespace_scope'])
        assert m.expanded(declarations[head]['attributes']['substitutionGroup'],
                          declarations[head]['namespace_scope'])==XBRLI+'item'
        assert attrs[ENUM+'linkrole']==ROLE
        assert attrs.get(ENUM+'headUsable')=='false'
        if head not in domains:
            paths=graph_witnesses(edges,head,False)
            domains[head]={'head':head,'head_usable':False,'paths':paths}
        paths=domains[head]['paths']
        expanded_uri=lambda name:name[1:].replace('}','#',1)
        allowed={expanded_uri(name):name for name in paths}
        rules=set_rules(r['decoded_text'],allowed)
        members=[]
        for token in rules['members']:
            name=allowed.get(token)
            members.append({'expanded_name_uri':token,'expanded_name':name,
                            'path':paths.get(name),'retained_domain_membership':name is not None})
        rows.append({'fact_id':r['fact_id'],'source_concept':r['source_concept'],
                     'source_context_id':r['source_context_id'],'source_span':r['source_span'],
                     'original_value':r['portable_candidate_value'],'declared_head':head,'head_usable':False,
                     'linkrole':ROLE,'rules':rules,'members':members,
                     'schema_xbrl_validation':'not_run','processor_admission':False,'value_mutated':False})
    return network,domains,rows

def check():
    network,domains,rows=derive();assertions=0
    def require(c):
        nonlocal assertions
        assert c
        assertions+=1
    require(network==load(U/'network.json'));require(domains==load(U/'domains.json'));require(rows==load(U/'occurrences.json'))
    require(len(rows)==16 and len({r['source_concept'] for r in rows})==8 and len(domains)==4)
    require(network['retained_resources']==27 and len(network['raw_arcs'])==718)
    for r in rows:
        require(r['rules']['passes_selected_rules'])
        require(r['original_value']=={'tag':'Text','text':r['rules']['normalized']})
        for member in r['members']:
            require(member['retained_domain_membership'] and bool(member['path']))
            require(member['path'][0][0]==r['declared_head'] and member['path'][-1][1]==member['expanded_name'])
    fixtures=load(U/'fixtures.json')
    allowed={'http://example.com#A','http://example.com#B'}
    for f in fixtures:
        result=set_rules(f['text'],allowed)
        require(result['errors']==f['expected_errors'])
    # Same lexical URI may belong to one domain and fail another.
    for f in load(U/'altered-controls.json'):
        original=next(r for r in rows if r['fact_id']==f['fact_id'])
        paths=domains[original['declared_head']]['paths']
        allowed_real={n[1:].replace('}','#',1) for n in paths}
        result=set_rules(f['text'],allowed_real)
        require(result['errors']==f['expected_errors'])
    guarded=load(U/'network-guard-controls.json')
    for f in guarded:
        attrs=dict(network['raw_arcs'][0]['attributes']);attrs.update(f['added_attributes'])
        try:require_simple_arc(attrs)
        except AssertionError:rejected=True
        else:rejected=False
        require(rejected)
    source=load(U/'source-ledger.json')
    for b in source['bindings']:require(bind(R/b['path'])==b)
    for a in source['anchors']:
        require(bind(R/a['source']['path'])==a['source'])
        excerpt='\n'.join((R/a['source']['path']).read_text().splitlines()[a['first_line']-1:a['last_line']])
        require(excerpt==a['excerpt'])
    for a in load(U/'acquisitions.json'):
        require(bind(R/a['body']['path'])==a['body'])
        receipt=load(R/a['receipt']['path'])
        info=json.loads(receipt['result']['output'])
        require(info['http_code']==200 and info['exitcode']==0)
        require((R/a['body']['path']).stat().st_size==info['size_download'])
    return {'status':'passed','assertions':assertions,'facts':len(rows),'concepts':8,
            'member_occurrences':sum(len(r['members']) for r in rows),'domain_heads':len(domains),
            'retained_resources':27,'raw_arcs':len(network['raw_arcs']),'unique_endpoint_edges':len(network['unique_endpoint_edges']),
            'domain_sizes':{k:len(v['paths']) for k,v in domains.items()},'fixtures':len(fixtures),
            'altered_controls':len(load(U/'altered-controls.json')),'acquisitions':3,
            'network_guard_controls':len(guarded),
            'all_selected_domain_set_rules_pass':True,'schema_xbrl_validation':'not_run',
            'upstream_executed':False,'whole_rows_closed':0}
