"""Retain first failed build; remove bibliography/prose duplicated in baseline."""
from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2]
out=H/'repair-before';out.mkdir(exist_ok=False)
for n in ['integrate.py','funding-control-authority.tex','authority.bib','source-preservation.json','reader-plan.md']:
 (out/n).write_bytes((H/n).read_bytes())
lock=json.loads((H/'source-preservation.json').read_text());target=R/lock['target'];source=R/lock['source']
for n,x in lock['sources'].items():assert sha256((source/n).read_bytes()).hexdigest()==x,n
p=H/'funding-control-authority.tex';text=p.read_text()
start=text.index('Conversion also changes the possible reporting relationship.')
end=text.index('\\section{Evidence over an interval is stronger than two snapshots}')
replacement=r'''The resulting holder interest also raises a reporting-perimeter question.
Section~\ref{sim:conversion-control-scope} follows the separate-statement,
consolidation and business-acquisition alternatives, including the possibility
of control before legal conversion. Its repaired dependency analysis preserves
uncertain control histories rather than choosing whichever journal balances.
The retained source compilations do not yet establish the complete accounting
authority for the fixture's 2027 issue and 2028 conversion. Classification,
measurement, control history and applicable edition therefore remain linked
questions with distinct evidence requirements.

'''
text=text[:start]+replacement+text[end:]
text=text.replace('Issuer, holder and group answer different accounting questions','Issuer and holder classify the same contract differently')
p.write_text(text)
bib=(H/'authority.bib').read_text();bib=bib[:bib.index('@misc{aasb10scope2026,')]
(H/'authority.bib').write_text(bib)
# The main chapter needs only links to the genuinely new funding/interval
# material; the earlier candidate already teaches the group/control question.
script=(H/'integrate.py').read_text().replace('sim:conversion-control-history','sim:conversion-control-scope')
(H/'integrate.py').write_text(script)
import importlib.util
spec=importlib.util.spec_from_file_location('integration_repair',H/'integrate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for n in lock['named_edits']:(target/n).write_text(m.transform(n,(source/n).read_text(),lock['base'],lock['version']))
(target/'simulation/funding-control-authority.tex').write_bytes(p.read_bytes())
lock['added']['simulation/funding-control-authority.tex']=sha256(p.read_bytes()).hexdigest()
lock['repair']='First build failed on duplicate bibliography entries already present in 5.24. Preserve baseline control-scope exposition and add only missing funding, issuer/holder and interval evidence.'
(H/'source-preservation.json').write_text(json.dumps(lock,indent=2)+chr(10))
(H/'repair.md').write_text('The first build and all before-repair inputs are retained. BibTeX found two keys already present in the protected5.24 bibliography. Inspection showed that simulation/conversion-scope.tex already integrates source/control and the /2 boundary repair. Remove repeated exposition from the new addition, reference the retained section, and add only missing funding/measurement, issuer/holder and whole-interval evidence. This is a narrower reader-facing integration, approximately4–6 pages. No protected predecessor text or evidence changed. Rebuild both PDFs in build-attempt-02; do not rerun preparation or evidence writers.'+chr(10))
print(json.dumps({'repair':'PASS','target':lock['target'],'new_words':len(text.split())}))
