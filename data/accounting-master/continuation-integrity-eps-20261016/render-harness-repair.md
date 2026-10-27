# Render-navigation repair

The first page-selection invocation stopped before rendering: it looked for
both `API` and `Appendix B` in the next appendix's text. The actual title is
“Core grammar, records and execution details.” This was a navigation-harness
failure, not a manuscript, arithmetic or build failure. No result JSON or
render directory was created by that attempt. The selector now identifies the
actual `Appendix B` page heading. No manuscript bytes changed in this repair.
