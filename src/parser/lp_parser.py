from ..core import LinearProblem, LinearConstraint, VariableBound
import re

TERM_PATTERN = re.compile(
    r"([+-]?\d*\.?\d*)([a-zA-Z][a-zA-Z0-9_]*)"
)
BOUND_SIMPLE = re.compile(r"([a-zA-Z]\w*)(<=|>=)(-?\d+\.?\d*)")
BOUND_DOUBLE = re.compile(r"(-?\d+\.?\d*)<=([a-zA-Z]\w*)<=(-?\d+\.?\d*)")
BOUND_FREE = re.compile(r"([a-zA-Z]\w*)\s+(free|unrestricted)", re.IGNORECASE)
BOUND_LEFT = re.compile(r"(-?\d+\.?\d*)<=([a-zA-Z]\w*)")


class LPParser:

    """
    Perse a linear programming problem from a text representation.
    """

    def __init__(self, txt: str) -> None:
        """
        Parses a linear programming problem from a text representation.

        ### parameters:
        - txt: str - Text representation of the linear programming problem.

       """
        self.txt = txt
        self.bounds: dict[str, VariableBound] = {}

    def parse(self) -> LinearProblem:
        """
        Parses the linear programming problem from the provided text.
        ### returns:
        - LinearProblem: An instance of LinearProblem representing
        the parsed problem.
        """

        lines = self.txt.strip().splitlines()
        objective_line = lines[0].strip()

        if not objective_line:
            raise ValueError("Objective function is missing")

        sense, objective_coeffs = self._parse_objective(objective_line)

        constraints: list[LinearConstraint] = []

        for line in lines[1:]:
            line = line.split('#', 1)[0].strip()
            if not line or line.startswith("#"):
                continue
            if self._is_bound(line):
                self._parse_bound(line)
                continue
            constraint = self._parse_constraint(line.strip())
            constraints.append(constraint)

        # agregar variables que solo aparecen en bounds
        variables = sorted({
            *self._extract_variables(objective_coeffs, constraints),
            *self.bounds.keys()
        })

        if not objective_coeffs:
            raise ValueError("Objective function cannot be empty")

        if not constraints:
            raise ValueError("At least one constraint is required")

        return LinearProblem(
            objective=objective_coeffs,
            sense=sense,
            constraints=constraints,
            variables=variables,
            bounds=self.bounds
        )

    def _parse_objective(self, line: str) -> tuple[str, dict[str, float]]:

        parts = line.split(maxsplit=1)

        if len(parts) != 2:
            raise ValueError(f"Invalid objective function: {line}")

        sense = parts[0].replace(":", "").lower()

        if sense not in {"max", "min"}:
            raise ValueError(f"Invalid optimization direction: {sense}")

        expr = parts[1]

        if "=" in expr:
            expr = expr.split("=", 1)[1]

        coefficients = self._parse_linear_expression(expr)

        return sense, coefficients

    def _parse_constraint(self, line: str) -> LinearConstraint:

        if "<=" in line:
            lhs, rhs = line.split("<=", 1)
            sense = "<="
        elif ">=" in line:
            lhs, rhs = line.split(">=", 1)
            sense = ">="
        elif "=" in line:
            lhs, rhs = line.split("=", 1)
            sense = "="
        else:
            raise ValueError(f"Invalid constraint: {line}")

        coefficients = self._parse_linear_expression(lhs.strip())

        try:
            rhs_value = float(rhs.strip())
        except ValueError:
            raise ValueError(f"Invalid RHS value in constraint: {line}")

        return LinearConstraint(
            coefficients=coefficients,
            rhs=rhs_value,
            sense=sense
        )

    def _extract_variables(self,
                           objective: dict[str, float],
                           constraints: list[LinearConstraint]
                           ) -> list[str]:

        variables: set[str] = set(objective.keys())

        for constraint in constraints:
            variables.update(constraint.coefficients.keys())

        return sorted(variables)

    def _parse_linear_expression(self, expr: str) -> dict[str, float]:
        if not expr.strip():
            raise ValueError("Empty linear expression")

        expr = expr.replace(" ", "").lstrip("+")
        expr = expr.replace("-", "+-")

        terms = expr.split("+")
        coefficients: dict[str, float] = {}

        for term in terms:

            term = term.strip()
            if not term:
                continue

            match = TERM_PATTERN.fullmatch(term)

            if not match:
                print("DEBUG TERM:", term)
                raise ValueError(f"Invalid term: {term}")

            coeff_str, var = match.groups()

            if coeff_str in ("", "+"):
                coeff = 1.0
            elif coeff_str == "-":
                coeff = -1.0
            else:
                coeff = float(coeff_str)

            coefficients[var] = coefficients.get(var, 0) + coeff

        return coefficients

    def _is_bound(self, line: str) -> bool:
        return (
            BOUND_SIMPLE.match(line)
            or BOUND_DOUBLE.match(line)
            or BOUND_FREE.match(line)
        ) is not None

    def _parse_bound(self, line: str) -> None:

        free_match = BOUND_FREE.match(line)

        if free_match:
            var = free_match.group(1)
            self.bounds[var] = VariableBound(variable=var,
                                             lower=None,
                                             upper=None)
            return

        line = line.replace(" ", "")

        # Caso: x >= 0
        match = BOUND_SIMPLE.match(line)

        if match:
            var, op, value = match.groups()
            value = float(value)

            bound = self.bounds.get(var, VariableBound(var))

            if op == ">=":
                bound.lower = value
            else:
                bound.upper = value

            self.bounds[var] = bound

            return

        match = BOUND_LEFT.match(line)

        if match:
            lower, var = match.groups()
            bound = self.bounds.get(var, VariableBound(var))
            bound.lower = float(lower)
            self.bounds[var] = bound
            return

        # Caso: 0 <= x <= 10
        match = BOUND_DOUBLE.match(line)

        if match:
            lower, var, upper = match.groups()

            bound = self.bounds.get(var, VariableBound(var))

            bound.lower = float(lower)
            bound.upper = float(upper)

            self.bounds[var] = bound

            return

        raise ValueError(f"Invalid bound format: {line}")
