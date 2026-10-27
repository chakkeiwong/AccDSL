"""Preserve native opening outcomes before optional population inspection."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'data/accounting-master/company-state-asset-cohort-dependencies-20261028'))
import cohorts
rel=cohorts.rel


def inspect(path,source,expected_digest):
    if rel.native.digest(path)!=expected_digest:
        raise ValueError('path identity mismatch')
    native=rel.native.wire(rel.native.execute(path,source))
    answer=dict(profile='CompanyPopulationAdmissionInspection/1',
        input_sha256=expected_digest,input=deepcopy(path),native_result=native,
        population_inspection=None,population_complete=False,
        source_admission=False,actor_information_admission=False,
        full_company_constructor=False)
    if (native['status'] not in {'complete_conditional','partial'}
            or sha256(source).hexdigest()!=path['initial_year']['source']['sha256']):
        answer.update(status='native_refusal',population_status='not_inspected',
                      reason=native.get('reason','native_refusal'))
        return answer
    if not rel.native.verify_chain(path,native):
        raise ValueError('native chain binding')
    first=native['years'][0]['run']
    if 'claims' not in first or 'assets' not in first:
        answer.update(status='opening_not_executable',population_status='unresolved',
            opening_status=first['status'],reason=first.get('reason','missing_required_inputs'),
            obligations=deepcopy(first.get('obligations',[])))
        return answer
    inspected=cohorts.inspect(path,source,expected_digest)
    if inspected['status']!='inspected':raise ValueError('population inspector disagrees with native admission')
    if inspected['relationship_result']['native_result']!=native:
        raise ValueError('population native result mismatch')
    answer.update(status='inspected',population_status='supplied_executed_prefix_only',
                  population_inspection=inspected)
    return answer
