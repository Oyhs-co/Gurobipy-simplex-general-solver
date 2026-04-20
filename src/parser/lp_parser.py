"""
Parser para problemas de programación lineal en formato texto.
"""

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
    Parser para problemas de programación lineal desde texto.

    ### atributos:
    - txt: str - Texto con la definición del problema de PL.
    - bounds: dict[str, VariableBound] - Diccionario de límites de variables.
    """

    def __init__(self, txt: str) -> None:
        """
        Inicializa el parser con el texto del problema.

        Args:
            txt: str - Texto con la definición del problema de PL.
        """
        self.txt = txt
        self.bounds: dict[str, VariableBound] = {}

    def parse(self) -> LinearProblem:
        """
        Parsea el problema de PL desde el texto proporcionado.

        Returns:
            LinearProblem: Instancia representando el problema parseado.

        Raises:
            ValueError: Si el formato es inválido.
        """

        lines = self.txt.strip().splitlines()
        objective_line = lines[0].strip()

        if not objective_line:
            raise ValueError("Falta la función objetivo")

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

        variables = sorted({
            *self._extract_variables(objective_coeffs, constraints),
            *self.bounds.keys()
        })

        if not objective_coeffs:
            raise ValueError("La función objetivo no puede estar vacía")

        if not constraints:
            raise ValueError("Se requiere al menos una restricción")

        return LinearProblem(
            objective=objective_coeffs,
            sense=sense,
            constraints=constraints,
            variables=variables,
            bounds=self.bounds
        )

    def _parse_objective(self, line: str) -> tuple[str, dict[str, float]]:
        """Parsea la función objetivo."""
        parts = line.split(maxsplit=1)

        if len(parts) != 2:
            raise ValueError(f"Función objetivo inválida: {line}")

        sense = parts[0].replace(":", "").lower()

        if sense not in {"max", "min"}:
            raise ValueError(f"Dirección de optimización inválida: {sense}")

        expr = parts[1]

        if "=" in expr:
            expr = expr.split("=", 1)[1]

        coefficients = self._parse_linear_expression(expr)

        return sense, coefficients

    def _parse_constraint(self, line: str) -> LinearConstraint:
        """Parsea una restricción."""
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
            raise ValueError(f"Restricción inválida: {line}")

        coefficients = self._parse_linear_expression(lhs.strip())

        try:
            rhs_value = float(rhs.strip())
        except ValueError:
            raise ValueError(f"Valor RHS inválido en restricción: {line}")

        return LinearConstraint(
            coefficients=coefficients,
            rhs=rhs_value,
            sense=sense
        )

    def _extract_variables(self,
                       objective: dict[str, float],
                       constraints: list[LinearConstraint]
                       ) -> list[str]:
        """Extrae todas las variables del problema."""
        variables: set[str] = set(objective.keys())

        for constraint in constraints:
            variables.update(constraint.coefficients.keys())

        return sorted(variables)

    def _parse_linear_expression(self, expr: str) -> dict[str, float]:
        """Parsea una expresión lineal."""
        if not expr.strip():
            raise ValueError("Expresión lineal vacía")

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
                raise ValueError(f"Término inválido: {term}")

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
        """Verifica si la línea es un bound."""
        return (
            BOUND_SIMPLE.match(line)
            or BOUND_DOUBLE.match(line)
            or BOUND_FREE.match(line)
        ) is not None

    def _parse_bound(self, line: str) -> None:
        """Parsea un bound de variable."""
        free_match = BOUND_FREE.match(line)

        if free_match:
            var = free_match.group(1)
            self.bounds[var] = VariableBound(variable=var,
                                             lower=None,
                                             upper=None)
            return

        line = line.replace(" ", "")

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

        match = BOUND_DOUBLE.match(line)

        if match:
            lower, var, upper = match.groups()

            bound = self.bounds.get(var, VariableBound(var))

            bound.lower = float(lower)
            bound.upper = float(upper)

            self.bounds[var] = bound

            return

        raise ValueError(f"Formato de bound inválido: {line}")