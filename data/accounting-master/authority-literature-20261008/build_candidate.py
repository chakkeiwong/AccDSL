"""Create the bounded V2.4 source candidate without touching V2.3."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "docs/design/proposal/manuscript-taxonomy-20261008"
NEW = ROOT / "docs/design/proposal/manuscript-authority-20261008"
if NEW.exists():
    raise SystemExit("Candidate already exists; preserve it and edit deliberately.")
for source in OLD.rglob("*"):
    if source.is_file() and source.suffix in {".tex", ".bib", ".lark"}:
        target = NEW / source.relative_to(OLD)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def replace(relative, before, after):
    path = NEW / relative
    text = path.read_text()
    if text.count(before) != 1:
        raise ValueError((relative, "Expected exactly one replacement", before))
    path.write_text(text.replace(before, after))


replace("accounting-product-proposal.tex", "Version 2.3", "Version 2.4")
replace("chapters/08-modules.tex",
        "lease provisions. Its entity-specific issuance and amendment chain and other\nASBE authority remain incomplete. Current ASC access is also unresolved.",
        "lease provisions. The official 2017 ASBE~22 text also supports the selected\ncredit-loss, interest and write-off distinctions worked through in\nChapter~\\ref{ch:banking} \\citep{mofasbe22}. Entity-specific issuance and amendment\nchains and broader ASBE authority remain incomplete. Current ASC access is also\nunresolved.")

bank = "sections/bank-methods.tex"
replace(bank,
        "The general measurement interface requires",
        "The 2017 ASBE~22 text makes the two horizons explicit. Article~47 defines\ncredit loss as the present value of all contractual cash flows less expected\nreceipts; a late receipt can therefore create a loss even when its nominal\namount is paid in full. Article~48 limits twelve-month ECL by the date of the\npossible default event, while retaining the resulting cash shortfalls over the\nasset's life. Article~52 assesses changes in default risk, rather than changes\nin the allowance, and Article~58 requires probability weighting, time value\nand reasonable, supportable information \\citep[Articles 47--48, 52, 58]{mofasbe22}.\nThese provisions support the following dated comparison. Article~84 states\n1 January 2018, but applying the standard to a particular company also requires\nits issuance schedule, subsequent amendments and adoption facts.\n\nThe general measurement interface requires")
replace(bank,
        "Assume a fixed-rate non-POCI amortised-cost loan originated for 100, one terminal payment 121 two years later, original EIR 10\\%, no fees, collateral, modifications, FX or taxes.",
        "Assume a fixed-rate non-POCI amortised-cost loan held to collect its contractual cash flows, originated for 100, with one terminal payment 121 two years later, original EIR 10\\%, no fees, collateral, modifications, FX or taxes. Since no payment falls due before maturity, an earlier default in this example is a separately established qualitative credit event, such as financial distress under the admitted default definition; it is not a missed instalment. Article~52 of ASBE~22 requires a definition consistent with credit-risk management and consideration of qualitative indicators \\citep{mofasbe22}.")
replace(bank,
        "The ratio change alone is not the defined SICR test. Immediately afterward, a distinct, ordered credit-impairment event establishes that only 60.5 will be collected at maturity. Required allowance is 110\\ensuremath{-}60.5/1.1=55; debit impairment 44/credit allowance 44. Net 55.",
        "The ratio change alone is not the defined SICR test. Only twelve months remain, so twelve-month and lifetime ECL both equal 11 under this revised forecast. This amount cannot distinguish the two classifications.\n\nImmediately afterward, a distinct, ordered credit-impairment event changes expected maturity collections to 60.5. This is a forecast mean, not a guaranteed or maximum recovery. Required allowance is 110\\ensuremath{-}60.5/1.1=55; debit impairment 44/credit allowance 44. Net 55. ASBE~22 Article~59(5) measures this non-POCI credit-impaired asset by gross balance less discounted expected receipts. Articles~38 and 39(2) then make amortised cost, after the allowance, the basis for subsequent-period interest \\citep{mofasbe22}.")
replace(bank,
        "In the next full year interest revenue is 55\\ensuremath{\\times}10\\%=5.5.",
        "The bank is assumed still to have reasonable prospects of fuller recovery before maturity. The separate finding that some contractual cash will not reasonably be recovered first arises at settlement on this branch. If that finding arose earlier, ASBE~22 Article~43 would require the corresponding earlier write-off. Expected collections alone do not justify postponing an already-required write-off.\n\nIn the next full year interest revenue is 55\\ensuremath{\\times}10\\%=5.5.")
replace(bank,
        "This is separate from the financing method's issuer-liability ten-percent test.",
        "ASBE~22 Articles~42 and 56 similarly separate remeasurement of a non-derecognised asset from its credit-risk reassessment \\citep{mofasbe22}. This is separate from the financing method's issuer-liability ten-percent test.")

with (NEW / "references.bib").open("a") as stream:
    stream.write(r"""
@misc{mofasbe22,
 author={{Ministry of Finance of the People's Republic of China}}, year={2017},
 title={{Accounting Standard for Business Enterprises No. 22: Recognition and Measurement of Financial Instruments}},
 url={https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170908_2694655.htm},
 note={Cai Kuai [2017] No. 7; official page dated 8 September 2017, retrieved 8 October 2026. Selected articles 17, 38--43, 46--63, 72--73, 83--84 inspected. Original Chinese preserved; English title and interpretations translated. The issuance notice's entity-group adoption schedule and a complete subsequent amendment chain remain unverified}
}
""")
print(NEW)
