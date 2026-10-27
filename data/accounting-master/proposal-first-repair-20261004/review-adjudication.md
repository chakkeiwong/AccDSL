# Controller review adjudication

4 October 2026, Hong Kong. The two independent sequential review passes are
`20261003T190824-e9275ee2` and `20261003T192443-0f35683d`. Each covered seven
controller scopes. Both stopped before phase work because they found defects.
This is the supervisor's adjudication of the actual findings after repair,
not a claim that independent reviewers unanimously approved the final bytes.

| Finding | Disposition and verification |
| --- | --- |
| Reboot could reuse a process identity. | Repaired: boot ID is persisted and compared before inspecting or signalling saved PIDs; different and missing boot IDs have negative tests. |
| Worker inventory omitted configuration/prior runs. | Repaired: a distinct inventory covers persistent configuration and prior evidence, with tests for new and modified configuration and old check records. Git internals remain protected by the worker sandbox. |
| Inventory exceptions could become review retries. | Repaired: unreadable files and introduced symlinks veto continuation, retain a diagnostic, and never retry. |
| Missing state could be recreated from a cached copy. | Repaired: observed persisted state cannot disappear silently; first initialization remains valid. |
| Failed replanning could yield with unresolved deletions. | Repaired: the scheduler checks deletion obligations before selecting another phase; the regression leaves the next independent phase untouched. |
| Preflight could overwrite the preserved baseline. | Repaired: byte preservation precedes preflight; detected writes veto the run and leave durable restoration obligations checked on resume. Overwrite, deletion and failure-after-write are tested. |
| Partial snapshots omitted verification inputs. | Repaired: bind original inputs and check record; changed/missing inputs require recheck. |
| Manuscript omitted figure/data inputs. | Repaired: TeX recorder dependencies include figures and project inputs outside the manuscript directory, with separate environment dependency identification. |
| Successful exit could be observed after the deadline. | Repaired: exit and elapsed time are observed together, conservatively retaining timeout classification. Between-poll and slow-registration cases preserve output without success. |
| Non-string verdicts bypassed review retry. | Repaired: type-check before set membership at both sites; list/object verdicts remain saved and use one fresh retry, then ReviewPending if still invalid. |
| Pending catalog edits lack a second state-level full-catalog hash. | Not a defect under the public entrypoint. The complete catalog already belongs to CONTROLS, so changed bytes invalidate the controller review before execution and changes during a run veto continuation. Pending work obtains a new reviewed plan; saved checked work requires the exact phase hash and dependencies; accepted work becomes stale on contract change. IDs and workflow direction separately require migration. A new regression proves that changing a pending criterion cannot reuse the old controller receipt. A second catalog identity would add a migration requirement without repairing an observed stale-execution path. |
| Blocked responses dropped next actions. | Repaired in plan, plan review, work and result review paths; current unblock instructions replace old instructions in refreshed plans. |
| Handled interruption could tear finalization. | Repaired: defer handled shutdown signals through final state/plan/manifest/event publication. Tests interrupt final refresh, terminal manifest publication and finalization after an earlier interruption. The signal is delivered only after the terminal evidence is saved. |
| Passing verification could be rebound to later input bytes. | Repaired: compare the checker's original hashes during checking, pending-review creation and acceptance; merge without replacing mismatched hashes. A stale passing check cannot create acceptance or a pending review. |
| Recovery omitted failed replan reviews. | Repaired: include replan directories and retries, and distinguish latest proposed/rejected plans from the latest approved plan. |
| Re-pinned sources could reuse a stale PDF. | Repaired: require the build-time before/after input hashes and resulting PDF hash. Changing and re-pinning source or figure bytes without a new build fails. |

Executed verification: 144 controller tests in 28.462 seconds and 17 proposal
evidence tests in 1.358 seconds, all passing. Logs are `controller-tests-r6.log`
and `proposal-tests-r3.log` in this directory. The public master reruns the full
current suite before it may reuse this adjudication.

Review scope remains local engineering behavior under cooperative workers.
Neither these tests nor this review establishes complete proposal content,
accounting validity, empirical forecasting validity or human acceptance.
The next operational validation is actual P15 proposal work, with fresh planning,
checks and independent content review. P08/product implementation stays held.
