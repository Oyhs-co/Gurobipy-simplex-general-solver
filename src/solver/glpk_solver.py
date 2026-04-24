"""
Solver GLPK para problemas de programacion lineal.
Implementacion usando swiglpk (interfaz nativa a GLPK).
"""

import time
from typing import Optional
from ctypes import POINTER, c_int, c_double

import swiglpk

from ..core import LinearProblem, Solution
from ..matrix import PolarsLP
from .base import BaseSolver, SolverStats


class GLPKSolver(BaseSolver):
    """Solver GLPK para problemas de programacion lineal."""
    
    def __init__(self, model: PolarsLP, config: Optional[BaseSolver.Config] = None):
        self.model = model
        self.config = config or self.Config()
        self._solution: Optional[Solution] = None
        self._linear_problem: Optional[LinearProblem] = None
        self._iterations = 0
        self._nodes = 0
    
    @property
    def solver_name(self) -> str:
        return "glpk"
    
    def solver_version(self) -> str:
        return "swiglpk"
    
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
        
        prob = None
        try:
            variables_list = list(problem.variables)
            num_vars = len(variables_list)
            
            if problem.sense.lower() == "max":
                prob = swiglpk.glp_create_prob()
                swiglpk.glp_set_prob_name(prob, "LP")
                swiglpk.glp_set_obj_dir(prob, swiglpk.GLP_MAX)
            else:
                prob = swiglpk.glp_create_prob()
                swiglpk.glp_set_prob_name(prob, "LP")
                swiglpk.glp_set_obj_dir(prob, swiglpk.GLP_MIN)
            
            swiglpk.glp_add_cols(prob, num_vars)
            
            for i, var in enumerate(variables_list):
                swiglpk.glp_set_col_name(prob, i + 1, var)
                
                bound = problem.bounds.get(var)
                
                if bound:
                    if bound.lower is not None and bound.upper is not None:
                        swiglpk.glp_set_col_bnds(prob, i + 1, swiglpk.GLP_DB, bound.lower, bound.upper)
                    elif bound.lower is not None:
                        swiglpk.glp_set_col_bnds(prob, i + 1, swiglpk.GLP_LO, bound.lower, 0.0)
                    elif bound.upper is not None:
                        swiglpk.glp_set_col_bnds(prob, i + 1, swiglpk.GLP_UP, 0.0, bound.upper)
                    else:
                        swiglpk.glp_set_col_bnds(prob, i + 1, swiglpk.GLP_FR, 0.0, 0.0)
                else:
                    swiglpk.glp_set_col_bnds(prob, i + 1, swiglpk.GLP_LO, 0.0, 0.0)
                
                coeff = problem.objective.get(var, 0)
                swiglpk.glp_set_obj_coef(prob, i + 1, coeff)
            
            num_constraints = len(problem.constraints)
            swiglpk.glp_add_rows(prob, num_constraints)
            
            ia = []
            ja = []
            ar = []
            
            for i, constraint in enumerate(problem.constraints):
                row_idx = i + 1
                
                swiglpk.glp_set_row_name(prob, row_idx, f"r{i}")
                
                if constraint.sense in ("<=", "<"):
                    swiglpk.glp_set_row_bnds(prob, row_idx, swiglpk.GLP_UP, 0.0, constraint.rhs)
                elif constraint.sense in (">=", ">"):
                    swiglpk.glp_set_row_bnds(prob, row_idx, swiglpk.GLP_LO, constraint.rhs, 0.0)
                else:
                    swiglpk.glp_set_row_bnds(prob, row_idx, swiglpk.GLP_FX, constraint.rhs, constraint.rhs)
                
                for var, coeff in constraint.coefficients.items():
                    var_idx = variables_list.index(var) + 1
                    ia.append(row_idx)
                    ja.append(var_idx)
                    ar.append(float(coeff))
            
            if ia:
                n = len(ia)
                ia_arr = swiglpk.intArray(n + 1)
                ja_arr = swiglpk.intArray(n + 1)
                ar_arr = swiglpk.doubleArray(n + 1)
                for i in range(n):
                    ia_arr[i + 1] = ia[i]
                    ja_arr[i + 1] = ja[i]
                    ar_arr[i + 1] = ar[i]
                swiglpk.glp_load_matrix(prob, n, ia_arr, ja_arr, ar_arr)
            
            smcp = swiglpk.glp_smcp()
            swiglpk.glp_init_smcp(smcp)
            smcp.msg_lev = swiglpk.GLP_MSG_OFF if not self.config.verbose else swiglpk.GLP_MSG_ALL
            
            swiglpk.glp_simplex(prob, smcp)
            
            solve_time = time.perf_counter() - start_time
            
            status = swiglpk.glp_get_status(prob)
            
            status_map = {
                swiglpk.GLP_OPT: "OPTIMAL",
                swiglpk.GLP_FEAS: "FEASIBLE",
                swiglpk.GLP_INFEAS: "INFEASIBLE",
                swiglpk.GLP_NOFEAS: "NOFEAS",
                swiglpk.GLP_UNBND: "UNBOUNDED",
                swiglpk.GLP_UNDEF: "UNDEFINED",
            }
            status_str = status_map.get(status, "UNKNOWN")
            
            variables = {}
            
            if status_str == "OPTIMAL":
                for i, var in enumerate(variables_list):
                    variables[var] = swiglpk.glp_get_col_prim(prob, i + 1)
                
                obj_value = swiglpk.glp_get_obj_val(prob)
                try:
                    self._iterations = swiglpk.glp_get_simplex_itcnt(prob)
                except:
                    self._iterations = 0
            else:
                obj_value = None
            
            swiglpk.glp_delete_prob(prob)
            
            self._solution = Solution(
                status=status_str,
                objective_value=obj_value,
                variables=variables,
            )
            
            return self._solution
            
        except Exception as e:
            if prob is not None:
                try:
                    swiglpk.glp_delete_prob(prob)
                except:
                    pass
            
            return Solution(
                status=f"ERROR: {str(e)}",
                objective_value=None,
                variables={},
            )
    
    def get_stats(self) -> SolverStats:
        """Obtiene estadisticas de la resolucion."""
        return SolverStats(
            iterations=self._iterations,
            nodes=self._nodes
        )