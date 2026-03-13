import polars as pl
from ..core import LinearProblem
from .matrix import PolarsLP


class LPBuilder:
    """
    Builds a linear programming problem from a text representation.
    """

    def __init__(self, problem: LinearProblem) -> None:
        """
        Initializes the LPBuilder with the provided text.

        ### parameters:
        - txt: str - Text representation of the linear programming problem.
       """
        self.problem = problem

    def build(self) -> PolarsLP:

        objective = self._build_objective()
        coefficients = self._build_coefficients()
        constraints = self._build_constraints()
        bounds = self._build_bounds()

        return PolarsLP(
            objective=objective,
            coefficients=coefficients,
            constraints=constraints,
            bounds=bounds,
            sense=self.problem.sense
        )

    def _build_objective(self) -> pl.DataFrame:

        rows: list[dict[str, str | float]] = []

        for var, coeff in self.problem.objective.items():
            rows.append({"variable": var, "coefficient": coeff})

        return pl.DataFrame(rows)

    def _build_coefficients(self) -> pl.DataFrame:
        rows: list[dict[str, str | float]] = []

        for i, constraint in enumerate(self.problem.constraints):

            cname = f"c{i+1}"

            for var, coeff in constraint.coefficients.items():
                rows.append({
                    "constraint": cname,
                    "variable": var,
                    "coefficient": coeff
                })

        return pl.DataFrame(rows)

    def _build_constraints(self) -> pl.DataFrame:
        rows: list[dict[str, str | float]] = []

        for i, constraint in enumerate(self.problem.constraints):

            cname = f"c{i+1}"

            rows.append({
                "constraint": cname,
                "sense": constraint.sense,
                "rhs": constraint.rhs
            })

        return pl.DataFrame(rows)

    def _build_bounds(self) -> pl.DataFrame:
        rows: list[dict[str, str | float | None]] = []

        for var, bound in self.problem.bounds.items():
            rows.append({
                "variable": var,
                "lower": bound.lower,
                "upper": bound.upper
            })

        return pl.DataFrame(rows)
