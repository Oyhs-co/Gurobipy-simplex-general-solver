"""
Módulo para resolver múltiples problemas de programación lineal.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import time

from ..core import LinearProblem, Solution
from ..parser import MultiLPParser
from ..matrix import LPBuilder
from .solver import SolverLP


@dataclass
class ProblemResult:
    """Resultado de resolver un problema individual."""
    problem: LinearProblem
    solution: Solution
    parse_time: float = 0.0
    build_time: float = 0.0
    solve_time: float = 0.0
    total_time: float = 0.0
    error: Optional[str] = None


@dataclass
class MultiSolverResult:
    """Resultado de resolver múltiples problemas."""
    results: List[ProblemResult] = field(default_factory=list)
    total_parse_time: float = 0.0
    total_build_time: float = 0.0
    total_solve_time: float = 0.0
    total_time: float = 0.0

    def get_successful_results(self) -> List[ProblemResult]:
        """Retorna solo los resultados exitosos."""
        return [r for r in self.results if r.error is None]

    def get_failed_results(self) -> List[ProblemResult]:
        """Retorna solo los resultados fallidos."""
        return [r for r in self.results if r.error is not None]


class MultiSolver:
    """Solver para múltiples problemas de programación lineal."""

    def __init__(self):
        self.results: List[ProblemResult] = []

    def solve_all(self, problems: List[LinearProblem]) -> MultiSolverResult:
        """
        Resuelve todos los problemas dados.

        Args:
            problems: Lista de problemas a resolver.

        Returns:
            MultiSolverResult con los resultados de cada problema.
        """
        result = MultiSolverResult()
        overall_start = time.perf_counter()

        for i, problem in enumerate(problems):
            problem_result = self._solve_single(problem, i + 1)
            result.results.append(problem_result)
            result.total_parse_time += problem_result.parse_time
            result.total_build_time += problem_result.build_time
            result.total_solve_time += problem_result.solve_time

        result.total_time = time.perf_counter() - overall_start
        return result

    def _solve_single(
        self, problem: LinearProblem, index: int
    ) -> ProblemResult:
        """Resuelve un solo problema."""
        result = ProblemResult(problem=problem, solution=Solution(
            status="",
            objective_value=None,
            variables={}
        ))

        try:
            # Build
            build_start = time.perf_counter()
            lp = LPBuilder(problem).build()
            result.build_time = time.perf_counter() - build_start

            # Solve
            solve_start = time.perf_counter()
            solver = SolverLP(lp)
            solution = solver.solve()
            result.solution = solution
            result.solve_time = time.perf_counter() - solve_start

            # Total
            result.total_time = (
                result.parse_time +
                result.build_time +
                result.solve_time
            )

        except Exception as e:
            result.error = str(e)
            result.solution.status = f"ERROR: {e}"

        return result

    @staticmethod
    def solve_from_text(text: str) -> MultiSolverResult:
        """
        Parsea y resuelve múltiples problemas desde texto.

        Args:
            text: Texto con múltiples problemas separados por delimitadores.

        Returns:
            MultiSolverResult con los resultados.
        """
        overall_start = time.perf_counter()

        # Parse
        parse_start = time.perf_counter()
        parser = MultiLPParser(text)
        problems = parser.parse_all()
        parse_time = time.perf_counter() - parse_start

        if not problems:
            result = MultiSolverResult()
            result.total_time = time.perf_counter() - overall_start
            return result

        # Solve each problem
        solver = MultiSolver()
        result = solver.solve_all(problems)
        result.total_parse_time = parse_time

        return result
