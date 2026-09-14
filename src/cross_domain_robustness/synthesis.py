"""Reproducible cross-domain robustness-retention synthesis."""

from __future__ import annotations

import argparse
import json
from importlib.resources import files
from pathlib import Path
from typing import Iterable


def load_source_metrics() -> dict:
    """Load the versioned inputs and their provenance."""
    resource = files("cross_domain_robustness").joinpath("source_metrics.json")
    return json.loads(resource.read_text(encoding="utf-8"))


def retention_ratio(easier: float, harder: float, *, lower_is_better: bool = False) -> float:
    """Return performance retained under a harder condition."""
    if easier <= 0 or harder <= 0:
        raise ValueError("retention-ratio inputs must be strictly positive")
    return easier / harder if lower_is_better else harder / easier


def trustlens_rrr_recall() -> float:
    values = load_source_metrics()["trustlens"]["recall"]
    return retention_ratio(values["development"], values["locked_test"])


def trustlens_rrr_calibration() -> float:
    values = load_source_metrics()["trustlens"]["ece"]
    return retention_ratio(values["development"], values["locked_test"], lower_is_better=True)


def ghg_rrr_frequency_weighted() -> tuple[float, float, float]:
    measures = load_source_metrics()["ghg"]["selected_measures"]
    nominal_total = sum(item["abatement_kg_co2e"] for item in measures)
    weighted_total = sum(
        item["abatement_kg_co2e"] * item["selection_frequency"] for item in measures
    )
    return weighted_total / nominal_total, nominal_total, weighted_total


def hospitality_rrr_temporal() -> float:
    values = load_source_metrics()["hospitality"]["mae"]
    return retention_ratio(values["rolling_development"], values["locked_test"], lower_is_better=True)


def hospitality_rrr_spatial() -> dict[str, float]:
    venues = load_source_metrics()["hospitality"]["spatial_improvement_over_baseline"]
    return {
        venue: retention_ratio(values["unseen_venue"], values["unseen_venue_and_future"])
        for venue, values in venues.items()
    }


def describe_range(values: Iterable[float]) -> dict[str, float]:
    values = list(values)
    if not values:
        raise ValueError("at least one value is required")
    low, high = min(values), max(values)
    return {"minimum": low, "maximum": high, "spread": high - low}


def run_synthesis() -> dict:
    naive = {
        "TrustLens AI (recall, development to locked test)": trustlens_rrr_recall(),
        "GHG module (frequency-weighted abatement retention)": ghg_rrr_frequency_weighted()[0],
        "Hospitality AI (MAE, rolling development to locked test)": hospitality_rrr_temporal(),
    }
    alternative = {
        "TrustLens AI (calibration ECE, development to locked test)": trustlens_rrr_calibration(),
        "Hospitality AI (spatial generalisation, Fox venue)": hospitality_rrr_spatial()["Fox_food_Francesco"],
        "Hospitality AI (spatial generalisation, Mouse venue)": hospitality_rrr_spatial()["Mouse_lodging_Vicente"],
    }
    naive_range = describe_range(naive.values())
    full_range = describe_range([*naive.values(), *alternative.values()])
    return {
        "naive_single_comparison_rrr": naive,
        "alternative_comparison_rrr": alternative,
        "diagnostics": {
            "naive_range": naive_range,
            "full_range": full_range,
            "spread_multiplier": full_range["spread"] / naive_range["spread"],
        },
    }


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Run the cross-domain robustness synthesis.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()
    rendered = json.dumps(run_synthesis(), indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    _cli()
