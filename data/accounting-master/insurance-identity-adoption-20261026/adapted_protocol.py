"""Pinned native protocol: only the two pair-key expressions differ."""
from copy import deepcopy
from native import n, idx
Refusal=n.Refusal
FinanceRefusal=n.FinanceRefusal
need=n.need
enc=n.enc
OPS=n.OPS
ROLES=n.ROLES
invariant=n.invariant
unpack=n.unpack

class PairProtocol(n.Auditor):
    def request(self,rq,sub,world):
        r=self.body(rq);s=self.body(sub)
        need(s['request_ref']==rq and self.blob(s['wire_blob'])==enc(r),'wire_binding')
        need(r['profile_ref']==self.alias['profile'],'request_profile')
        identity=idx.pair_key(r['client_id'],r['request_id'])
        if identity in world['decisions']:
            prior=world['decisions'][identity]
            need(prior['request_ref']==rq,'identity_conflict')
            return dict(replay=prior)
        need(not r['require_current'] or r['view_ref']==world['current_view_ref'],'stale_view')
        need(r['expected_heads']==world['heads'],'stale_head')
        need(self.body(r['view_ref'])['context_ref']==r['context_ref'],'request_context')
        if r['operation']==OPS[0]:
            need(set(r['arguments'])=={'proposal_ref'},'operation_arguments');p=self.proposal(r['arguments']['proposal_ref']);b=self.body(p['basis_ref'])
            need(p['before_heads']==r['expected_heads'] and b['view_ref']==r['view_ref'] and b['context_ref']==r['context_ref'],'request_basis')
            return dict(output_ref=p['result_ref'],after_heads=p['after_heads'])
        need(r['operation']==OPS[1] and set(r['arguments'])=={'state_refs'},'operation_arguments')
        need(r['arguments']['state_refs']==r['expected_heads'],'report_heads')
        for h in r['expected_heads'].values():self.state(h)
        invariant(unpack(self.values(r['expected_heads'])))
        return dict(after_heads=r['expected_heads'])
    def exchange(self,e):
        rq,sub=e['request_ref'],e['submission_ref'];r=self.body(rq);res=self.body(e['response_ref']);before=e['world_before'];after=e['world_after']
        need(res['request_ref']==rq and res['submission_ref']==sub,'response_request_binding')
        try:answer=self.request(rq,sub,before)
        except (Refusal,FinanceRefusal) as error:
            need(res['disposition']=='rejected' and res['diagnostics']==[error.code],'wrong_rejection')
            need(res['output_ref'] is None and res['receipt_ref'] is None and res['published_digests']==[] and not res['additional_commit'],'rejection_payload')
            need(after==before,'rejection_mutated_world');return
        if 'replay' in answer:
            prior=self.body(answer['replay']['response_ref'])
            need(res['disposition']=='replayed' and not res['additional_commit'],'replay_disposition')
            need(all(res[k]==prior[k] for k in ('output_ref','receipt_ref','diagnostics','published_digests','request_ref','submission_ref')),'changed_replay_bytes')
            need(after==before,'duplicate_commit');return
        output=res['output_ref'];receipt=self.body(res['receipt_ref'])
        need(receipt['request_ref']==rq and receipt['output_ref']==output and receipt['before_heads']==before['heads'] and receipt['after_heads']==answer['after_heads'],'receipt_binding')
        need(receipt['written_roles']==[role for role in ROLES if before['heads'][role]!=answer['after_heads'][role]],'receipt_write_set')
        if r['operation']==OPS[0]:
            need(output==answer['output_ref'],'output_binding');result=self.body(output);codes=result['diagnostics'];status='unresolved_published' if codes else 'committed'
        else:
            report=self.body(output);need(output['kind']=='ComponentReport' and report['state_refs']==r['expected_heads'] and report['context_ref']==r['context_ref'],'report_binding');codes=[];status='report_published'
        need(receipt['status']==status and res['disposition']==('partial' if codes else 'completed') and res['diagnostics']==codes and res['additional_commit'],'result_status')
        need(res['published_digests']==self.closure([rq,sub,res['receipt_ref']]),'publication_dependencies')
        expected=deepcopy(before);expected['heads']=answer['after_heads'];expected['published_records']=sorted(set(before['published_records'])|set(self.closure([e['response_ref']])))
        if r['operation']==OPS[0] and self.body(output)['journal']:expected['journals'].append(dict(request_ref=rq,result_ref=output,lines=self.body(output)['journal']))
        identity=idx.pair_key(r['client_id'],r['request_id']);expected['decisions'][identity]=dict(request_ref=rq,response_ref=e['response_ref'],output_ref=output,receipt_ref=res['receipt_ref'])
        need(after==expected,'partial_publication')
