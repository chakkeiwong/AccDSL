# Recovery and plan audit

20 October 2026. Read-only preservation passed for 2,880 files, the recorded
HEAD/index, 36 tracked dirty paths and empty staging. Preparation exists;
construction, checking and recording have not completed. Both XHTML request
receipts are now preserved, including the failed sandbox request and successful
trusted retry. No acquisition is repeated.

The finite structural plan remains appropriate. Its preservation criterion is
clarified before implementation: retain the original raw source and decoded
string exactly, then compare the XML-normalized character/event sequence from
two extraction paths. XML entity processing, line-ending normalization and
attribute-value normalization need not preserve the literal fragment spelling.
They must be explicit and fixtures must distinguish those layers. ElementTree
and the independent event walk share Expat; agreement checks extraction logic,
not independent XML parser correctness. No XHTML version is selected by the
DTR annotation. Whole-document XHTML rules cannot be imposed on a fragment.
An unnamespaced fragment is therefore an observation, not a validity verdict.

The comparator, acceptance scope and stop conditions remain unchanged: finite
retained input correspondence only; source corruption or lost text vetoes that
result and triggers repair; protected-state change vetoes continuation. No
rendering, installed validation, dependency execution or empirical claim follows.
