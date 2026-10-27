"""Selected all-preserve financing carry over unchanged report/carry engines."""
from copy import deepcopy
from pathlib import Path
import importlib.util,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('carry_financing_contract',HERE.parent/'financing-opening-invariants-20261026/financing_contract.py')
financial=importlib.util.module_from_spec(spec);spec.loader.exec_module(financial)
import company_book_carry_v1 as carry
core=carry.core
PROFILE='SelectedFinancingCarry/1'
FLAGS=dict(source_admission=False,accounting_admission=False,fiscal_admission=False,durable=False,production_ready=False)

def policies(book):
    return {p:dict(kind='preserve',provenance='Selected synthetic financing carry preserves every supplied historical leaf') for p in book['memory_types']}

def selection(contract,schemas,mapping,retained_account):
    return dict(profile=PROFILE,financial_contract=deepcopy(contract),financial_contract_sha256=core.digest(contract),
      schemas_sha256=core.digest(schemas),mapping_sha256=core.digest(mapping),retained_account=retained_account,
      memory_policy='all_preserve',residuals=['Selected synthetic carry only; no source, legal or fiscal/accounting admission',
      'Stored conditional findings remain historical; no automatic freshness'])

def make_call(selected,request,reviewed):
    return dict(profile=PROFILE,selection_sha256=core.digest(selected),request_sha256=core.digest(request),reviewed=reviewed)

def propose(selected,request,reviewed,call):
    result=dict(profile=PROFILE,**FLAGS);stage='selection'
    try:
        core.need(call==make_call(selected,request,reviewed),'stale_selected_carry_call')
        core.need(reviewed==core.digest(selected),'independent_carry_selection')
        core.closed(selected,['profile','financial_contract','financial_contract_sha256','schemas_sha256','mapping_sha256',
                             'retained_account','memory_policy','residuals'],'selected_carry')
        core.need(selected['profile']==PROFILE and selected['memory_policy']=='all_preserve','selected_carry_policy')
        financial_contract=selected['financial_contract']
        core.need(core.digest(financial_contract)==selected['financial_contract_sha256'],'selected_financing_contract')
        report_request=request['report_request'];before=report_request['closing'];schemas=report_request['schemas']
        core.need(core.digest(schemas)==selected['schemas_sha256'],'selected_schemas')
        core.need(core.digest(report_request['mapping'])==selected['mapping_sha256'],'selected_report_mapping')
        core.need(request['retained_account']==selected['retained_account'],'selected_retained_account')
        stage='memory_policy'
        supplied=request['memory_policies'];core.need(type(supplied) is dict and set(supplied)==set(before['memory_types']),'complete_preservation_policy')
        for pointer,p in supplied.items():
            core.closed(p,['kind','provenance'],'preservation_policy')
            core.need(p['kind']=='preserve','history_reset_forbidden:'+pointer)
            carry.engine.text(p['provenance'],'preservation_provenance')
        stage='closing_state';checked=financial.snapshot(financial_contract,before,schemas);result['closing_assessment']=checked
        if checked['status']!='requirements_satisfied':return dict(result,status=checked['status'],failed_stage=stage)
        stage='typed_carry';candidate=carry.propose(request);result['diagnostic_carry']=candidate
        if candidate['status']!='proposed':return dict(result,status=candidate['status'],failed_stage=stage,reason=candidate.get('reason','carry_refusal'))
        after=candidate['next_opening'];closed=candidate['closed_book'];stage='history_frame'
        core.need(after['memory']==before['memory'],'all_memory_preserved')
        core.need(after['memory_types']==before['memory_types'] and after['memory_schema']==before['memory_schema'],'memory_types_preserved')
        core.need(closed['flows']==before['flows'],'closing_flows_preserved')
        core.need(after['flows']==[],'new_period_flows_empty')
        core.need(after['seen']==before['seen']+[request['close_id']],'event_history_preserved')
        stage='next_snapshot';checked=financial.snapshot(financial_contract,after,schemas);result['opening_assessment']=checked
        if checked['status']!='requirements_satisfied':return dict(result,status=checked['status'],failed_stage=stage)
        stage='fiscal_opening_structure'
        opening_report=carry.reports.report(carry.reports.request(after,after,schemas,report_request['mapping']))
        result['opening_report']=opening_report
        core.need(opening_report['status']=='reported','next_opening_report:'+opening_report.get('reason',''))
        return dict(result,status='proposed_selected_carry',failed_stage=None,next_opening=deepcopy(after))
    except (ValueError,KeyError,TypeError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',failed_stage=stage,reason=str(exc)[:300])
