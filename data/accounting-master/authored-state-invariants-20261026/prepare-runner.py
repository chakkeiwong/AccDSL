"""Derive only explicit guard insertion points; keep native runner preserved."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;source=HERE.parent/'authored-program-composition-20261026/runner.py'
target=HERE/'guarded_runner.py';assert not target.exists()
text=source.read_text()
text=text.replace('import registry as methods','import registry as methods'+chr(10)+'import guards')
text=text.replace("PROFILE='AuthoredCompanyProgram/1'","PROFILE='GuardedAuthoredCompanyProgram/1'")
text=text.replace("'memory_definition','registries','commands']","'memory_definition','registries','commands','state_invariant','expected_invariant_sha256']")
text=text.replace("core.need(body['profile']==PROFILE,'program_profile');base.text(body['name'],'program_name')",
    "core.need(body['profile']==PROFILE,'program_profile');base.text(body['name'],'program_name')"+chr(10)+
    "    guards.validate(body['state_invariant']);core.need(digest(body['state_invariant'])==body['expected_invariant_sha256'],'invariant_digest')")
marker='def invalid(exc):'
insert='''class InvariantFailure(ValueError):
    def __init__(self,stage,assessment):
        self.stage=stage;self.assessment=assessment
        super().__init__('state_invariant:'+stage+':'+assessment['status'])

def guard(body,book,stage):
    assessment=guards.assess(body['state_invariant'],book,body['memory_definition'],body['schemas'])
    if assessment['status']!='collection_total_requirements_satisfied':raise InvariantFailure(stage,assessment)
    return assessment

'''
assert text.count(marker)==1;text=text.replace(marker,insert+marker)
text=text.replace('try:validate(body)',"try:validate(body);guard(body,body['opening'],'opening')")
text=text.replace('except Exception as exc:return invalid(exc)',
    "except Exception as exc:return {**invalid(exc),**({'invariant':exc.assessment,'stage':exc.stage} if isinstance(exc,InvariantFailure) else {})}")
text=text.replace("typed.typed_book(current,body['memory_definition'],body['schemas'])",
    "typed.typed_book(current,body['memory_definition'],body['schemas']);guard(body,current,'before')")
text=text.replace("if success:typed.typed_book(after,body['memory_definition'],body['schemas'])",
    "if success:typed.typed_book(after,body['memory_definition'],body['schemas']);guard(body,after,'after')")
old="'request':request,'result':result};break"
new="'request':request,'result':result,**({'invariant':exc.assessment,'stage':exc.stage} if isinstance(exc,InvariantFailure) else {})};break"
assert old in text;text=text.replace(old,new)
target.write_text(text)
print('Prepared explicit guarded successor')
