"""Fórmulas físicas preliminares (PROJECT_SPEC.md §8). Funciones puras, sin dependencias.

Las usa scripts/fetch_data.py para precalcular, y scoring.py (Fase 2) las reutilizará.
Son aproximaciones para prefactibilidad: NO son un estudio de ingeniería.
"""
from typing import Iterable, Optional

PERFORMANCE_RATIO = 0.80      # PR base (spec §8), aproximación
NOCT_DELTA_C = 20.0           # Tcell = Tamb + 20 (spec §8)
TEMP_COEFF = 0.004            # pérdida por °C sobre 25 °C (spec §8)


def solar_kwh_per_kwp_year(ghi_kwh_m2_day: Optional[float], temp_mean_c: Optional[float]) -> Optional[float]:
    """Generación FV específica estimada (kWh/kWp/año)."""
    if ghi_kwh_m2_day is None or temp_mean_c is None:
        return None
    t_cell = temp_mean_c + NOCT_DELTA_C
    temp_factor = 1 - TEMP_COEFF * (t_cell - 25)
    return ghi_kwh_m2_day * 365 * PERFORMANCE_RATIO * temp_factor


def air_density_kg_m3(elevation_m: Optional[float]) -> Optional[float]:
    """Densidad del aire por altitud (atmósfera estándar, spec §8)."""
    if elevation_m is None:
        return None
    return 1.225 * (1 - 2.25577e-5 * elevation_m) ** 4.25588


def wind_power_density_w_m2(wind_speed_ms: Optional[float], rho: Optional[float]) -> Optional[float]:
    """0.5·rho·v³ con la velocidad MEDIA. Índice de recurso, no energía de turbina.

    Usar la media subestima la densidad de potencia real (que depende de la distribución
    de velocidades). Sirve para comparar celdas entre sí, no como valor absoluto.
    """
    if wind_speed_ms is None or rho is None:
        return None
    return 0.5 * rho * wind_speed_ms ** 3


def min_max_0_100(values: Iterable[Optional[float]]) -> list:
    """Normaliza a 0-100 entre las celdas con dato; None se conserva como None."""
    vals = list(values)
    present = [v for v in vals if v is not None]
    if not present:
        return [None for _ in vals]
    lo, hi = min(present), max(present)
    if hi == lo:
        return [None if v is None else 50.0 for v in vals]
    return [None if v is None else round(100 * (v - lo) / (hi - lo), 1) for v in vals]
