"""A separate existence result; original enumeration limits stay unchanged."""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'revised-source-actor-messages-20261027'))
import messages as m
import checker as c
import logic

def terms(rows,keys):
    positions={key:i for i,key in enumerate(keys)};out=[]
    for r in rows:
        first,second=m.b.policy.keys(r,'never')
        if r['status']=='refused1':term=((positions[('first',first)],int(r['a1']=='draw')),)
        elif r['status']=='refused2':term=((positions[('first',first)],int(r['a1']=='draw')),(positions[('second',second)],int(r['a2']=='draw')))
        else:continue
        out.append((term,r['id']))
    return out

def base(contexts,decl,e):
    keys,rows,unresolved,summaries=c.reconstruct(contexts,decl,e)
    clauses=terms(rows,keys)
    limits=dict(max_keys=64,max_rows=10000,max_edges=20000)
    result=dict(profile='TwoStagePolicyExistenceCertificate/1',**m.w.FLAGS,actual_information_claim=False,
                declaration_sha256=m.identity(decl),contexts=summaries,keys=m.b.canonical(keys),required_keys=len(keys),
                row_ids=[r['id'] for r in rows],unresolved_contexts=unresolved,limits=limits,
                population='not_enumerated',scope='resolved_context_restrictions_only' if unresolved else 'all_supplied_contexts')
    return result,keys,rows,clauses

def evaluate(contexts,decl,e):
    out,keys,rows,clauses=base(contexts,decl,e)
    if not keys or not rows:status='unassessed_no_resolved_world_rows';certificate=None
    elif len(keys)>64 or len(rows)>10000 or len(logic.edges(clauses))>20000:status='unassessed_resource_bound';certificate=None
    else:
        certificate=logic.solve(len(keys),clauses)
        status=('conditionally_infeasible_resolved_subset' if out['unresolved_contexts'] else 'conditionally_infeasible') if certificate['kind']=='contradiction' else 'unresolved_contexts' if out['unresolved_contexts'] else 'conditionally_feasible'
    return dict(out,status=status,certificate=certificate)

def verify(result,rid,contexts,decl,e):
    assert m.identity(result)==rid
    out,keys,rows,_=base(contexts,decl,e)
    assert set(result)==set(out)|{'status','certificate'}
    for k,v in out.items():assert m.identity(result[k])==m.identity(v),k
    # Independent refusal extraction uses full retained message/action memory.
    positions={key:i for i,key in enumerate(keys)};clauses=[]
    for r in rows:
        if r['status']=='accepted':continue
        one=('unknown',r['message1']);term=[(positions[('first',one)],int(r['a1']=='draw'))]
        if r['status']=='refused2':
            two=(one,r['a1'],None,tuple(r['message2']))
            term.append((positions[('second',two)],int(r['a2']=='draw')))
        clauses.append((tuple(term),r['id']))
    if not keys or not rows:assert result['certificate'] is None and result['status']=='unassessed_no_resolved_world_rows';return True
    if len(keys)>64 or len(rows)>10000 or len(logic.edges(clauses))>20000:assert result['certificate'] is None and result['status']=='unassessed_resource_bound';return True
    cert=result['certificate'];logic.verify(len(keys),clauses,cert)
    expected=('conditionally_infeasible_resolved_subset' if out['unresolved_contexts'] else 'conditionally_infeasible') if cert['kind']=='contradiction' else 'unresolved_contexts' if out['unresolved_contexts'] else 'conditionally_feasible'
    assert result['status']==expected;return True
