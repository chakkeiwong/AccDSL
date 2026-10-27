"""Selected continuation keeps an external verified prefix and cumulative report."""
from pathlib import Path
from copy import deepcopy as cp
import importlib.util,sys
H=Path(__file__).resolve().parent
P=H.parent/'coupon-partial-settlement-20261027'
sys.path.insert(0,str(P))
spec=importlib.util.spec_from_file_location('coupon_prefix_checker',P/'verify.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
s=prior.s

def run(source,sid,selection,selection_id,prefix_instructions,prefix,prefix_id,instructions):
    assert s.identity(source)==sid and s.identity(selection)==selection_id
    assert selection==s.select(source,sid)
    assert s.identity(prefix)==prefix_id
    assert prior.verify(prefix,source,sid,selection,selection_id,prefix_instructions)
    assert len(instructions)==1
    command=s.program(selection,instructions)['commands'][0]
    before=cp(prefix['execution']['current'])
    request=s.rt.call(before,selection['registry'],command)
    proposal=s.rt.methods.propose(before,request)
    current=cp(proposal['transition']['after']) if proposal['status']=='proposed' else cp(before)
    execution=dict(profile='SelectedCouponContinuationStep/1',status=proposal['status'],
        before_sha256=s.identity(before),command=command,request=request,proposal=proposal,
        current=current,after_sha256=s.identity(current))
    report=s.rt.reports.report(s.rt.reports.request(selection['opening'],current,selection['schemas'],selection['mapping']))
    return dict(profile='SelectedPartialCouponContinuation/1',**s.FLAGS,
        source_carry_sha256=sid,selection_sha256=selection_id,prefix_sha256=prefix_id,
        prefix_instructions=cp(prefix_instructions),instructions=cp(instructions),
        execution=execution,report=report,report_opening_sha256=s.identity(selection['opening']),
        origin_archive=cp(selection['origin_archive']),prefix_archive=cp(prefix),
        interpretation='same_period_cumulative_report_exact_prefix_no_merging')
