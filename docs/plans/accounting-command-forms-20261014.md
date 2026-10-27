# Command forms for direct accounting preparation

14 October 2026. The user requests grouped permissions and stable command forms
to reduce interruptions. This concerns the authorized P17/P18/P19 program;
runtime implementation and the historical controller remain held.

## Tool choices and approval scope

Use ordinary sandboxed file tools for local reads, edits and calculations. Use
the tools' working-directory argument instead of `cd`, and pass commands
directly without shell wrappers, command substitution or chained separators.
Record full logs on disk and return concise results. Search JSON with structured
parsing; use `rg -l` or `rg --files` before searching raw one-line records.

The existing user rules already allow direct `curl`, `latexmk -lualatex`, Git
add/commit and the configured read-only Claude wrapper. Local PDF extraction
and rendering have worked in the sandbox. No GPU, installation, external
message or reviewer launch is needed for the present source/manuscript work.
If a later unit genuinely needs a new permission, prepare the exact action and
group the known requests before their dependent work. Do not ask again for
existing authorization or elevate a local operation solely because it edits a
file. Actual sandbox restrictions still apply.

The additional rules are reviewable in [accdsl-direct-work.rules](accdsl-direct-work.rules).
They cover two fixed document-helper subcommands. Existing direct Git rules
are already sufficient. The helper validates proposal/evidence roots, writes full build
logs, caps render batches at 20 pages and rejects arbitrary shell operations.
The existing global rules and approval policy are preserved. Installing this
one rule file under `/home/chakwong/.codex/rules/` requires access outside the
session's writable roots; that is the only new grouped installation request.

The official Codex rules page and Markdown route returned HTTP 403 in trusted
requests. Rule syntax and matching are therefore checked with the installed
`codex execpolicy check --help` and actual parser, rather than claimed from an
unread official page. Rule installation and session reload behavior must be
distinguished: the installed rules can be checked immediately, while the
running session's permission snapshot may require a later reload to include
them. Existing approved forms and sandboxed operations remain usable meanwhile.

## Exact forms

Use the absolute helper path consistently; do not substitute `python -c`,
`bash -lc` or a newly generated temporary script for the same operation.

```sh
python3 /home/chakwong/python/AccDSL/scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-sql-logic-20261014 --evidence data/accounting-master/accounting-sql-three-valued-logic-20261013
python3 /home/chakwong/python/AccDSL/scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-sql-logic-20261014 --evidence data/accounting-master/accounting-sql-three-valued-logic-20261013 --pages 68-70,221
```

Change only the candidate/evidence paths and requested pages for subsequent
units. Keep each new PDF in a distinct candidate directory. After a PDF changes,
use a fresh rendering evidence directory to avoid mixing versions.

For source downloads, use direct `curl -fSL --max-time 60 --output <file>
--dump-header <headers> <https-url>` with the normal trusted-network setting
when needed; the existing `curl` rule applies. Save HTML/JSON/PDF bytes before
reading selected fields. An HTTP access failure is evidence about that route,
not permission to disable checks or invent source support.

For any authorized commit, preserve the unrelated index and use explicit paths:

```sh
git add -- <task-files>
git commit --only -F /tmp/accdsl-commit-message.txt -- <task-files>
```

Set the tool's working directory to the repository; do not add a `git -C`
wrapper. These Git writes use trusted access because `.git` is mounted
read-only in the sandbox. Never use a bare commit when unrelated changes are
staged. The existing direct `git add` / `git commit` prefixes cover these
forms; the new file adds no broader Git permission.

## Focused verification

The final narrow rule file was installed with the user's approved command.
Installed and repository copies both have SHA256
`df29ccc3bbf176cbeef5f17d6d12324b349a64445cb5fc5e15dbd5dcba49e588`.
It permits only the fixed helper's `build` and `render` subcommands; redundant
Git additions were removed. No approval is currently pending.

Before installation, the installed Codex parser matched the helper build form
and rejected an unrelated `python3 -c` form from the new rule set. The helper
rejected a candidate outside the proposal directory and an evidence path
outside the accounting-master directory before executing a build. Actual
render/build results are preserved with the current SQL integration evidence.
This verifies command handling; it does not promote scientific or proposal
readiness.
