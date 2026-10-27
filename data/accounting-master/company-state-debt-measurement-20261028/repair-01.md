# Preserve the issuer extension namespace

28 October 2026. Attempt01 stopped during concept validation, before native
lowering or numerical interpretation. The adapter incorrectly assumed all
thirteen debt-note occurrences belonged to the2024 US-GAAP namespace.
Retained f-946 instead uses Apple's http://www.apple.com/20240928 namespace.

The correction binds that exact namespace for the inspected occurrence and
adds an adverse case that rejects silently changing it to US-GAAP. The old
adapter and runner are copied into attempt-01 with the failure record.
Run fresh attempt-02. This is an implementation/default-assumption failure;
it does not invalidate the source card or the intended reported-value relation.
