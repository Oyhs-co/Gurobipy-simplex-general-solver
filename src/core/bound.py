from dataclasses import dataclass


@dataclass
class VariableBound:
    variable: str
    lower: float | None = None
    upper: float | None = None
