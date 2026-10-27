# POCI lifecycle source and representation audit

16 October 2026. Retained historical EU 2023/1803 original:
`docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt`, SHA256
`37f207b1ecdde43e3971cf076f127576d3d7810c791385ba5b1c35f110f17664`.

| Inspected technical anchors/local lines | Use and boundary |
|---|---|
| IFRS9.5.1.1–1A, 35100–35120 | Admitted acquisition fair value and fees; price is not automatically fair value |
| 5.4.1(a)–5.4.4, 35180–35225 | POCI credit-adjusted EIR on amortised cost from initial recognition; the cure rule in5.4.2 specifically refers to5.4.1(b); write-off when no reasonable recovery expectation |
| 5.5.13–14, 35410–35425 | Only cumulative changes in lifetime ECL since initial recognition; favorable revisions are impairment gains even beyond initial expectations |
| Appendix A, 37430–37535, 37630–37710 | Amortised cost, credit loss, credit-adjusted EIR, gross carrying amount, loss allowance and POCI definitions |
| B5.4.6–9, 40155–40200 | Distinguish credit revisions from other contractual estimates/modifications; include initial ECL in the POCI rate; high risk alone is insufficient; partial write-off finding |
| B5.5.44–45, 40803–40816 | POCI discounting uses the original credit-adjusted EIR |

Existing `standards-mapping-v1.md` and `standards-fixtures-v1.json`, case A07,
check only 60×20%=12 and explicitly leave full roll-forwards open. The
P17 banks scope and `r03-bank-residual-audit-20261016/result.md` preserve
the POCI obligation. This is a new historical EU method application; it does
not treat the earlier AASB source as proof of whole-standard equivalence.

For a fixed zero-coupon claim C at integer annual term T, let E0 be the
initial expected terminal receipt and P its separately admitted acquisition
value. A supplied r is accepted only if r>−1 and P=E0/(1+r)^T exactly.
Expected credit shortfall `(C−E0)/(1+r)^T` is embedded in this rate/price
relation; the initial *subsequent-change* allowance is zero under5.5.13.
No calibrated distribution or inference that a discount establishes POCI is
supplied by this example.

Before actual payments, use Gt=P(1+r)^t as the carrying amount before the
subsequent loss adjustment. At a reporting-date estimate Et, net amortised
cost is Nt=Et/(1+r)^(T−t), and the signed allowance is Lt=Gt−Nt. Equivalently,
`Lt=[(C−Et)−(C−E0)]/(1+r)^(T−t)`: the difference from initial expected
shortfalls expressed at the same reporting date. This supplies the required
5.5.13 cumulative-change meaning. An improved estimate can make L negative;
flooring it at zero would suppress the gain required by5.5.14.

For an unchanged estimate over one year, G grows by rG, L by rL, and N by
`rG−rL=rN`. Recognize interest rN under5.4.1(a); classify rL as discount
unwind in the allowance bridge. A later credit revision changes N by its
discounted cash effect, with the opposite change in L and an impairment gain
or loss. Thus no repeated impairment arises merely from the clock advancing.
This is an explicit signed gross/allowance bookkeeping decomposition of the
required net-interest and cumulative-loss amounts, not a contractual principal
schedule or a general ledger presentation prescription.

At maturity, known receipt x and a supplied no-reasonable-further-recovery
finding imply final expected collection x. First measure the remaining net
asset at x, recognizing the last credit gain/loss; then collect x and remove
G and L atomically. The signed entry is cash+x, gross asset−G, allowance+L,
where the allowance account is credit-positive in its reported amount. Since
G−L=x, the entry balances even after favorable revisions. Retain C−x as
the uncollected contractual amount. Financial derecognition under5.4.4 does
not establish legal discharge; this method leaves legal release not assessed.
No promised later recovery or forgiveness is invented.

The skeptical audit passes for this finite terminal-claim profile. General
installments, modifications, non-credit revisions, fees, FX, tax, post-write-off
recoveries and actual calibrated forecasts remain separate. Missing POCI,
classification, fair-value or credit findings refuse. No present-law or actual
bank readiness is concluded. The positive-base rate convention allows zero
and negative rates; independently authored cases must check that no positive-
rate default is silently introduced.
