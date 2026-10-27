# Exact timestamp projection for common method requirements

26 October 2026. S2/S3/S4; MC05/19/20/24/25/33/34 and G13/G14/G18.

Question: can supplied information timestamps be bound exactly and compared
through the existing requirement evaluator without date or microsecond loss?
The timing audit found a schema-accepted submicrosecond collision. Preserve
the original parser and its valid full-second examples; add a separate profile.

Skeptical audit passes for a bounded ExactInstantProjection/1. Inputs remain
exactly bound text/unknown values from MethodInputBinding/2. A strict conversion
produces rational seconds on one explicit Gregorian UTC axis. Subsequent
ordering uses existing MethodRequirements/2 comparisons. No new interpreter,
dispatcher, source admission or native profile mutation. Projection success
alone must not establish source-view membership or actual availability.

Default/assumption audit: require YYYY-MM-DDTHH:MM:SS, optional 1–18 decimal
fraction digits, and Z or a signed HH:MM offset. The 18-digit bound is a local
resource/scope choice, not a financial fact. Reject more digits rather than
truncate. Reject leap seconds, 24:00, unknown negative-zero offset, missing
offset, calendar-day-only values, named timezones and malformed civil dates.
Use exact integer day/second arithmetic and Fraction, never float timestamps.
Retain original spelling and offset; canonical value equality must not erase
distinct input-byte identities. UTC normalization must stay in years 1–9999.

Primary criterion: manually derived cases and all retained native full-second
comparisons agree; the two submicrosecond values stay distinct. Equivalent
offsets compare equal, malformed/unsupported encodings refuse, unknown inputs
remain unknown, wrong raw/schema/plan digests refuse. Match text/typed requirement
assessments across the projected values. Schema validity and original context
roles remain separate from evidence truth.

1. Write the projection fields, time axis and provenance contract.
2. Implement only the conversion/binding reference and independent diagnostics.
3. Compare retained native timing, offset/date boundaries and precision limits.
4. Integrate the repaired boundary into a protected manuscript successor and
   refresh the remaining program. No whole requirement closes.

Artifacts: data/accounting-master/exact-information-time-20261026/.
CPU only; no installs, agents, commits, fees, outreach, publication or E3.
