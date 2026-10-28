"""Scoped finite evaluation memo; supplied evidence identity is not authority."""
from copy import deepcopy
from paths import enumerate_paths
from quotient import Refusal, digest, key, reuse


def binding(model, partition, policy, scenarios, evidence):
    if not isinstance(evidence, dict) or set(evidence) != {'identity', 'revision'}:
        raise Refusal('evidence_binding')
    if any(not isinstance(v, str) or not v for v in evidence.values()):
        raise Refusal('evidence_binding')
    return {name: digest(value) for name, value in {
        'model': model, 'partition': partition, 'policy': policy,
        'scenarios': scenarios, 'evidence': evidence}.items()}


def evaluate(certificate, model, partition, policy, scenarios, evidence, max_nodes=1000):
    bound = binding(model, partition, policy, scenarios, evidence)
    compressed = reuse(certificate, model, partition)
    full = enumerate_paths(model, scenarios, policy, max_nodes=max_nodes)
    reduced = enumerate_paths(compressed, scenarios, policy, max_nodes=max_nodes)
    if full['status'] != 'exact' or reduced['status'] != 'exact':
        return {'schema': 'ScopedFiniteEvaluation/1', 'status': 'unknown',
                'bindings': bound, 'original': full, 'compressed': reduced}
    if key(full['paths']) != key(reduced['paths']):
        raise Refusal('path_disagreement')
    return {'schema': 'ScopedFiniteEvaluation/1', 'status': 'exact',
            'bindings': bound, 'paths': deepcopy(full['paths'])}


def reuse_evaluation(saved, certificate, model, partition, policy, scenarios, evidence):
    if not isinstance(saved, dict) or saved.get('status') != 'exact':
        raise Refusal('not_exact_evaluation')
    if saved.get('bindings') != binding(model, partition, policy, scenarios, evidence):
        raise Refusal('stale_evaluation')
    fresh = evaluate(certificate, model, partition, policy, scenarios, evidence)
    if key(saved) != key(fresh):
        raise Refusal('evaluation_mismatch')
    return deepcopy(fresh)
