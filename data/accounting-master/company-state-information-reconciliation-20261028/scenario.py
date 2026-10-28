"""Explicit hypothetical loan assumptions layered beside a dated actual view."""
from copy import deepcopy
from pathlib import Path
import importlib.util
from inference import digest
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'data/accounting-master/company-state-actor-causal-stress-20261028/information.py'
s=importlib.util.spec_from_file_location('retained_actual_loan_information',p)
information=importlib.util.module_from_spec(s);s.loader.exec_module(information)

def actual(records,sources,actor,loan,cutoff):
    value=information.view(records,sources,actor,loan,cutoff)
    return dict(context='actual',view=value,view_sha256=digest(value),source_admission=False)

def branch(actual_view,assumption):
    if actual_view.get('context')!='actual' or actual_view.get('view_sha256')!=digest(actual_view.get('view')):
        raise ValueError('actual_view_binding')
    if set(assumption)!={'id','context','loan_id','loan_type','reason'}:raise ValueError('assumption_fields')
    if assumption['context']!='hypothetical':raise ValueError('hypothetical_context_required')
    if not assumption['id'] or not isinstance(assumption['reason'],str) or not assumption['reason'].strip():raise ValueError('assumption_provenance')
    view=actual_view['view']
    if assumption['loan_id']!=view['loan_id']:raise ValueError('loan_identity_mismatch')
    if assumption['loan_type'] not in ['fixed','floating',None]:raise ValueError('unsupported_loan_type')
    result=dict(context='hypothetical',branch_id=assumption['id'],actual_view_sha256=actual_view['view_sha256'],
                assumption=deepcopy(assumption),actual_knowledge_verified=False,source_admission=False,loan_types=None)
    if view['status'] not in ['known','not_available']:
        return {**result,'status':'unresolved_actual_view','actual_status':view['status']}
    if assumption['loan_type'] is None:return {**result,'status':'unresolved_assumption'}
    present=view['observation']['loan_type'];types={present} if present is not None else {'fixed','floating'}
    kept=types & {assumption['loan_type']}
    return {**result,'status':'conditional_branch' if kept else 'conflict_with_actual_view','loan_types':sorted(kept)}
