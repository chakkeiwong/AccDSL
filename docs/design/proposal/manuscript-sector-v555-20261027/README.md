# AccDSL 5.55 — sector interfaces

This protected successor preserves the5.54-R2 package revision2 and adds
the dated premium-allocation book/report connection and explicit bank
profile boundaries. The candidate remains not_ready; independent reader,
domain, implementation and whole-document acceptance remain open.

Run python3 -I -B verify_package.py here to check declared package bytes.
Build the two TeX roots with LuaLaTeX through latexmk in the retained
TeX Live2026 environment, using a private writable TEXMFVAR/TEXMFCACHE.
No dependency installation or publication is implied.

Six companions now accompany the specification:

| Component | Scope | Instructions |
| --- | --- | --- |
| Historical Core0 | Historical language/reference fixtures | companions/historical-core0/README.md |
| Selected term program | Bounded term execution | companions/selected-term/README.md |
| Refinancing domain | Conditional cash identities and counterexamples | companions/refinancing-domain/README.md |
| Source/history/opening/report |37 retained exchanges | companions/source-history-replay/README.md |
| Dated PAA book | Seven conditional cases and21 controls | companions/insurance-paa-dated-book/RUN.md |
| Bank interfaces | Separate AU/US and exact-time profiles | companions/bank-interfaces/RUN.md |

Each component retains its own assumptions and comparison contract.
Use a fresh output directory; never run archived one-shot writers.
The bank replay excludes historical Git/index preservation and checks
declared copied inputs instead; this distinction is explicit in its notes.
All materials are for internal preparation. Original source rights,
current applicability, clean installation and other runtimes remain separate.
Evidence paths beginning data/, docs/ or scripts/ refer to the AccDSL
repository layout reconstructed by the relevant archive, where included.
DEPENDENCIES.md and PACKAGE-REVISION.json preserve version and access limits.
