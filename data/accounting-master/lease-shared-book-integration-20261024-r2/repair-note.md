# Repair the TeX inclusion depth

The first Version3.72 build failed before producing a PDF: TeX reported text
input levels=15 at the new section heading. This is a build implementation
failure, not rejection of lease mathematics or the simulator direction. The
failed source and build records remain unchanged and their hashes are locked.

Skeptical repair audit: include the new section beside the archive from
family-outcome-queries.tex, after the archive input returns. This reduces one
nesting level without reordering or deleting prose. Reuse exactly the drafted
lease section. No memory-limit override or baseline change is needed. Primary
criterion remains preserved source meaning and a clean rendered successor.
Record and finish only from this r2 package. No failed controls were advanced.
