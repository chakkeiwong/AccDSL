# Source and extraction review

The exact historical source was reached through retained links: official home
index, full index, XBRL 2.1 release history, dated HTML, then the normative RTF
filename expressly named by that HTML. The RTF URL is a sibling resolution of
that filename, not an invented publication edition. Source-ledger receipts are
transcriptions of the completed curl JSON, with original headers and response
bodies retained and hashed. Four navigation/acquisition calls after the home
page complete the five-URL budget. The initial sandbox DNS failure is separate.

Inspected HTML spans (one-based source lines): 584–605 title/date and normative
filename; 725–746 status and Appendix A authority; 21045–21130 maintenance
wording and instance-schema opening; complete bounded instance-schema section
from its h2 anchor through before the linkbase-schema h2. The schema itself is
read in its entirety by exact correspondence and ordered structural comparison;
this is not a claim to have read the entire 6.6 MB specification or all normative
method prose. The RTF contains the correction_date property 2008-07-02 and
the same dated document title; the appendix heading explicitly says normative.

The HTML maintenance prose still contains a 2006-12-18 archive directory. That
does not change the document title/status date; it was not used to locate a
substitute schema. No assertion about that old archive was made or tested.

The RTF extraction starts at the first literal XML prolog after the unique
instance_schema_filename bookmark-start and ends at the first closing schema
tag. All 55,351 selected raw bytes are ASCII. The parser accepts only observed
formatting controls and paragraph breaks; other controls fail. The starred pn
destinations contain inspected formatting controls, no text. Physical RTF line
breaks and group braces are representation syntax; paragraph controls emit LF.
The exact source equality after three declared adjustments is stronger than
the supplementary whitespace-normalized element comparison. The latter retains
all effective namespace mappings, expanded element/attribute names, lexical
attribute values, order and annotation text. It does not validate XSD semantics.

Initial extraction failed on an over-escaped starred-destination test. A failed
patch and a failed quoting correction changed no source bytes. The successful
literal-marker repair preceded the only successful extraction. No frozen prior
unit was edited. The zero-line splitlines diff omits the final-newline difference;
exact-correspondence.json explicitly records it. No unexpected difference was
normalized away.

Actual local artifact commands, all with CUDA_VISIBLE_DEVICES=-1 and
/home/chakwong/miniconda3/envs/tfgpu/bin/python3:

- verify.py --prepare (once, completed)
- compare.py --extract (initial failure, then one successful extraction)
- record_sources.py (once, completed)
- verify.py --check (once, completed)
- verify.py --record (completion command recorded in run-manifest.json)
- verify.py (fresh read-only completion replay)

The run manifest and this note together distinguish acquisition, construction,
checks and replay. Curl durations cover transfer work, while the manifest's
start/record timestamps include human/tool approval and reasoning time. Dates
are recorded on completion; the start-date filenames are intentionally retained.
