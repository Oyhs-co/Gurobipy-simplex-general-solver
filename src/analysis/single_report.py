"""
Módulo de análisis para problemas de programación lineal.
Reporte académico profesional usando fpdf2.
Utiliza BaseReport y builders del módulo analysis.
"""

from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any

import tempfile
import os

from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

from ..core import LinearProblem, LinearConstraint, Solution
from ..visualization import FeasibleRegionVisualization
from .base import BaseReport, ReportBuilder
from .builders.cover import CoverBuilder
from .builders.summary import SummaryBuilder
from .builders.problem_data import ProblemDataBuilder
from .builders.optimal_solution import OptimalSolutionBuilder
from .builders.slack_analysis import SlackAnalysisBuilder
from .builders.sensitivity_analysis import SensitivityAnalysisBuilder
from .builders.iis_section import IISSectionBuilder


PAGE_WIDTH = 215.9
PAGE_HEIGHT = 279.4
MARGIN = 15
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN


class ReporteAcademico(FPDF):
    """Clase PDF para reportes académicos."""
    
    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, "ISLA LP Analysis Report", align='C', new_y=YPos.NEXT)
        self.ln(2)
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.3)
        self.line(MARGIN, self.get_y(), PAGE_WIDTH - MARGIN, self.get_y())
        self.ln(3)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(100, 100, 100)
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 10, f"Página {self.page_no()} | {fecha}", align='C')


@dataclass
class ExecutionTimes:
    parse_time: float = 0.0
    build_time: float = 0.0
    solve_time: float = 0.0
    visualize_time: float = 0.0
    pdf_time: float = 0.0
    total_time: float = 0.0


class LPAnalysis(BaseReport):
    """
    Genera reportes académicos profesionales para problemas de programación lineal.
    Implementa BaseReport y utiliza builders para cada sección.
    """
    
    def __init__(self, problem: LinearProblem, solution: Solution, 
                 times: Optional[ExecutionTimes] = None,
                 system_info: Optional[Dict] = None,
                 solver_name: str = "gurobi"):
        super().__init__(problem, solution, "report.pdf")
        self.times = times or ExecutionTimes()
        self.system_info = system_info if system_info is not None else {}
        self.solver_name = solver_name
        self.page_count = 0
        self.pdf = None
    
    def build(self) -> None:
        """
        Construye la estructura completa del reporte usando builders.
        """
        if self.pdf is None:
            self.pdf = ReporteAcademico()
            self.pdf.set_margins(MARGIN, MARGIN, MARGIN)
            self.pdf.set_auto_page_break(auto=True, margin=15)
        
        # Portada
        self.pdf.add_page()
        self.page_count += 1
        CoverBuilder(self).build()
        
        # Resumen ejecutivo
        self.pdf.add_page()
        self.page_count += 1
        SummaryBuilder(self).build()
        
        # Datos del problema
        self.pdf.add_page()
        self.page_count += 1
        ProblemDataBuilder(self).build()
        
        # Solución óptima
        self.pdf.add_page()
        self.page_count += 1
        OptimalSolutionBuilder(self).build()
        
        # Análisis de holguras y sensibilidad
        if len(self.problem.variables) == 2:
            self.pdf.add_page()
            self.page_count += 1
            SensitivityAnalysisBuilder(self).build()
        
        # Sección IIS si es infactible
        if not self.solution.is_optimal():
            self.pdf.add_page()
            self.page_count += 1
            IISSectionBuilder(self).build()
    
    def save(self) -> None:
        """
        Guarda el reporte en el archivo de salida.
        """
        if self.pdf:
            self.pdf.output(self.output_path)
    
    def generate_pdf(self, output_path: str) -> None:
        """
        Genera el reporte académico completo (método legacy).
        
        Args:
            output_path: Ruta del archivo PDF de salida.
        """
        self.output_path = output_path
        self.generate()
