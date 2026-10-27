# Bounded caller follow-up

The acquired ValidateXbrl.py has no direct validateTextBlockFacts call. Its
lines 163 and 447 enumerate plugin hooks; absence here does not establish
absence elsewhere. The retained exact-pin Cntlr.py imports ModelManager at
line 26 and calls ModelManager.initialize at line 316. Acquire
arelle/ModelManager.py at the same pin to trace the actual validation dispatch.
This is one additional bounded source request under the plan's adaptive rule.
Do not execute its code or infer a selected profile from an import.

The acquired ModelManager.py imports arelle.Validate at line 9; its validate
method calls Validate.validate(self.modelXbrl) at line 213. Acquire
arelle/Validate.py at the same pin to inspect that exact dispatch. This is a
dependent source addition supported by the actual call, not a repository-wide
search or a guess that ValidateXbrl.py directly performs the profile check.

Validate.py dispatches to ValidateXbrl, whose Start/Finally plugin hooks are
confirmed. Neither inspected file directly calls validateTextBlockFacts.
DisclosureSystem.py lines 203–205 and 268–282 show base and plugin
configuration loading and the optional pattern/image values. Acquire the
official exact-commit recursive Git tree metadata (same 2 MiB/45-second bound)
to identify existing validator/plugin/configuration paths without inventing
one or downloading the repository. The tree is a path inventory, not a
repository-wide content search or a caller-absence proof. Select at most two
initial relevant source/configuration paths from the actual returned entries;
record those choices before fetching. Further direct dependencies require a
new scoped note. No global search completeness claim is authorised.

The nontruncated tree (3,773 entries) names arelle/config/disclosuresystems.xml
and arelle/plugin/validate/FERC/__init__.py; no paths match the queried EFM/GFM
directories. Select those two actual blobs: the configuration answers defaults
and legacy profile identities, and FERC is a concrete plugin candidate whose
message family occurs in the inspected text checker. This does not claim the
FERC plugin is applicable to the retained Apple report. Its applicability is
the question, and external/installed plugins remain outside this tree.

FERC/__init__.py lines 39–55, 84 and 221–234 establish a real guarded caller
and the plugin's config.xml reference. Acquire that exact tree-listed
arelle/plugin/validate/FERC/config.xml to resolve this caller's declared
activation/configuration values. The guard requires validateDisclosureSystem
and FERCplugin; no source evidence makes that profile applicable to Apple.

The caller includes INLINEXBRLDOCUMENTSET in its inline branch, whereas
ValidateFilingText.loadDTD tests only Type.INLINEXBRL. Before interpreting
that distinction, acquire arelle/ModelDocument.py and
arelle/ModelDocumentType.py at the same pin: the checker imports the former's
Type, and the caller imports the latter's ModelDocumentType. These actual
references and tree-listed paths justify two final source acquisitions.
Check the alias and constants statically. No document-set runtime will run.

Restart recovery on 20 October verified all 3,468 protected files, the same
36 tracked dirty paths, HEAD and empty staging before construction. No
dependencies.json/checks.json/completion.json existed. The remaining optional
diagnostic searches only the frozen decoded strings of the 56 fragments for
the two unequal entity names, &there; and &there4;. Literal absence/presence
is explanatory only; it cannot establish entity expansion or runtime impact.
The source inquiry still survives skeptical review: a demonstrated FERC
caller does not select an Apple disclosure profile, and equal declaration
counts cannot serve as a name-equivalence test. No continuation veto fired.
