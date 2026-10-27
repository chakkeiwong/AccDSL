# Parser repair before recording

The first18-method run reported two errors. The forward-call fixture selected
local function call lines as main nodes; its corrected selection moves only
nodes after the final end_function. A malformed rational reached the typed
compiler's jsonschema exception directly; the frontend now reports it as an
Invalid semantic error, preserving the underlying cause. The typed compiler is
unchanged. Pre-repair sources are retained in attempt-01. All18 methods pass
after these changes. These were harness/error-interface defects; neither
invalidates pure-function semantics or the broader simulator direction.
