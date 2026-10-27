from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from unittest.mock import patch
import json
from examples import fixtures,m
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def canonical(x):return m.annual.caller.canonical(x)

def conformance():
    checks=[];rows=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    lock=json.loads((HERE/'source-lock.json').read_text())
    for p,h in lock.items():check('protected:'+p,sha(ROOT/p)==h)
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests_pass',tests['exit_code']==0)
    for p,h in tests['files'].items():check('tested_bytes:'+p,sha(ROOT/p)==h)
    examples=fixtures()
    for row in examples:
        name=row['case'];before=canonical(row);source=row['source'];program=row['program'];imports=row['imports']
        with patch.object(m.runtime,'run',side_effect=AssertionError('hidden evaluation')), patch.object(m.annual.root,'run',side_effect=AssertionError('hidden root')):
            text=m.compile_text(source,imports);typed=m.compile_program(program,imports)
        check(name+':compile_pure',text['executed'] is typed['executed'] is False)
        check(name+':exact_lowering',canonical(text['request'])==canonical(typed['request'])==canonical(row['request']))
        check(name+':exact_roundtrip',m.lower(source)==program and m.render(m.lower(source))==source)
        check(name+':semantic_hash',text['request_sha256']==typed['request_sha256']==m.annual.book.digest(row['request']))
        check(name+':raw_source_hash',text['source_text_sha256']==sha256(source.encode()).hexdigest() and typed['source_text_sha256'] is None)
        lines=source.splitlines();spans=text['source_spans']['operations']
        check(name+':span_count',len(spans)==len(program['operations']))
        for i,span in enumerate(spans):
            op=program['operations'][i];key=op['event']['event']['id'] if op['kind']=='native' else op['event']['id']
            check(name+':span'+str(i),span['id']==key and span['kind']==op['kind'] and lines[span['start_line']-1].startswith('operation ') and lines[span['end_line']-1]=='end_operation;')
            for field,numbers in span['field_lines'].items():check(name+':field'+str(i)+':'+field,all(lines[n-1].startswith(field+' ') for n in numbers))
        a=m.execute_text(source,imports);b=m.execute_program(program,imports);direct=m.runtime.run(row['request'])
        check(name+':full_execution_match',canonical(a)==canonical(b)==canonical(direct))
        check(name+':semantic_status',a['status']==row['expected_status'])
        check(name+':semantic_stop',(a['stop']['status'] if a.get('stop') else None)==row['expected_stop'])
        check(name+':exact_prefix',a['remaining_operations']==row['request']['operations'][len(a['trace']):])
        check(name+':no_admission',a['annual_ready'] is False and a['source_admission'] is False and a['accounting_admission'] is False)
        check(name+':inputs_preserved',canonical(row)==before)
        rows.append({'case':name,'program':program,'request_sha256':text['request_sha256'],
            'source':source,'source_sha256':text['source_text_sha256'],'spans':text['source_spans'],
            'result':a,'imports_sha256':m.annual.book.digest(imports)})
    row=next(r for r in examples if r['legacy'] is not None);source=row['source'];imports=row['imports']
    same='\n'+source.replace('operations;','operations;\n',1)
    a=m.compile_text(source,imports);b=m.compile_text(same,imports)
    check('whitespace_semantic_invariance',a['request_sha256']==b['request_sha256'] and a['program_sha256']==b['program_sha256'])
    check('whitespace_raw_distinction',a['source_text_sha256']!=b['source_text_sha256'] and a['source_spans']!=b['source_spans'])
    check('crlf_semantic_invariance',m.compile_text(source.replace('\n','\r\n'),imports)['request']==row['request'])
    mode=next(l for l in source.splitlines() if l.startswith('mode '));info=next(l for l in source.splitlines() if l.startswith('information '))
    negatives={
        'duplicate_field':source.replace(mode,mode+'\n'+mode,1),
        'duplicate_information':source.replace(info,info+'\n'+info,1),
        'missing_field':source.replace(mode+'\n','',1),
        'unknown_field':source.replace(mode,'invented '+mode,1),
        'after_end':source+'operations;',
        'missing_end':source.replace('end_program;',''),
        'invalid_profile':source.replace(m.PROFILE,'Wrong/1'),
        'duplicate_json':source.replace('"selected":{','"selected":{},"selected":{',1),
        'bom':'\ufeff'+source,'bare_cr':source+'\r','unicode_separator':source+'\u2028',
        'utf8':b'\xff','trailing_token':source.replace(mode,mode+' junk;',1)}
    for name,bad in negatives.items():
        reason=None
        try:m.compile_text(bad,imports)
        except m.Invalid as exc:reason=str(exc)
        check(name+':rejected',reason is not None);rows.append({'case':name,'expected':'compile_rejection','reason':reason})
    for name,mutate in [
        ('zero_denominator',lambda p:p['operations'][1]['event'].update(amount='1/0')),
        ('nonreduced',lambda p:p['operations'][1]['event'].update(amount='2/2')),
        ('invalid_date',lambda p:p['operations'][0]['event']['interval'].update(activity_through='2027-02-30')),
        ('float',lambda p:p['operations'][1]['event'].update(amount=1.0)),
        ('duplicate_operation',lambda p:p['operations'].append(deepcopy(p['operations'][0]))),
        ('root_path',lambda p:p.update(root_sha256='/tmp/root.json')),
        ('unknown_information_key',lambda p:p['operations'][0]['event']['information'].update(invented={'status':'unknown','reason':'Missing'})),
        ('unknown_operation',lambda p:p['operations'][0].update(kind='script'))]:
        p=deepcopy(row['program']);mutate(p);reason=None
        try:m.compile_program(p,imports)
        except m.Invalid as exc:reason=str(exc)
        check(name+':rejected',reason is not None);rows.append({'case':name,'expected':'compile_rejection','reason':reason})
    for name,registry in [('missing_import',{}),('changed_import',{row['program']['root_sha256']:{'changed':True}})]:
        reason=None
        try:m.compile_program(row['program'],registry)
        except m.Invalid as exc:reason=str(exc)
        check(name+':rejected',reason is not None);rows.append({'case':name,'expected':'compile_rejection','reason':reason})
    partial=next(r for r in examples if r['case']=='inventory_partial')
    source=partial['source'];imports=partial['imports'];line=next(l for l in source.splitlines() if l.startswith('finding '))
    for name,bad in [('missing_inventory_finding',source.replace(line+'\n','',1)),('duplicate_inventory_finding',source.replace(line,line+'\n'+line,1))]:
        reason=None
        try:m.compile_text(bad,imports)
        except m.Invalid as exc:reason=str(exc)
        check(name+':rejected',reason is not None);rows.append({'case':name,'expected':'compile_rejection','reason':reason})
    legacy=deepcopy(partial['program']);legacy['profile']=m.base.PROFILE
    rejected=False
    try:m.base.compile_program(legacy,imports)
    except m.Invalid:rejected=True
    check('frozen_legacy_profile_rejects_optional_sale',rejected)
    for row in examples:
        if row['legacy'] is None:continue
        prior=row['legacy'];a=m.base.compile_text(prior['source'],prior['imports'])['request'];b=m.compile_text(row['source'],row['imports'])['request']
        check(row['case']+':unchanged_legacy_lowering',{k:v for k,v in a.items() if k!='profile'}=={k:v for k,v in b.items() if k!='profile'})
    return checks,rows,tests,lock
