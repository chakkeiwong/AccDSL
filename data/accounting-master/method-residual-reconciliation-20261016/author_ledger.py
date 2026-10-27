"""Author a current disposition without changing any original operation promise."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / 'data/accounting-master'
CANDIDATE = ROOT / 'docs/design/proposal/manuscript-bank-poci-rollforward-20261016'
PLAN = ROOT / 'docs/plans/accounting-method-residual-reconciliation-20261016.md'

# These are authored judgments, not classifications inferred from file counts.
# Columns: id; evidence aliases; current bounded delivery; internal repair IDs; application dependencies.
ROWS = '''
P17-04.01;CP CR CC;Performance, gross billing, collection, advance allocation and successive contract changes;C1 C2;Contract eligibility, control, price and progress
P17-04.02;CP CC;Prepaid billing including state-only allocation and duplicate rejection;C2;Shared contract identities and opening balances
P17-04.03;CR CC;Actual return settlement, handling/NRV distinctions and group tax/cash join;C2;Return rights, stock condition and handling classification
P17-04.04;CR MIX;Distinct/integrated changes and one allocated mixed amendment, assurance/service distinction;C1;Enforceable allocations, faithful progress and warranty facts
P17-04.05;CP CC HI;Production cohorts, joint/byproducts, financing payables and inventory-sale/NRV joins;C2;Actual costing policy, yields, capacity, lots and NRV
P17-04.06;CP;Benefit changes, funding, ceiling/availability and multiemployer conditional methods;C2;Employee law/data, actuarial values and common-control allocations
P17-04.07;CP CB;Inspection/replacement/restoration and original/restated/current annual PPE/tax example;C2;Asset cohorts, prior information and recoverable values
P17-04.08;CR GC;Floor redistribution, capped reversal, corporate/NCI impairment and restoration methods;C1 S1;Recoverable values and provision facts; zero-weight CGU rule unresolved
P17-04.09;CR;Per-right lease reduction, repeated reduction, payment and depreciation;C2;Rights attribution, discount/calendar/variable-payment terms
P17-04.10;CR CT CB;Origin-specific deferred tax, compound-tax unwind and annual comparative reconstruction;C2;Actual rates, tax bases, recovery, offsets and applicable law
P17-04.11;CC CE CT HI;Shared two-entity close, gross cash, NCI, maturity conversion/redemption and tax-aware EPS;C2 J1;Complete openings, reporting periods and cash classifications
P17-04.12;GC CC;Reciprocal and inventory elimination, control/FX/restatement methods and a same-currency company join;J1;Control, functional currency, reciprocal identities and actual rates
P17-04.13;SRC;Historical source profiles distinguish ASC/ASBE access from EU/AU conditional methods;S2;Operative topic/issuer-class/edition admission
P17-05.01;FC CT;Debt basis, fees, EIR, due/unpaid states and compound cash/tax schedule;B1 C2;Actual agreements, dates, reset fixings and valuations
P17-05.02;FC;Inclusive ten-percent and qualitative findings, fee purposes, recalc/repurchase and unpaid claims;B1;Actual qualitative substantiality and legal remedies
P17-05.03;FC CE CT;Shares, treasury equity, compound issue/repurchase and original-term maturity conversion;F1 S1;Legal capital, actual rights/values; early-conversion measurement remains source-specific
P17-05.04;FC CE;Service/market conditions, cash choices, simple participation and ordered multiple-series/company EPS;F1;Senior/capped/dependent participation, actual conditions and valuation
P17-05.05;FC RH AH PH HI;Repeated item additions, acquired derivative origins, homogeneous partial discontinuation and inventory sale/NRV;F2 J1;Valuations, designation, effectiveness and recoverability findings
P17-05.06;GC CC;Acquisition/control, partial goodwill, impairment and group/foreign-operation bindings;J1;Business/control conclusions, purchase valuations and actual tax
P17-05.07;GC CC;Ownership without loss of control and foreign-operation full/retained disposals;J1;Dated ownership, rights, valuation and disposal consideration
P17-05.08;GC CC;Reciprocal allocations, inventory margin/tax elimination and later external sale release;J1;Matched legal books, control intervals and shared lots
P17-05.09;GC;Hyperinflation before translation, exchangeability purpose/date and transition origins;J1;Actual indices, currency/rate estimations and perimeter
P17-05.10;SRC;JPMorgan/Apple issuer and guarantee source inquiries preserve unresolved rights;S2;Actual agreements, succession, obligor identities, ranks and perimeter
P17-06.01;BC BA;Origination/deposit/transfer distinctions and restricted US bank book;B1 J1;Actual contract/currency/admission and compatible book joins
P17-06.02;BC PC;Ordinary credit/cure methods plus original-rate POCI subsequent-loss lifecycle;B1;Calibrated credit forecasts, class/POCI/write-off findings and actual terms
P17-06.03;BC;Full and partial/revolving draws retain original risk and provision/allowance origins;B1;Draw/cancellation dates, commitment horizons and eligibility
P17-06.04;BC;Modification/cure, collateral, fees, transfers and guarantee/option continuing involvement;B1;Rights/risks/control, servicing values and actual cash classification
P17-06.05;BC BA;Confirmed funding receipts, full/partial/pending withdrawal payments and funding interest;B1 J1;Facility access, collateral, venues, maturity and behavior
P17-06.06;BA;Restricted US eligibility, allowance cap/excess and separate leverage denominator;S2 J1;Operative-date chain, actual regulatory perimeter, eligibility and payout facts
P17-06.07;BA VAL;Joint-law, cutoff, survival and unweighted-family queries plus future validation protocol;V1;Calibration, decision objectives and future authorized empirical evidence
P17-07.01;IC IA;GMM future-service CSM/loss order, finite service/finance and groupwise opening;I1 J1;Actual FCF/RA, coverage units and finance policy
P17-07.02;IC IA;Closed group membership, separate openings and adverse pooling;J1;Actual insurer portfolio, cohort and profitability membership
P17-07.03;IC IA;Covered quota changes, timing/recovery and conditional nonlinear stop-loss query;I1 I2;Actual treaty terms, collectability and calibrated joint distribution
P17-07.04;IC IA;Acquisition cost allocation, impairment/reversal, group transfer and route assessment;I2 J1;Actual asset recoverability, allocated costs and expense reconciliation
P17-07.05;IC IG;Priced finite guarantee, VFA pool/fee/service and mitigation distinction;I1 J1 V1;Actual underlying model, risk adjustment, eligibility and dependence
P17-07.06;IA;Transition dates, route/impracticability and supplied groupwise opening/recovery;I2;Complete histories and supported transition valuation inputs
P17-07.07;IA VAL;Conditional/process/backward-law distinctions, reserve center, dependence and future comparator design;V1 L1;Actual triangles/tails, calibration and independent downstream evaluation
P17-07.08;IC IA;Closed accounting/query profiles, atomic publication/replay and both lost-acknowledgement worlds;J1 R8;Actual durable runtime and compatible migrations remain held
P17-08.01;CORE CC;Finite construction/search, witnesses and joint company conditional outputs;V1 R8;General implementation correctness requires later conformance
P17-08.02;CORE;Empty-family, unknown, mixed and certainty semantics remain explicit;V1 R8;Broader solver behavior is unexecuted
P17-08.03;CORE;Exact/rounded/integer projections, strict endpoints and rational enclosures;B1 R8;Numerical policies must be explicit; no implicit cent grid
P17-08.04;CORE;Query-specific grouping/state distinctions and changed-query refusal;J1 R8;Wider transition equivalence needs proof or checked conformance
P17-08.05;CB CORE;Original/revised clocks and annual comparative/earliest-opening reconstruction;C2 R8;Actual publication precision, report vintages and wider transition facts
P17-08.06;BA IA CORE;Joint-law attachment, unresolved mass, conditional/interventional and partial results;V1;Identifiable calibrated laws and causal assumptions are not inferred
P17-08.07;CC GC;Contexts/partitions, state-only allocations and explicit finite subset migration;J1 R6;General adapter field preservation and cross-profile admission
P17-08.08;VAL;Frozen future target/vintage/comparator/budget-ladder/veto design for six tasks;V1 L1;Target-specific tuning/sample budgets require development evidence before empirical promotion
'''

EVIDENCE = {
 'CP':'extended-method-exchanges-20261015/corporate-v5/result.md',
 'CR':'extended-method-exchanges-20261015/corporate-residuals/semantic-contract.md',
 'CC':'company-composition-20261016/result.md', 'CE':'company-eps-join-20261016/result.md',
 'CT':'compound-tax-rollforward-20261016/result.md', 'CB':'comparative-rebuild-20261016/result.md',
 'FC':'extended-method-exchanges-20261015/financing-v2/semantic-contract.md',
 'BC':'extended-method-exchanges-20261015/bank-v2/semantic-contract.md',
 'BA':'extended-method-exchanges-20261015/bank-assessment/semantic-contract.md',
 'GC':'extended-method-exchanges-20261015/group/semantic-contract.md',
 'IC':'extended-method-exchanges-20261015/insurance/semantic-contract.md',
 'IA':'extended-method-exchanges-20261015/insurance-assessment/semantic-contract.md',
 'IG':'finite-method-decisions-20261015/insurance/result.md',
 'PC':'bank-poci-rollforward-20261016/result.md',
 'RH':'repeated-rebalancing-20261016/result.md', 'AH':'added-instruments-20261016/result.md',
 'PH':'partial-hedge-discontinuation-20261016/result.md', 'HI':'hedge-inventory-subsequent-20261016/result.md',
 'SRC':'candidate-reconciliation-20261016/result.md',
 'CORE':'p17-completion-20261014/P17-08/operation-matrix.md',
 'VAL':'future-validation-20261015/result.md',
 'MIX':'finite-method-decisions-20261015/corporate/residual-disposition.md',
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    started=time.monotonic()
    target=OUT/'residual-ledger.json'
    assert not target.exists()
    original_path=BASE/'extended-method-exchanges-20261015/coverage.json'
    original=json.loads(original_path.read_text())
    original_by_id={r['id']:r for r in original['rows']}
    rows=[];checks=[];sources={original_path,PLAN,Path(__file__).resolve()}
    ms_path=BASE/'bank-poci-rollforward-20261016/manuscript-checks.json'
    ms=json.loads(ms_path.read_text());sources.add(ms_path)
    assert ms['version']=='3.25' and ms['failures']==0
    pdf=ROOT/ms['pdf'];assert sha(pdf)==ms['pdf_sha256'];sources.add(pdf)
    for line in ROWS.strip().splitlines():
        id,aliases,delivered,repair_ids,dependencies=line.split(';',4)
        old=original_by_id[id];matrix=ROOT/old['matrix'];sources.add(matrix)
        assert old['original_row'] in matrix.read_text().splitlines()
        evidence=[]
        for alias in aliases.split():
            p=BASE/EVIDENCE[alias];assert p.is_file(),p;sources.add(p)
            evidence.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),role='located prior scoped evidence; no fresh re-execution'))
        rows.append(dict(id=id,operation=old['operation'],original_row=old['original_row'],matrix=old['matrix'],
            delivered_within_scope=delivered,evidence=evidence,remaining_internal_units=repair_ids.split(),
            application_dependencies=dependencies,full_requirement_closed=False,
            interpretation='Methods, closed exchanges, source applicability, actual facts and held runtime remain separate.'))
        checks.append(dict(name=id,passed=rows[-1]['original_row']==old['original_row']))
    assert len(rows)==46 and set(r['id'] for r in rows)==set(original_by_id)
    checks.append(dict(name='all-original-46-once',passed=len({r['id'] for r in rows})==46))
    evidence_paths={e['path'] for r in rows for e in r['evidence']}
    for p in sorted(evidence_paths):checks.append(dict(name=p,passed=(ROOT/p).is_file()))
    ledger=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),candidate_version='3.25',candidate_pdf=ms['pdf'],
        candidate_pdf_sha256=ms['pdf_sha256'],baseline=str(original_path.relative_to(ROOT)),baseline_sha256=sha(original_path),
        scope='All46 original operation rows; authored documentary disposition, not accounting or runtime acceptance.',
        counts=dict(Counter(r['id'].split('.')[0] for r in rows)),rows=rows,readiness='not_ready')
    target.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n')
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sorted(sources)]),indent=2)+'\n')
    table=['# All46 original operations after Version3.25','','Original wording and hashes are preserved in `residual-ledger.json`. A finite','case does not close a whole row. Repair IDs refer to `repair-queue.md`.','', '| Row | Located delivery | Remaining internal work | Application dependencies |','|---|---|---|---|']
    for r in rows:table.append('| '+' | '.join([r['id']+' '+r['operation'],r['delivered_within_scope'],', '.join(r['remaining_internal_units']),r['application_dependencies']])+' |')
    (OUT/'residual-ledger.md').write_text('\n'.join(table)+'\n')
    (OUT/'checks.json').write_text(json.dumps(dict(checks=len(checks),failures=0,detail=checks,meaning='Row/pointer preservation only; substantive judgments are authored.'),indent=2)+'\n')
    manifest=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/method-residual-reconciliation-20261016/author_ledger.py',
        environment=sys.executable+'; standard library; no ML import',gpu_status='intentionally hidden with CUDA_VISIBLE_DEVICES=-1',
        data_version='Original46 operation rows and Version3.25',random_seeds='N/A deterministic documentary audit',
        wall_seconds=round(time.monotonic()-started,3),plan=str(PLAN.relative_to(ROOT)),result=str((OUT/'result.md').relative_to(ROOT)),
        output_paths=[str((OUT/n).relative_to(ROOT)) for n in ('residual-ledger.json','residual-ledger.md','input-lock.json','checks.json')])
    (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(rows=len(rows),by_matrix=ledger['counts'],checks=len(checks),failures=0)))

if __name__=='__main__':main()
