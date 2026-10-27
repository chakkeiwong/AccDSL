"""Protected minimal 3.16 integration; no inherited content removal."""
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "docs/design/proposal/manuscript-ordered-eps-20261016"
NEXT = ROOT / "docs/design/proposal/manuscript-company-eps-20261016"


def main():
    assert not NEXT.exists()
    sources=sorted(p for p in BASE.rglob("*") if p.is_file() and p.suffix in {".tex",".bib",".lark"})
    assert len(sources)==114
    lock=[]
    for source in sources:
        rel=source.relative_to(BASE); snap=OUT/"baseline-sources"/rel
        snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,snap)
        lock.append(dict(path=str(rel),sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    (OUT/"baseline-source-lock.json").write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),files=lock),indent=2)+"\n")
    for source in sources:
        target=NEXT/source.relative_to(BASE);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    for name in ("company-eps-join.tex","company-eps-records.tex"):
        text=(OUT/name).read_text()
        text=re.sub(r"\b(profit|interests|cash|equity|Capital|capital|receives|of|repayment of|liability|coupon|rate|by|from|paid|is|remains|earnings|interest|receipts|payments|opening cash|addback|than|profit|shares)(?=\d)",r"\1 ",text)
        text=re.sub(r"\b(the|its|and|a)(?=\d)",r"\1 ",text)
        (OUT/name).write_text(text)
        (NEXT/"sections"/name).write_text(text)
    title=NEXT/"accounting-product-proposal.tex";title.write_text(title.read_text().replace("Version 3.15 (proposal candidate)","Version 3.16 (proposal candidate)"))
    chapter=NEXT/"chapters/14-financing-groups.tex";text=chapter.read_text()
    anchor="\\input{sections/eps-lifecycle}"
    assert text.count(anchor)==1
    chapter.write_text(text.replace(anchor,anchor+"\n\n\\input{sections/company-eps-join}"))
    appendix=NEXT/"chapters/17-portable-reference.tex";appendix.write_text(appendix.read_text()+"\n\\input{sections/company-eps-records}\n")
    eps=NEXT/"sections/eps-lifecycle.tex";text=eps.read_text()
    anchor="After conversion, 600 actual shares enter basic EPS for 92 days."
    qualification="""The transfer of carrying amount in this early-conversion illustration is a
supplied accounting treatment for the EPS example. IAS~32.AG32 expressly
addresses conversion at maturity; a general earlier-conversion measurement
rule requires separate source and terms analysis. The maturity-conversion
company case in Section~\\ref{sec:company-eps-join} uses that explicit rule.
"""
    assert text.count(anchor)==1
    eps.write_text(text.replace(anchor,qualification+anchor))
    (OUT/"early-conversion-qualification.txt").write_text(qualification)
    print(json.dumps(dict(baseline_sources=len(sources),successor=str(NEXT.relative_to(ROOT)),changed_inherited_files=4,new_sections=2)))


if __name__=="__main__":
    main()
