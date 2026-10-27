# Pending direct self-review findings

1. I1 OperationResult.request_ref currently has no nullable/malformed-input rule.
   A parse failure cannot return a Ref to a valid OperationRequest. Add an exact
   submission reference, nullable validated request Ref, and preserve no usable
   result on rejection. Check against native invalid request=null behavior.
2. The platform mapping turns native mathematical failed into unresolved even
   while retaining the failed diagnostic. A status superset containing failed
   would communicate the verdict more directly and avoid lossy consumers; assess
   whether the explicit native payload is sufficient or the superset is preferable.

These are author findings, not independent acceptance. Group with reviewer
findings before refreshing the review-bound candidate and final checks.
