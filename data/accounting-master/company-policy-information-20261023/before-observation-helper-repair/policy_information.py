"""Synthetic dependency timing; a derived result is not a saved historical run."""
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import json
import sys

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / 'company-information-20261023'))
import information as parent_information

digest = parent_information.digest
closed = parent_information.closed
EVENTS = parent_information.EVENTS


@dataclass(frozen=True)
class TrustedContext:
    """Provided by the local caller, never deserialized from a policy packet."""
    exchange_sha256: str
    materializer: dict
    observation_hashes: frozenset
    validate_exchange: Callable
    source_view: Callable
    generate: Callable
    execute: Callable


def components(policy, materializer):
    return [{'slot': 'policy', 'sha256': digest(policy)},
            {'slot': 'materializer', 'sha256': digest(materializer)}]


def schema():
    sha = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
    unknown = closed({'status': {'const': 'unknown'},
                      'reason': {'type': 'string', 'minLength': 1}})
    observed = closed({'status': {'const': 'observed_synthetic'},
                       'observation_sha256': sha})
    declaration = closed({
        'slot': {'enum': ['policy', 'materializer']},
        'component_sha256': sha,
        'events': closed({e: {'oneOf': [unknown, observed]} for e in EVENTS})})
    return closed({
        'profile': {'const': 'PolicyInformationDraft/1'},
        'evidence_class': {'const': 'authored_synthetic'},
        'exchange_sha256': sha, 'parent_path_sha256': sha,
        'child_path_sha256': sha, 'policy_sha256': sha,
        'materializer_sha256': sha,
        'declarations': {'type': 'array', 'minItems': 2, 'maxItems': 2,
                         'items': declaration}})


def _clocks(items, observations, trusted_hashes, mode, cutoff):
    """Use the predecessor's interval convention without changing its files."""
    if mode not in ['archival_exploration', 'investor_information', 'system_as_of']:
        raise ValueError('information mode')
    if mode == 'archival_exploration':
        if cutoff is not None:
            raise ValueError('archival cutoff')
        at = None
    else:
        at = parent_information.interval({'time': cutoff, 'precision': 'utc_instant'})[0]
    required = (['authored', 'published'] if mode == 'investor_information'
                else ['authored', 'ingested', 'accepted'])
    needed_pairs = ([('authored', 'published')] if mode == 'investor_information'
                    else [('authored', 'ingested'), ('ingested', 'accepted')])
    late, unresolved, eligible = [], [], []
    for item in items:
        clocks = {}
        for event, ref in item['events'].items():
            if ref['status'] == 'unknown':
                continue
            h = ref['observation_sha256']
            if h not in observations:
                raise ValueError('observation bytes missing')
            observation = observations[h]
            if digest(observation) != h:
                raise ValueError('observation digest mismatch')
            Draft202012Validator(parent_information.observation_schema()).validate(observation)
            if (observation['component_sha256'] != item['component_sha256']
                    or observation['event'] != event):
                raise ValueError('observation component or event mismatch')
            bounds = parent_information.interval(observation)
            if h in trusted_hashes:
                clocks[event] = bounds
        for before, after in [('authored', 'published'), ('authored', 'ingested'),
                              ('ingested', 'accepted')]:
            if before not in clocks or after not in clocks:
                continue
            first, last = clocks[before], clocks[after]
            if first[0] > last[1] or (first[0] == last[1] and last[0] != last[1]):
                raise ValueError('impossible observation chronology')
            if first[1] > last[0] and (before, after) in needed_pairs:
                unresolved.append({'slot': item['slot'], 'event': before + '<=' + after,
                                   'reason': 'CHRONOLOGY_ORDER_UNRESOLVED'})
        if mode == 'archival_exploration':
            continue
        for event in required:
            ref = item['events'][event]
            entry = {'slot': item['slot'], 'event': event}
            if ref['status'] == 'unknown':
                unresolved.append(dict(entry, reason='MISSING_OBSERVATION'))
                continue
            h = ref['observation_sha256']
            if h not in trusted_hashes:
                unresolved.append(dict(entry, reason='UNTRUSTED_OBSERVATION'))
                continue
            if event == 'published' and observations[h]['audience'] != 'public':
                unresolved.append(dict(entry, reason='PUBLIC_AVAILABILITY_NOT_ESTABLISHED'))
                continue
            start, end = clocks[event]
            if at < start:
                late.append(dict(entry, reason='AFTER_INFORMATION_CUTOFF'))
            elif start != end and at < end:
                unresolved.append(dict(entry, reason='TIME_PRECISION_UNRESOLVED'))
            else:
                eligible.append(entry)
    status = ('archival_synthetic' if mode == 'archival_exploration' else
              'ineligible' if late else 'unresolved' if unresolved else 'eligible_synthetic')
    return {'status': status, 'eligible': eligible, 'unavailable': late,
            'unresolved': unresolved, 'component_count': len(items)}


