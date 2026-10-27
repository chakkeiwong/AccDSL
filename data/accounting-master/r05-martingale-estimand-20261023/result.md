# Shared regimes, starting information and expected score differences

Let one fair Bernoulli regime R determine every score difference for nine
companies and three cohorts: d_ik = R and X_k = R. The realised average is R;
its unconditional expectation is 1/2 and its variance is 1/4. These are exact
properties of an illustrative distribution, not estimates from companies.

If the initial information is sigma(R), then E[X_k | F_(k-1)] = R for all
three cohorts. Every martingale residual is zero, and the expected average
conditional on the starting information is R. This says nothing about a
zero-width interval for the unconditional expectation 1/2: the starting
conditioning set has changed the quantity being estimated.

If F_0 is trivial and the first cohort reveals R, then the predictable means
are (1/2, R, R). The residuals are (R-1/2, 0, 0). The first residual has mean
zero and variance 1/4. The martingale calculation therefore retains the
initial regime uncertainty. Later identical observations do not create new
independent regime draws. No impossibility of martingale inference follows.
The original `reference.py` implicitly used the first information set; it is
retained as an incomplete diagnostic and superseded by `conditional_reference.py`.

Direct covariance calculation gives correlation one between any company or
cohort cells. There are 27 nominal cells but one independent regime draw.
The computed within-sample variance is zero in either realised regime, so the
naive iid estimated variance of the average is zero. Even substituting the
true cell variance into an iid formula gives (1/4)/27 = 1/108, compared with
the actual 1/4. Independent-cell inference is wrong for this distribution.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Accept exact illustration | Nine identities reproduce under explicit filtrations | None within stated toy | No mapping to actual company dependence | Declare starting information and joint future law | E3 power or required sample size |
| Reject iid-cell shortcut here | Actual average variance differs from iid calculation | Perfect dependence invalidates shortcut | Real dependence remains unknown | Use cohort/joint dependence model in design | General invalidity of iid methods |
| Keep martingale route unselected | Target-matched conditional null and loss control required | No E3-specific derivation supplied | Unbounded CRPS, future law, conditioning | Derive only after the target is specified | Distribution-free E3 interval |

| Inference status | Finding |
|---|---|
| Hard veto screen | Iid-cell variance and zero-residual unconditional shortcut fail for this toy |
| Statistically supported ranking | None |
| Descriptive-only differences | No stochastic estimates; toy expectations are exact |
| Default readiness | No inference method adopted |
| Next evidence needed | Target, filtration, source/outcome process and a checked interval derivation |

The strongest competing reading is a study explicitly conditional on known R;
there its zero residuals are correct. The error would be claiming the same
bound for an unconditional target. The user's settled E3 choices allow a
declared starting conditioning set; they did not settle that choice.

Results and measured replay runtime are recorded by the successor unit at
`../r05-consistency-recovery-20261023/`. No forecast or admission changes.
