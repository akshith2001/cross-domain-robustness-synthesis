import unittest

from cross_domain_robustness.synthesis import (
    trustlens_rrr_recall,
    trustlens_rrr_calibration,
    ghg_rrr_frequency_weighted,
    hospitality_rrr_temporal,
    hospitality_rrr_spatial,
    run_synthesis,
)


class TestIndividualRRRComputations(unittest.TestCase):
    def test_trustlens_recall_rrr_matches_source_numbers(self):
        # 0.833 / 0.879 from the TrustLens AI research report, Section 4.2
        self.assertAlmostEqual(trustlens_rrr_recall(), 0.833 / 0.879, places=6)

    def test_trustlens_calibration_rrr_matches_source_numbers(self):
        self.assertAlmostEqual(trustlens_rrr_calibration(), 0.032 / 0.070, places=6)

    def test_ghg_frequency_weighted_nominal_total_matches_published_figure(self):
        rrr, nominal_total, weighted_total = ghg_rrr_frequency_weighted()
        # The optimizer's own published result: 5 measures, 2,560 kg CO2e/year nominal
        self.assertAlmostEqual(nominal_total, 2560.0, places=1)
        self.assertLess(weighted_total, nominal_total)
        self.assertAlmostEqual(rrr, weighted_total / nominal_total, places=6)

    def test_hospitality_temporal_rrr_matches_source_numbers(self):
        self.assertAlmostEqual(hospitality_rrr_temporal(), 111.87 / 159.92, places=6)

    def test_hospitality_spatial_rrr_both_venues_present(self):
        result = hospitality_rrr_spatial()
        self.assertIn("Fox_food_Francesco", result)
        self.assertIn("Mouse_lodging_Vicente", result)
        self.assertAlmostEqual(result["Fox_food_Francesco"], 0.408 / 0.548, places=6)
        self.assertAlmostEqual(result["Mouse_lodging_Vicente"], 0.503 / 0.325, places=6)


class TestCoreClaim(unittest.TestCase):
    """These tests directly verify the paper's central claim: that including
    an equally valid alternative comparison widens the cross-domain RRR
    range substantially relative to the naive single-comparison range."""

    def test_naive_range_is_narrower_than_full_range(self):
        summary = run_synthesis()
        naive_vals = list(summary["naive_single_comparison_rrr"].values())
        alt_vals = list(summary["alternative_comparison_rrr"].values())
        naive_spread = max(naive_vals) - min(naive_vals)
        full_spread = max(naive_vals + alt_vals) - min(naive_vals + alt_vals)
        self.assertGreater(
            full_spread, naive_spread,
            "Including alternative comparisons should widen, not narrow, the observed RRR range."
        )

    def test_full_spread_is_at_least_double_naive_spread(self):
        # A conservative, round-number version of the paper's headline claim
        # (observed: naive spread 0.248, full spread 1.091 — more than 4x).
        summary = run_synthesis()
        naive_vals = list(summary["naive_single_comparison_rrr"].values())
        alt_vals = list(summary["alternative_comparison_rrr"].values())
        naive_spread = max(naive_vals) - min(naive_vals)
        full_spread = max(naive_vals + alt_vals) - min(naive_vals + alt_vals)
        self.assertGreaterEqual(full_spread, 2 * naive_spread)

    def test_trustlens_ranking_flips_between_metrics(self):
        # TrustLens should rank as the MOST robust naive domain, but its own
        # alternative (calibration) score should be the single LOWEST value
        # across both naive and alternative results — i.e. its ranking flips.
        summary = run_synthesis()
        naive = summary["naive_single_comparison_rrr"]
        alt = summary["alternative_comparison_rrr"]
        trustlens_naive_key = "TrustLens AI (recall, dev→locked test)"
        trustlens_alt_key = "TrustLens AI (calibration ECE, dev→locked test)"

        self.assertEqual(max(naive, key=naive.get), trustlens_naive_key)

        all_vals = {**naive, **alt}
        self.assertEqual(min(all_vals, key=all_vals.get), trustlens_alt_key)

    def test_at_least_one_alternative_exceeds_unity(self):
        # The Mouse_lodging_Vicente venue should show RRR > 1 (performance
        # improved under the harder condition) — an honest anomaly the
        # synthesis explicitly reports rather than hides.
        summary = run_synthesis()
        alt_vals = list(summary["alternative_comparison_rrr"].values())
        self.assertTrue(any(v > 1.0 for v in alt_vals))


class TestReproducibility(unittest.TestCase):
    def test_run_synthesis_is_deterministic(self):
        s1 = run_synthesis()
        s2 = run_synthesis()
        self.assertEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()
