"""
Solver de programación lineal usando Gurobi Optimizer.
"""

from dataclasses import dataclass, field
from typing import Optional
import gurobipy as gp
from gurobipy import GRB
import polars as pl

from ..matrix import PolarsLP
from ..core import Solution
from ..core.exceptions import LPInfeasibleError, LPUnboundedError, LPError


@dataclass
class SolverConfig:
    """Configuración del solver Gurobi."""
    verbose: bool = False
    time_limit: Optional[float] = None
    mip_gap: Optional[float] = None
    threads: Optional[int] = None
    method: int = -1
    presolve: int = 1
    display_interval: int = 1

    def apply(self, model: gp.Model) -> None:
        """Aplica la configuración al modelo."""
        model.setParam("OutputFlag", 1 if self.verbose else 0)
        
        if self.time_limit is not None:
            model.setParam("TimeLimit", self.time_limit)
        if self.mip_gap is not None:
            model.setParam("MIPGap", self.mip_gap)
        if self.threads is not None:
            model.setParam("Threads", self.threads)
        if self.method != -1:
            model.setParam("Method", self.method)
        if self.presolve != 1:
            model.setParam("Presolve", self.presolve)
        if self.display_interval != 1:
            model.setParam("DisplayInterval", self.display_interval)


class SolverLP:
    """
    Solver de programación lineal usando Gurobi Optimizer.

    ### atributos:
    - lp: PolarsLP - El problema de PL a resolver.
    - model: gp.Model - El modelo de Gurobi.
    - config: SolverConfig - Configuración del solver.
    """

    def __init__(self, lp: PolarsLP, config: Optional[SolverConfig] = None):
        """
        Inicializa el solver con un problema de PL.

        Args:
            lp: PolarsLP - El problema de PL a resolver.
            config: SolverConfig - Configuración del solver (default: config por defecto).
        """
        self.lp = lp
        self.config = config or SolverConfig()
        self.model = gp.Model("LP")
        self.config.apply(self.model)
        self.iis_constraints: list[str] = []
        self.iis_variables: list[str] = []

    def solve(self) -> Solution:
        """
        Resuelve el problema de programación lineal.

        Returns:
            Solution: Objeto con el estado, valores y metadatos de la solución.
        """
        self._build_model()

        self.model.optimize()

        return self._extract_solution()

    def diagnose_infeasibility(self) -> dict:
        """
        Diagnostica la causa de infactibilidad usando IIS.

        Un IIS (Irreducible Infeasible Set) es el subconjunto más pequeño
        de restricciones que sigue siendo infactible.

        Returns:
            dict: Diccionario con información del IIS.
        """
        self._build_model()

        self.model.optimize()

        if self.model.status != GRB.INFEASIBLE:
            return {
                "is_infeasible": False,
                "message": "El modelo es factible"
            }

        self.model.computeIIS()

        iis_constraints = []
        for constr in self.model.getConstrs():
            if constr.iisconstr:
                iis_constraints.append(constr.constrName)

        iis_variables = []
        for var in self.model.getVars():
            if var.iisvar:
                iis_variables.append(var.varName)

        self.iis_constraints = iis_constraints
        self.iis_variables = iis_variables

        return {
            "is_infeasible": True,
            "iis_constraints": iis_constraints,
            "iis_variables": iis_variables,
            "message": f"IIS encontrado: {len(iis_constraints)} restricciones, {len(iis_variables)} variables"
        }

    def _build_model(self) -> None:
        """Construye el modelo de Gurobi desde la representación PL."""
        bounds_map: dict[str, tuple[float | None, float | None]] = {}
        for row in self.lp.bounds.iter_rows(named=True):
            bounds_map[row["variable"]] = (row.get("lower"), row.get("upper"))

        variables: dict[str, gp.Var] = {}
        all_vars: set[str] = set()

        for row in self.lp.objective.iter_rows(named=True):
            all_vars.add(row["variable"])
        for row in self.lp.coefficients.iter_rows(named=True):
            all_vars.add(row["variable"])
        all_vars.update(bounds_map.keys())

        for var_name in sorted(all_vars):
            lb, ub = bounds_map.get(var_name, (None, None))

            if lb is None and ub is None and var_name not in bounds_map:
                lb = 0.0
                ub = GRB.INFINITY
            elif lb is None and ub is None:
                lb = -GRB.INFINITY
                ub = GRB.INFINITY
            else:
                lb = 0.0 if lb is None else lb
                ub = GRB.INFINITY if ub is None else ub

            variables[var_name] = self.model.addVar(
                vtype=GRB.CONTINUOUS,
                lb=lb,
                ub=ub,
                name=var_name
            )

        self.model.update()

        objective_expr = gp.LinExpr()
        for row in self.lp.objective.iter_rows(named=True):
            var_name = row["variable"]
            coeff = row["coefficient"]
            objective_expr += coeff * variables[var_name]

        sense = GRB.MAXIMIZE if self.lp.sense.lower() == "max" else GRB.MINIMIZE
        self.model.setObjective(objective_expr, sense)

        for row in self.lp.constraints.iter_rows(named=True):
            constraint_expr = gp.LinExpr()
            coeff_filter = self.lp.coefficients.filter(
                pl.col("constraint") == row["constraint"]
            )
            for coeff_row in coeff_filter.iter_rows(named=True):
                var_name = coeff_row["variable"]
                coeff = coeff_row["coefficient"]
                constraint_expr += coeff * variables[var_name]

            if row["sense"] == "<=":
                self.model.addConstr(
                    constraint_expr <= row["rhs"],
                    name=row["constraint"]
                )
            elif row["sense"] == ">=":
                self.model.addConstr(
                    constraint_expr >= row["rhs"],
                    name=row["constraint"]
                )
            elif row["sense"] == "=":
                self.model.addConstr(
                    constraint_expr == row["rhs"],
                    name=row["constraint"]
                )

    def _extract_solution(self) -> Solution:
        """Extrae la solución del modelo de Gurobi."""
        if self.model.status == GRB.OPTIMAL:
            return self._extract_optimal_solution()
        elif self.model.status == GRB.INFEASIBLE:
            return self._extract_infeasible_solution()
        elif self.model.status == GRB.UNBOUNDED:
            return self._extract_unbounded_solution()
        else:
            return Solution(
                status=f"STATUS_{self.model.status}",
                objective_value=None,
                variables={},
                iterations=int(self.model.IterCount),
                nodes=int(self.model.NodeCount)
            )

    def _extract_optimal_solution(self) -> Solution:
        """Extrae la solución óptima con valores duales y costos reducidos."""
        var_values = {}
        reduced_costs = {}

        for var in self.model.getVars():
            var_values[var.varName] = var.x
            rc = var.rc
            if abs(rc) > 1e-10:
                reduced_costs[var.varName] = rc

        dual_values = {}
        for constr in self.model.getConstrs():
            pi = constr.pi
            if abs(pi) > 1e-10:
                dual_values[constr.constrName] = pi

        if self.config.verbose:
            self._print_solution(var_values, self.model.objVal)

        return Solution(
            status="OPTIMAL",
            objective_value=self.model.objVal,
            variables=var_values,
            dual_values=dual_values if dual_values else None,
            reduced_costs=reduced_costs if reduced_costs else None,
            iterations=int(self.model.IterCount),
            nodes=int(self.model.NodeCount)
        )

    def _extract_infeasible_solution(self) -> Solution:
        """Extrae solución para problema infactible."""
        if self.config.verbose:
            print("Estado: El modelo es infactible")

        iis_info = self.diagnose_infeasibility()

        return Solution(
            status="INFEASIBLE",
            objective_value=None,
            variables={}
        )

    def _extract_unbounded_solution(self) -> Solution:
        """Extrae solución para problema no acotado."""
        if self.config.verbose:
            print("Estado: El modelo es no acotado")

        return Solution(
            status="UNBOUNDED",
            objective_value=None,
            variables={}
        )

    def _print_solution(self, var_values: dict[str, float], obj_val: float) -> None:
        """Imprime la solución (solo cuando verbose=True)."""
        print(f"Valor óptimo: {obj_val:.2f}")
        for var, value in sorted(var_values.items()):
            print(f"{var} = {value:.2f}")