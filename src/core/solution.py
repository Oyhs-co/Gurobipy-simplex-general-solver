from dataclasses import dataclass


@dataclass
class Solution:
    """
    Represents the solution of a linear programming problem.

    ### attributes:
    - status: str - Status of the solution.
    - objective_value: float | None - Value of the objective function.
    - variables: dict[str, float] - Values of the decision variables.
    """
    status: str
    objective_value: float | None
    variables: dict[str, float]
