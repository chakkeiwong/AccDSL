"""Independently form actor messages and check saved full-rule populations."""
from itertools import product
import json
import messages as m

def wire(v):return json.dumps(v,separators=(',',':'),ensure_ascii=False)

def rows(c,mode,e,heads):
    f1,f2,o1,o2=heads;registry=c['family']['input']['original']['registry'];world=c['world']['world'];out=[]
    maps=[next(v for v in c['mapping']['maps'] if v['source_head']==o) for o in (o1,o2)];prefix=m.identity(c)+'/'+'/'.join(heads)+'/'
    for r in e.rows:
        if not (r['receipt']==world['receipt'] and (world['family']=='mixed' or r['right'])):continue
        first=list(r['obs1']) if registry[o1]['payload']['view']=='refined' else list(r['obs1'][:1])
        one=next(v['token'] for v in maps[0]['first'] if v['key']==first)
        two=None if r['obs2'] is None else next(v['token'] for v in maps[1]['second'] if v['key']==list(r['obs2'][-2:]))
        if mode=='numeric_and_reported_receipt':
            one=wire([one,registry[f1]['payload']['receipt']])
            if two is not None:two=wire([two,registry[f2]['payload']['receipt']])
        out.append(dict(id=prefix+r['row_id'],support=r['row_id'],mechanism='hidden',
                        a1=r['a1'],a2=r['a2'],message1=wire([one,None]),message2=None if two is None else [two,''],status=r['status']))
    return out

def keys(rows):
    one={('unknown',r['message1']) for r in rows}
    two={(('unknown',r['message1']),r['a1'],None,tuple(r['message2'])) for r in rows if r['message2'] is not None}
    return [('first',k) for k in sorted(one,key=repr)]+[('second',k) for k in sorted(two,key=repr)]

def reconstruct(contexts,decl,e):
    universe=[];known=[];unresolved=[];summaries=m.prepare(contexts,decl,m.identity(decl),e)
    for c,summary in zip(contexts,summaries):
        registry=c['family']['input']['original']['registry']
        fs=[h for h in sorted(registry) if registry[h]['slot']=='financial_family' and registry[h]['disposition']=='assertion']
        obs=[h for h in sorted(registry) if registry[h]['slot']=='observation_scheme' and registry[h]['disposition']=='assertion']
        if c['world']['world'] is not None:
            for heads in product(fs,fs,obs,obs):universe.extend(rows(c,decl['mode'],e,heads))
        if summary['world_binding']['status']!='conditional_fixed_world':unresolved.append(summary['context_sha256']);continue
        for a,z in c['family']['outcomes']:
            known.extend(rows(c,decl['mode'],e,(a['heads']['financial_family'],z['heads']['financial_family'],a['heads']['observation_scheme'],z['heads']['observation_scheme'])))
    return keys(universe),known,unresolved,summaries

def verify(result,rid,contexts,decl,e):
    m.need(m.identity(result)==rid,'external_result')
    ks,rs,unresolved,summaries=reconstruct(contexts,decl,e)
    fixed=dict(profile='RevisedSourceActorPolicy/1',**m.w.FLAGS,actual_information_claim=False,
               declaration_sha256=m.identity(decl),contexts=summaries,keys=m.b.canonical(ks),required_keys=len(ks),
               rows=rs,unresolved_contexts=unresolved,scope='resolved_context_restrictions_only' if unresolved else 'all_supplied_contexts')
    m.j.t.fields(result,list(fixed)+['status','candidates','rejections'],'saved_result_fields')
    for k,v in fixed.items():m.need(m.identity(result[k])==m.identity(v),'exact_'+k)
    if not ks:
        m.need(result['status']=='unresolved_no_world_domain' and result['candidates'] is None and result['rejections'] is None,'no_world_domain');return True
    if len(ks)>decl['max_policy_keys']:
        m.need(result['status']=='unresolved_domain_budget' and result['candidates'] is None and result['rejections'] is None,'unassessed_budget');return True
    if not rs:
        m.need(result['status']=='unresolved_contexts' and result['candidates'] is None and result['rejections'] is None,'no_rows_no_policy');return True
    expected=m.p.oracle(rs,ks)
    m.need(result['candidates']==[list(v) for v in sorted(expected)],'independent_total_candidates')
    status='unresolved_contexts' if unresolved else 'conditionally_feasible' if expected else 'conditionally_infeasible'
    m.need(result['status']==status,'exact_status')
    lookup={r['id']:r for r in rs};seen=set()
    for item in result['rejections']:
        m.j.t.fields(item,['policy','row'],'rejection_fields');rule=item['policy']
        m.need(type(rule) is list and len(rule)==len(ks) and all(type(v) is int and v in (0,1) for v in rule),'total_assignment')
        q=tuple(rule);m.need(q not in seen and q not in expected,'unique_rejected_rule');seen.add(q)
        row=lookup[item['row']];actions=dict(zip(ks,rule));one=('unknown',row['message1'])
        m.need(actions[('first',one)]==int(row['a1']=='draw'),'first_witness_action')
        if row['status']=='refused2':
            two=(one,row['a1'],None,tuple(row['message2']))
            m.need(actions[('second',two)]==int(row['a2']=='draw'),'second_witness_action')
        else:m.need(row['status']=='refused1','actually_refused')
    m.need(len(seen)+len(expected)==2**len(ks),'entire_rule_universe');return True
