# Function-record dependency and diagnostic formatting

Both pinned pybind11.h files match their retained tree blobs. Each failed
load_args returns the special non-null TRY_NEXT_OVERLOAD sentinel. The actual
pylcs binding registers lcs_sequence_length once. To finish the non-overload
path without assuming next/is_operator defaults, acquire the two exact
include/pybind11/attr.h files identified by the retained trees. These use the
two helper requests already allowed by the plan; total budget remains four.
Expected blobs:dce875a6b996036e833a451997d21c81af11c9ed and
1044db94d906ac5fcf6faab6ac7668187314598f.

The newer dispatcher catches error_already_set around argument repr; the older
dispatcher does not at that terminal location. Retained pytypes.h supplies
repr,UTF8 string conversion and the newer raise_from helper, so no additional
helper retrieval is needed for those edges. Scope the nominal TypeError to
successful diagnostic construction and ordinary positional built-in strings.
Do not infer an observed crash, historical impact,all-version guarantee or
universal outcome for malicious/custom repr or allocation failure.
