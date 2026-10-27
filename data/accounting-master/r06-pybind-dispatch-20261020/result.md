# Failed string conversion in two pybind11 dispatchers

20 October2026. R06/R04; P15/P17/P19; MC23/24/26/29/30/31/33–35.

Both inspected source versions route an ordinary rejected string argument to
an incompatible-function-arguments TypeError if diagnostic construction
succeeds. The original encoding error was cleared by the string caster and
is not directly propagated as UnicodeEncodeError. This completes a conditional
source account; no exception was observed in a native runtime.

The pinned versions remain v2.2.0 at2a5a5ec0a47c245fbf1bb1a8a90b4c3278e01693
and v2.11.1 at8a099e44b3d5f85b20f05828d919d2332a8de841. Four newly acquired
pybind11.h/attr.h files match the exact blobs and sizes in the retained trees.
The complete dispatcher bodies and selected binding,record,caster,argument
loader,repr and error-helper spans are retained in32 anchors and28 bindings.
Neither version is identified as the actual pylcs binary's build dependency.

The source path is explicit:

1. The inspected pylcs module registers lcs_sequence_length once,with two
   const std::string reference arguments. Its separate lcs alias is a different
   Python name. Overloads registered for edit-distance names do not add an
   overload to this name.
2. module.def resolves siblings by that name. A new function record starts
   with next=nullptr and is_operator=false. For normal fresh module creation,
   this target therefore has one non-operator signature.
3. Each string caster clears the failed Unicode encoding error and returns
   false. argument_loader propagates a required caster's failure; the wrapper
   returns PYBIND11_TRY_NEXT_OVERLOAD before invoking the LCS function body.
   The sentinel is the special non-null pointer value1,not a null return value.
4. The dispatcher skips the no-conversion pass for a single signature. Its
   second-pass loop is conditional on actual overloads. No alternative
   signature for this target can rescue the failed load in the inspected
   ordinary path.
5. The terminal sentinel branch builds the incompatible-arguments diagnostic,
   calls PyErr_SetString(PyExc_TypeError,...) and returns nullptr. The later
   null-result branch reports failure to convert a return value; it is a
   different path and cannot explain this rejected argument.

There is a meaningful secondary limit. v2.2.0 calls repr directly while
building the terminal message,after the earlier call/translation try/catch.
Its repr helper throws error_already_set if Python repr fails, and its
string conversion has a separate failure path. v2.11.1 wraps positional
argument repr and keyword-value repr in local error_already_set catches and
substitutes “<repr raised Error>”. The newer dispatcher also supports chaining
a still-pending Python error through raise_from(TypeError,...). The inspected
helper sets that new error and attaches the prior error as cause/context.

The nominal conclusion therefore assumes ordinary positional built-in strings,
normal module registration and successful diagnostic allocation/construction.
No universal final exception,process outcome or historical impact is inferred
for custom repr,allocation failure or an arbitrary malformed object. The
newer local repr catch does not prove every operation during message creation
is failure-proof. A comparison of these sources is not evidence that every
intermediate/later release behaves the same way.

For the upstream GriTS wrapper,the previous equality shortcut still matters:
equal inputs may return1 before pylcs is called. This source trace describes
calls that actually reach a rejected converter. Bytes/bytearray and malformed
UTF8 remain governed by their separately recorded input-domain analysis; no
validation policy or runtime behavior is silently added here.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Complete the bounded dispatcher account | Exact source edges now reach the terminal diagnostic | Four Git blobs and source/protection checks pass | Diagnostic construction can fail independently | Preserve the qualified TypeError account | Observed runtime result or universal error guarantee |
| Retain version-specific repr behavior | Complete terminal branches and helper definitions inspected | No source-identity mismatch | Actual installed dependency and host behavior | Keep build/runtime identities separate | A measured crash,security result or release-wide ranking |
| Continue the master program | This closes one source question without changing the manuscript | No global continuation veto | Substantive method/source and acceptance gaps remain | Re-audit current remaining obligations and select a distinct consequential source/method task | Closure by source-count accumulation |

There is no stochastic experiment,performance ranking or new numerical
implementation. The checks establish source identity and preserved excerpts;
the control-flow argument above supplies the interpretation. Six additive
ledgers and a separate R08 supplement preserve3.44/396/not_ready,all53
obligations,six interactions and46 operations with zero whole-row closures.

Post-run red team: an actual build can use a different pybind11 version,
custom caster or registration environment. A built module under a separately
authorised protocol would be needed to establish installed behavior. Nothing
here invalidates the target,prior string examples or the wider design.
Safe replay is verify.py without flags after recording; do not repeat completed
one-time stages. Independent/domain/human acceptance remains pending.
