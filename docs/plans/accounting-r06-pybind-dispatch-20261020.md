# R06 — source-only pybind11 argument-failure dispatch

20 October2026. R06/R04; P15/P17/P19; MC23/24/26/29/30/31/33–35.
Output:data/accounting-master/r06-pybind-dispatch-20261020/.

Question: for the inspected single pylcs.lcs_sequence_length binding, what
does each of the two pinned pybind11 dispatchers do after std::string
argument conversion returns false? Preserve the converter's clearing of
the original Python encoding error and distinguish a load failure from an
exception in the function body or return conversion. Do not execute code.

Baselines are the completed r04-pybind-strings-20261020 source paths at
v2.2.0/2a5a5ec0a47c245fbf1bb1a8a90b4c3278e01693 and
v2.11.1/8a099e44b3d5f85b20f05828d919d2332a8de841. The new release-source
comparison does not identify either as the actual pylcs binary dependency.
The retained trees identify include/pybind11/pybind11.h blobs
fbde332a514b9e5050cb2edfb2d92b5d90d47625 and
3bce1a01bae6bf8f38a394cc3a4a959c046b395d respectively. Acquire these exact
two files from the official pinned repository; use retained cast/helper
files wherever possible. At most two further directly needed helper files
may be acquired after a written dependency note, never a floating version.

Skeptical audit: a failed string load is not itself a propagated
UnicodeEncodeError. The dispatcher may try another overload or conversion
pass, construct a different error, or fail while formatting it. Trace that
path and inspect the actual no-overload binding before asserting an exception
class. The ordinary final diagnostic and secondary error-construction failure
must remain distinct. Read enough surrounding control flow to avoid selecting
a return-conversion error branch. No actual exception is claimed observed.

Evidence contract: primary success is a complete bounded source path from
argument_loader/load_args through the selected function wrapper,dispatcher
sentinel and terminal error branch,with exact source anchors. Vetoes for the
dependent claim are an uninspected call edge,version mismatch,overload
assumption or conflated secondary failure. Missing material triggers a helper
read or narrower conclusion. Source counts and local string illustrations
are explanatory only; prior examples will not be rerun. No runtime,error
message ABI,all-version,performance,financial validity or build-identity
claim follows.

Assumptions: two releases are explicit bounded comparators inherited from the
prior plan; not the entire pybind11>=2.2 range. Pylcs registers this function
once with two std::string const references and no custom caster; verify its
actual source. Ordinary built-in str rejection is the primary case; subclasses,
custom repr and memory-allocation failures require explicit limits. The
earliest diagnostic is Git blob equality before control-flow reading.

Premortem: the apparent terminal TypeError path may invoke repr that itself
raises. Preserve this alternative; a nominal error class is not an absolute
guarantee for every malformed object. No source-only result can close the
distributed/installed native build gap. That gap is a promotion veto,not a
global continuation veto; continue other ready internal work.

Each HTTPS request:15-second connect,45-second total,512KiB maximum,retained
headers/body/actual receipt; trusted retry only for sandbox/network failure.
Use standard-library reading and CPU-only
CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B.
Prepare once,successful construction once,--check,--record once,then no-flag
replay only. Preserve3.44/396/not_ready,53/6/46,zero whole-row closures,
protected predecessors,HEAD/index,36 dirty paths and empty staging. Four live
controls and a separate R08 supplement may advance. Runtime/controller,
installations,empirical work,commits,outreach,publication and fees remain held.
