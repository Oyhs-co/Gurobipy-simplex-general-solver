from dataclasses import dataclass, field
from typing import Optional
from .constants import OPTIMALITY_TOLERANCE

@dataclass
class Solution:
    """
    Representa la solución de un problema de programación lineal.
    
    ### Atributos:
    - status: str - Estado de la solución (OPTIMAL, INFEASIBLE, UNBOUNDED, etc.)
    - objective_value: float | None - Valor de la función objetivo en el óptimo.
    - variables: dict[str, float] - Valores de las variables de decisión.
    - dual_values: dict[str, float] - Precios sombra para restricciones (opcional).
    - reduced_costs: dict[str, float] - Costos reducidos para variables (opcional).
    - iterations: int - Número de iteraciones del simplex (opcional).
    - nodes: int - Número de nodos branch-and-bound (opcional).
    """
    status: str
    objective_value: Optional[float]
    variables: dict[str, float]
    dual_values: Optional[dict[str, float]] = None
    reduced_costs: Optional[dict[str, float]] = None
    iterations: int = 0
    nodes: int = 0

    def is_optimal(self) -> bool:
        """Verifica si la solución es óptima usando tolerancia."""
        return self.status.strip().upper() == "OPTIMAL"

    def is_infeasible(self) -> bool:
        """Verifica si el problema es infactible."""
        return self.status == "INFEASIBLE"

    def is_unbounded(self) -> bool:
        """Verifica si el problema es no acotado."""
        return self.status == "UNBOUNDED"

    def has_errors(self) -> bool:
        """Verifica si hubo un error durante la resolución."""
        return self.status.startswith("ERROR")

    def print_summary(self, verbose: bool = False) -> str:
        """
        Genera un resumen formateado de la solución.

        Args:
            verbose: Si es True, incluye valores duales y costos reducidos.

        Returns:
            str: Cadena formateada con el resumen de la solución.
        """
        lines = []
        lines.append(f"Estado: {self.status}")

        if self.objective_value is not None:
            lines.append(f"Valor objetivo: {self.objective_value:.4f}")

        if self.variables:
            lines.append("Variables:")
            for var, value in sorted(self.variables.items()):
                lines.append(f"  {var} = {value:.4f}")

        if verbose:
            if self.reduced_costs:
                lines.append("Costos reducidos:")
                for var, cost in sorted(self.reduced_costs.items()):
                    lines.append(f"  {var}: {cost:.4f}")

            if self.dual_values:
                lines.append("Precios sombra (dual):")
                for constr, price in sorted(self.dual_values.items()):
                    lines.append(f"  {constr}: {price:.4f}")

            if self.iterations > 0:
                lines.append(f"Iteraciones: {self.iterations}")
            if self.nodes > 0:
                lines.append(f"Nodos: {self.nodes}")

        return "\n".join(lines)

    def __str__(self) -> str:
        """Representación en cadena de la solución."""
        if self.status == "OPTIMAL" and self.objective_value is not None:
            vars_str = ", ".join(
                f"{k}={v:.2f}" for k, v in sorted(self.variables.items())
            )
            return f"OPTIMAL: Z={self.objective_value:.4f} ({vars_str})"
        return f"{self.status}"