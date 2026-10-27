"""One declared provisional transition with retained conditional history evidence."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import conditional_company_opening_v1 as source

engine=source.engine
core=engine.core
reports=source.reports
PROFILE='ConditionalCompanyContinuation/1'
FLAGS=source.FLAGS
SOURCE_SHA256='b9911e670e9eb8814f5711517d917ef736fed35124a6b6987fe9705c6c98ef94'


def run(body):
    try:
        core.need(sha256(Path(source.__file__).read_bytes()).hexdigest()==SOURCE_SHA256,'opening_dependency_hash')
        engine.memory.bounded(body)
        engine.closed(body,['profile','opening_request','opening_result','transition_request','equity_movements','notes'])
        core.need(body['profile']==PROFILE,'profile')
        opening=source.map_opening(body['opening_request'])
        core.need(core.canonical(opening)==core.canonical(body['opening_result']),'opening_recomputation_mismatch')
        result={'profile':PROFILE,**FLAGS,'request_sha256':core.digest(body),'opening_result':deepcopy(opening),
                'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'source_sha256':SOURCE_SHA256}
        if opening['status'] in ['unresolved','candidate_opening_with_unresolved_obligations']:
            return {**result,'status':'unresolved','reason':'opening_obligations_remain'}
        core.need(opening['status']=='conditional_opening','conditional_opening_required')
        request=body['transition_request'];book=opening['opening']
        core.need(request['expected_state_sha256']==core.digest(book),'opening_state_mismatch')
        core.need(request['schemas'].get(book['memory_schema'])==opening['schemas'][book['memory_schema']], 'opening_schema_mismatch')
        proposal=engine.propose(book,request)
        if proposal['status']!='proposed':return {**result,'status':proposal['status'],'reason':'transition_refused','transition':proposal}
        report_request=reports.request(book,proposal['after'],request['schemas'],opening['report_mapping'],body['equity_movements'],body['notes'])
        report=reports.report(report_request)
        core.need(report['status']=='reported','continuation_report:'+report.get('reason',''))
        return {**result,'status':'conditional_continuation','transition':proposal,
                'report_request':report_request,'report':report,'current':deepcopy(proposal['after']),
                'scope':'Selected conditional history plus one declared synthetic method; no admitted execution'}
    except Exception as exc:return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}


def verify(body,result):
    try:return core.canonical(run(body))==core.canonical(result)
    except Exception:return False
