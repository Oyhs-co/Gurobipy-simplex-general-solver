"""
Módulo core para el solver de programación lineal.
"""

from __future__ import annotations
from dataclasses import dataclass
from .constraint import LinearConstraint
from .bound import VariableBound


@dataclass
class LinearProblem:
    """
    Representa un problema de programación lineal.

    ### atributos:
    - objective: dict[str, float] - Coeficientes de la función objetivo.
    - sense: str - Dirección de optimización ("max" o "min").
    - constraints: list[LinearConstraint] - Lista de restricciones lineales.
    - variables: list[str] - Lista de nombres de variables.
    - bounds: dict[str, VariableBound] - Límites de cada variable.
    - name: str - Nombre opcional del problema.
    """

    objective: dict[str, float]
    sense: str
    constraints: list[LinearConstraint]
    variables: list[str]
    bounds: dict[str, VariableBound]
    name: str = ""