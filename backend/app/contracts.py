"""Contratos de API (ver docs/CONTRACTS.md). Dueño: P1. Cambios => avisar al equipo."""
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

Quality = Literal["real", "aproximado", "sintetico"]


class Weights(BaseModel):
    solar: float = Field(ge=0, le=1)
    wind: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def at_least_one(self):
        if self.solar + self.wind <= 0:
            raise ValueError("al menos un peso debe ser > 0")
        return self

    def normalized(self) -> dict:
        total = self.solar + self.wind
        return {"solar": self.solar / total, "wind": self.wind / total}


class ScoresRequest(BaseModel):
    weights: Weights


class Scenario(BaseModel):
    """Parámetros económicos (USD). None = no informado => resultado 'No calculable', nunca inventado."""
    system_kwp: float = Field(gt=0, le=10000)
    cost_per_kwp_usd: Optional[float] = Field(default=None, ge=0)
    energy_value_usd_kwh: Optional[float] = Field(default=None, ge=0)
    self_consumption_pct: float = Field(default=100, ge=0, le=100)
    om_usd_year: Optional[float] = Field(default=None, ge=0)
    export_value_usd_kwh: Optional[float] = Field(default=None, ge=0)


class SimulateRequest(Scenario):
    cell_id: str = Field(min_length=1)


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    selected_cell_id: Optional[str] = Field(default=None, min_length=1)
    weights: Weights
    scenario: Optional[Scenario] = None
