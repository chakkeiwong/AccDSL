"""Locate all original obligations without modifying historical judgments."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=json.loads((OUT/'baseline.json').read_text())
P='docs/design/proposal/'
M=P+'manuscript-production-cost-20261015/'
D='data/accounting-master/p17-completion-20261014/'
S={
 'profile':P+'architecture/initial-profile-v1.md',
 'evidence':P+'architecture/evidence-contract-v3.md',
 'time':P+'architecture/time-contract-v2.md',
 'history':P+'architecture/history-families-contract-v1.md',
 'language':P+'architecture/language-ir-contract-v1.md',
 'interface':P+'architecture/interfaces-contract-v1.md',
 'persistence':P+'architecture/persistence-contract-v1.md',
 'failure':P+'architecture/failure-contract-v1.md',
 'ix':P+'architecture/platform-contract-examples-v1.json',
 'portable':M+'sections/portable-values.tex',
 'operations':M+'sections/operations-storage.tex',
 'registry':M+'chapters/17-portable-reference.tex',
 'northstar':M+'chapters/13-reference-company.tex',
 'northstar_fixture':'docs/design/fixtures/northstar.json',
 'apple':D+'P17-02/result.md',
 'apple_map':D+'P17-02/connected-package-map.json',
 'conflict':D+'P17-03/result.md',
 'source_admission':M+'sections/source-admission.tex',
 'corporate':P+'methods/corporate-methods-v1.md',
 'corp_extensions':P+'methods/corporate-extensions-v1.md',
 'production':D+'P17-04/production-cost/result.md',
 'estimate':D+'P17-04/error-estimate/result.md',
 'finance':P+'methods/financing-methods-v1.md',
 'finance_matrix':D+'P17-05/operation-matrix.md',
 'eps':D+'P17-05/eps-lifecycle/result.md',
 'group':D+'P17-05/group-fx-disposal/result.md',
 'bank':D+'P17-06/prudential-connection/result.md',
 'bank_draw':D+'P17-06/commitment-draw/result.md',
 'bank_matrix':D+'P17-06/operation-matrix.md',
 'insurance':D+'P17-07/connected-groups/result.md',
 'insurance_matrix':D+'P17-07/operation-matrix.md',
 'atomic':D+'P17-10/insurance-atomic/result.md',
 'atomic_schema':D+'P17-10/insurance-atomic/record-schemas.json',
 'state_only':D+'P17-10/state-only/result.md',
 'revision':P+'architecture/sector-evidence-revision-20261014.md',
 'revision_result':D+'P17-08/sector-revision/result.md',
 'query':P+'architecture/query-resolution-supplement-20261014.md',
 'forecast':P+'methods/forecasting-methods-v1.md',
 'standards':P+'methods/standards-methods-v1.md',
 'standards_map':P+'methods/standards-mapping-v1.md',
 'method':P+'methods/method-boundary-v1.md',
 'literature':P+'methods/literature-methods-v1.md',
 'sql':'data/accounting-master/accounting-sql-three-valued-logic-20261013/result.md',
 'bootstrap':D+'P17-09/bootstrap-consistency/result.md',
 'reserving':D+'P17-10/reserving-adapter/result.md',
 'reuse':P+'methods/software-reuse-methods-v1.md',
 'validation':M+'chapters/10-validation.tex',
 'research':M+'chapters/12-research.tex',
 'p19':'docs/plans/accounting-p19-completion-20261014.md',
 'p18':'docs/plans/accounting-p18-completion-20261014.md',
 'master':'docs/plans/accounting-master-current.md',
 'mc35':'docs/design/review/internal-before-expert.md',
}
# ID | judgment | evidence | delivered | residual | residual categories | queue
DATA='''
MC01|scoped_evidence|apple apple_map|All retained package/reference/note populations have specific dispositions.|Connect material unresolved units to one case result; recursive bodies and semantics remain incomplete.|design source actual_fact|R02
MC02|specified_scoped|language portable query apple|Exact values, contextual compatibility and invalid scale/sign examples exist.|Complete corporate wire fields and linked context examples.|design runtime|R01
MC03|scoped_evidence|evidence apple apple_map|Narrative qualifications and unformalized text survive conditional translation.|Trace material narrative obligations to affected family/query membership without invented thresholds.|design source actual_fact|R02
MC04|specified_scoped|conflict source_admission evidence revision|Actual navigation contradiction, extraction distinction and review consequences are delivered.|Complete portable review bindings; obtain independent acceptance. A monetary conflict is not an extra requirement.|design runtime review|R01 R08
MC05|specified_scoped|time apple revision estimate|Original/latest/harmonized views and retrospective/prospective distinctions are explicit.|Complete corporate original/corrected exchanges; real historical byte availability remains unknown.|design actual_fact runtime|R01 R02
MC06|specified_scoped|group finance_matrix|Acquisition, NCI, eliminations, translation and disposal connect to the same statements.|Bind group sequence to shared fields/adverse behavior; actual control/valuation remains conditional.|design actual_fact review|R03
MC07|specified_scoped|language ix apple query|Mappings and disjoint/exhaustive partitions distinguish overlapping populations.|Complete report-map and unallocated-residual exchanges.|design runtime|R01 R02
MC08|specified_scoped|history northstar apple sql|Continuous debt mix and coupled alternatives are preserved; incompatible remainders are rejected.|Complete portable family dependencies and real-case target-layer labels.|design actual_fact runtime|R01 R02
MC09|specified_scoped|history query validation|Templates, admissibility, witnesses, coverage and partial formulation are distinct.|Supply connected construction/query/resume records; engine completeness is later evidence.|design runtime|R01
MC10|specified_scoped|history method estimate revision|Facts, readings, treatment, estimates, behavior and shocks remain distinct.|Carry categories and admission through exact corporate and real-case exchanges.|design actual_fact|R01 R02
MC11|specified_scoped|query bank_draw insurance finance_matrix|Changed queries expose lost debt, credit-risk and cohort memory.|Complete common profile fields and remaining sector interaction decisions.|design runtime|R01 R03
MC12|specified_scoped|forecast query reserving|Unweighted families, finite laws, likelihood updates and unresolved mass are explicit.|Target-specific reference/calibration protocol remains generic; parameters need separate admission.|design empirical|R05
MC13|specified_scoped|northstar method atomic state_only|Corporate economic events and independent journal/state invariants exist; insurance exchanges are exact.|Complete corporate source-to-method/event/transaction closure.|design runtime review|R01
MC14|specified_scoped|forecast revision ix|Stress, observation and intervention differ; policy information excludes simulated future realizations.|Complete corporate information-view fields and changed-cutoff outputs.|design runtime empirical|R01 R05
MC15|specified_scoped|northstar corporate corp_extensions production estimate|Northstar joins all ordinary corporate operations across annual/interim periods; later methods expand coverage.|Complete portable connected specification and finite authority/scope dispositions for promised additional methods.|design source review|R01 R03
MC16|specified_scoped|northstar apple group bank insurance|Full Northstar statements and real annual/interim networks coexist with connected sector reconciliations.|Complete corporate report payload/shared indexing; preserve real-package unknowns.|design actual_fact runtime|R01 R02
MC17|design_partial|finance finance_matrix eps revision_result|Debt/EIR/modification/default, compound conversion and dated EPS are delivered.|Declared hedge/benchmark, options and changed-conversion scope needs authority and worked consequences.|design source actual_fact|R03
MC18|specified_scoped|failure query reserving|Joint regions, bounds, failure and unexecuted probability mass remain visible.|Complete corporate partial/unsupported report and recovery closure.|design runtime|R01
MC19|design_partial|standards standards_map method|Dated AASB/IFRS, selected US and ASBE methods and matched contrasts exist.|Reconcile promised operations with exact edition/amendment/eligibility evidence; historical analogy cannot grant current admission.|design source actual_fact|R03
MC20|specified_scoped|method bank insurance atomic|Bank/insurance records use common method and admission semantics; invalid pooling is rejected.|Complete supported method scope and shared fields for remaining interactions.|design source runtime|R03
MC21|specified_scoped|bank bank_draw bank_matrix revision|Connected bank cases preserve deposits, credit, commitment risk, funding, capital and liquidity distinctions.|Decide finite remaining restructuring/funding scope and target-specific later validation; actual facts remain missing.|design source actual_fact empirical|R03 R05
MC22|design_partial|insurance atomic insurance_matrix|Issued/held group service/finance/claims roll-forward and atomic/replay exchanges are complete within their scope.|Priced guarantees and acquisition/reinsurance interaction need supported methods and validation design.|design source actual_fact empirical|R03 R05
MC23|specified_scoped|language reuse validation sql|DSL, typed code, XBRL, ledger, rule and inference roles have a fair comparison protocol.|Reconcile consequential competitors and omission decisions; empirical superiority is unclaimed.|design source empirical|R04 R06
MC24|design_partial|language portable registry atomic_schema|Core 0 and portable value/type/expression meanings plus scoped closed schemas exist.|Descriptive operation entries lack complete corporate wire records and matched source/typed/IR/result closure.|design runtime|R01
MC25|design_partial|interface persistence atomic reserving|Common envelope, identity, owners, replay-first lookup and recovery are specified; sector examples are exact.|Complete corporate arguments/results/dependencies, correction, conflict, recovery and failed migration exchanges.|design runtime|R01
MC26|specified_scoped|history query language|Affine/finite/quantized limits, strict endpoints, rounding and budget behavior are explicit.|Bind capability/query records to complete corporate exchanges; solver correctness remains later.|design runtime|R01
MC27|specified_scoped|conflict evidence revision|Actual conflict has proposal, acceptance, rejection, alternatives, supersession and invalidation.|Complete portable review bindings and independent/human feedback; no actual adjudication is claimed.|design runtime review human|R01 R08
MC28|design_partial|northstar apple conflict group bank atomic|Full synthetic financial case, named real networks and group/sector interactions exist.|Complete corporate exact workflow and one real-package conditional-results trace; separate companies cannot become one history.|design source actual_fact review|R01 R02 R03
MC29|evidence_partial|literature research sql bootstrap|Technical reading, version/correction and actual screening decisions are retained.|Audit current consequential claims against primary support/direct alternatives, not arbitrary new source counts.|design source review|R04
MC30|evidence_partial|literature research bootstrap production|Original sources, exact versions/hashes and blocked records survive.|Check current claim/library manifest and remaining naming/version support gaps.|design source|R04
MC31|evidence_partial|reuse reserving validation|Official interface/license inspections and exact reserving exchanges establish scoped reuse candidates.|Consolidate selected versions, dependency/model/taxonomy terms and missing consequential adapter exchanges.|design source runtime|R06
MC32|integration_pending|p18 northstar registry operations|2.93 preserves mathematics/sources and includes scoped rendered inspections.|Whole-candidate argument/contract/rendering repair and review remain; builds do not establish comprehension.|design manuscript review human|R07 R08
MC33|specified_scoped|validation p19 atomic|Conformance/corpus/workload and separate engineering/accounting/science judgments are explicit.|Bind complete initial-profile fixtures and justified workloads to the final candidate assessment.|design runtime empirical review|R01 R05 R08
MC34|specified_scoped|master p19 profile|All 53 original obligations retain phase ownership and dependencies.|Replace stale routing with finite audit queue; reconcile first implementation slice after repairs.|design coordination|R00 R08
MC35|specified_scoped|mc35 p19|Internal preparation and acceptance are separate; no paid engagement is authorized.|Finish feasible internal repairs before bounded professional questions; human feedback remains pending.|design review human|R08
G1|specified_scoped|history northstar query|Templates, joint constraints, outside-scope possibilities and partial search are specified.|Complete connected construction/query/checkpoint records.|design runtime|R01
G2|design_partial|language portable atomic_schema registry|Core 0 and portable semantics coexist with scoped exact schemas.|Complete initial corporate schema and matched source-to-result fixtures; old Core 0 is not its substitute.|design runtime|R01
G3|specified_scoped|query history|F,V parameterization, strict attainment and quantization are derived within explicit scope.|Bind numerical capabilities/results to the corporate profile.|design runtime|R01
G4|specified_scoped|northstar corporate group estimate|Full corporate annual/interim operations, correction and connected group/FX methods exist.|Connect exact interfaces; do not present the separate group case as Northstar history.|design runtime|R01 R03
G5|design_partial|northstar apple conflict|Known synthetic history, real annual/interim package and actual contradiction are delivered.|Complete synthetic exact exchanges and real-case conditional-results specification with unresolved facts.|design source actual_fact|R01 R02
G6|specified_scoped|forecast northstar query|Operating baseline, information timing and finite/continuous worked models are substantive.|Target-specific future inference/calibration protocol remains a design deliverable; no experiment is authorized.|design empirical|R05
G7|design_partial|standards finance bank insurance|Sources, cross-standard contrasts, hybrids, bank and insurance methods exist.|Finish finite declared method residuals and interaction/source obligations.|design source actual_fact|R03
G8|evidence_partial|literature sql bootstrap|Source-specific technical, reference, version and correction screening is delivered.|Reconcile consequential claims and competitors across all six ledgers and the current candidate.|design source review|R04
G9|design_partial|reuse reserving atomic|Adapter field-loss/error/subset boundaries and exact reserving exchanges exist.|Complete corporate exchanges and selected dependency/terms locks; broad benchmarking is unnecessary now.|design source runtime|R01 R06
G10|specified_scoped|validation p19 atomic|Finite conformance cases, corpus review and acceptance distinctions are documented.|Complete initial-profile inputs/outputs, workload decisions and candidate-bound review.|design runtime review|R01 R05 R08
G11|scoped_evidence|apple apple_map source_admission|All declared source/reference/note populations preserve disposition and narrative unknowns.|Connect material unresolved units to affected current queries and target-layer admission.|design source actual_fact|R02
G12|specified_scoped|language ix apple group|Context/partition mappings separate populations; equal amounts do not prove equal measurements.|Complete report-map and residual wire fields.|design runtime|R01 R02
G13|specified_scoped|time apple revision northstar|Multi-clock original/revised/interim consequences are explicit.|Supply exact corporate selection results; real public-byte timing remains query-specific unknown.|design actual_fact|R01 R02
G14|specified_scoped|forecast revision ix|Exogenous, conditioning, intervention and restricted decision information differ.|Complete scenario/information fields and adverse look-ahead exchanges.|design runtime|R01
G15|specified_scoped|evidence history method estimate|Category-specific admission preserves assertions while rejecting unsupported treatment.|Carry distinctions through connected corporate and real-case exchanges.|design runtime|R01 R02
G16|specified_scoped|query bank_draw insurance|Changed queries reject lost credit/cohort memory and retain detailed constituents.|Complete portable resolution/refinement/error payloads; no general compression theorem follows.|design runtime|R01
G17|specified_scoped|conflict revision evidence|Actual source-backed review and frozen/current selective invalidation are delivered.|Complete review closure and independent acceptance; feedback absence does not stop drafting.|design runtime review human|R01 R08
G18|specified_scoped|language persistence atomic reserving|Canonical identity, legacy mapping, replay and commit ambiguity are explicit.|Complete corporate closure and failed-migration outputs; physical durability is later evidence.|design runtime|R01
'''
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=[s.split('|') for s in DATA.strip().splitlines()]
    original=BASE['original_obligations']['records']
    assert len(rows)==53 and [r[0] for r in rows]==[r['id'] for r in original]
    evidence={}
    for k,p in S.items():
        frozen=OUT/'evidence-snapshot'/p
        if not frozen.exists():
            frozen.parent.mkdir(parents=True,exist_ok=True)
            frozen.write_bytes((ROOT/p).read_bytes())
        evidence[k]={'path':p,'snapshot_path':str(frozen.relative_to(ROOT)),'sha256':sha(frozen)}
    records=[]
    for old,r in zip(original,rows):
        ident,judgment,refs,delivered,residual,categories,queue=r
        refs=refs.split(); assert set(refs)<=evidence.keys()
        records.append({**old,'candidate_version':'2.93','current_documentary_judgment':judgment,
          'supported_scope':delivered,'evidence_keys':refs,'residual':residual,
          'residual_categories':categories.split(),'repair_ids':queue.split(),
          'acceptance':'not_assessed_as_complete'})
    data={'date':'2026-10-15','purpose':'convergence audit; not a replacement full assessment',
      'candidate_version':'2.93','candidate_pdf_sha256':BASE['pdf_sha256'],'readiness':'not_ready',
      'evidence':evidence,'records':records,
      'limits':['Scoped specification credit is not acceptance.','Source-result notes retain their original source-reading limits.','No new external source acquisition or runtime validation.']}
    (OUT/'evidence-ledger.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    lines=['# Version 2.93: all 53 original obligations','',
      '15 October 2026. Located convergence audit, not a replacement for the frozen 2.72 assessment. Exact original obligations and both historical statuses remain in the JSON companion. No row claims independent or human acceptance. The candidate remains **not_ready**.','',
      'Residual classes distinguish missing design/source support, unknown actual facts, later runtime/empirical work, manuscript repair and independent/human acceptance. Missing design cannot be renamed implementation; private facts cannot be invented.','',
      '| ID | Prior | Scoped judgment | Delivered evidence | Residual and next action |','|---|---|---|---|---|']
    for r in records:
        refs=', '.join('['+k+'](../../../'+evidence[k]['snapshot_path']+')' for k in r['evidence_keys'])
        lines.append('| '+r['id']+' | '+r['recorded_status']+' | '+r['current_documentary_judgment']+' | '+r['supported_scope']+' '+refs+' | '+r['residual']+' **'+', '.join(r['repair_ids'])+'** ('+', '.join(r['residual_categories'])+') |')
    (OUT/'evidence-ledger.md').write_text('\n'.join(lines)+'\n')
    checks=[{'id':r['id'],'original_fields_preserved':all(r[k]==v for k,v in o.items()),'residual_and_evidence_present':bool(r['residual'] and r['evidence_keys'])} for r,o in zip(records,original)]
    protected=[{'path':x['path'],'pass':sha(ROOT/x['path'])==x['sha256']} for x in BASE['source_manifest']]
    index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
    index_ok=hashlib.sha256(index).hexdigest()==BASE['unrelated_index_sha256']
    passed=all(x['original_fields_preserved'] and x['residual_and_evidence_present'] for x in checks) and all(x['pass'] for x in protected) and index_ok
    (OUT/'ledger-checks.json').write_text(json.dumps({'pass':passed,'scope':'integrity only','rows':checks,'protected':protected,'unrelated_index_preserved':index_ok},indent=2)+'\n')
    print(json.dumps({'rows':len(records),'evidence_files':len(evidence),'protected_files':len(protected),'index_preserved':index_ok,'integrity_pass':passed}))
    assert passed
if __name__=='__main__': main()
