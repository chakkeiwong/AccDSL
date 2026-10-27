# Repair of the long reference path

The first build succeeded but verification refused two new underfull warnings
in the final authoring paragraph (badness 1389 and 1635). Rendered PDF 401
showed stretched spacing around the long inline reference path. The original
source, baseline record, logs, build record, PDF and image remain in
attempt-01-path-spacing/.

The repair places that same directory in a short, explicitly broken path block.
No statement, definition or source reference is removed. Only the additive
passage changes. The successor's expected-content hash is renewed after saving
the failed attempt; predecessor source/PDF hashes and authoring evidence locks
remain unchanged. Rebuild and rendered verification are required before acceptance.
