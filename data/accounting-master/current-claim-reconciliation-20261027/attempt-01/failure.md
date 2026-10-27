# First recording attempt stopped during metadata inspection

The source ledger uses the literal value `not available` for one metadata
source. The new integrity recorder treated it as a filesystem path and stopped
before arithmetic or ledger output. No retained evidence was changed and no
success was recorded. Preserve this attempt and handle that explicit metadata
sentinel in a new attempt. An actual missing declared file must still fail.
