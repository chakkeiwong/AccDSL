from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;S=H.parent/'acquisition-revisions-20261027';R=H.parents[2]
assert not (H/'reference.py').exists()
assert json.loads((S/'discovery-probe-01/finding.json').read_text())['status']=='FAIL'
code=(S/'reference.py').read_text().replace('ConditionalAcquisitionRevisionView/1','ConditionalAcquisitionRevisionView/2')
old="if available is not None and h.moment(available)>cutoff:"
new="if discovered>cutoff:\n            return dict(**common,status='original_view',selected='original',reason='revision_not_yet_discovered',alternatives=alternatives[:1])\n        if available is not None and h.moment(available)>cutoff:"
assert old in code;code=code.replace(old,new);(H/'reference.py').write_text(code)
code=(S/'verify.py').read_text().replace("plan='docs/plans/accounting-acquisition-revisions-20261027.md'","plan='docs/plans/accounting-acquisition-revision-discovery-repair-20261027.md'")
needle="b=fixture();b['payload']['revision']['available_at']['manager']=None;run('unknown_availability',bind(b),'unresolved_views',None,reason='revision_availability_unknown')"
extra="""b=fixture(cutoff='2026-01-10T00:00:00Z');b['payload']['revision']['available_at']['manager']=None;run('unknown_before_discovery',bind(b),'original_view','original',reason='revision_not_yet_discovered')
        b=fixture(cutoff='2026-01-15T00:00:00Z');b['payload']['revision']['available_at']['manager']=None;run('unknown_at_discovery',bind(b),'unresolved_views',None,reason='revision_availability_unknown')
        b=fixture(cutoff='2026-01-10T00:00:00Z');run('known_before_discovery',b,'original_view','original',reason='revision_not_yet_discovered')
        b=fixture(cutoff='2026-01-10T00:00:00Z');b['payload']['revision']['available_at']['manager']=None;b['payload']['revision']['disposition']='later_event';run('later_event_before_discovery',bind(b),'original_view','original',reason='revision_not_yet_discovered')
        """+needle
assert needle in code;code=code.replace(needle,extra)
code=code.replace("files.update(R/p for p in json.loads((m.D/'attempt-01/source-lock.json').read_text()))","files.update(R/p for p in json.loads((m.D/'attempt-01/source-lock.json').read_text()))\n    files.update(R/p for p in json.loads((H/'predecessor-lock.json').read_text()))\n    files.add(H/'predecessor-lock.json');files.add(R/'docs/plans/accounting-acquisition-revision-discovery-repair-20261027.md')")
(H/'verify.py').write_text(code);(H/'contract.md').write_text((S/'contract.md').read_text().replace('views /1','views /2')+'\nDiscovery lower bound: before discovery, retain only original regardless of an unknown availability. At discovery and later, unknown availability may retain both. The /1 failure and its counterexample remain preserved.\n')
lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file() and 'inputs' not in p.parts and '__pycache__' not in p.parts}
(H/'predecessor-lock.json').write_text(json.dumps(lock,indent=2)+'\n');print('Prepared separate /2 discovery repair and predecessor lock.')
