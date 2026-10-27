"""Adapt the existing protected integration checks to the next named section."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;old=HERE.parent/'nested-invariant-integration-20261026/integrate.py'
target=HERE/'integrate.py';assert not target.exists()
text=old.read_text()
text=text.replace('Version 5.13','Version 5.14').replace('bounded nested semantic design','selected term-state and event design')
text=text.replace('manuscript-invariant-unicode-v513-20261026','manuscript-nested-invariants-v514-20261026')
text=text.replace("TARGET=ROOT/'docs/design/proposal/manuscript-nested-invariants-v514-20261026'", "TARGET=ROOT/'docs/design/proposal/manuscript-term-execution-v515-20261026'")
text=text.replace('d3284ce5c52a6c0b4abebb9bb35f758f1dea7e11a1212b8d8784185f4b3002e7','233f22f891ae2d0ded9c3aa7ef046b8f70c5f5cb6a8d9b3cd43c2a64b1424839')
text=text.replace("NEW='sections/nested-term-invariants.tex'","NEW='sections/selected-term-execution.tex'")
start=text.index('def expected(');end=text.index('def prepare():',start)
new="""def expected(name,text):
    if name=='accounting-product-proposal.tex':
        old='Version 5.14 (proposal candidate)';assert text.count(old)==1
        return text.replace(old,'Version 5.15 (proposal candidate)')
    if name=='sections/common-program-authoring.tex':
        old=BS+'input{sections/nested-term-invariants}';assert text.count(old)==1
        return text.replace(old,old+chr(10)+chr(10)+BS+'input{sections/selected-term-execution}')
    if name=='chapters/06-language.tex':
        old='Those checks preserve the separate need for structural admission and do not'+chr(10)+'yet replace the complete native opening or execution contract.'
        assert text.count(old)==1
        return text.replace(old,'Section~'+BS+'ref{sec:selected-term-execution} binds them to an explicit selected'+chr(10)+'state contract and direct source for prospective amendments, assessments,'+chr(10)+'collections and carry. This bounded synthetic continuation preserves the'+chr(10)+'separate requirements for actual-source and accounting admission.')
    if name=='sections/nested-term-invariants.tex':
        old='This difference identifies the remaining boundary rather than an alternative'+chr(10)+'''form of opening admission. Exact native structural schemas, role and cost
selection, and migration premises still need their own selected contract.
The bundle grants no execution or accounting admission and is not yet bound
into the opening-to-program execution path. Direct source authoring for these
nested profiles also remains to be supplied.'''
        assert text.count(old)==1
        return text.replace(old,'This difference identifies a separate structural condition rather than an'+chr(10)+'''alternative form of opening admission. The semantic bundle by itself grants
no execution or accounting admission. Section~'''+BS+'''ref{sec:selected-term-execution}
supplies the selected structural contract, direct nested source and bounded
event/carry composition while retaining actual-source and accounting limits.''')
    return text
"""
text=text[:start]+new+text[end:]
text=text.replace('assert len(sources)==234','assert len(sources)==235')
start=text.index('    units=');end=text.index('    for name in sources:',start)
new='''    units={
      'term-structural-admission-20261026':('',61,681),
      'nested-contract-source-20261026':('attempt-01',16,4573),
      'nested-assessment-construction-20261026':('attempt-02',14,381),
      'term-event-carry-binding-20261026':('attempt-01',12,439),
      'term-full-event-binding-20261026':('attempt-01',19,548),
      'term-event-source-20261026':('attempt-01',9,1018)}
    evidence={}
    for unit_name,(attempt,controls,assertions) in units.items():
        unit=HERE.parent/unit_name;data=unit/attempt;checks=read(data/'checks.json')
        assert checks['passed'] and checks.get('controls',checks.get('source_controls'))==controls and checks['assertions']==assertions
        for n,h in read(data/'source-lock.json').items():
            assert sha(ROOT/n)==h,n
            if n in evidence:assert evidence[n]==h,n
            evidence[n]=h
        for path in list(unit.iterdir())+list(data.iterdir()):
            if path.is_file():evidence[str(path.relative_to(ROOT))]=sha(path)
    assert read(HERE.parent/'term-full-event-binding-20261026/date-boundary.json')['passed']
'''
text=text[:start]+new+text[end:]
text=text.replace("HERE/'nested-term-invariants.tex'","HERE/'selected-term-execution.tex'")
text=text.replace("HERE.parent/'invariant-unicode-rebased-20261026/control-input-hashes.json'","HERE.parent/'nested-invariant-integration-20261026/control-input-hashes.json'")
text=text.replace("candidate='5.14'","candidate='5.15'")
text=text.replace("assert 'Version 5.14' in doc[0].get_text()","assert 'Version 5.15' in doc[0].get_text()")
text=text.replace("if 'A claim can remain outstanding while its due date changes.' in s","if 'Carry the historical terms through a complete command' in s")
text=text.replace("if 'term-semantic-composition-20261026/' in s","if 'term-event-source-20261026/' in s")
text=text.replace("version='5.14'","version='5.15'")
target.write_text(text)
print('Created integrate.py; no build or advancement yet')
