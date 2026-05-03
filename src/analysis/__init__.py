"""
Módulo de análisis para problemas de programación lineal.
"""

from .base import BaseReport, ReportBuilder
from .styles import COLORS, FONTS, LAYOUT, CHART_COLORS
from .tables import draw_dataframe_table, format_numeric_column
from .utils import get_system_info, format_number
from .builders.cover import CoverBuilder
from .builders.summary import SummaryBuilder
from .builders.problem_data import ProblemDataBuilder
from .builders.optimal_solution import OptimalSolutionBuilder
from .builders.slack_analysis import SlackAnalysisBuilder
from .builders.sensitivity_analysis import SensitivityAnalysisBuilder
from .builders.iis_section import IISSectionBuilder
from .builders.convergence import ConvergenceBuilder
from .builders.comparison_charts import ComparisonChartsBuilder
from .builders.system_info import SystemInfoBuilder
from .multi_analysis import MultiLPAnalysis
from .benchmark_results import (
    BenchmarkVisualizer, 
    ResultsExporter, 
    export_benchmark_results,
)
from .benchmark_report import BenchmarkReport

__all__ = [
    "BaseReport",
    "ReportBuilder",
    "COLORS",
    "FONTS",
    "LAYOUT",
    "CHART_COLORS",
    "draw_dataframe_table",
    "format_numeric_column",
    "get_system_info",
    "format_number",
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
    "MultiLPAnalysis", 
    "BenchmarkVisualizer",
    "ResultsExporter",
    "export_benchmark_results",
    "BenchmarkReport"
]
