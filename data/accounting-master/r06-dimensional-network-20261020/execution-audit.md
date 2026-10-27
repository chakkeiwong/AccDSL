# Execution and recovery audit

Restart recovery replay of r06-numeric-accuracy-20261020 passed: 3,078 protected
files and 31 completion bindings. This successor's preparation protects 3,110
files, the original HEAD/index and 36 tracked dirty paths.

The retained schemas declare definitionArc as xl:arcType. Its optional order
has no XML Schema default; the XBRL prose supplies ordering value 1 when absent.
Those facts do not justify inserting an absent order into the post-schema
attribute set for relationship equivalence. Explicit order is present on all
actual arcs. The finite numeric comparator accepts only integral decimals
within the exact binary64 integer range; actual orders lie in 0..690.
Dimensional attributes have semantic defaults, which are used for traversal and
future applicability separately from raw non-exempt attribute presence.

The global policy's 20 October context rules were read during recovery. Commands
after that read use bounded output; the earlier broad file search was truncated
and replaced by exact paths. No source acquisition was needed.

Commands, in sequence, with
CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B:

1. predecessor verify.py without flags — recovery replay.
2. this unit verify.py --prepare — once.
3. one read-only diagnostic imported compare.py and ran the authored fixtures
   and derive() before artifact construction; it exposed no implementation error.
4. this unit build_records.py — once.
5. this unit verify.py --check — once; 90 assertions.
6. this unit verify.py --record — once, after notes/control updates.
7. this unit verify.py without flags — final read-only replay.

The automatic manifest records the lifecycle commands; this note supplies the
construction command and diagnostic distinction. All work uses the standard
library with GPU deliberately hidden. No upstream runtime, installation,
empirical execution, commit or external action occurred.
