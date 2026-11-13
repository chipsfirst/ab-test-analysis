import numpy as np
import pytest

from src.experiment import analyze_proportions, bootstrap_mean_diff, holm


def test_analyze_proportions_known_values():
    result = analyze_proportions(success_control=960, n_control=12000,
                                 success_treatment=1140, n_treatment=12000)
    assert result.diff == pytest.approx(0.015, abs=1e-12)
    assert result.p_control == pytest.approx(0.08)
    assert result.p_treatment == pytest.approx(0.095)
    assert result.se == pytest.approx(0.003648, rel=1e-3)
    assert result.z == pytest.approx(4.112, rel=1e-2)
    assert result.p_value < 1e-4
    assert result.ci_low < result.diff < result.ci_high
    assert result.relative_lift == pytest.approx(0.1875, rel=1e-9)
    assert 0 < result.cohens_h < 0.1


def test_no_difference_gives_zero_z():
    result = analyze_proportions(100, 1000, 100, 1000)
    assert result.diff == 0
    assert result.z == 0
    assert result.p_value == pytest.approx(1.0)
    assert result.ci_low < 0 < result.ci_high


def test_invalid_group_size():
    with pytest.raises(ValueError):
        analyze_proportions(10, 0, 10, 100)


def test_bootstrap_is_reproducible_and_detects_shift():
    rng = np.random.default_rng(1)
    control = rng.normal(100, 15, 2000)
    treatment = rng.normal(105, 15, 2000)

    first = bootstrap_mean_diff(treatment, control, iterations=500, seed=7)
    second = bootstrap_mean_diff(treatment, control, iterations=500, seed=7)

    assert first == pytest.approx(second)
    assert first[0] < 5 < first[1]
    assert first[0] > 0


def test_holm_matches_manual_example():
    adjusted = holm([0.01, 0.04, 0.03])
    assert adjusted == pytest.approx([0.03, 0.06, 0.06])


def test_holm_caps_at_one():
    adjusted = holm([0.5, 0.9])
    assert np.all(adjusted <= 1.0)


def test_holm_rejects_bad_input():
    with pytest.raises(ValueError):
        holm([])
    with pytest.raises(ValueError):
        holm([0.1, 1.2])
