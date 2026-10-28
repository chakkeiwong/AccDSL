"""Structured conflict/repair, actual/scenario separation, retained exact cases."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip,json,platform,subprocess,sys,time,traceback
import inference as inf
import scenario

H=Path(__file__).resolve().parent;ROOT=H.parents[2];OUT=H/sys.argv[1]
OUT.mkdir(exist_ok=False);start=time.monotonic();checks=[];results=[];controls=[];sources=set();reuse_records=[]
def dump(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+chr(10))
def ck(name,actual,expected):
    # Full values are retained in result files; compact equality checks avoid huge logs.
    large=isinstance(actual,(list,dict)) or isinstance(expected,(list,dict))
    checks.append(dict(name=name,passed=actual==expected,actual_sha256=inf.digest(actual) if large else None,expected_sha256=inf.digest(expected) if large else None,actual=None if large else actual,expected=None if large else expected))
def save(name,inputs,result):results.append(dict(name=name,inputs=deepcopy(inputs),result=deepcopy(result)));return result
def refuse(name,fn,reason):
    try:fn();actual='accepted'
    except ValueError as exc:actual=str(exc)
    controls.append(dict(name=name,reason=actual));ck(name,actual,reason)
def model(prior=None,likelihood=None,ident='supplied-v1'):
    return dict(id=ident,prior=prior or {'fixed':'1/2','floating':'1/2'},likelihood=likelihood or {'fixed':'1','floating':'1'},provenance='Declared synthetic finite type/observation model, not an issuer estimate')
def read(path):
    p=ROOT/'data/accounting-master'/path;sources.add(p);return json.loads(p.read_text())
def reuse(directory,selected):
    folder=ROOT/'data/accounting-master'/directory
    rows=read(directory+'/checks.json');byname={r.get('name',r.get('id')):r for r in rows}
    for name in selected:
        row=byname[name];ck('saved/'+name,row['actual'],row['expected']);ck('saved pass/'+name,row['passed'],True)
    files=sorted(p for p in folder.iterdir() if p.is_file());sources.update(files)
    manifest=folder/'run-manifest.json'
    if manifest.exists():
        data=json.loads(manifest.read_text())
        for path,expected in data.get('source_hashes',{}).items():
            p=ROOT/path;sources.add(p);ck('retained dependency/'+path,sha256(p.read_bytes()).hexdigest(),expected)
    reuse_records.append(dict(directory=directory,selected_checks=selected,files={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}))

def main():
    for prior in ['1/5','1/2','4/5']:
        weights={'fixed':prior,'floating':str(1-Q(prior))};original=deepcopy(weights);trajectory=[]
        for year in range(12):
            body=model(weights,{'fixed':'1/3','floating':'1/3'},'equal-'+str(year));r=inf.update(body)
            trajectory.append(r);ck('uninformative/'+prior+'/'+str(year),r['posterior'],original);weights=r['posterior']
        save('uninformative trajectory'+prior,dict(initial=original,likelihood='1/3 each type'),trajectory)
    b=model(likelihood={'fixed':'9/10','floating':'1/10'});r=save('informative',b,inf.update(b))
    ck('informative posterior',r['posterior'],{'fixed':'9/10','floating':'1/10'})
    ck('persistent type IDs',r['type_support'],['fixed','floating'])
    expected=sum(Q(r['posterior'][k])*v for k,v in [('fixed',5),('floating',7)])
    ck('posterior mean not a single company coupon',str(expected),'26/5');ck('mean outside individual states',expected in [5,7],False)
    zero=model(likelihood={'fixed':'0','floating':'0'},ident='zero-model');conflict=save('zero likelihood conflict',zero,inf.update(zero))
    ck('zero conflict',conflict['status'],'conflict');ck('no fallback posterior',conflict['posterior'],None)
    ck('unresolved types retained',conflict['type_support'],['fixed','floating'])
    proposal=dict(supersedes=conflict['model_sha256'],reason='Proposed source-error likelihood; requires independent review',model=model(likelihood={'fixed':'1/10','floating':'1/10'},ident='repair-v2'))
    before=deepcopy(conflict);repair=save('separate proposed repair',proposal,inf.propose_repair(conflict,proposal))
    ck('conflict immutable',conflict,before);ck('original conflict embedded',repair['original'],conflict)
    ck('repair retains prior',repair['candidate']['posterior'],zero['prior'])
    ck('repair not admitted',[repair[k] for k in ['automatic_replacement','source_admission','actual_model_correct']],[False]*3)
    still=deepcopy(proposal);still['model']=model(likelihood={'fixed':'0','floating':'0'},ident='still-conflict-v2')
    r=save('failed repair remains conflict',still,inf.propose_repair(conflict,still));ck('candidate still fails',r['candidate']['status'],'conflict')
    b=model(likelihood={'fixed':None,'floating':'1/10'});r=save('unknown likelihood',b,inf.update(b));ck('unknown remains unresolved',r['status'],'unresolved')
    b=model(prior={'fixed':'0','floating':'1'},likelihood={'fixed':'1','floating':'0'});r=save('zero support cannot recover',b,inf.update(b));ck('zero prior support conflict',r['status'],'conflict')
    for name,mutate,reason in [('wrong target',lambda p:p.update(supersedes='0'*64),'repair_target'),('same model ID',lambda p:p['model'].update(id='zero-model'),'new_model_identity_required'),('no reason',lambda p:p.update(reason=''),'repair_reason')]:
        p=deepcopy(proposal);mutate(p);refuse(name,lambda:inf.propose_repair(conflict,p),reason)
    altered=deepcopy(conflict);altered['posterior']={'fixed':'1','floating':'0'}
    refuse('forged original conflict',lambda:inf.propose_repair(altered,proposal),'changed_original_result')
    for name,b,reason in [('negative prior',model(prior={'fixed':'-1','floating':'2'}),'negative_prior'),('bad normalization',model(prior={'fixed':'1','floating':'1'}),'prior_not_one'),('bad likelihood',model(likelihood={'fixed':'2','floating':'1'}),'likelihood_range'),('different support',model(likelihood={'fixed':'1'}),'same_type_support_required')]:
        refuse(name,lambda:inf.update(b),reason)
    prior={'common':'99/100','distress':'1/100'};values={'common':'0','distress':'100'}
    strata=save('conditional type strata',dict(prior=prior,values=values),inf.conditional_strata(prior,values))
    ck('both types retained',strata['type_coverage'],['common','distress'])
    ck('strata supplied expectation',str(sum(Q(x['mass'])*Q(x['conditional_value']) for x in strata['rows'])),'1')
    extinction=Q(99,100)**100;save('one percent iid extinction',dict(probability='1/100',draws=100),dict(exact=str(extinction),interpretation='No distress draw despite possible distress; iid fixed-count premise'))
    ck('extinction exceeds one third',extinction>Q(1,3),True);ck('extinction below two fifths',extinction<Q(2,5),True)
    ck('strata not full population',strata['real_history_coverage'],False)
    refuse('missing distress stratum',lambda:inf.conditional_strata(prior,{'common':'0'}),'strata_support_mismatch')
    content='Synthetic loan L floating, public and analyst receipt in2028';h=sha256(content.encode()).hexdigest();sources_map={h:content}
    row=dict(id='terms',source_sha256=h,loan_id='L',loan_type='floating',authored='2027-01-01T00:00:00+00:00',effective='2027-01-01T00:00:00+00:00',published='2028-01-01T00:00:00+00:00',access={'analyst':dict(route='public_document',at='2028-01-01T00:00:00+00:00')})
    early=scenario.actual([row],sources_map,'analyst','L','2027-12-31T00:00:00+00:00')
    save('early actual',dict(records=[row],sources=sources_map),early)
    ck('future terms not actual knowledge',early['view']['status'],'not_available')
    before=deepcopy(early)
    for kind in ['fixed','floating']:
        a=dict(id='what-if-'+kind,context='hypothetical',loan_id='L',loan_type=kind,reason='Explicit conditional case, not an actual disclosure')
        r=save('hypothetical '+kind,dict(actual=early,assumption=a),scenario.branch(early,a))
        ck(kind+'/conditional branch',r['status'],'conditional_branch');ck(kind+'/only assumed type',r['loan_types'],[kind])
        ck(kind+'/actual unchanged',early,before);ck(kind+'/not knowledge',r['actual_knowledge_verified'],False)
    changed=deepcopy(row);changed['loan_type']='fixed'
    other=scenario.actual([changed],sources_map,'analyst','L','2027-12-31T00:00:00+00:00');ck('future content cannot resolve earlier view',other,early)
    late=save('later actual',dict(records=[row],sources=sources_map),scenario.actual([row],sources_map,'analyst','L','2028-01-01T00:00:00+00:00'))
    ck('actual receipt resolves supplied type',late['view']['observation']['loan_type'],'floating')
    a=dict(id='what-if-fixed',context='hypothetical',loan_id='L',loan_type='fixed',reason='Test conjunction with known actual terms')
    r=save('conflicting hypothetical',dict(actual=late,assumption=a),scenario.branch(late,a));ck('no silent actual overwrite',r['status'],'conflict_with_actual_view')
    a['loan_type']=None;ck('unknown assumption remains unresolved',scenario.branch(early,a)['status'],'unresolved_assumption')
    a['context']='actual';refuse('scenario relabeled actual',lambda:scenario.branch(early,a),'hypothetical_context_required')
    a['context']='hypothetical';a['loan_id']='other';refuse('wrong loan branch',lambda:scenario.branch(early,a),'loan_identity_mismatch')
    forged=deepcopy(early);forged['view']['status']='known';refuse('changed actual binding',lambda:scenario.branch(forged,a),'actual_view_binding')
    reuse('company-state-quiet-rights-scope-20261028/attempt-01',['rights merge fee8/status','rights merge fee8/witness','quiet coupons fee8call','quiet coupons fee8locked','rights fee8/full path equality'])
    reuse('company-state-approximation-boundaries-20261028/attempt-01',['lost/rare count','lost/weight ESS','lost/underlying family preserved','lost/missing support audit','retained/rare count'])
    reuse('company-state-evidence-failures-20261028/attempt-02',['before correction/selected ids','before correction/quantity','before correction/full known history','at publication/selected ids','at publication/quantity','at publication/full known history','as originally reported/quantity','as originally reported/full known history','future amount 4/1/same attachment','future amount 7/1/same attachment'])
    reuse('company-state-evidence-failures-20261028/consumer-attempt-01',['before correction/whole native outcome','at publication/whole native outcome','as originally reported/whole native outcome','outside complete domain/outcome carried','outside complete domain/conditional support'])
    saved=read('company-state-evidence-failures-20261028/consumer-attempt-01/results.json');byid={r['id']:r['output'] for r in saved}
    for ident in ['outside complete domain','correction with unlinked alias']:
        view=byid[ident]['decision_view'];ck(ident+'/conflict at consumer',view['outcome'],'conflict');ck(ident+'/not executable',view['conditional_inputs_supported'],False)
    for ident,amount in [('before correction','6/1'),('at publication','5/1'),('as originally reported','6/1')]:
        view=byid[ident]['decision_view'];ck(ident+'/exact assertion',view['assertions'][0]['interval']['lower'],amount)
    original=read('unified-program-20261028/failure-map.json');ids=['LIT-F010','LIT-F011','LIT-F012','LIT-F013','LIT-F014','LIT-F015'];rows=[r['original_row'] for r in original['rows'] if r['original_row']['id'] in ids]
    ck('original rows',len(rows),6);dump('original-rows.json',rows)
    return dict(passed=all(c['passed'] for c in checks),checks=len(checks),result_groups=len(results),refusal_controls=len(controls),reused_units=len(reuse_records),failed=[c['name'] for c in checks if not c['passed']],original_rows=ids)

try:
    summary=main();dump('verification.json',summary)
except Exception:
    dump('failure.json',dict(error=traceback.format_exc(),checks_passed=sum(c['passed'] for c in checks)));raise
finally:
    dump('checks.json',checks);dump('results.json',results);dump('controls.json',controls);dump('reused-evidence.json',reuse_records)
    for name in ['check.py','inference.py','scenario.py']:(OUT/name).write_bytes((H/name).read_bytes());sources.add(H/name)
    sources.add(ROOT/'docs/plans/company-state-information-reconciliation-20261028.md')
    sources.update(Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT))
    dump('source-hashes.json',{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(sources)})
    dump('manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=platform.python_version(),cpu_gpu='CPU only; no accelerator imports',random_seeds='N/A deterministic exact examples',data_version='Authored finite models plus complete saved prior results',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan='docs/plans/company-state-information-reconciliation-20261028.md',result=str(H.relative_to(ROOT)/'result.md'),artifacts=str(OUT.relative_to(ROOT))))
print(json.dumps(summary));raise SystemExit(not summary['passed'])
