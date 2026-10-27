"""Distinct test clocks for a policy and a method; no historical observation."""
from copy import deepcopy
from policy_information import components, digest, EVENTS


def make(parent_fixture, parent, policy, materializer, child_sha256):
    observations = deepcopy(parent_fixture['observations'])
    declarations = []
    schedules = {
        'policy': {'authored': '2025-03-09T09:00:00Z', 'published': '2025-03-10',
                   'ingested': '2025-03-09T10:00:00Z', 'accepted': '2025-03-09T11:00:00Z'},
        'materializer': {'authored': '2025-03-11T09:00:00Z', 'published': '2025-03-12',
                         'ingested': '2025-03-11T10:00:00Z', 'accepted': '2025-03-11T11:00:00Z'}}
    for component in components(policy, materializer):
        refs = {}
        for event in EVENTS:
            observation = {
                'profile': 'SyntheticInformationObservation/1',
                'component_sha256': component['sha256'], 'event': event,
                'audience': 'public' if event == 'published' else 'internal',
                'time': schedules[component['slot']][event],
                'precision': 'calendar_day_utc' if event == 'published' else 'utc_instant',
                'provenance': 'authored_test_clock_not_historical_evidence'}
            h = digest(observation)
            observations[h] = observation
            refs[event] = {'status': 'observed_synthetic', 'observation_sha256': h}
        declarations.append({'slot': component['slot'], 'component_sha256': component['sha256'],
                             'events': refs})
    return {
        'parent_declaration': deepcopy(parent_fixture['declaration']),
        'declaration': {
            'profile': 'PolicyInformationDraft/1', 'evidence_class': 'authored_synthetic',
            'exchange_sha256': parent_fixture['declaration']['exchange_sha256'],
            'parent_path_sha256': digest(parent), 'child_path_sha256': child_sha256,
            'policy_sha256': digest(policy), 'materializer_sha256': digest(materializer),
            'declarations': declarations},
        'observations': observations, 'trusted_observation_hashes': sorted(observations),
        'trust_scope': 'Caller-selected synthetic fixture only; no real-world authentication'}


def change_observation(fixture, slot, event_key, *, parent=False, trusted=True, **changes):
    declaration = fixture['parent_declaration' if parent else 'declaration']
    item = next(d for d in declaration['declarations'] if d['slot'] == slot)
    ref = item['events'][event_key]
    observation = deepcopy(fixture['observations'][ref['observation_sha256']])
    observation.update(changes)
    h = digest(observation)
    fixture['observations'][h] = observation
    ref['observation_sha256'] = h
    if trusted and h not in fixture['trusted_observation_hashes']:
        fixture['trusted_observation_hashes'].append(h)
