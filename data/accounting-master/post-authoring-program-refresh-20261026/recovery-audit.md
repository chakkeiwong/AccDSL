# Control refresh completion

The first refresh wrote all ten controls, then correctly failed its identity
check because the historical note omitted the new PDF/hash. Added that identity
to five historical notes without repeating the completed backup/write phase.
All ten controls now select the new plan and exact 4.48 PDF. Final metadata is
recorded by finish-refresh.py; do not rerun either one-time writer.
