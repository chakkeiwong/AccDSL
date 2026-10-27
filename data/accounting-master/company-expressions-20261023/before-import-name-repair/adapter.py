"""Explicit output-to-policy mapping; the caller supplies the protected generator."""
from copy import deepcopy
from expressions import FLAGS,SCALAR,digest,evaluate

def materialize(program,path,policy,output_map,generator):
    try:
        if set(output_map)!={'fraction','installment_shares'}: raise ValueError('output mapping fields')
        if not isinstance(output_map['fraction'],str) or not isinstance(output_map['installment_shares'],list):
            raise ValueError('mapping types')
        names=[output_map['fraction']]+output_map['installment_shares']
        if not all(isinstance(n,str) for n in names): raise ValueError('mapping names')
        evaluated=evaluate(program)
        if evaluated['status']=='invalid': return dict(FLAGS,status='invalid',reason='expression_program',evaluation=evaluated)
        if set(names)!=set(program['outputs']): raise ValueError('mapping must cover every declared output and use existing names')
        if len(output_map['installment_shares'])!=len(policy['collection_operations']): raise ValueError('installment count')
        for name in names:
            if digest(evaluated['outputs'][name]['type'])!=digest(SCALAR): raise ValueError('policy output requires context-free dimensionless number')
        if any(evaluated['outputs'][name]['status']!='known' for name in names):
            return dict(FLAGS,status='unresolved',reason='policy_expression_unknown',evaluation=evaluated)
        candidate=deepcopy(policy)
        candidate['fraction']=evaluated['outputs'][output_map['fraction']]['value']
        candidate['installment_shares']=[evaluated['outputs'][n]['value'] for n in output_map['installment_shares']]
        generated=generator(path,candidate)
        if generated['status']!='materialized_conditional_path':
            return dict(FLAGS,status=generated['status'],reason='policy_generator_refusal',evaluation=evaluated,policy_assessment=generated)
        return dict(FLAGS,status='materialized_expression_policy',program_sha256=digest(program),
                    evaluation=evaluated,output_map=deepcopy(output_map),policy=candidate,
                    policy_sha256=digest(candidate),materialization=generated,
                    information_scope='Expression inputs and method require their own evidence; parent policy timing is not inherited')
    except Exception as exc:
        return dict(FLAGS,status='invalid',reason='expression_policy_adapter',detail=type(exc).__name__+':'+str(exc).splitlines()[0][:250])
