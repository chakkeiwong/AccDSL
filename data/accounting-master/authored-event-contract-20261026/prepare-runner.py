from pathlib import Path
HERE=Path(__file__).resolve().parent;target=HERE/'contract_runner.py';assert not target.exists()
text=(HERE.parent/'authored-state-invariants-20261026/guarded_runner.py').read_text()
text=text.replace("HERE.parent/'authored-method-registry-20261026'","HERE.parent/'authored-method-registry-20261026'")
text=text.replace('import guards','sys.path.insert(0,str(HERE.parent/\'authored-state-invariants-20261026\'))'+chr(10)+'import guards'+chr(10)+'import contract')
text=text.replace("PROFILE='GuardedAuthoredCompanyProgram/1'","PROFILE='ContractedAuthoredCompanyProgram/1'")
text=text.replace("'state_invariant','expected_invariant_sha256']","'state_invariant','expected_invariant_sha256','event_contract','expected_event_contract_sha256']")
text=text.replace("def guard(body,book,stage):", "def guard(body,book,stage):"+chr(10)+"    contract.control(body,book)")
text=text.replace("try:validate(body);guard(body,body['opening'],'opening')",
    "try:validate(body);contract.validate(body);guard(body,body['opening'],'opening')")
text=text.replace('request=None;result=None','request=None;result=None;event_evidence=None')
text=text.replace("typed.typed_book(current,body['memory_definition'],body['schemas']);guard(body,current,'before')",
    "typed.typed_book(current,body['memory_definition'],body['schemas']);guard(body,current,'before')"+chr(10)+
    "            event_evidence=contract.before(body,current,command)")
text=text.replace("'opening_before_sha256':digest(opening),'opening_after_sha256':digest(next_opening)}",
    "'opening_before_sha256':digest(opening),'opening_after_sha256':digest(next_opening),'event_contract':event_evidence}")
text=text.replace("'status':'invalid','reason':str(exc)[:300],'before_sha256':digest(current)",
    "'status':exc.status if isinstance(exc,contract.ContractFailure) else 'invalid','reason':str(exc)[:300],'before_sha256':digest(current)")
text=text.replace("'request':request,'result':result,**", "'request':request,'result':result,'event_contract':event_evidence,**")
target.write_text(text);print('Prepared explicit full-intent contract runner')
