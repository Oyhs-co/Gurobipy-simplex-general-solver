"""
Solver CBC (COIN-OR) para problemas de programacion lineal.
Implementacion usando PuLP.
"""

import time
from typing import Optional

import pulp
from pulp import LpProblem, LpVariable, LpMinimize, LpMaximize, LpBinary, LpContinuous, LpStatus

from ..core import LinearProblem, Solution, VariableBound
from ..matrix import PolarsLP
from .base import BaseSolver, SolverStats


class CBCSolver(BaseSolver):
    """Solver CBC para problemas de programacion lineal."""
    
    def __init__(self, model: PolarsLP, config: Optional[BaseSolver.Config] = None):
        self.model = model
        self.config = config or self.Config()
        self._solution: Optional[Solution] = None
        self._problem_obj: Optional[LinearProblem] = None
    
    @property
    def solver_name(self) -> str:
        return "cbc"
    
    def solver_version(self) -> str:
        try:
            return f"PuLP {pulp.__version__}"
        except:
            return "PuLP"
    
    def set_problem(self, problem: LinearProblem) -> None:
        """Establece el problema a resolver."""
        self._problem_obj = problem
    
    def _build_problem(self, problem: LinearProblem) -> 'LpProblem':
        """Construye el problema PuLP."""
        sense = LpMaximize if problem.sense.lower() == "max" else LpMinimize
        prob = LpProblem("LP", sense)
        
        variables = {}
        for var in problem.variables:
            bound = problem.bounds.get(var)
            
            lb = 0
            ub = None
            
            if bound:
                if bound.lower is not None:
                    lb = bound.lower
                if bound.upper is not None:
                    ub = bound.upper
            
            variables[var] = LpVariable(var, lowBound=lb, upBound=ub, cat=LpContinuous)
        
        terms = []
        for var in problem.variables:
            coeff = problem.objective.get(var, 0)
            if coeff != 0:
                terms.append(coeff * variables[var])
        
        if terms:
            prob += sum(terms), "Objetivo"
        
        for i, constraint in enumerate(problem.constraints):
            expr = sum(
                coeff * variables[var]
                for var, coeff in constraint.coefficients.items()
            )
            
            if constraint.sense in ("<=", "<"):
                prob += (expr <= constraint.rhs), f"c{i}"
            elif constraint.sense in (">=", ">"):
                prob += (expr >= constraint.rhs), f"c{i}"
            else:
                prob += (expr == constraint.rhs), f"c{i}"
        
        return prob
    
    def solve(self) -> Solution:
        """Resuelve el problema."""
        if self._problem_obj is None:
            return Solution(
                status="ERROR: No problem set",
                objective_value=None,
                variables={},
            )
        
        start_time = time.perf_counter()
        
        try:
            prob = self._build_problem(self._problem_obj)
            
            solver = pulp.PULP_CBC_CMD(msg=self.config.verbose)
            
            prob.solve(solver)
            
            solve_time = time.perf_counter() - start_time
            
            status_map = {
                "Optimal": "OPTIMAL",
                "Not Solved": "NOT_SOLVED",
                "Infeasible": "INFEASIBLE",
                "Unbounded": "UNBOUNDED",
                "Undefined": "UNDEFINED",
            }
            status = status_map.get(LpStatus[prob.status], str(prob.status))
            
            variables = {}
            
            if status == "OPTIMAL":
                for var in prob.variables():
                    if var.varValue is not None:
                        variables[var.name] = var.varValue
            
            self._solution = Solution(
                status=status,
                objective_value=pulp.value(prob.objective),
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