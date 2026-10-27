"""One-time role-separated timing screen; default recomputation is read-only."""
import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import time

U = Path(__file__).resolve().parent
R = U.parents[2]
VINTAGE = R/'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json'
CALENDAR = R/'data/accounting-master/r05-fiscal-year-protocol-20261023/calendar-sources.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bound = lambda p: {'path':str(p.relative_to(R)), 'sha256':sha(p)}
load = lambda p: json.loads(p.read_text())


def resolve(ref):
    p = R/ref['path']
    assert sha(p) == ref['sha256'], ref['path']
    node = load(p)
    for part in ref['json_pointer'].split('/')[1:]:
        part = part.replace('~1','/').replace('~0','~')
        node = node[int(part)] if isinstance(node,list) else node[part]
    return node


def bounds(day):
    """Conservative closed civil-date envelope with UTC offset in [-24h,+24h]."""
    d = datetime.combine(date.fromisoformat(day),datetime.min.time(),timezone.utc)
    return d-timedelta(days=1), d+timedelta(days=2)


def relation(event_day, cutoff_day):
    if event_day is None:
        return 'unverified'
    e,c = bounds(event_day),bounds(cutoff_day)
    if e[1] <= c[0]:
        return 'supported_for_date_role_only'
    if e[0] > c[1]:
        return 'contradicted_for_date_role_only'
    return 'unverified'


def calculate():
    v = load(VINTAGE)
    calendars = {x['issuer_id']:x for x in load(CALENDAR)['rows']}
    assert len(v['rows']) == 192 and len(v['families']) == 9
    assert all(r['selected_byte_available_at'] is None and r['as_of_admission'] is False for r in v['rows'])
    candidates = []
    for index,row in enumerate(v['rows']):
        coverage = row['active_coverage']['record']
        issuer = row['issuer_id']
        last_interim = 'q3' if issuer in ('apple','caterpillar','jpmorgan') else 'interim_h1'
        yr,cl = coverage['period_year'],coverage['report_class']
        if (yr,cl) not in ((2024,'annual'),(2025,last_interim),(2025,'annual')):
            continue
        assert resolve(row['active_coverage']['source']) == coverage
        meta = row['frozen_date_metadata']
        assert resolve(meta['source']) == meta['record']
        assert meta['record']['selected_sha256'] == row['selected']['sha256'] == coverage['sha256']
        assert sha(R/row['selected']['path']) == coverage['sha256']
        cutoff = calendars[issuer]['reported_end']
        start = (date.fromisoformat(cutoff)+timedelta(days=1)).isoformat()
        records = [('filing_date_metadata',meta,meta['record']['selected_date'])]
        for item in row['official_filing_events']:
            # This 27-record selection contains none; refuse silent schema guesses.
            raise AssertionError('official event schema must be inspected before use')
        for item in row['attributed_publication_declarations']:
            assert resolve(item['source']) == item['record']
            assert item['record']['pdf_sha256'] == coverage['sha256']
            records.append(('issuer_publication_declaration',item,item['record']['declared_date']))
        roles = [{'role':role,'date':day,'source':record['source'],
                  'date_screen':relation(day,cutoff),'selected_byte_admission':False}
                 for role,record,day in records]
        candidates.append({'document_id':row['document_id'],'issuer_id':issuer,
            'input_candidate_kind': 'older_annual' if yr == 2024 else 'latest_interim' if cl != 'annual' else 'immediately_preceding_annual',
            'report_year_label':yr,'report_class':cl,
            'reconciliation_pointer':f'/rows/{index}','selected':row['selected'],
            'conditional_target_label':'FY2026','conditional_target_start':start,
            'illustrative_cutoff_date':cutoff,'actual_cutoff_instant':None,
            'calendar_provenance':{'source':bound(CALENDAR),'issuer_id':issuer,
                 'assumption':'target starts immediately after reported FY2025 end; not established as pre-origin knowledge'},
            'date_roles':roles,'official_filing_event_count':0,
            'first_outcome_release':None,'selected_byte_available_at':None,
            'as_of_admission':False,'financial_mapping_admitted':False,
            'forecast_issuance_admitted':False})
    assert len(candidates)==27 and len({r['document_id'] for r in candidates})==27
    assert Counter(r['issuer_id'] for r in candidates) == Counter({i:3 for i in calendars})
    date_roles=[role for r in candidates for role in r['date_roles'] if role['date'] is not None]
    observed={r['document_id'] for r in candidates if any(x['date'] is not None for x in r['date_roles'])}
    # Independent expected counts from inspected named records, not inferred admissions.
    counts={'rows':27,'issuers':9,'distinct_dated_reports':len(observed),
            'reports_without_date_role':27-len(observed),
            'date_roles_by_kind':dict(Counter(x['role'] for x in date_roles)),
            'date_roles_by_screen':dict(Counter(x['date_screen'] for x in date_roles)),
            'byte_admissions':0,'prospective_forecasts':0}
    assert counts['distinct_dated_reports']==12 and counts['reports_without_date_role']==15
    assert counts['date_roles_by_kind']=={'filing_date_metadata':4,'issuer_publication_declaration':8}
    assert counts['date_roles_by_screen']=={'contradicted_for_date_role_only':5,'supported_for_date_role_only':7}
    return {'scope':'27 retained input candidates for conditional FY2026 illustration; not a forecast or selected cutoff',
            'sources':[bound(VINTAGE),bound(CALENDAR)],
            'date_envelope':'Each named day maps to [day-24h, next-day+24h] UTC; conservative closed envelope under the stated civil-offset bound, not observed UTC timing',
            'date_role_is_not_byte_time':True,'counts':counts,'rows':candidates}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--record',action='store_true');args=ap.parse_args()
    start=time.monotonic()
    result=calculate()
    if args.record:
        assert not (U/'matrix.json').exists() and not (U/'matrix-run.json').exists()
        with (U/'matrix.json').open('x') as f:
            json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
        with (U/'matrix-run.json').open('x') as f:
            json.dump({'calculation_wall_seconds':time.monotonic()-start,
                       'recorded_utc':datetime.now(timezone.utc).isoformat(),
                       'seeds':'N/A deterministic date/hash checks'},f,indent=2);f.write('\n')
    elif (U/'matrix.json').exists():
        assert load(U/'matrix.json')==result
    print(json.dumps({'status':'recorded' if args.record else 'read-only calculation passed',**result['counts']}))


if __name__ == '__main__':
    main()
