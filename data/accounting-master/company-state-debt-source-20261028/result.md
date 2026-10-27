# A retained debt note narrows state without identifying instruments

28 October 2026. All111 source/context/arithmetic checks pass. Source:
Apple2024 Form10-K Note9, physical PDF46/printed43, exact retained PDF and XBRL
archive. The rendered page was inspected before the authored expectations.
This is a historical reported-source construction, not current financial advice.

The note reports principal of97,341 USD million at28September2024. The maturity
table allocates it as10,930;12,342;9,936;7,800;5,153;51,180 under printed
2025,2026,2027,2028,2029 andThereafter labels. These add to97,341. The printed
reconciliation deducts321 of unamortized premium/discount and issuance costs,
net, and358 of hedge-accounting adjustments, giving96,662 carrying debt.
Its current10,912 and noncurrent85,750 components sum to96,662.

This supplies more information than an annual issuance aggregate, but distinct
quantities must remain distinct. The next principal bucket exceeds current
carrying debt by18. The note does not allocate that difference to individual
instruments in the inspected table, so the construction does not do so. The
97,341 principal caption is tagged DebtInstrumentCarryingAmount; mapping from
the tag name alone would obscure its printed role. The adjustment facts are
positive numbers in XBRL but deductions in the table. Their signed effect is
bound to the selected reconciliation, not guessed from the literal sign.

The note describes senior unsecured notes with interest in arrears, a stated
coupon range and an issuance-summary calendar maturity range. It also describes
interest-rate and cross-currency swaps on portions of the note population.
Therefore the fixed coupon description alone does not determine the company's
economic interest-rate or currency exposure. Instrument-specific swap links
and terms are needed before propagating a shock or computing dated payments.
No new numerical swap allocation is inferred here.

All13 selected fact occurrences bind context c-21, issuer0000320193,
instant2024-09-28, USD and decimals−6. Their PDF captions and amounts agree.
The reported arithmetic is exact in displayed millions; underlying amounts
may be rounded. The future-payment year labels are preserved. Exact maturity
dates and a full fiscal/calendar interpretation are not manufactured from
the issuance-summary heading or the first bucket's taxonomy name.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Add selected debt-note constraints to the construction record | PDF/XBRL identity, meaning/sign and reported reconciliations checked |111 checks pass | Instrument, book and exact cash-date mappings remain absent | Bind selected debt exhibits/terms and derivative relationships | Executable issuer opening or source/accounting admission |
| Preserve principal/carrying/maturity distinctions | Same-date amounts retain separate roles | No replacement of current carrying by next principal bucket | Distribution of adjustments and intra-year payments | Retain component alternatives until supported | A balancing total identifies the company's financial state |

The previous180 target obligations and15 issuer dependency rows are unchanged;
no original target is marked ready. The construction exposes missing instrument
IDs, legal obligors, precise principal/coupon dates, currency/swap mappings,
adjustment allocations, source availability and full population coverage.
Those are concrete next evidence requirements, not an excuse to discard useful
aggregate restrictions already supported by the source.

The strongest alternative explanation for a misread source is semantic mapping:
a valid XBRL number can still be assigned the wrong role or sign. Inspecting
the printed reconciliation addresses that local risk. It does not establish
whole-filing completeness, latent exact amounts, legal rights or valuation.
No statistical ranking, fraud/default inference or release acceptance is made.

Command, HEAD, input hashes, Python/CPU-only environment and elapsed time are
in attempt-01/run-manifest.json. source-to-state.json preserves each fact's
role, signed reconciliation and remaining fields; note9-page46.txt and the
source-page-46.png reading retain the inspected context. Frozen sources and
selected manuscript packages are unchanged.
