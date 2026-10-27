"""Finite join sensitivity; no numerical calculation or processor conformance."""
from collections import Counter, defaultdict
from fractions import Fraction
import importlib.util
import json
from pathlib import Path

U=Path(__file__).resolve().parent;R=U.parents[2];B=R/'data/accounting-master'
def imported(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old=imported('alignment_old_network',B/'r06-calculation-bindings-20261020/compare.py')
oim=imported('alignment_oim',B/'r06-oim-mapping-20261020/compare.py')
load,bind=old.load,old.bind
O=oim.O
MAP=B/'r06-oim-mapping-20261020/mapping.json'
CALC=B/'r06-calculation-bindings-20261020/calculation-bindings.json'
MODES=('equal','contributor_subset_total','total_subset_contributor')
def token(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def aligned(s,t,mode):
    if mode=='equal':return s==t
    if mode=='contributor_subset_total':return all(k in t and t[k]==v for k,v in s.items())
    assert mode=='total_subset_contributor'
    return all(k in s and s[k]==v for k,v in t.items())
def independent(s,t,mode):
    a={(k,token(v)) for k,v in s.items()};b={(k,token(v)) for k,v in t.items()}
    return a==b if mode=='equal' else (a<=b if mode=='contributor_subset_total' else b<=a)
def derive():
    data=load(MAP);prior=load(CALC);net=old.network()
    assert net==prior['network']
    arcs=[a for a in net['raw_arcs'] if a['id'] in set(net['effective_arc_ids'])]
    assert len(arcs)==209 and not net['same_base_endpoint_groups']
    nodes=load(oim.COVER)['type_nodes'];endpoints=[]
    for uri,d in net['endpoint_declarations'].items():
        assert d['substitution_group']==old.X+'item'
        path=oim.ancestry(d['type'],nodes)
        assert path[-1] in (oim.XS+'decimal',oim.XS+'integer')
        endpoints.append({'uri':uri,'concept':d['qname'],'path':path,'decimal_supported':True})
    bykey=defaultdict(list)
    for f in data['facts']:bykey[token(f['dimensions'])].append(f)
    points=[];byconcept=defaultdict(list);factpoint={}
    for i,rows in enumerate(bykey.values(),1):
        dims=rows[0]['dimensions'];assert all(f['dimensions']==dims for f in rows)
        q=dims[O+'concept'];p={'id':f'dp-{i:04d}','concept':q,
          'dimensions_without_concept':{k:v for k,v in dims.items() if k!=O+'concept'},
          'members':[f['fact_id'] for f in rows],'nil_only':all(f['nil'] for f in rows),
          'numeric':all(f['numeric'] for f in rows)}
        assert p['numeric'] or not any(f['numeric'] for f in rows)
        points.append(p);byconcept[q].append(p)
        for f in rows:factpoint[f['fact_id']]=p['id']
    groups=defaultdict(list)
    for a in arcs:groups[(a['role'],a['interpreted']['arcrole'],a['source_qname'])].append(a)
    joins={k:[] for k in MODES};candidates={k:[] for k in MODES}
    comparisons=0;witnesses=[];no_totals=[];nil_totals=[];nil_contributors=[]
    for (role,arcrole,concept),relations in sorted(groups.items()):
        assert len({a['target_qname'] for a in relations})==len(relations)
        if not byconcept.get(concept):no_totals.append({'role':role,'concept':concept,'arcs':[a['id'] for a in relations]})
        for t in byconcept.get(concept,[]):
            assert t['numeric']
            if t['nil_only']:
                nil_totals.append({'role':role,'point':t['id']});continue
            selected={k:[] for k in MODES}
            for arc in relations:
                for s in byconcept.get(arc['target_qname'],[]):
                    assert s['numeric']
                    if s['nil_only']:
                        if aligned(s['dimensions_without_concept'],t['dimensions_without_concept'],'equal'):
                            nil_contributors.append({'role':role,'total':t['id'],'arc':arc['id'],'point':s['id'],'members':s['members']})
                        continue
                    sd,td=s['dimensions_without_concept'],t['dimensions_without_concept']
                    flags={k:aligned(sd,td,k) for k in MODES}
                    assert flags=={k:independent(sd,td,k) for k in MODES}
                    comparisons+=1
                    key=[role,t['id'],arc['id'],s['id']]
                    for k,accepted in flags.items():
                        if accepted:joins[k].append(key);selected[k].append({'arc':arc['id'],'point':s['id']})
                    if any(flags.values()) and not flags['equal']:
                        witnesses.append({'key':key,'total_members':t['members'],'contributor_members':s['members'],
                          'total_concept':t['concept'],'contributor_concept':s['concept'],'relations':flags,
                          'total_only_dimensions':{k:v for k,v in td.items() if k not in sd},
                          'contributor_only_dimensions':{k:v for k,v in sd.items() if k not in td}})
            for k in MODES:
                selected_arcs={a['arc'] for a in selected[k]}
                candidates[k].append({'role':role,'arcrole':arcrole,'total_point':t['id'],'total_members':t['members'],
                  'contributors':selected[k],'binds':bool(selected[k]),
                  'arcs_without_reported_contributor':[a['id'] for a in relations if a['id'] not in selected_arcs]})
    eqset={tuple(j) for j in joins['equal']};oldset=set();bridge=[]
    old_by={(c['role'],c['summation_fact']):c for c in prior['calculation_candidates']}
    equal_by={(c['role'],c['total_point']):c for c in candidates['equal']}
    for c in prior['calculation_candidates']:
        t=factpoint[c['summation_fact']];new=equal_by[(c['role'],t)]
        oldjoins={(x['arc_id'],factpoint[x['fact_id']]) for x in c['contributing_facts']}
        newjoins={(x['arc'],x['point']) for x in new['contributors']}
        assert oldjoins==newjoins
        for a,s in oldjoins:oldset.add((c['role'],t,a,s))
        bridge.append({'old_total_fact':c['summation_fact'],'role':c['role'],'data_point':t,
          'old_binds':c['binds'],'old_nonbinding_reasons':c['nonbinding_reasons'],'equal_dimension_has_contributor':new['binds']})
    assert eqset==oldset
    for c in candidates['equal']:
        assert all((c['role'],fid) in old_by for fid in c['total_members'])
    counts={'arcs':len(arcs),'roles':len({a['role'] for a in arcs}),'calculations':len(groups),
      'endpoint_concepts':len(endpoints),'facts':len(factpoint),'all_dimension_points':len(points),
      'numeric_points':sum(p['numeric'] for p in points),'nil_only_points':sum(p['nil_only'] for p in points),
      'candidate_pair_comparisons':comparisons,'old_occurrence_candidates':len(bridge),
      'old_bound_occurrences':sum(b['old_binds'] for b in bridge),
      'candidate_data_points':len(candidates['equal']),'absent_total_calculations':len(no_totals),
      'nil_total_candidates':len(nil_totals),'aligned_nil_only_contributors':len(nil_contributors),
      'strict_subset_witnesses':len(witnesses)}
    modes={k:{'joins':len(joins[k]),'bound_candidates':sum(c['binds'] for c in candidates[k]),
      'nonbinding_candidates':sum(not c['binds'] for c in candidates[k]),
      'extra_joins_vs_equal':len(set(map(tuple,joins[k]))-eqset)} for k in MODES}
    return {'counts':counts,'modes':modes,'data_points':points,'endpoint_checks':endpoints,
      'joins':joins,'candidates':candidates,'directed_only_witnesses':witnesses,'old_candidate_bridge':bridge,
      'absent_total_calculations':no_totals,'nil_total_candidates':nil_totals,
      'aligned_nil_only_contributors':nil_contributors,'arithmetic_performed':False,
      'alignment_policy_selected':False,'authoritative_clarification':False}

def fixtures():
    rows=[]
    def expect(name,s,t,wanted):
        actual={k:aligned(s,t,k) for k in MODES}
        assert actual==dict(zip(MODES,wanted)),name
        assert actual=={k:independent(s,t,k) for k in MODES}
        rows.append({'name':name,'contributor_dimensions':s,'total_dimensions':t,'results':actual})
    a={'entity':'e','period':['s','t'],'unit':'USD'}
    expect('identical',a,dict(a),(True,True,True))
    expect('contributor less qualified',a,dict(a,axis='member'),(False,True,False))
    expect('contributor more qualified',dict(a,axis='member'),a,(False,False,True))
    expect('different member',dict(a,axis='m1'),dict(a,axis='m2'),(False,False,False))
    expect('different units',a,dict(a,unit='EUR'),(False,False,False))
    expect('different periods',a,dict(a,period=['s','u']),(False,False,False))
    expect('different entities',a,dict(a,entity='f'),(False,False,False))
    expect('different language',dict(a,language='en'),dict(a,language='fr'),(False,False,False))
    expect('missing language',a,dict(a,language='en'),(False,True,False))
    expect('empty dimensions',{},a,(False,True,False))
    expect('both empty',{}, {},(True,True,True))
    expect('different typed date',dict(a,axis={'type':'date','v':'2024-01-01'}),dict(a,axis={'type':'date','v':'2024-01-02'}),(False,False,False))
    expect('disjoint axis sets',dict(a,axis1='m'),dict(a,axis2='n'),(False,False,False))
    return rows

def check():
    ledger=load(U/'source-ledger.json');count=0
    for b in ledger['bindings']:
        assert bind(R/b['path'])==b;count+=1
    for a in ledger['anchors']:
        p=R/a['source']['path'];assert bind(p)==a['source'];count+=1
        assert chr(10).join(p.read_text().splitlines()[a['first_line']-1:a['last_line']])==a['excerpt'];count+=1
    result=derive();assert result==load(U/'alignment.json');count+=1
    cases=fixtures();assert cases==load(U/'fixtures.json');count+=len(cases)+1
    for mode in MODES:
        assert all(set(j) or j for j in result['joins'][mode]);count+=1
        assert result['modes'][mode]['bound_candidates']+result['modes'][mode]['nonbinding_candidates']==result['counts']['candidate_data_points'];count+=1
    return {'assertions':count,'fixtures':len(cases),'source_anchors':len(ledger['anchors']),
      'input_bindings':len(ledger['bindings']),**result['counts'],'modes':result['modes'],
      'arithmetic_performed':False,'alignment_policy_selected':False,'conformance_admitted':False,'whole_rows_closed':0}