def query(trust, exchange, raw, parent_name, parent_declaration, declaration,
          observations, policy, materialization, child_result, mode, cutoff=None):
    """Verify content/derivation and join input timing at one common cutoff."""
    flags = {'real_world_admission': False, 'forecast_admission': False,
             'historical_execution_established': False,
             'real_behavior_evidence': False, 'temporal_admission': False}
    try:
        parent_view = parent_information.query(
            exchange, raw, parent_name, parent_declaration, observations,
            trust.observation_hashes, trust.exchange_sha256,
            trust.validate_exchange, trust.source_view, mode, cutoff)
        if parent_view['status'] == 'invalid':
            raise ValueError('parent information invalid: ' + parent_view.get('detail', ''))
        records = exchange['record_registry']
        root = records[exchange['root_ref']['digest']]['body']
        matches = [records[r['digest']]['body'] for r in root['path_refs']
                   if records[r['digest']]['body']['name'] == parent_name]
        if len(matches) != 1:
            raise ValueError('parent path membership')
        parent = json.loads(raw[matches[0]['path_blob']['digest']])
        generated = trust.generate(parent, policy)
        if generated.get('status') != 'materialized_conditional_path':
            return dict(flags, status=generated.get('status', 'invalid'),
                        reason='policy_not_materialized', policy_assessment=generated,
                        parent_information=parent_view)
        if digest(generated) != digest(materialization):
            raise ValueError('policy materialization mismatch')
        Draft202012Validator(schema()).validate(declaration)
        expected = {'exchange_sha256': trust.exchange_sha256,
                    'parent_path_sha256': digest(parent),
                    'child_path_sha256': generated['child_path_sha256'],
                    'policy_sha256': digest(policy),
                    'materializer_sha256': digest(trust.materializer)}
        if any(declaration[k] != v for k, v in expected.items()):
            raise ValueError('policy information identity')
        items = declaration['declarations']
        if len({x['slot'] for x in items}) != len(items):
            raise ValueError('duplicate component slot')
        if {x['slot']: x['component_sha256'] for x in items} != {
                x['slot']: x['sha256'] for x in components(policy, trust.materializer)}:
            raise ValueError('exact component coverage')
        # No packet-supplied code is imported. The local caller binds this engine.
        replayed = trust.execute(generated['path'])
        if digest(replayed) != digest(child_result):
            raise ValueError('derived accounting result mismatch')
        policy_view = _clocks(items, observations, trust.observation_hashes, mode, cutoff)
        statuses = [parent_view['status'], policy_view['status']]
        if mode == 'archival_exploration':
            if statuses != ['archival_synthetic', 'archival_synthetic']:
                raise ValueError('archival dependency status')
            status = 'archival_synthetic'
        else:
            if any(s not in ['ineligible', 'unresolved', 'eligible_synthetic'] for s in statuses):
                raise ValueError('dependency timing status')
            status = ('ineligible' if 'ineligible' in statuses else
                      'unresolved' if 'unresolved' in statuses else 'eligible_synthetic')
        return dict(flags, status=status, temporal_admission=status == 'eligible_synthetic',
                    mode=mode, cutoff=cutoff,
                    result_kind='derived_synthetic_consequence',
                    parent_information=parent_view, policy_information=policy_view,
                    identities=expected, child_result_sha256=digest(child_result),
                    derivation_verified=True, accounting_execution_verified=True,
                    child_execution_status=child_result['status'],
                    child_clock_inherited=False,
                    scope='Synthetic dependency timing and current trusted replay; no past run established')
    except Exception as exc:
        return dict(flags, status='invalid', reason='policy_information_semantics',
                    detail=type(exc).__name__ + ':' + str(exc).splitlines()[0][:400])
