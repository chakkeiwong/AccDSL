# Execution audit and recovery note

22 October 2026. P18/P19, R07/R08; MC04/18/23/25/29/30/32–35.
The original audited plan and the grammar amendment precede their respective
source changes. The exact comparator is protected Version 3.46, not an older
release or an unbuilt working tree. The completed diagnosis is not rerun.

The first preparation copied 144 sources and made seven diagnosed repairs.
Its 41.39-second build produced PDF
28ece05611ea3bf831b7092961daf906d92bd1d5eddbe95748bdc551f039f0c3.
The final first-attempt reading after recovery inspected pages 171–172 and
212–215; earlier local observations were preserved from the continuation.
Source/bibliography inspection confirmed thirteen author-subject agreement
errors and distinguished singular Halaj, Pierson and dataset subjects.

amend_grammar.py saved the complete first candidate tree, locks, diff, logs,
manifests, renders, checks and observations, with 191 file bindings, before
changing the literature source. It appended exact old/new replacements to
the source lock. build_attempt2.py then ran the same bounded LuaLaTeX command,
retaining its separate stdout and manifest; the canonical build manifest now
refers to attempt 2. render_final.py generated 26 final-build pages. Each was
actually viewed in ordered local segments at no more than three images per
tool call. Rendering alone was not counted as reading.

All Python commands used CUDA_VISIBLE_DEVICES=-1 and the existing tfgpu
python3 with -B. LuaLaTeX used the recorded task-local TEXMFVAR/TEXMFCACHE.
There was no GPU initialization or new dependency. The final build took
19.072451348998584 seconds. No timing comparison or performance claim follows.

Preservation checks retain 7,443 protected files, git HEAD/index and all 36
tracked dirty paths. The four declared live controls may be refreshed only
after the candidate evidence is recorded; unrelated dirty bytes remain exact.
The final source delta is reversible to 3.46, and all displayed mathematics
and citations match exactly. No evidence of a failed source/build harness,
corrupted artifact or global continuation veto was found.

Safe completed-repair replay is verify.py without flags. Never rerun prepare.py,
amend_grammar.py, either build helper, either render helper, verify.py --record
or the one-time control refresh. Future regression evidence is additive under
regression/ and excluded from the frozen local-repair completion bindings.
Its judgments must start pending. Independent acceptance remains pending;
this does not stop the authorised internal queue.
