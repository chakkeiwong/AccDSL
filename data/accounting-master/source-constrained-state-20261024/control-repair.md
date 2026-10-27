# Control-writer repair

The first finish.py command failed Python parsing at its generated multiline
note before any control file changed. The checked source-state implementation
and recorded results were not affected. Preserve finish.py and its manifest
hash; use finish_control.py, which writes the note with explicit line joining.
It requires a fresh read-only replay before updating controls and records its
own hash in control-refresh.json. No scientific or accounting conclusion changes.
