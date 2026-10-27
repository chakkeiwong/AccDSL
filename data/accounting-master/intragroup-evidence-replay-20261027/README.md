# Internal intragroup inventory replay

This copied component reproduces five exact conditional profiles cited by the
current manuscript: downstream inventory elimination and same-year realisation,
downstream next-year carry, upstream elimination and upstream next-year carry.
The complete population is 204 positive/conditional cases and 147 refusal
controls. Tax, ordinary rights, dates, revenue recognition and depreciation are
supplied synthetic premises. No actual company/source admission is established.

After checking the archive identity in preservation.json, extract into a new
directory and run with the recorded Python environment:

```sh
python3 -I -B /absolute/copy/data/accounting-master/intragroup-evidence-replay-20261027/replay.py --root /absolute/copy --output /absolute/copy/output-01
```

The output directory must be new and inside the copy. The original recorded
environment is Python 3.11.15 with jsonschema and its dependencies. Environment
versions and observed installed-file hashes are saved by the driver. No
dependency installer is included. The --smoke option runs one case and one
refusal per profile for debugging only, without the full conformance claim.

The driver calls unchanged report functions and independent authored fixture
functions. It never invokes original archival writers. Complete outputs compare
exactly, with no timing or witness normalization. Independent rational checks
replay all available legal/group journals and check balance, profit and NCI
identities. Unknown tax keeps its full unresolved output without a final report.
All source/accounting/posting/report/execution admission flags remain false.

The child access audit begins before project imports. It checks Python-visible
reads against the declared inputs and installed Python environment, refuses
network/subprocess calls, and restricts writes to the new output directory.
Interpreter startup and arbitrary native system calls remain outside the audit.
Original source documents may be retained because native hash locks read them;
this does not recheck their interpretation, applicability or redistribution
rights. The package is for internal use. Independent implementation, general
accounting correctness, clean installation and release acceptance remain open.
