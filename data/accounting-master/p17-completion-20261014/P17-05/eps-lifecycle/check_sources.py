"""Verify the retained primary-source bytes and complete IAS33 page inventory."""
import hashlib
import json
from pathlib import Path
import time
import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
started=time.perf_counter()
manifest=json.loads((OUT/"source-manifest.json").read_text())
checks=[]
def check(name,ok):
    checks.append({"name":name,"passed":bool(ok)})
for source in manifest["sources"]:
    p=ROOT/source["path"]
    check("sha:"+source["path"],hashlib.sha256(p.read_bytes()).hexdigest()==source["sha256"])
    check("bytes:"+source["path"],p.stat().st_size==source["bytes"])
source=ROOT/manifest["sources"][0]["path"]
doc=fitz.open(source)
check("full_source_pages",len(doc)==992)
check("complete_page_inventory",manifest["read_pages"]==list(range(233,248)))
for start,end in [(233,236),(237,240),(241,244),(245,247)]:
    expected="".join(f"\n=== PHYSICAL PAGE {i} ===\n"+doc[i-1].get_text() for i in range(start,end+1))
    check("exact_page_extract:"+str(start),(OUT/f"ias33-pages-{start}-{end}.txt").read_text()==expected)
text=" ".join(" ".join(doc[i-1].get_text() for i in range(233,248)).split())
for token in ["Earnings per Share","weighted average number","continuing operations",
              "most dilutive to the least dilutive","future","RETROSPECTIVE ADJUSTMENTS",
              "This appendix is an integral part","Control number","Participating equity",
              "Partly paid shares"]:
    check("operative_text:"+token,token in text)
check("historical_currentness_boundary",not manifest["current_amendment_chain_established"])
review=(OUT/"source-review.md").read_text()
check("review_has_scope_and_dispositions","A2,A11–A16" in review and "not a current" in review)
check("corrigendum_text_retained",(ROOT/"docs/design/research/p08-v3-preparation/eu-2023-1803-date-corrigendum.txt").exists())
result={"passed":all(c["passed"] for c in checks),"check_count":len(checks),"checks":checks,"wall_seconds":time.perf_counter()-started}
(OUT/"source-checks.json").write_text(json.dumps(result,indent=2)+chr(10))
print(json.dumps({"passed":result["passed"],"checks":len(checks),"failed":[c["name"] for c in checks if not c["passed"]]}))
raise SystemExit(0 if result["passed"] else 1)
