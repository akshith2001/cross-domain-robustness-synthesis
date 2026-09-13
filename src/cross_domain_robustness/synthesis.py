"""Cross-domain robustness synthesis: does a single retention ratio generalise?

This script attempts the most natural, simplest possible cross-domain
comparison of "robustness under stress" across three independently developed
research projects (TrustLens AI, the GHG scenario model's optimisation
module, and Hospitality Sustainability AI), using only numbers each project
has already published and locked. It then tests whether that comparison is
robust to the (defensible, non-cherry-picked) choice of which within-domain
comparison counts as "the" stress test — and reports honestly that it is not.

All input numbers below are taken directly from each project's own locked,
published results (research reports / READMEs / rank-reversal analysis
output), not re-estimated or newly measured. Sources are cited inline.
"""

import json


# ---------------------------------------------------------------------------
# Step 1: naive cross-domain Robustness Retention Ratio (RRR)
# RRR = performance under the "harder"/stress condition / performance under
# the "easier"/nominal condition, using the single most natural comparison
# available in each project's own existing, published evaluation design.
# ---------------------------------------------------------------------------

def trustlens_rrr_recall():
    """TrustLens AI: development higher-risk recall -> locked final-test recall.
    Source: TrustLens AI research report, Section 4.2 (Generalisation Gap).
    """
    dev_recall = 0.879
    test_recall = 0.833
    return test_recall / dev_recall


def ghg_rrr_frequency_weighted():
    """GHG optimisation module: frequency-weighted retained abatement.

    The originally selected (0-noise) 5-measure set achieves 2,560 kg
    CO2e/year nominally. Under 1,000 Monte Carlo perturbations of cost and
    abatement within stated uncertainty, each measure survives in the
    optimal set only some fraction of the time (its "selection frequency").
    This computes what fraction of the nominal abatement is retained if we
    weight each measure's contribution by how often it actually remains the
    robust choice.
    Source: ghg-scenario-model rank-reversal analysis, --samples 1000 run.
    """
    measures = {
        "Reduce tap-running time (kitchen)": (620.0, 1.000),
        "Kitchen equipment scheduling optimisation": (260.0, 0.730),
        "Boiler efficiency service and tune": (900.0, 0.972),
        "Waste segregation and recycling programme": (300.0, 0.566),
        "Delivery-route consolidation": (480.0, 1.000),
    }
    nominal_total = sum(abatement for abatement, _ in measures.values())
    weighted_total = sum(abatement * freq for abatement, freq in measures.values())
    return weighted_total / nominal_total, nominal_total, weighted_total


def hospitality_rrr_temporal():
    """Hospitality Sustainability AI: development -> locked final-test MAE.

    Uses the SAME lag-feature model's pooled rolling-development MAE versus
    its locked final-period MAE (lower MAE is better, so this is expressed
    as an inverse-error retention ratio for comparability with the other
    two domains, where higher is better).
    Source: Hospitality Sustainability AI research report, Sections 5.1 and 4.2.
    """
    dev_mae = 111.87
    test_mae = 159.92
    return dev_mae / test_mae  # inverse-error retention: 1.0 = no degradation


# ---------------------------------------------------------------------------
# Step 2: stress-test the comparison itself. Recompute each domain's RRR
# using a DIFFERENT, equally natural and equally non-cherry-picked
# within-domain comparison, and see whether the cross-domain ranking holds.
# ---------------------------------------------------------------------------

def trustlens_rrr_calibration():
    """TrustLens AI: development ECE -> locked final-test ECE (lower is better)."""
    dev_ece = 0.032
    test_ece = 0.070
    return dev_ece / test_ece  # inverse-error retention


def hospitality_rrr_spatial():
    """Hospitality Sustainability AI: unseen-venue-only vs unseen-venue+future-period
    improvement over baseline, for each of the two locked venues separately.
    Source: docs/UNSEEN_VENUE_RESULTS.md and docs/UNSEEN_FUTURE_RESULTS.md.
    """
    venue_only = {"Fox_food_Francesco": 0.548, "Mouse_lodging_Vicente": 0.325}
    venue_and_future = {"Fox_food_Francesco": 0.408, "Mouse_lodging_Vicente": 0.503}
    return {
        venue: venue_and_future[venue] / venue_only[venue]
        for venue in venue_only
    }


def run_synthesis():
    naive = {
        "TrustLens AI (recall, dev→locked test)": trustlens_rrr_recall(),
        "GHG module (frequency-weighted abatement retention)": ghg_rrr_frequency_weighted()[0],
        "Hospitality AI (MAE, rolling-dev→locked test)": hospitality_rrr_temporal(),
    }

    alternative = {
        "TrustLens AI (calibration ECE, dev→locked test)": trustlens_rrr_calibration(),
        "Hospitality AI (spatial generalisation, Fox venue)": hospitality_rrr_spatial()["Fox_food_Francesco"],
        "Hospitality AI (spatial generalisation, Mouse venue)": hospitality_rrr_spatial()["Mouse_lodging_Vicente"],
    }

    return {"naive_single_comparison_rrr": naive, "alternative_comparison_rrr": alternative}


def _cli():
    import argparse
    parser = argparse.ArgumentParser(
        description="Cross-domain robustness synthesis: test whether a single "
        "retention-ratio metric generalises across three independently "
        "evaluated research projects."
    )
    parser.add_argument("--output", type=str, default=None, help="Optional path to write JSON results.")
    args = parser.parse_args()

    summary = run_synthesis()
    text = json.dumps(summary, indent=2)
    print(text)

    naive_vals = list(summary["naive_single_comparison_rrr"].values())
    alt_vals = list(summary["alternative_comparison_rrr"].values())
    print("\nNaive RRR range: {:.3f} to {:.3f} (spread {:.3f})".format(
        min(naive_vals), max(naive_vals), max(naive_vals) - min(naive_vals)
    ))
    print("With alternative within-domain comparisons included, RRR range: {:.3f} to {:.3f} (spread {:.3f})".format(
        min(naive_vals + alt_vals), max(naive_vals + alt_vals), max(naive_vals + alt_vals) - min(naive_vals + alt_vals)
    ))

    if args.output:
        with open(args.output, "w") as f:
            f.write(text)


if __name__ == "__main__":
    _cli()
