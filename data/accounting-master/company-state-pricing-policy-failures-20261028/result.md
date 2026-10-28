# Pricing policy, funding capacity and numerical status

28 October 2026. C04/T07; SIM-F025/028/029. Attempt01 passes109 checks over39
solver cases and2 native programs. The benchmark is the retained chapter26
finite financing example, with explicitly assumed equal pricing weights, gross
return1 and assets60/140. No empirical probability, actual offer or equilibrium
admission follows.

The exact price schedule partitions all nonnegative faces into [0,60], (60,140]
and (140,infinity). Price is F,30+F/2 and100 respectively. Needs0/40/60/80/100/110
are checked in every region; boundary prices and an above140 face are separately
compared with the independent min(face,assets) state-payoff equation. Need100
has face140 and every face above140; need110 has no root in any region. Because
the final interval has no upper face bound, this is not an inference from a
truncated face search. It is infeasibility only in the specified asset/financing
channel, not proof that a company has no other funding option.

A deliberately wrong price tail100+(F−140)/1000 creates a false root10140 for
need110. The original state-payoff law still gives100 there, leaving10 unfunded.
Neither a large face nor a small approximation slope creates valid financing.

For policy consistency, the retained S/R example has S assets100/100 and R
assets0/180. At fixed face80, S prices debt80 and equity20; R prices debt40 and
equity50. Post-issuance residual maximization favors R, so retaining S's debt
price after permitting R overstates price by40. With credible prior commitment,
S face80 and R face160 both raise80, leaving equity20 and10. This checks the
exact conditional arithmetic and timing distinction. It does not implement an
equilibrium policy solver, demonstrate actual commitment or estimate behavior.

A separate zero-budget pricing call returns Unknown with incomplete coverage
and its retained formula. Under two account maps, the existing native discounted
issue still executes an explicit face100/proceeds80/quote0.8 offer. Every issue
balance and memory value agrees with the independent supplied-offer expectation;
full native replay passes. Unknown pricing neither changes the offered terms nor
injects a default transition. The offer remains a synthetic premise, not evidence
of actual market access, and successful execution does not resolve the separate
endogenous pricing query. This tests the result distinction; it is not a test of
an iterative root-finder convergence rate or a complete service router.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain SIM-F025 conditional discriminator | S/R price and equity values match exact state payoffs under distinct commitment timings | Safe-price/risky-policy mismatch identified | Actual behavior, commitment and equilibrium | Preserve policy/offer assumptions when joining endogenous services | Dynamic equilibrium solved |
| Retain SIM-F028 status discriminator | Unknown pricing coexists with unchanged conditional offered issue | No default or invented offer injected; native states replay | Real offer evidence and broader solver routing | Bind actual offer/authority independently; test future router explicitly | Unknown means default or market rejection |
| Retain SIM-F029 no-root discriminator | Whole-domain regions and original payoff agree on capacity100 | False positive tail root rejected by original law | Other financing channels and asset process | Continue specified alternatives rather than inventing debt proceeds | Global company insolvency |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Wrong price tail and policy mismatch fail their exact criteria; zero budget remains Unknown |
| Statistically supported ranking | Not applicable: exact deterministic cases |
| Descriptive-only differences |109 checks and39 solver calls describe tested coverage only |
| Default readiness | No solver, financial-policy or native implementation default changes |
| Next evidence needed | Actual asset law, offers, policy/commitment evidence, service composition and other channels |

Post-run red team: solving the authored regions cannot validate their applicability
to a real issuer. The independent state-payoff equation catches the false-tail
control, but shares the declared asset/pricing assumptions. The weakest evidence
is actual economic applicability and missing dynamic service integration. No
global continuation veto fired; remaining original cases and ordered review
remain ready. All original task criteria/statuses and release statuses persist.

Final verification matches all1,179 protected hashes, including997 frozen-release
files. The current workspace's program suite passes18 tests. Concurrent goal-
alignment edits expanded that validator from its earlier nine tests; those
unrelated edits are preserved separately. This unit's refresh verifies29 source
hashes, preserves all task criteria/statuses/dependencies and records38 reviewed
original rows,163 outside this pass. Main reading remains336/831, resume337.
