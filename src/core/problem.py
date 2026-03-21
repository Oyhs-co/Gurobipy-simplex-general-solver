from __future__ import annotations
from dataclasses import dataclass
from .constraint import LinearConstraint
from .bound import VariableBound


@dataclass
class LinearProblem:

    """
    Represents a linear programming problem.

    ### attributes:
    - objective: List[float] - Coefficients of the objective function.
    - sense: str - Optimization direction ("max" or "min").
    - constraints: List[LinearConstraint] - List of linear constraints.
    - name: str - Optional name for the problem.
    """

    objective: dict[str, float]
    sense: str
    constraints: list[LinearConstraint]
    variables: list[str]
    bounds: dict[str, VariableBound]
    name: str = ""
