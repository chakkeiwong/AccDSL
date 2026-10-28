"""Preserve observable assertions while carrying conflict status to their consumer."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'data/accounting-master/unified-program-20261028/information_views.py'
FIELDS=('id','content','source_sha256','context','observation','interval','lineage','period','supersedes','dependence_group','role')
STATUSES={'selected_conditional_inputs':'conditional_inputs','conditional_conflict':'conflict',
          'unresolved_information_view':'unresolved','invalid':'invalid','unsupported':'unsupported'}


def _project(audit):
    """Only used after the pinned selector; not a source authentication API."""
    status=audit.get('status')
    if status not in STATUSES: raise ValueError('unsupported_native_status')
    assertions=[]
    if status in {'selected_conditional_inputs','conditional_conflict'}:
        projection=audit.get('policy_evidence')
        if not isinstance(projection,dict) or set(projection)!={'view','assertions','source_admission'}:
            raise ValueError('projection_fields')
        if projection['source_admission'] is not False or projection['view']!=audit['query']:
            raise ValueError('projection_context')
        expected=[{k:deepcopy(audit['source_records'][key][k]) for k in FIELDS}
                  for key in audit['selected_ids']]
        if projection['assertions']!=expected: raise ValueError('projection_assertions')
        assertions=deepcopy(expected)
    elif 'policy_evidence' in audit:
        raise ValueError('unexpected_projection')
    return dict(profile='ConflictAwareDecisionView/1',outcome=STATUSES[status],
        conditional_inputs_supported=status=='selected_conditional_inputs',
        assertions=assertions,view=deepcopy(audit.get('query')),
        source_admission=False,actual_actor_knowledge=False,forecast_admission=False,
        production_execution_authorized=False,probability_model=None)


def build(base,sources,query):
    pins=json.loads((HERE/'decision-view-source-lock.json').read_text())
    for path,expected in pins.items():
        candidate=ROOT/path
        if not candidate.is_file() or sha256(candidate.read_bytes()).hexdigest()!=expected:
            return dict(status='refused',reason='native_identity',native_executed=False,decision_view=None)
    sys.path.insert(0,str(SOURCE.parent));sys.path.insert(0,str(ROOT/'scripts'))
    spec=importlib.util.spec_from_file_location('conflict_view_native',SOURCE)
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    audit=native.select(base,sources,query)
    try:decision=_project(audit)
    except (ValueError,KeyError,TypeError) as exc:
        return dict(status='refused',reason=str(exc),native_executed=True,audit_result=audit,decision_view=None)
    return dict(status='complete_conditional',native_executed=True,
        audit_result=audit,decision_view=decision,
        scope='Conditional source-view consumer only; source population and semantic admission remain external')

