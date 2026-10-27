# JPMorgan complete Form 10-K repair result

The four exact issuer-feed `docs.tenkDoc` candidates were acquired and checked:

| Year | PDF bytes | Pages | SHA256 |
| ---: | ---: | ---: | --- |
| 2022 | 6,947,859 | 382 | `c269899950f36edfa496e3c8447a51d86d0a206442a96dc24dcd9317d55b957c` |
| 2023 | 5,812,622 | 422 | `95ca23db9e9e64045860a3f8c0f0a5de85a28146690955868bd3d304625f2d86` |
| 2024 | 7,776,252 | 436 | `4df8c8007381845715ad56955a4f16c34bdc9e6df6b39a2e7e1c878c2fe0c566` |
| 2025 | 3,767,625 | 410 | `e16cdad03ca84732dbe21b2595c112e975d5a3f27bce9f394828160275bfe79c` |

All **29 final documentary checks pass**. Each file is a readable PDF with a Form 10-K,
JPMorgan issuer identity, SEC language, Item 1A and signatures. The complete
filing candidates directly address the prior annual-report exclusion notices:
2022 omitted pages 1–42 and 304; 2023 pages 1–44 and 322; 2024 pages 1–48 and
334; 2025 pages 1–42 and 328.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain four complete-filing candidates | Exact issuer-feed URL, PDF response/hash and structural Form 10-K checks | No acquisition or structural veto | Full semantic equivalence to regulator filing and earliest byte availability | Keep source and annual counterpart as separate package records | Whole-filing semantic acceptance |
| Repair the documented package omission | Candidate structure covers the omitted filing sections by source identity and page extent | Prior partial-content interpretation repaired at source layer | Detailed section-by-section comparison remains | Map complete 10-K pages/sections to corpus package and preserve provenance | Selected annual PDF becomes the complete filing |
| Preserve historical availability uncertainty | Filing/event clocks remain separate from mirror retrieval | As-of byte admission still vetoed | Exact public availability and byte vintage | Continue event/availability ledger | Forecasting readiness |
| Preserve V2.26 | No manuscript source or hash changed | No candidate-preservation veto | Independent/human/domain acceptance | Continue other internal gaps | Full readiness |

The four PDFs were retrieved from exact issuer-hosted links recorded in the
previous event unit. Each response used a 40 MiB streamed cap and returned a
valid PDF. `checks-attempt-1.json` preserves one initial checker attempt that
failed only because its 2025 omission-text predicate was too strict; the
predicate was repaired to match the retained notice wording and the final run
passes. This is harness repair evidence, not a source failure.

The complete candidates repair the identified source-selection gap, but no
claim is made that they are byte-identical to the SEC primary HTML filings, that
all exhibits and incorporated documents are semantically closed, or that their
filing dates are the first public availability of these exact PDFs. The frozen
corpus counts and 56/136 date assessment remain unchanged. No statistical
comparison applies.

Version 2.26 remains 168 pages, SHA256
`d7c60268490921ec7edbc964ece351ebcdbd478ce422fa20b59de844e3ab48d7`.
Readiness stays `not_ready`. No OCR/model execution, installation, GPU,
professional outreach, fees or publication occurred.
