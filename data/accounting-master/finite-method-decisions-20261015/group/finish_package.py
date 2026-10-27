"""Freeze the extension descriptor without changing any portable record."""
from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/"extension-package.json").exists()
d=json.loads((OUT/"portable-exchanges.json").read_text());a=d["aliases"]
c=json.loads((ROOT/"data/accounting-master/p17-completion-20261014/P17-05/group-fx-disposal/source-manifest.json").read_text())["date_corrigendum"]
p=ROOT/c["path"];assert sha(p)==c["sha256"]
package={
    "package_key":"GroupForeignOperation","version":"1",
    "record_schemas":{"path":str((OUT/"record-schemas.json").relative_to(ROOT)),"sha256":sha(OUT/"record-schemas.json")},
    "operation_signatures":[a["signature.accounting.commit@1"],a["signature.report.build@1"]],
    "supported_contexts":[{"entity":"Group-P","book":"Consolidated","currency":"USD",
        "source_currency":"EUR","calendar":"relative_A_O_R_D","basis":"historical_conditional_IFRS","scope":"synthetic_pretax_ordinary_interests"}],
    "state_requirements":["exact_legal_book_read_set","control_and_perimeter","rate_direction_and_instant",
        "signed_balances","profit_oci_by_parent_and_nci","classified_cash_movements","branch_fork_provenance"],
    "authority_refs":[a["source"]],"method_refs":[a["method"]],
    "capability_requirements":["exact_rational","immutable_closure","owner_compare_and_swap","business_event_replay"],
    "migration_refs":[],
    "example_refs":[{"exchange_id":x["id"],"request_ref":x["request_ref"],"response_ref":x["response_ref"]} for x in d["exchanges"]],
    "packet":{"path":str((OUT/"portable-exchanges.json").relative_to(ROOT)),"sha256":sha(OUT/"portable-exchanges.json")},
    "additional_sources":[{"path":c["path"],"sha256":c["sha256"],"purpose":c["effect"]}],
    "compatibility":"Common I1 envelope fields; separately locked group bodies. No automatic corporate-state migration or runtime registration."
}
(OUT/"extension-package.json").write_text(json.dumps(package,indent=2)+"\n")
print(json.dumps({"package":"GroupForeignOperation/1","examples":len(package["example_refs"]),"corrigendum_verified":True}))
