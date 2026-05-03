"""
Módulo de builders para reportes de análisis.
Todos los builders usan styles.py, tables.py y utils.py centralizados.
"""

from .cover import CoverBuilder
from .summary import SummaryBuilder
from .problem_data import ProblemDataBuilder
from .optimal_solution import OptimalSolutionBuilder
from .slack_analysis import SlackAnalysisBuilder
from .sensitivity_analysis import SensitivityAnalysisBuilder
from .iis_section import IISSectionBuilder
from .convergence import ConvergenceBuilder
from .comparison_charts import ComparisonChartsBuilder
from .system_info import SystemInfoBuilder

__all__ = [
    "CoverBuilder",
    "SummaryBuilder",
    "ProblemDataBuilder",
    "OptimalSolutionBuilder",
    "SlackAnalysisBuilder",
    "SensitivityAnalysisBuilder",
    "IISSectionBuilder",
    "ConvergenceBuilder",
    "ComparisonChartsBuilder",
    "SystemInfoBuilder",
]
