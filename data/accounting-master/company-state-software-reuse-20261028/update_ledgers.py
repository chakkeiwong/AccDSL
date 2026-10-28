"""Add current software comparison to six survey ledgers without replacing history."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'docs/design/research/company-state-program-20261028'
NOTE=str((D/'software-and-company-state.md').relative_to(ROOT))
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def read(p):return json.loads(p.read_text())
def relative(p):return str(p.relative_to(ROOT))
assert read(H/'attempt-01/verification.json')['status']=='pass'
source_hashes=read(H/'attempt-01/run-manifest.json')['source_hashes']
assert all(sha256((ROOT/p).read_bytes()).hexdigest()==v for p,v in source_hashes.items())
files=['source-support.json','citation-venue.json','backward-snowball.json','forward-snowball.json','claim-support.json','omitted-paper-risk.json','search-log.json']
old={name:read(D/name) for name in files};new=deepcopy(old)
with (H/'ledgers-before.json').open('x') as stream:json.dump(old,stream,indent=2)
A='docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/arelle/'
software=[
 dict(id='SW-ARELLE-01F6A465',title='Arelle selected fact/value/duplicate code',path=A+'arelle__ModelInstanceObject.py',version='Commit01f6a4656c2c6551d2f05f31c9d74366d133ee7e; retained05October source record',reading_status='ModelInstanceObject179–235/465–579 and ValidateDuplicateFacts34–284; static targeted method reading',allowed_claims='Distinguish structural duplicate grouping, numeric consistency and destructive selection of representatives; preserve every source occurrence',forbidden_claims='Full XBRL validation or runtime importer success; selected subset retains all provenance by itself',official_code='Commit-linked primary source; seven inherited source hashes verify'),
 dict(id='SW-QUANTLIB-COUPON-SNAPSHOT',title='QuantLib retained FloatingRateCoupon implementation',path='docs/design/research/software/lballabio_QuantLib-ql_cashflows_floatingratecoupon.cpp',version='02October exact content snapshot; matched commit/dependency build not established',reading_status='Entire107-line implementation, including constructor, fixing date, pricing dependency, accrued amount, discounting and index fixing',allowed_claims='Describe saved code defaults and explicit calendar/pricer dependencies',forbidden_claims='Latest release behaviour, matched runtime equivalence, simple-rate formula for every pricer, accounting admission',official_code='Primary repository source archived by tools.json; only byte identity established here'),
 dict(id='SW-ACTUS-SERVICE-TREE7293',title='ACTUS retained service observer and event exchange',path='docs/design/research/software/actus-interface-20261023/EventController.java',version='Tree7293157a7f272925dbce68b5a037d2e23c585c9e; four exact Git blobs; core version correspondence open',reading_status='Controller31–44/97–139, TimeSeries26–46/109–119, Event6–28; prior full specification/PAM audit reused',allowed_claims='Describe explicit horizon fallback, carry-forward observer and compact floating-point event exchange; identify adapter obligations',forbidden_claims='ACTUS core execution, complete calendar correspondence, actual future information admission or current core unavailability',official_code='Four local bodies match Git blob identities and retained service tree'),
 dict(id='SW-Z3-LOCAL-RATIONAL-WRAPPER',title='AccDSL finite rational wrapper over installed Z3',path='scripts/rational_solver_v1.py',version='Exact local hash; installed Z34.16.0 / z3-solver4.16.0.0 observed, not new environment lock',reading_status='Affine restrictions90–140; result/finite domain/budget/solver handling202–319; exact original persistent-family cases inspected',allowed_claims='Describe local executed finite support, partial-search and unsupported-fragment semantics',forbidden_claims='Solver finds omitted economic premises, all-contract reconstruction completeness, unbounded fragment support or default performance superiority',official_code='Local wrapper plus retained upstream README/build/license; full upstream implementation audit not claimed')]
for row in software:
 assert row['id'] not in {r['id'] for r in new['source-support.json']['sources']}
 row.update(sha256=sha256((ROOT/row['path']).read_bytes()).hexdigest(),classification='SOFTWARE',continuation_note=NOTE,publication_integrity='Historical software source record, not an academic correction/retraction assessment',runtime_evidence='Local wrapper exercised' if row['id'].startswith('SW-Z3') else 'Static source inspection only')
 new['source-support.json']['sources'].append(row)
 new['citation-venue.json']['rows'].append(dict(id=row['id'],citation_count=None,citation_source='N/A software-source comparison; no academic citation ranking',access_date='2026-10-28',venue=None,venue_metric=None,venue_metric_source='N/A',note='Source version and code reading scope recorded separately; no new web retrieval'))
claims=[
 ('SW-ARELLE-STRUCTURE','SW-ARELLE-01F6A465','Concept/context/unit grouping and item duplicate checks do not compare item values.','ModelInstanceObject179–235/528–579','Use for candidate grouping only; separate value and occurrence decisions.'),
 ('SW-ARELLE-CONSISTENCY','SW-ARELLE-01F6A465','Complete duplicate sets require equal decimals and values; numeric consistency uses explicit rounding-range rules.','ValidateDuplicateFacts34–191','Pinned source semantics; no whole-validation or runtime claim.'),
 ('SW-ARELLE-PROVENANCE','SW-ARELLE-01F6A465','Deduplication methods select representative subsets, so full occurrence provenance must be preserved separately.','ValidateDuplicateFacts193–275','Local preservation consequence; not a defect allegation about selecting representatives.'),
 ('SW-QL-FIXING','SW-QUANTLIB-COUPON-SNAPSHOT','Fixing date uses accrual start or end and index calendar/lag/convention; index supplies missing lag/day counter.','floatingratecoupon.cpp33–89','Historical content snapshot; matched runtime version remains open.'),
 ('SW-QL-PRICER','SW-QUANTLIB-COUPON-SNAPSHOT','Coupon rate requires a pricer and delegates swapletRate; simple reference-plus-spread for every pricer is unsupported.','floatingratecoupon.cpp91–105','Pricer/index implementation and same-version test still required.'),
 ('SW-ACTUS-HORIZON','SW-ACTUS-SERVICE-TREE7293','Controller falls back to LocalDateTime.now plus five years when no named end date is supplied.','EventController119–139','AccDSL needs explicit horizon; no current-service behaviour claim.'),
 ('SW-ACTUS-OBSERVER','SW-ACTUS-SERVICE-TREE7293','Observer uses base normalization and last-at-or-before lookup; equal map timestamps replace prior entries.','EventController31–44/97–115;TimeSeries26–46/109–119','Source lineage, availability, empty series and base-zero checks remain adapter work.'),
 ('SW-ACTUS-OUTPUT','SW-ACTUS-SERVICE-TREE7293','Event exchange has type/time/currency and double payoff/state fields, with no AccDSL source or journal fields.','Event.java6–28','Proposed contract effects only; source/accounting and numeric policy separate.'),
 ('SW-Z3-TARGET','SW-Z3-LOCAL-RATIONAL-WRAPPER','Persistent equality excludes mixed paths; removing it changes feasible support while annual marginal ranges remain unchanged.','rational_solver_v1.py202–319;company-state-persistent-rate-failures-20261028/attempt-01','Exact local comparison does not establish correctness of missing source constraints.')]
for ident,src,claim,anchor,limits in claims:
 new['claim-support.json']['rows'].append(dict(id=ident,source_id=src,claim=claim,anchor=anchor,limits=limits,support_class='IMPLEMENTATION_EVIDENCE'))
gaps=[
 ('SW-ARELLE-01F6A465','Version-matched duplicate/rounding and Session runtime dependencies','Import supplied contexts/units and preserve all original occurrence IDs while exposing selected representatives','T03/S09'),
 ('SW-QUANTLIB-COUPON-SNAPSHOT','Matched source commit, index/calendar/pricer definitions and official tests','Compare fixed, reset, fixing-lag, arrears, missing-pricer and explicit evaluation-date cases under a resolved environment','S09/T07'),
 ('SW-ACTUS-SERVICE-TREE7293','Matched core1.1.0/spec/dictionary/calendar/event-order implementation','Run supplied same-date/zero-rate/missing-observer/reset cases only after source correspondence; existing PAM arithmetic is not that run','S09/T07'),
 ('SW-Z3-LOCAL-RATIONAL-WRAPPER','Exact resolver/distribution provenance and original solver architecture sources','Keep wrapper support/Unknown checks; inspect independent encoding coverage and installation record for recipient reproducibility','S09/R05')]
for seed,candidate,action,task in gaps:
 new['backward-snowball.json']['rows'].append(dict(seed=seed,candidate=candidate,anchor='Inspected imports/calls and source metadata',classification='SOFTWARE',action=action,status='consequential_dependency_open'))
 new['forward-snowball.json']['rows'].append(dict(seed=seed,title='Version-linked successor and correction/change comparison',source_file=NOTE,classification='SOFTWARE',screening_level='No new forward repository/release search in this local pass',disposition='Check exact version changes after matched source is available; no current-release equivalence or no-correction claim'))
 new['omitted-paper-risk.json']['rows'].append(dict(id='OR-'+seed,candidate=candidate,reason='Missing matched source or runtime dependency limits the intended component claim',disposition=action,task=task,acceptable_for_final_survey=False))
new['search-log.json']['rows'].append(dict(date='2026-10-28',task='S09',queries=['Retained software/source registers for Arelle/QuantLib/ACTUS/Z3','Exact ModelInstanceObject byte comparison against05October commit record','ACTUS four Git blobs and service tree','Current source-context/gross-history/persistent-rate results'],outcome='40 source-integrity checks pass; four connected source-code comparisons, no new web retrieval or external runtime',evidence=relative(H/'attempt-01/verification.json')))
for name,data in new.items():
 key='sources' if name=='source-support.json' else 'rows'
 assert data[key][:len(old[name][key])]==old[name][key]
 dump(D/name,data)
summary={name:dict(before=len(old[name]['sources' if name=='source-support.json' else 'rows']),after=len(new[name]['sources' if name=='source-support.json' else 'rows'])) for name in files}
dump(H/'ledger-update.json',dict(status='pass',existing_rows_unchanged=True,summary=summary))
print(json.dumps(dict(status='pass',source_records=4,claims=9,all_six_ledgers_updated=True,existing_rows_preserved=True)))

