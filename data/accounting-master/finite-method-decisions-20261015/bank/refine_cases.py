"""Preserve the initial draft and clarify write-off timing once."""
from pathlib import Path
import json, shutil, hashlib
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
backup=OUT/"before-credit-timing-review"
assert not backup.exists()
backup.mkdir()
for name in ["cases.json","independent-checks.json","checked-statements.json"]:
    shutil.copy2(OUT/name,backup/name)
d=json.loads((OUT/"cases.json").read_text())
c=next(c for c in d["cases"] if c["id"]=="delayed_collateral")
c["law"][1]["payments"][0]["receipt_role"]="conditional_mean"
c["conditional_default_recoveries"]=[
    {"weight":"1/4","net_receipt":"121","period":3},
    {"weight":"1/2","net_receipt":"1331/20","period":3},
    {"weight":"1/4","net_receipt":"121/10","period":3}]
c["writeoff_assessment"]={
    "before_sale":"reasonable_fuller_recovery_supported_by_supplied_law",
    "actual_outcome_index":1,
    "at_sale":"independent_exhaustion_finding_no_remaining_reasonable_recovery",
    "earlier_no_recovery_finding":"requires_earlier_partial_writeoff",
    "default_event":"supplied_qualitative_credit_impairment_at_2024_07_01"}
for c in d["cases"]:
    if c["kind"]=="modified":
        c["assessment_time"]="2024-12-31"
        c["payment_time"]="2025-12-31"
        c["assessment_order"]="modification_then_forecast_then_distinct_credit_review_same_close"
        c["cure_event"]="operating_licence_reinstated_and_repayment_capacity_verified" if c["cured"] else None
(OUT/"cases.json").write_text(json.dumps(d,indent=2)+"\n")
text=(ROOT/"docs/design/research/p08-v1/aasb9.txt").read_text()
lines=text.splitlines(keepends=True)
spans=[]
for name,start,end in [
    ("amortised_cost_definition",2407,2416),
    ("gross_and_interest_definitions",2495,2516),
    ("gross_definition",2539,2541),
    ("credit_impaired_ecl",4877,4881),
    ("default_horizon_and_discount",4967,4979)]:
    value="".join(lines[start-1:end])
    spans.append({"id":name,"first_line":start,"last_line":end,"text":value,
                  "sha256":hashlib.sha256(value.encode()).hexdigest()})
(OUT/"supplemental-source-support.json").write_text(json.dumps({
    "text_path":"docs/design/research/p08-v1/aasb9.txt",
    "text_sha256":hashlib.sha256(text.encode()).hexdigest(),"spans":spans},indent=2)+"\n")
print(json.dumps({"refined_cases":3,"preserved_initial_draft":str(backup.relative_to(ROOT)),
                  "supplemental_spans":len(spans)}))
