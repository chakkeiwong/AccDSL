# Endpoint assessments and control history

ConversionScopeDependencies/2 preserves the input fields of /1 and requires
canonical YYYY-MM-DD calendar dates. It is a conditional evidence-dependency
reference, not a new core DSL admission rule or an accounting implementation.
The old /1 code remains frozen under baseline.py; the wrapper reuses its
record/context checks and current reporting-view decisions. The output changes
explicitly: endpoint timing replaces an asserted uninterrupted-control history,
conditional dependencies retain acquisition, loss and continued-control routes,
and measurement reference strings no longer erase measurement prerequisites.

The 3x3 table in expected-endpoints.json is authored separately from code. If
both endpoints are controlled, control may have continued or may have been
lost and regained. If neither endpoint is controlled, an intervening gain/loss
remains possible. Different known endpoints require at least one corresponding
transition; unknown endpoints preserve the union of consistent alternatives.
History classes describe coarse alternatives, not a finite enumeration of all
events. No interval is declared complete. Extra cycles are represented by the
additional-change classes; actual event dates and effects remain unspecified.

Two snapshots cannot determine the method for the conversion event. For a
consolidated view, routes therefore retain control_history_unresolved. Possible
acquisition dependencies are explicitly conditional on a gain, relevant entity
status and business/common-control assessments at that gain. Current separate
or investment-entity policy routes still do not establish how an earlier event
was accounted for. Loss dependencies include the reporting context before
selecting a deconsolidation or investment-measurement method.

This follows the inspected distinctions in AASB10 §§7–8,20,23,25, B47–B53,
B96 and B98–B99; dates/records and output names are local engineering choices.
The sources support the required questions. They do not establish actual
control, business status, valuations or a complete2027/2028 edition chain.
The 75% vote fraction stays descriptive. All source/accounting/posting flags
remain false, even when every supplied field has an evidence reference.

The v1 boundary diagnostic is preserved separately. Its unknown-prior route
selected a business combination; its loss case lacked loss dependencies; its
date parser accepted compact form. The first two are wrong relative to the
declared uncertainty-preserving routing target. Canonical dates are a new
explicit specification constraint. This repair preserves old evidence and
does not retrospectively claim that the original21 cases covered these gaps.
