# Bounded program preparation repair

The first prepare attempt failed before writing examples: applying the
4,096-node single-component guard to the entire program rejected the combined
templates and invariant. The existing complete-program validator instead uses
a 1 MB total byte limit and individual command/definition checks. The successor
now follows that structure: whole-program 1 MB cap; at most 64 rules and 64
commands; the unchanged 4,096-node/depth bounds on each rule component, command
and remaining field. Individual predicate and constructor limits remain intact.
This is an aggregate container repair, not permission for oversized methods.
