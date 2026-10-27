# Exact insurer-to-book adapter: implementation audit

25 October2026. Governing plan:
docs/plans/accounting-insurance-loss-book-20261025.md, protected by the completed
sector-posting-boundary source lock. This note refines the interface without
rewriting that frozen plan or changing the native source/cases.

An additional mismatch was found before implementation: the native illustrative
currency is CU, while CompanyBook/1 accepts exactly three capital letters. A
silent rename would erase context. Require an explicit bound context adapter:
native context hash, host context hash, unit scale1/1 and a supplied explanation
that host XCU denotes the same illustrative unit. This is a syntactic alias,
not FX conversion, ISO currency admission or a scale change. Entity stays exactly
Synthetic Insurer; the native group and historical rule remain in the retained
request and its hash. Tests must refuse missing/changed mappings and nonunit scale.

Use only the two retained native loss_schedule requests. Recompute their full
results with the unchanged calculator before generating methods. Report-only
native output remains report-only; the new operation proposes a separate
declared-book trace, never mutates the native result or grants posting authority.

The initial book has exact cash200 and liability−100; selected temporary accounts
are zero. Extra balanced assets/equity and unrelated memory are permitted and
must survive. K is positive currency-valued memory, next_step a dimensionless
exact rational, and case_ref the exact native-request hash. No capital account
is a method target. Method pre/postconditions check every scoped balance, K,
progress and case identity at each step. Actual event dates bind to native dates.

Native journal sequence is finance, combined claim/RA release, then claims cash
at each period date. The K release is the sum of its separately retained claim
and RA origins; both origins remain in the result. Reports after steps3 and6
are cumulative within the supplied host interval. They do not perform annual
close or pretend1January events happened on31December.

The adapter passes a proposed statement mapping and explicit missing notes to
the frozen report engine. Claim payments have an explicitly supplied operating
cash premise. Dependency/shape/context/state/memory/alias failures reject before
any proposal escapes; unknown/false native findings retain native refusal status.
No current standards, actuarial, production or source-completeness claim follows.

The first discriminator passed with all six native journals and six loss origins
retained once. Sixteen focused tests then passed in19.579 seconds, including two
charts/two loss-component cases, complement preservation, exact replay, zero
gross reversal, unknown/false source findings, forged results, wrong opening,
date truncation/shifting, and skipped/repeated steps. Record/replay now includes
the frozen book-transition, method-clock and report regressions, plus eight full
cases covering complements present/absent. This is exact conformance, not a
claim that the source assumptions apply to a real insurer.

Recovery audit before recording: the verifier's two fixture paths exist, but
those paths alone omit dynamically loaded regression fixtures and retained
annual-report data. Capture repository files actually read during each test
and case computation, including Python source behind cached bytecode, and lock
them alongside imported engine modules. Stop tracking before writing or reading
the generated case records, so replay compares the same dependency set. This
repairs provenance completeness before the first record; no frozen source,
engine, comparator or plan changes. The exact-state criterion and all refusal
checks remain unchanged.
