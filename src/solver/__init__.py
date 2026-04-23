"""
Modulo de solvers para programacion lineal.
Proporciona interfaz abstracta y implementaciones concretas.
"""

from .base import BaseSolver, SolverStats, SolverRegistry, register_solver
from .gurobi import GurobiSolver
from .multi_solver import MultiSolver, MultiSolverResult, ProblemResult
from .benchmark import BenchmarkRunner, BenchmarkResult, BenchmarkConfig, run_quick_benchmark

SolverLP = GurobiSolver
SolverConfig = GurobiSolver.Config

SolverRegistry.register("gurobi", GurobiSolver, available=True)

try:
    from .highs_solver import HiGHSSolver
    SolverRegistry.register("highs", HiGHSSolver, available=True)
except ImportError as e:
    from .highs_solver import HiGHSSolver
    SolverRegistry.register("highs", HiGHSSolver, available=False)
    SolverRegistry.set_unavailable("highs", f"highspy not available: {e}")

try:
    from .glpk_solver import GLPKSolver
    SolverRegistry.register("glpk", GLPKSolver, available=True)
except ImportError as e:
    from .glpk_solver import GLPKSolver
    SolverRegistry.register("glpk", GLPKSolver, available=False)
    SolverRegistry.set_unavailable("glpk", f"swiglpk not available: {e}")

try:
    from .cbc import CBCSolver
    import pulp
    if "PULP_CBC_CMD" in pulp.listSolvers():
        SolverRegistry.register("cbc", CBCSolver, available=True)
    else:
        SolverRegistry.register("cbc", CBCSolver, available=False)
        SolverRegistry.set_unavailable("cbc", "PULP_CBC_CMD not found")
except ImportError as e:
    from .cbc import CBCSolver
    SolverRegistry.register("cbc", CBCSolver, available=False)
    SolverRegistry.set_unavailable("cbc", f"not available: {e}")

__all__ = [
    "BaseSolver",
    "SolverStats", 
    "SolverRegistry",
    "register_solver",
    "GurobiSolver",
    "CBCSolver",
    "HiGHSSolver",
    "GLPKSolver",
    "SolverLP",
    "SolverConfig",
    "MultiSolver",
    "MultiSolverResult", 
    "ProblemResult",
    "BenchmarkRunner",
    "BenchmarkResult",
    "BenchmarkConfig",
    "run_quick_benchmark"
]