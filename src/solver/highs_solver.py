"""
Solver HiGHS para problemas de programacion lineal.
Implementacion usando highspy (interfaz nativa a HiGHS).
"""

import time
from typing import Optional

import highspy

from ..core import LinearProblem, Solution
from ..matrix import PolarsLP
from .base import BaseSolver, SolverStats


class HiGHSSolver(BaseSolver):
    """Solver HiGHS para problemas de programacion lineal."""
    
    def __init__(self, model: PolarsLP, config: Optional[BaseSolver.Config] = None):
        self.model = model
        self.config = config or self.Config()
        self._solution: Optional[Solution] = None
        self._linear_problem: Optional[LinearProblem] = None
    
    @property
    def solver_name(self) -> str:
        return "highs"
    
    def solver_version(self) -> str:
        return "highspy"
    
    def set_problem(self, problem: LinearProblem) -> None:
        """Establece el problema a resolver."""
        self._linear_problem = problem
    
    def solve(self) -> Solution:
        """Resuelve el problema."""
        problem = self._linear_problem
        
        if problem is None and self.model is not None:
            from ..matrix import LPBuilder
            lp_builder = LPBuilder(self.model)
            problem = lp_builder._problem
        
        if problem is None:
            return Solution(
                status="ERROR: No problem set",
                objective_value=None,
                variables={},
            )
        
        start_time = time.perf_counter()
        
        try:
            variables_list = list(problem.variables)
            num_vars = len(variables_list)
            
            hp = highspy.Highs()
            
            INF = 1e30
            
            for var in variables_list:
                bound = problem.bounds.get(var)
                
                lb = 0.0 if not bound or bound.lower is None else bound.lower
                ub = INF if not bound or bound.upper is None else bound.upper
                
                hp.addVar(lb, ub)
            
            cost_map = problem.objective
            for i, var in enumerate(variables_list):
                cost = cost_map.get(var, 0)
                if cost != 0:
                    hp.changeColCost(i, cost)
            
            for constraint in problem.constraints:
                indices = []
                values = []
                
                for var, coeff in constraint.coefficients.items():
                    var_idx = variables_list.index(var)
                    indices.append(var_idx)
                    values.append(coeff)
                
                num_nz = len(indices)
                indices_arr = indices
                values_arr = values
                
                if constraint.sense in ("<=", "<"):
                    hp.addRow(-INF, constraint.rhs, num_nz, indices_arr, values_arr)
                elif constraint.sense in (">=", ">"):
                    hp.addRow(constraint.rhs, INF, num_nz, indices_arr, values_arr)
                else:
                    hp.addRow(constraint.rhs, constraint.rhs, num_nz, indices_arr, values_arr)
            
            if problem.sense.lower() == "max":
                hp.changeObjectiveSense(highspy.ObjSense.kMaximize)
            
            hp.run()
            
            solve_time = time.perf_counter() - start_time
            
            model_status = hp.getModelStatus()
            
            if model_status == highspy.HighsModelStatus.kOptimal:
                status = "OPTIMAL"
            elif model_status == highspy.HighsModelStatus.kInfeasible:
                status = "INFEASIBLE"
            elif model_status == highspy.HighsModelStatus.kUnbounded:
                status = "UNBOUNDED"
            else:
                status = str(model_status)
            
            variables = {}
            
            if status == "OPTIMAL":
                solution = hp.getSolution()
                for i, var in enumerate(variables_list):
                    variables[var] = solution.col_value[i]
            
            self._solution = Solution(
                status=status,
                objective_value=hp.getObjectiveValue() if status == "OPTIMAL" else None,
                variables=variables,
            )
            
            return self._solution
            
        except Exception as e:
            return Solution(
                status=f"ERROR: {str(e)}",
                objective_value=None,
                variables={},
            )
    
    def get_stats(self) -> SolverStats:
        """Obtiene estadisticas de la resolucion."""
        return SolverStats()