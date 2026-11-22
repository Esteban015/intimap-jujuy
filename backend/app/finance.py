"""Simulación solar preliminar (USD). Función pura; única implementación (la usan /api/simulate y el asistente).

  annual_kwh        = system_kwp × solar_kwh_kwp_year            (indicador de Fase 1: GHI·365·0,80·factor T)
  capex_usd         = system_kwp × cost_per_kwp_usd
  self_consumed_kwh = annual_kwh × self_consumption_pct / 100
  surplus_kwh       = annual_kwh − self_consumed_kwh               (sin valor salvo export_value_usd_kwh explícito)
  gross_savings     = self_consumed_kwh × energy_value_usd_kwh  (+ surplus_kwh × export_value_usd_kwh si se informa)
  net_savings       = gross_savings − om_usd_year                  (om no declarado => se toma 0 y se advierte)
  simple_payback    = capex_usd / net_savings                       solo si net_savings > 0

Recuperación SIMPLE: no es VAN, TIR ni rentabilidad garantizada.
"""
from typing import Optional

NC = "No calculable"

LIMITATIONS = [
    "Recuperación simple: sin VAN, TIR, inflación, financiamiento ni variaciones tarifarias.",
    "Sin degradación de paneles, reemplazo de inversor ni baterías.",
    "Sin costos de conexión, permisos ni sombreado del sitio.",
    "Producción estimada con datos climatológicos de baja resolución (~28 km a 1°).",
    "No define ángulo de montaje, altura ni aptitud estructural del terreno.",
]


def _r(v: Optional[float], nd: int = 0):
    return None if v is None else round(v, nd)


def simulate_solar(solar_kwh_kwp_year: Optional[float], s) -> dict:
    """s: contracts.Scenario. Devuelve resultados + motivos de 'No calculable' + advertencias."""
    results, not_calc, warnings = {}, {}, []

    if solar_kwh_kwp_year is None:
        for k in ("annual_kwh", "self_consumed_kwh", "surplus_kwh", "capex_usd", "gross_savings_usd_year",
                  "net_savings_usd_year", "simple_payback_years"):
            results[k] = None
            not_calc[k] = "la celda no tiene indicador solar (dato faltante)"
        return _pack(s, results, not_calc, warnings)

    annual = s.system_kwp * solar_kwh_kwp_year
    self_c = annual * s.self_consumption_pct / 100
    surplus = annual - self_c
    results.update(annual_kwh=_r(annual), self_consumed_kwh=_r(self_c), surplus_kwh=_r(surplus))

    capex = None if s.cost_per_kwp_usd is None else s.system_kwp * s.cost_per_kwp_usd
    results["capex_usd"] = _r(capex)
    if capex is None:
        not_calc["capex_usd"] = "falta el costo por kWp"

    export_value = 0.0
    if surplus > 0:
        if s.export_value_usd_kwh is None:
            warnings.append("Los excedentes no se valorizan: no se informó tarifa de inyección.")
        else:
            export_value = surplus * s.export_value_usd_kwh
            warnings.append("Los excedentes se valorizan con la tarifa de inyección informada por el usuario.")
    results["export_value_usd_year"] = _r(export_value, 2)

    if s.energy_value_usd_kwh is None:
        gross = None
        not_calc["gross_savings_usd_year"] = "falta el valor de la energía (USD/kWh)"
    else:
        gross = self_c * s.energy_value_usd_kwh + export_value
    results["gross_savings_usd_year"] = _r(gross, 2)

    om = s.om_usd_year
    if om is None:
        warnings.append("Mantenimiento no declarado: se tomó 0 USD/año; el ahorro neto puede estar sobreestimado.")
        om = 0.0
    results["om_usd_year"] = _r(om, 2)
    net = None if gross is None else gross - om
    results["net_savings_usd_year"] = _r(net, 2)
    if net is None:
        not_calc["net_savings_usd_year"] = "falta el ahorro bruto"

    if capex is None or net is None:
        results["simple_payback_years"] = None
        not_calc["simple_payback_years"] = "faltan costo de instalación o valor de la energía"
    elif net <= 0:
        results["simple_payback_years"] = None
        not_calc["simple_payback_years"] = "el ahorro neto anual es cero o negativo"
    else:
        results["simple_payback_years"] = _r(capex / net, 1)

    return _pack(s, results, not_calc, warnings)


def _pack(s, results, not_calc, warnings) -> dict:
    return {
        "inputs": s.model_dump(),
        "currency": "USD",
        "results": results,
        "not_calculable": not_calc,
        "warnings": warnings,
        "limitations": LIMITATIONS,
        "formulas": {
            "annual_kwh": "system_kwp × solar_kwh_kwp_year",
            "capex_usd": "system_kwp × cost_per_kwp_usd",
            "self_consumed_kwh": "annual_kwh × self_consumption_pct / 100",
            "gross_savings_usd_year": "self_consumed_kwh × energy_value_usd_kwh (+ excedente × tarifa de inyección, si se informa)",
            "net_savings_usd_year": "gross_savings_usd_year − om_usd_year",
            "simple_payback_years": "capex_usd / net_savings_usd_year (solo si > 0)",
        },
        "disclaimer": "Escenario hipotético editable. No es una cotización, tarifa oficial ni garantía de rentabilidad.",
    }
