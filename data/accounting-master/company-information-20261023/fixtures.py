"""Authored test clocks, explicitly not evidence of past availability."""
from information import components,digest


def make(path,exchange_sha256):
    observations={};declarations=[]
    times={'authored':'2025-03-06T09:00:00Z','published':'2025-03-07',
           'ingested':'2025-03-06T10:00:00Z','accepted':'2025-03-06T11:00:00Z'}
    for component in components(path):
        events={}
        for event,time in times.items():
            observation={'profile':'SyntheticInformationObservation/1',
                'component_sha256':component['sha256'],'event':event,
                'audience':'public' if event=='published' else 'internal','time':time,
                'precision':'calendar_day_utc' if event=='published' else 'utc_instant',
                'provenance':'authored_test_clock_not_historical_evidence'}
            h=digest(observation);observations[h]=observation
            events[event]={'status':'observed_synthetic','observation_sha256':h}
        declarations.append({'slot':component['slot'],'component_sha256':component['sha256'],'events':events})
    return {'declaration':{'profile':'CompanyInformationDraft/1',
        'exchange_sha256':exchange_sha256,'path_sha256':digest(path),
        'evidence_class':'authored_synthetic','declarations':declarations},
        'observations':observations,'trusted_observation_hashes':sorted(observations),
        'trust_scope':'synthetic fixture only; not authenticated real-world observation'}
