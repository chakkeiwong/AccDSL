"""Finite supplied-registry selection and exact decision reference."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('finite_vintage',ROOT/'data/accounting-master/inference-vintage-20261026/inference.py')
inference=importlib.util.module_from_spec(spec);spec.loader.exec_module(inference)

def select(model,registry,sources,actor,cutoff):
    """Maximal available heads in a declared closed registry; no factual admission."""
    try:
        at=inference._time.instant(cutoff)
        inference.need(isinstance(actor,str) and actor,'actor_required')
        inference.need(isinstance(registry,dict) and isinstance(sources,dict),'registry_maps')
        for h,r in registry.items():
            inference.need(inference.identity(r)==h,'record_identity')
            inference.need(r['source_sha256'] in sources,'source_missing')
        for h,text in sources.items():inference.need(inference.source_identity(text)==h,'source_identity')
        parents={h:r['supersedes'] for h,r in registry.items()}
        for h in registry:
            seen=set();current=h
            while current is not None:
                inference.need(current not in seen,'cycle');seen.add(current)
                inference.need(current in registry,'missing_ancestry')
                r=registry[current]
                inference.need(r['slot']==registry[h]['slot'] and r['information_id']==registry[h]['information_id'],'replacement_identity')
                current=parents[current]
        available=set();future=[];unknown=[]
        for h,r in registry.items():
            stamp=r['available_at'].get(actor)
            if stamp is None:unknown.append(h);continue
            if inference._time.instant(stamp)>at:future.append(h)
            else:available.add(h)
        if unknown:return dict(status='unresolved',reason='unknown_actor_availability',records=sorted(unknown))
        ancestors=set()
        for h in available:
            current=parents[h]
            while current is not None:ancestors.add(current);current=parents[current]
        heads=sorted(available-ancestors,key=lambda h:(registry[h]['slot'],h))
        slots=[registry[h]['slot'] for h in heads]
        if len(set(slots))!=len(slots):return dict(status='unresolved',reason='incomparable_available_revisions',heads=heads)
        included=set()
        for h in heads:
            while h is not None:included.add(h);h=parents[h]
        selected={h:deepcopy(registry[h]) for h in sorted(included)}
        source_ids={r['source_sha256'] for r in selected.values()}
        request=dict(profile=inference.PROFILE,model=deepcopy(model),actor=actor,cutoff=cutoff,heads=heads,evidence=selected,sources={h:sources[h] for h in sorted(source_ids)})
        result=inference.evaluate(request)
        if result['status']!='complete':return dict(status=result['status'],reason=result.get('reason'),inference=result)
        return dict(status='selected',request=request,inference=result,excluded_future=sorted(future),scope='closed_supplied_registry_only',source_admission=False)
    except (ValueError,KeyError,TypeError,AttributeError) as e:return dict(status='invalid',reason=str(e))

def decide(selection,losses):
    try:
        inference.need(selection['status']=='selected','complete_selection_required')
        request=selection['request'];result=inference.evaluate(request)
        inference.need(result==selection['inference'],'selection_inference_mismatch')
        states=request['model']['states']
        inference.need(isinstance(losses,dict) and losses and all(isinstance(a,str) and a for a in losses),'named_actions')
        expectations={}
        for action,by_state in losses.items():
            vector=inference.vector(by_state,states,'loss')
            expectations[action]=sum(Fraction(result['posterior'][s])*vector[s] for s in states)
        minimum=min(expectations.values())
        return dict(status='complete',actor=request['actor'],cutoff=request['cutoff'],request_sha256=inference.identity(request),losses_sha256=inference.identity(losses),expected_losses={a:inference.fmt(x) for a,x in expectations.items()},minimizers=sorted(a for a,x in expectations.items() if x==minimum),scope='declared_finite_feasible_actions')
    except inference.Unresolved as e:return dict(status='unresolved',reason=str(e))
    except (ValueError,KeyError,TypeError,AttributeError) as e:return dict(status='invalid',reason=str(e))
