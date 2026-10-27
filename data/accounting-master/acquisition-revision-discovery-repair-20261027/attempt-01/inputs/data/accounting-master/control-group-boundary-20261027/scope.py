"""Bind conditional interval evidence to the current group-report scope only."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import importlib.util,re,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(R/'scripts'))
import group_period_report_v1 as group
PINS={
 'data/accounting-master/control-history-contract-20261026/history.py':'84653abad6bbf3dbd6c6e26ef4f2ae71e8bbb5261e6275e1e24b056a115944d2',
 'data/accounting-master/exact-information-time-20261026/projection.py':'5df5d2ac93d0e443b71575e4ab21b0f96de07c82a652bf47ed2b00f00ff6614c',
 'scripts/group_period_report_v1.py':'13cef76b375c0e8ba44ef22db8950606dcbd9ba8b492a44fb9fb6c4377ab1566'}
spec=importlib.util.spec_from_file_location('group_control_history',R/'data/accounting-master/control-history-contract-20261026/history.py')
history=importlib.util.module_from_spec(spec);spec.loader.exec_module(history)
PROFILE='ConditionalControlGroupScope/1'
FLAGS=dict(source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False,executed=False)
REQUIRED={
 'unresolved_history':['resolve_control_coverage'],
 'outside_controlled_group':['select_non_control_reporting_scope'],
 'changing_perimeter_methods_required':['dated_control_assessment','acquisition_or_loss_method','period_member_and_flow_allocation','ownership_and_nci_method'],
 'nci_methods_required':['ownership_and_nci_method'],
 'stable_scope_candidate':['remaining_group_report_checks']}

def scope(body):
    try:
        for p,h in PINS.items():history.need(sha256((R/p).read_bytes()).hexdigest()==h,'dependency_hash:'+p)
        group.engine.binding.bounded(body)
        history.fields(body,['profile','history_request','group_request','expected_history_sha256','expected_group_sha256','calendar_offset','basis_bridge'],'scope')
        history.need(body['profile']==PROFILE,'scope_profile')
        h=body['history_request'];g=body['group_request']
        history.need(history.digest(h)==body['expected_history_sha256'],'history_binding')
        history.need(history.digest(g)==body['expected_group_sha256'],'group_binding')
        history.fields(g,['profile','opening','closing','legal_reports','internal_cash_pairs'],'group')
        history.need(g['profile']==group.PROFILE,'group_profile')
        bridge=body['basis_bridge'];history.fields(bridge,['history_basis','group_measurement_basis','premise'],'basis_bridge')
        for value in bridge.values():history.text(value)
        history.need(bridge['history_basis']==h['basis'],'history_basis_binding')
        offset=body['calendar_offset']
        history.need(type(offset) is str and re.fullmatch(r'Z|[+-]\d{2}:\d{2}',offset) is not None,'calendar_offset')
        history.moment('2025-01-01T00:00:00'+offset)
        edges=[];periods=[]
        for side in ['opening','closing']:
            c=g[side]
            history.fields(c,['profile','world','books','schemas','chart','account_maps','eliminations','compatibility','control_edge_id'],'composition')
            history.need(c['profile']==group.composition.PROFILE,'composition_profile')
            w=c['world'];group.composition.world.validate(w)
            history.need(w['context']['mode']=='synthetic','synthetic_scope_only')
            history.need(type(c['books']) is dict and len(c['books'])==2 and set(c['books'])==set(w['books']),'two_books_required')
            history.need(len(w['control_edges'])==1,'single_edge_required')
            e=w['control_edges'][0];edges.append(e)
            history.need(e['id']==c['control_edge_id'],'edge_binding')
            history.need(h['subject']==[e['parent'],e['child']],'history_subject_binding')
            entities={b['context']['entity'] for b in c['books'].values()}
            history.need(entities==set(h['subject']),'book_subject_binding')
            for book in c['books'].values():
                p=book['period'];history.fields(p,['start','end_exclusive'],'period')
                for value in p.values():group.core.scalar(value,'date')
                history.need(p['start']<p['end_exclusive'],'period_order');periods.append(p)
            history.need(c['compatibility']['measurement_basis']==bridge['group_measurement_basis'],'group_basis_binding')
        history.need(edges[0]==edges[1],'period_control_edge_changed')
        history.need(all(p==periods[0] for p in periods),'period_binding')
        p=periods[0];e=edges[0]
        history.need(e['start']<=p['start'] and p['end_exclusive']<=e['end_exclusive'],'edge_interval_coverage')
        for name in ['start','end_exclusive']:
            expected=history.moment(p[name]+'T00:00:00'+offset)
            history.need(history.moment(h['interval'][name])==expected,'calendar_interval_binding:'+name)
        result=history.evaluate(h)
        statuses={a['status'] for a in result['atoms']}
        fraction=group.number(e['ownership_fraction'])
        if 'unresolved' in statuses:route='unresolved_history'
        elif statuses=={'no'}:route='outside_controlled_group'
        elif result['conditional_transitions']:route='changing_perimeter_methods_required'
        else:
            history.need(statuses=={'yes'} and result['continuous_control_under_assertions'],'inconsistent_history_result')
            route='stable_scope_candidate' if fraction==1 else 'nci_methods_required'
        return dict(profile=PROFILE,status='scope_assessed',**FLAGS,route=route,
                    required_methods=deepcopy(REQUIRED[route]),history=deepcopy(result),
                    history_request_sha256=history.digest(h),group_request_sha256=history.digest(g),
                    calendar_embedding=dict(period=deepcopy(p),fixed_offset=offset),basis_bridge=deepcopy(bridge),
                    supplied_control_edge=deepcopy(e),dependency_sha256=deepcopy(PINS),
                    implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                    scope='Conditional scope correspondence only; no report, control assessment or acquisition accounting is executed.')
    except Exception as exc:
        return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
