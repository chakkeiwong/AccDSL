# Direct content-model dependencies

20 October 2026. The pinned loadDTD function selects config/edbody.dtd for
non-inline documents and config/xhtml1-strict-ix.dtd for inline documents.
Acquire these two exact-commit files under the same2MiB/45second limit, retaining
responses/failures and allowing one trusted retry for sandbox/network failure.
Read their declarations as source; do not load or execute a DTD validator or
external entities. No further transitive acquisition is automatic.

Skeptical audit: wrappers and filenames alone do not establish content-model
requirements. These two directly named files are the smallest missing source
evidence. Actual configuration path, runtime type, transitive external entities
and filing-profile applicability remain distinct duties. A route failure blocks
that source claim only; other ready work continues.
