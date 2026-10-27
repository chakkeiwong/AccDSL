# Metadata assembly recovery

The first assemble.py invocation stopped at the first technical-span anchor
assertion after writing the normalized access page and acquisitions.json.
Its initial span numbers came from newline-based sed navigation, whereas the
verifier uses Python splitlines(keepends=True), which also splits PDF form-feed
characters. No source or calculation was invalidated. The page/request records
were preserved byte-for-byte. Corrected Python line indices were located by
the exact88/91/B134/B135/B136 anchors; the assembler was changed to validate
already written identical outputs and finish only the missing source-review.
No preparation, network acquisition or completed-unit recording was repeated.
The completion binds the corrected assembler and this recovery record.
