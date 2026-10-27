"""Read asset-cohort dependencies from the unchanged native company path."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'data/accounting-master/company-state-relationship-dependencies-20261028'))
import relationships as rel


def inspect(path,source,expected_digest):
    related=rel.inspect(path,source,expected_digest)
    if related['status']!='inspected':
        return dict(status='native_refusal',relationship_result=related,cohorts=None)
    result=related['native_result']
    assets=deepcopy(path['initial_year']['assets'])
    origins={a['id']:dict(kind='supplied_opening',input_path='/initial_year/assets/'+str(i)) for i,a in enumerate(assets)}
    events,reads,years,prefixes=[],[],[],[]
    definitions=[path['initial_year'],*path['continuations']]
    for yi,definition in enumerate(definitions):
        if yi>=len(result['years']):break
        native_year=result['years'][yi];run=native_year['run']
        applied=run.get('journals',run.get('applied',[]))
        by_id={j['event']:j for j in applied}
        for oi,op in enumerate(definition['operations']):
            if op['id'] not in by_id:continue
            journal=by_id[op['id']]['journal'];event=rel.event_key(yi,op['id'])
            cost_before=sum((Q(a['cost']) for a in assets),Q(0))
            accum_before=sum((Q(a['accumulated']) for a in assets),Q(0))
            if op['kind']=='plant_addition':
                p=op['payload'];cid=p['asset_id']
                if cid in origins:raise ValueError('duplicate executed asset')
                assets.append(dict(id=cid,cost=p['cost'],life=p['life'],
                                   accumulated='0/1',in_service=p['in_service']))
                location=('/initial_year' if yi==0 else '/continuations/'+str(yi-1))+'/operations/'+str(oi)+'/payload'
                origins[cid]=dict(kind='executed_addition',event=event,input_path=location)
                events.append(dict(kind='adds_cohort',event=event,asset_id=cid,cost=p['cost'],
                    life=p['life'],in_service=p['in_service'],
                    guards=['fresh_asset_id','positive_life','service_not_before_acquisition',
                            'no_unsupported_midyear_service','cash_available']))
            if op['kind']=='depreciation':
                for asset in assets:
                    old=Q(asset['accumulated']);cost=Q(asset['cost']);life=Q(asset['life'])
                    eligible=asset['in_service']<=definition['period']['start']
                    remaining=cost-old
                    charge=min(cost/life,remaining) if eligible else Q(0)
                    asset['accumulated']=rel.wire(old+charge)
                    reads.append(dict(event=event,asset_id=asset['id'],
                        read_fields=['cost','life','accumulated','in_service','period_start','depreciation_method'],
                        method=definition['depreciation_method'],period_start=definition['period']['start'],
                        in_service=asset['in_service'],eligible=eligible,
                        cost=rel.wire(cost),life=rel.wire(life),accumulated_before=rel.wire(old),
                        uncapped_annual_charge=rel.wire(cost/life),remaining_cost=rel.wire(remaining),
                        charge=rel.wire(charge),accumulated_after=asset['accumulated']))
            cost_after=sum((Q(a['cost']) for a in assets),Q(0))
            accum_after=sum((Q(a['accumulated']) for a in assets),Q(0))
            if cost_after-cost_before!=Q(journal.get('plant_cost','0/1')):
                raise ValueError('plant cost journal mismatch')
            if accum_after-accum_before!=-Q(journal.get('accum_depreciation','0/1')):
                raise ValueError('accumulated depreciation journal mismatch')
            if Q(journal.get('depreciation','0/1')) and op['kind']=='depreciation':
                if accum_after-accum_before!=Q(journal['depreciation']):
                    raise ValueError('depreciation charge mismatch')
            prefixes.append(dict(event=event,assets=deepcopy(assets)))
        if 'assets' in run:
            if assets!=run['assets']:raise ValueError('native asset population mismatch')
            if 'closing_memory' in native_year and assets!=native_year['closing_memory']['assets']:
                raise ValueError('native asset carry mismatch')
            years.append(dict(year=yi,native_status=run['status'],assets=deepcopy(assets)))
    return dict(profile='CompanyAssetCohortInspection/1',status='inspected',
        input_sha256=expected_digest,relationship_result=related,
        cohorts=[dict(**a,origin=origins[a['id']],physical_location=None,legal_title=None,
                      source_support=None) for a in assets],
        addition_events=events,depreciation_dependencies=reads,year_ends=years,prefixes=prefixes,
        population_coverage='supplied synthetic fixed-asset cohorts only',
        scope_exclusions=['disposals','impairment','revaluation','component_replacement','midyear_proration',
                          'tax_basis_differences','actual_asset_rights','exhaustive_company_population'],
        source_admission=False,executable_reduction=None)
