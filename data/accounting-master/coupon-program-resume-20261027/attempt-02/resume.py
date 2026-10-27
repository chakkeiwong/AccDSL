"""Bounded selected coupon resume with separate fiscal opening and current book."""
from pathlib import Path
from copy import deepcopy as cp
import importlib.util,sys
H=Path(__file__).resolve().parent
P=H.parent/'coupon-partial-settlement-20261027';sys.path.insert(0,str(P))
spec=importlib.util.spec_from_file_location('resume_prefix_checker',P/'verify.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
s=prior.s;identity=s.identity
PLAN='SelectedCouponProgramResume/1';CHECKPOINT='SelectedCouponProgramCheckpoint/1'

def make_plan(source,sid,sel,ident,prefix_instructions,prefix,pid,suffix,trace_limit=None):
    assert identity(source)==sid and identity(sel)==ident and sel==s.select(source,sid)
    assert identity(prefix)==pid
    assert prior.verify(prefix,source,sid,sel,ident,prefix_instructions)
    assert prefix==s.run(source,sid,sel,ident,prefix_instructions)
    body=s.program(sel,suffix);s.rt.validate(body)
    limit=s.rt.MAX_TRACE_BYTES if trace_limit is None else trace_limit
    assert type(limit) is int and 2<=limit<=s.rt.MAX_TRACE_BYTES
    plan=dict(profile=PLAN,source_carry_sha256=sid,selection_sha256=ident,prefix_sha256=pid,
        opening_sha256=identity(sel['opening']),initial_current_sha256=identity(prefix['execution']['current']),
        registry_sha256=identity(sel['registry']),prefix_instructions=cp(prefix_instructions),
        suffix=cp(suffix),trace_limit=limit,command_limit=s.rt.MAX_COMMANDS)
    assert len(s.rt.core.canonical(plan))<=s.rt.core.MAX_BYTES
    return plan

def binding(source,sid,sel,ident,prefix,pid,plan,plan_id):
    assert identity(plan)==plan_id
    assert plan==make_plan(source,sid,sel,ident,plan['prefix_instructions'],prefix,pid,plan['suffix'],plan['trace_limit'])

def finish(sel,prefix,plan,current,trace,trace_bytes,status,stop):
    report=s.rt.reports.report(s.rt.reports.request(sel['opening'],current,sel['schemas'],sel['mapping']))
    assert report['status']=='reported'
    return dict(profile=CHECKPOINT,**s.FLAGS,plan_sha256=identity(plan),
        source_carry_sha256=plan['source_carry_sha256'],selection_sha256=plan['selection_sha256'],
        prefix_sha256=plan['prefix_sha256'],opening_sha256=plan['opening_sha256'],
        cursor=len(trace),current=cp(current),trace=cp(trace),trace_bytes=trace_bytes,status=status,
        stop=cp(stop),remaining=cp(plan['suffix'][len(trace):]),report=report,
        origin_archive=cp(prefix['origin_archive']),
        interpretation='selected_same_period_resume_no_durable_commit')

def extend(sel,prefix,plan,checkpoint,count):
    assert type(count) is int and 0<=count<=plan['command_limit']
    if checkpoint is None:
        current=cp(prefix['execution']['current']);trace=[];trace_bytes=2
    else:
        if checkpoint['status']!='paused_budget':return cp(checkpoint)
        current=cp(checkpoint['current']);trace=cp(checkpoint['trace']);trace_bytes=checkpoint['trace_bytes']
    end=min(len(plan['suffix']),len(trace)+count)
    commands=s.program(sel,plan['suffix'])['commands'];stop=None;status='paused_budget'
    while len(trace)<end:
        i=len(trace);command=commands[i];before=identity(current)
        request=s.rt.call(current,sel['registry'],command);proposal=s.rt.methods.propose(current,request)
        after=proposal['transition']['after'] if proposal['status']=='proposed' else current
        row=dict(index=i,command=cp(command),request=request,proposal=proposal,
            before_sha256=before,after_sha256=identity(after))
        size=len(s.rt.core.canonical(row))
        if trace_bytes+size>plan['trace_limit']:
            status='resource_limited';stop=dict(index=i,command=cp(command),reason='trace_size_limit',
                before_sha256=before,request_sha256=identity(request),proposal_sha256=identity(proposal),candidate_bytes=size)
            break
        if proposal['status']!='proposed':
            status='refused';stop=dict(row,reason=proposal.get('reason',proposal.get('transition',{}).get('reason','engine_refusal')))
            break
        trace.append(row);trace_bytes+=size;current=cp(after)
    if stop is None and len(trace)==len(plan['suffix']):status='complete'
    return finish(sel,prefix,plan,current,trace,trace_bytes,status,stop)

def validate_checkpoint(sel,prefix,plan,checkpoint):
    assert type(checkpoint) is dict and type(checkpoint.get('cursor')) is int
    cursor=checkpoint['cursor'];assert 0<=cursor<=len(plan['suffix'])
    status=checkpoint['status'];assert status in ('paused_budget','complete','refused','resource_limited')
    upto=cursor+(status in ('refused','resource_limited'))
    expected=extend(sel,prefix,plan,None,upto)
    assert checkpoint==expected

def run(source,sid,sel,ident,prefix,pid,plan,plan_id,count,checkpoint=None,checkpoint_id=None):
    binding(source,sid,sel,ident,prefix,pid,plan,plan_id)
    assert type(count) is int and 1<=count<=plan['command_limit']
    if checkpoint is not None:
        assert identity(checkpoint)==checkpoint_id
        validate_checkpoint(sel,prefix,plan,checkpoint)
    else:assert checkpoint_id is None
    return extend(sel,prefix,plan,checkpoint,count)
