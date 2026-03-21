import gurobipy as gp
from gurobipy import GRB
import polars as pl
from ..matrix import PolarsLP
from ..core import Solution


class SolverLP:
    def __init__(self, lp: PolarsLP):
        self.lp = lp
        self.model = gp.Model("LP")

    def solve(self) -> Solution:
        """Resuelve el problema y devuelve la solucion."""
        # Construir mapa de restricciones de variables (bounds)
        bounds_map: dict[str, tuple[float | None, float | None]] = {}
        for row in self.lp.bounds.iter_rows(named=True):
            bounds_map[row["variable"]] = (row.get("lower"), row.get("upper"))

        # Crear variables
        variables: dict[str, gp.Var] = {}
        all_vars = set()
        for row in self.lp.objective.iter_rows(named=True):
            all_vars.add(row["variable"])
        for row in self.lp.coefficients.iter_rows(named=True):
            all_vars.add(row["variable"])
        all_vars.update(bounds_map.keys())

        for var_name in sorted(all_vars):
            lb, ub = bounds_map.get(var_name, (None, None))

            # Por defecto, las variables son no negativas (lb=0)
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

        # Establecer funcion objetivo
        objective_expr = gp.LinExpr()
        for row in self.lp.objective.iter_rows(named=True):
            var_name = row["variable"]
            coeff = row["coefficient"]
            objective_expr += coeff * variables[var_name]

        sense = GRB.MAXIMIZE if self.lp.sense.lower() == "max" else GRB.MINIMIZE
        self.model.setObjective(objective_expr, sense)

        # Agregar restricciones
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

        # Optimizar el modelo
        self.model.optimize()

        # Crear y devolver objeto Solution
        if self.model.status == GRB.OPTIMAL:
            print(f"Valor optimo: {self.model.objVal:.2f}")
            var_values = {}
            for var in self.model.getVars():
                print(f"{var.varName} = {var.x:.2f}")
                var_values[var.varName] = var.x
            return Solution(
                status="OPTIMAL",
                objective_value=self.model.objVal,
                variables=var_values
            )
        elif self.model.status == GRB.INFEASIBLE:
            print("El modelo es infactible.")
            return Solution(
                status="INFEASIBLE",
                objective_value=None,
                variables={}
            )
        elif self.model.status == GRB.UNBOUNDED:
            print("El modelo es no acotado.")
            return Solution(
                status="UNBOUNDED",
                objective_value=None,
                variables={}
            )
        else:
            print(f"Estado: {self.model.status}")
            return Solution(
                status=f"STATUS_{self.model.status}",
                objective_value=None,
                variables={}
            )
