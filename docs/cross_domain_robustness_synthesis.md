# Does a single robustness metric generalise across domains?

## Motivation

Three independent research projects in this portfolio, TrustLens AI
(credit-risk classification), the Cross-Sector Greenhouse Gas Scenario
Model (climate/energy optimisation), and Hospitality Sustainability AI
(building-energy forecasting), each already test their own model's
behaviour under some form of stress: population drift and individual
out-of-distribution screening, Monte Carlo perturbation of cost and
abatement assumptions, and generalisation to unseen venues and future time
periods, respectively. A natural question is whether these three,
independently designed evaluations can be summarised under one common
"robustness retention ratio" (RRR), so that a reviewer could ask "which of
these systems degrades least under stress?" and get a single, comparable
answer.

This note reports that they cannot, and explains why, using only numbers
each project has already published and locked.

## Step 1: the naive comparison looks clean

Taking the single most natural, non-cherry-picked stress comparison
already present in each project's own evaluation design:

| Domain | Comparison | RRR |
|---|---|---|
| TrustLens AI | Development recall (0.879) → locked test recall (0.833) | 0.948 |
| GHG optimisation module | Nominal abatement (2,560 kg CO2e/yr) → frequency-weighted retained abatement under 1,000 Monte Carlo perturbations | 0.912 |
| Hospitality Sustainability AI | Rolling-development MAE (111.87) → locked final-test MAE (159.92), inverse-error | 0.700 |

This produces a tidy, monotonic-looking ranking: TrustLens appears most
robust, the GHG module close behind, and Hospitality noticeably less
robust. It is the kind of clean result that is tempting to present as a
finding in itself.

## Step 2: an equally valid alternative comparison breaks the ranking

Each of these projects also reports at least one other, equally
non-cherry-picked stress comparison. Substituting these:

| Domain | Alternative comparison | RRR |
|---|---|---|
| TrustLens AI | Development ECE (0.032) → locked test ECE (0.070), inverse-error | 0.457 |
| Hospitality Sustainability AI | Unseen-venue-only → unseen-venue-and-future-period improvement, Fox_food_Francesco | 0.745 |
| Hospitality Sustainability AI | Unseen-venue-only → unseen-venue-and-future-period improvement, Mouse_lodging_Vicente | 1.548 |

The naive comparison's range was 0.700 to 0.948 (a spread of 0.248). Once
these alternative, equally defensible comparisons are included, the range
becomes 0.457 to 1.548, a spread of 1.091, more than four times wider.
TrustLens AI moves from "most robust" (0.948, by recall) to "least robust"
(0.457, by calibration) depending purely on which reported metric is used
for the same development-to-locked-test comparison. One Hospitality venue
(Mouse_lodging_Vicente) shows RRR > 1: the model performed *better* under
the harder, doubly-stressed condition (unseen venue and future period)
than under the easier, single-stress condition (unseen venue only), an
honest anomaly, not a modelling error, that a single scalar summary would
either hide or misreport as "no degradation."

## Why this happens

"Robustness" is not one construct. Each project's own governance framing
already distinguishes several logically separate threats: TrustLens
separates discrimination (recall, balanced accuracy) from calibration
(ECE); the GHG module separates cost uncertainty from abatement-potential
uncertainty; Hospitality separates temporal generalisation (same venues,
future dates) from spatial generalisation (new venues). A single retention
ratio necessarily collapses one of these axes and silently privileges
whichever metric was chosen, which is exactly the failure mode that this
portfolio's existing governance layers (TrustLens's locked precedence
rules, the GHG module's rank-reversal analysis) were built to avoid within
a single domain. Naively porting a scalar summary *across* domains
reintroduces the same failure mode at a higher level.

## Implication for a cross-domain trustworthy-AI evaluation framework

A defensible cross-domain robustness benchmark cannot be a single number
per system. Based on this synthesis, a minimal adequate summary would need
to report a small **vector** of named, domain-appropriate retention
scores, at minimum: (1) a discrimination/accuracy-based score, (2) a
calibration-based score, and (3) a generalisation-axis score (temporal,
spatial, or parameter-uncertainty, whichever is domain-appropriate), and
present them together rather than aggregated. Any single-number leaderboard
comparing "how robust" different systems or domains are should be treated
with the same scepticism this portfolio already applies to single-point
accuracy claims.

## Limitations

- This synthesis uses three research prototypes built by one author with
  related design philosophies; it does not sample the space of possible
  ML systems or domains, and the specific numeric spread reported here
  (0.248 naive vs. 1.091 with alternatives) is illustrative of the
  phenomenon, not a general-purpose estimate of "how much" metric choice
  matters.
- Only one alternative comparison per domain was tested where available;
  a fuller study would enumerate all defensible within-domain comparisons
  systematically rather than selecting one.
- This is a synthesis of already-published, already-locked numbers from
  each project's own prior evaluation; it is not a new predictive model
  or a new dataset, and its contribution is the cross-domain comparison
  and the honest negative result about metric portability, not new
  primary evidence within any one domain.

## Reproduce

```bash
pip install -e .
python -m unittest discover -s tests -v
cdrs-synthesis --output results.json
python figures/plot_spread.py
```
