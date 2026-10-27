# Source audit before illustrations

The retained current metric does check ragged rows in _get_n_cols; the input
contract must preserve that positive finding rather than claiming no validation.
The HTML evaluator rejects a bare string, failed parse and location scoring
without boxes. The cell-list entry point rejects a flat list. These checks do
not validate each cell's text, span indices, occupied slots or finite geometry.
TableCell has no __post_init__; from_dict retains explicit None/bytes and
defaults missing text to empty. Grid construction overwrites duplicate slots
and infers extents from the largest index. Negative, repeated or disjoint
indices have no explicit source-level rejection in this conversion path.

BBox.__post_init__ rejects reversed axes only. Its floating-point area and the
IoU union can overflow or underflow even for finite ordered coordinates. The
smallest discriminating examples use identical boxes, whose exact positive-area
IoU is one. Predeclare: unit box; degenerate zero-area box; reversed axes;
NaN x0; infinite x1; finite width overflow; finite area overflow; finite union
overflow; finite area underflow. Exact Fraction arithmetic on the actual finite
float inputs is the comparator. Do not infer NumPy/SciPy downstream behavior.

The evaluator appends each metric's sample inside a sequential loop, with no
rollback in the inspected method. If an earlier metric succeeds and a later
one fails, partial accumulation is possible. This is a conditional control-flow
finding, not an executed integration result. The proposed wrapper should stage
all per-sample outcomes before a single commit, or explicitly report a partial
transaction rather than silently mixing denominators.

Newly noticed separate question: the multi-table function selects an assignment
using lower scores, then sums pair upper scores on that same assignment. Its
meaning as a global assignment upper bound requires separate mathematical
inspection. Preserve this as the next unit; do not silently broaden this unit's
geometry/input claim into an assignment theorem.
