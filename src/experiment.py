"""Статистические расчёты для анализа A/B-теста.

Функции вынесены из ноутбука, чтобы их можно было покрыть тестами
и переиспользовать.
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class ProportionResult:
    p_control: float
    p_treatment: float
    n_control: int
    n_treatment: int
    diff: float
    se: float
    z: float
    p_value: float
    ci_low: float
    ci_high: float
    relative_lift: float
    cohens_h: float


def analyze_proportions(success_control, n_control, success_treatment, n_treatment, alpha=0.05):
    """Двусторонний z-тест для разницы долей с доверительным интервалом."""
    if n_control <= 0 or n_treatment <= 0:
        raise ValueError('размеры групп должны быть положительными')

    p_control = success_control / n_control
    p_treatment = success_treatment / n_treatment
    diff = p_treatment - p_control

    variance = (p_control * (1 - p_control) / n_control
                + p_treatment * (1 - p_treatment) / n_treatment)
    se = float(np.sqrt(variance))
    z = float(diff / se) if se > 0 else 0.0
    p_value = float(2 * stats.norm.sf(abs(z)))

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    ci_low = float(diff - z_alpha * se)
    ci_high = float(diff + z_alpha * se)

    relative_lift = float(diff / p_control) if p_control > 0 else float('nan')
    cohens_h = float(2 * np.arcsin(np.sqrt(p_treatment)) - 2 * np.arcsin(np.sqrt(p_control)))

    return ProportionResult(
        p_control=p_control,
        p_treatment=p_treatment,
        n_control=int(n_control),
        n_treatment=int(n_treatment),
        diff=float(diff),
        se=se,
        z=z,
        p_value=p_value,
        ci_low=ci_low,
        ci_high=ci_high,
        relative_lift=relative_lift,
        cohens_h=cohens_h,
    )


def bootstrap_mean_diff(a, b, iterations=2000, seed=42, alpha=0.05):
    """Бутстрэп-интервал для разницы средних: a − b."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size == 0 or b.size == 0:
        raise ValueError('выборки не должны быть пустыми')

    rng = np.random.default_rng(seed)
    diffs = np.empty(iterations)
    for i in range(iterations):
        diffs[i] = (a[rng.integers(0, a.size, a.size)].mean()
                    - b[rng.integers(0, b.size, b.size)].mean())
    return tuple(float(v) for v in np.percentile(diffs, [alpha / 2 * 100, (1 - alpha / 2) * 100]))


def holm(pvalues):
    """Поправка Холма — Бонферрони; возвращает скорректированные p-value."""
    pvalues = np.asarray(pvalues, dtype=float)
    if pvalues.ndim != 1 or pvalues.size == 0:
        raise ValueError('нужен непустой одномерный массив p-value')
    if np.any((pvalues < 0) | (pvalues > 1)):
        raise ValueError('p-value должны быть в диапазоне [0, 1]')

    order = np.argsort(pvalues)
    m = pvalues.size
    adjusted = np.empty(m)
    running = 0.0
    for rank, index in enumerate(order):
        value = (m - rank) * pvalues[index]
        running = max(running, value)
        adjusted[index] = min(1.0, running)
    return adjusted
