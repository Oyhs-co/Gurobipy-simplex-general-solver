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
    """

    objective: dict[str, float]
    sense: str
    constraints: list[LinearConstraint]
    variables: list[str]
    bounds: dict[str, VariableBound]
