from dataclasses import dataclass


@dataclass
class VariableBound:
    """
    Representa los límites de una variable.

    ### atributos:
    - variable: str - Nombre de la variable.
    - lower: float | None - Límite inferior (None = sin límite).
    - upper: float | None - Límite superior (None = sin límite).
    """

    variable: str
    lower: float | None = None
    upper: float | None = None