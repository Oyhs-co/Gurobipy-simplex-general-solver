"""
Modulo de analisis para problemas de programacion lineal.
Reporte academico profesional usando fpdf2.
"""

from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import tempfile
import os
import platform
import sys

from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

from ..core import LinearProblem, Solution


PAGE_WIDTH = 215.9
PAGE_HEIGHT = 279.4
MARGIN = 20


@dataclass
class ExecutionTimes:
    parse_time: float = 0.0
    build_time: float = 0.0
    solve_time: float = 0.0
    visualize_time: float = 0.0
    pdf_time: float = 0.0
    total_time: float = 0.0


class LPAnalysis:
    """Genera reportes academicos profesionales para problemas de programacion lineal."""

    def __init__(self, problem: LinearProblem, solution: Solution, 
                 times: Optional[ExecutionTimes] = None):
        self.problem = problem
        self.solution = solution
        self.times = times or ExecutionTimes()
        self.page_count = 0

    def generate_pdf(self, output_path: str) -> None:
        """Genera un reporte academico completo."""
        pdf = ReporteAcademico()
        pdf.set_margins(MARGIN, MARGIN, MARGIN)
        pdf.set_auto_page_break(auto=True, margin=15)
        
        pdf.add_page()
        self.page_count += 1
        self._build_portada(pdf)
        
        pdf.add_page()
        self.page_count += 1
        self._build_header(pdf)
        self._build_resumen_ejecutivo(pdf)
        self._build_detalles_tecnicos(pdf)
        
        pdf.add_page()
        self.page_count += 1
        self._build_header(pdf)
        self._build_datos_problema(pdf)
        self._build_funcion_objetivo(pdf)
        self._build_restricciones_tabla(pdf)
        
        pdf.add_page()
        self.page_count += 1
        self._build_header(pdf)
        self._build_solucion_optima(pdf)
        self._build_holgura_dual(pdf)
        self._build_costos_reducidos(pdf)
        
        if len(self.problem.variables) == 2:
            pdf.add_page()
            self.page_count += 1
            self._build_header(pdf)
            self._build_analisis_sensibilidad(pdf)
            self._build_grafico(pdf)
        else:
            pdf.add_page()
            self.page_count += 1
            self._build_header(pdf)
            self._build_analisis_sensibilidad(pdf)
        
        pdf.output(output_path)

    def _build_header(self, pdf: 'ReporteAcademico') -> None:
        """Construye el encabezado."""
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "SOLUCION DE PROGRAMA LINEAL", align=Align.C,
                 new_y=YPos.NEXT)
        
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(3, 8, "Metodo Simplex - Solucionador con Gurobi",
                 align=Align.C, new_y=YPos.NEXT, center=True)
        
        pdf.ln(5)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.8)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)

    def _build_portada(self, pdf: 'ReporteAcademico') -> None:
        """Construye la portada del reporte."""
        pdf.set_font('Helvetica', 'B', 24)
        pdf.set_text_color(0, 51, 102)
        pdf.ln(40)
        pdf.cell(0, 12, "SOLUCION DE PROGRAMA LINEAL", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(10)
        
        pdf.set_font('Helvetica', 'I', 14)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, "Reporte Academico de Optimizacion", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(30)
        
        pdf.set_font('Helvetica', '', 12)
        pdf.set_text_color(60, 60, 60)
        
        tipo = "Maximizacion" if self.problem.sense.lower() == "max" else "Minimizacion"
        pdf.cell(0, 8, f"Tipo de problema: {tipo}", align=Align.C, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 8, f"Numero de variables: {len(self.problem.variables)}", align=Align.C, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 8, f"Numero de restricciones: {len(self.problem.constraints)}", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(30)
        
        pdf.set_font('Helvetica', 'I', 11)
        pdf.set_text_color(100, 100, 100)
        fecha = datetime.now().strftime("%d de %B de %Y")
        pdf.cell(0, 8, f"Fecha de generacion: {fecha}", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(10)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(1)
        pdf.line(PAGE_WIDTH/2 - 40, pdf.get_y(), PAGE_WIDTH/2 + 40, pdf.get_y())
        
        pdf.set_text_color(0, 0, 0)

    def _build_resumen_ejecutivo(self, pdf: 'ReporteAcademico') -> None:
        """Construye el resumen ejecutivo."""
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "Resumen Ejecutivo", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.3)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(2)
        
        pdf.set_fill_color(245, 250, 255)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 32, 'F')
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        
        tipo = "MAXIMIZACION" if self.problem.sense.lower() == "max" else "MINIMIZACION"
        pdf.cell(40, 6, f"Tipo:")
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(60, 6, tipo)
        pdf.set_font('Helvetica', '', 10)
        pdf.ln(6)
        
        pdf.cell(40, 6, f"Variables:")
        pdf.cell(60, 6, f"{len(self.problem.variables)}")
        pdf.ln(6)
        
        pdf.cell(40, 6, f"Restricciones:")
        pdf.cell(60, 6, f"{len(self.problem.constraints)}")
        pdf.ln(6)
        
        pdf.cell(40, 6, f"Estado:")
        if self.solution.status == 'OPTIMAL':
            pdf.set_text_color(0, 128, 0)
            pdf.cell(60, 6, "OPTIMA")
        else:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(60, 6, self.solution.status)
        pdf.ln(6)
        
        pdf.set_text_color(0, 0, 0)
        pdf.cell(40, 6, f"Valor optimo (Z*):")
        pdf.set_text_color(0, 0, 150)
        pdf.set_font('Helvetica', 'B', 10)
        if self.solution.objective_value is not None:
            pdf.cell(60, 6, f"{self.solution.objective_value:,.4f}")
        else:
            pdf.cell(60, 6, "No disponible")
        
        pdf.ln(8)
        pdf.set_text_color(0, 0, 0)

    def _build_detalles_tecnicos(self, pdf: 'ReporteAcademico') -> None:
        """Construye la seccion de detalles tecnicos."""
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "Informacion del Sistema", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.3)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(2)
        
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(60, 60, 60)
        
        pdf.cell(90, 5, f"Python: {sys.version.split()[0]}")
        pdf.cell(90, 5, f"Sistema: {platform.system()} {platform.release()}")
        pdf.ln(4)
        
        pdf.cell(90, 5, f"Procesador: {platform.processor()}", fill=True)
        pdf.cell(90, 5, f"Arquitectura: {platform.machine()}")
        pdf.ln(4)
        
        pdf.cell(90, 5, f"Hostname: {platform.node()}", fill=True)
        fecha_gen = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.cell(90, 5, f"Fecha generacion: {fecha_gen}")
        pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
        
        self._build_analisis_tiempos(pdf)
    
    def _build_analisis_tiempos(self, pdf: 'ReporteAcademico') -> None:
        """Construye la seccion de analisis de tiempos."""
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "Analisis de Tiempos de Ejecucion", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.3)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(2)
        
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 6, 'F')
        
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(87.95, 6, "Etapa", align=Align.C, fill=True)
        pdf.cell(87.95, 6, "Tiempo (s)", align=Align.C, fill=True)
        pdf.ln(6)
        
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 0, 0)
        
        times_data = [
            ("Analisis Lexico/Sintactico", self.times.parse_time),
            ("Construccion del modelo", self.times.build_time),
            ("Resolucion (Gurobi)", self.times.solve_time),
            ("Generacion de visualizaciones", self.times.visualize_time),
            ("Generacion del reporte PDF", self.times.pdf_time),
        ]
        
        for stage, time_val in times_data:
            pdf.cell(87.95, 5, stage, align=Align.L)
            pdf.cell(87.95, 5, f"{time_val:.4f}", align=Align.R)
            pdf.ln(5)
        
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN + 5, pdf.get_y(), PAGE_WIDTH - MARGIN - 5, pdf.get_y())
        pdf.ln(2)
        
        pdf.cell(87.95, 5, "TIEMPO TOTAL DE EJECUCION", align=Align.L)
        pdf.cell(87.95, 5, f"{self.times.total_time:.4f}", align=Align.R)
        
        pdf.ln(5)
        pdf.set_text_color(0, 0, 0)

    def _build_datos_problema(self, pdf: 'ReporteAcademico') -> None:
        """Construye la tabla de datos del problema."""
        
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "DATOS DEL PROBLEMA", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, "Variables del problema:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
        
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(58.6, 7, "Variable", align=Align.C, fill=True)
        pdf.cell(58.6, 7, "Limite Inferior", align=Align.C, fill=True)
        pdf.cell(58.7, 7, "Limite Superior", align=Align.C, fill=True)
        pdf.ln(7)
        
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        
        for var in self.problem.variables:
            bound = self.problem.bounds.get(var)
            lower = "0" if bound is None or bound.lower is None else str(bound.lower)
            upper = "Sin limite" if bound is None or bound.upper is None else str(bound.upper)
            
            pdf.cell(58.6, 6, str(var), align=Align.C)
            pdf.cell(58.6, 6, lower, align=Align.C)
            pdf.cell(58.7, 6, upper, align=Align.C)
            pdf.ln(6)
        
        pdf.ln(5)

    def _build_funcion_objetivo(self, pdf: 'ReporteAcademico') -> None:
        """Construye la seccion de funcion objetivo."""
        
        pdf.ln(3)
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, "Funcion Objetivo:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        sense = "MAXIMIZAR" if self.problem.sense.lower() == "max" else "MINIMIZAR"
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(30, 7, f"Tipo: {sense}")
        pdf.ln()
        
        obj_str = self._format_objective()
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 102, 0)
        pdf.cell(15, 8, "Z =")
        pdf.cell(0, 8, obj_str, new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    def _build_restricciones_tabla(self, pdf: 'ReporteAcademico') -> None:
        """Construye la tabla de restricciones."""
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, "Restricciones del problema:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
        
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(255, 255, 255)
        
        w = [20, 95.9, 25, 35]
        headers = ["#", "Expresion", "Tipo", "RHS"]
        
        for i, h in enumerate(headers):
            pdf.cell(w[i], 7, h, align=Align.C, fill=True)
        pdf.ln(7)
        
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        
        for i, c in enumerate(self.problem.constraints):
            cstr = self._format_constraint(c)
            
            pdf.cell(w[0], 6, str(i + 1), align=Align.C)
            pdf.cell(w[1], 6, cstr[:40], align=Align.C)
            pdf.cell(w[2], 6, c.sense, align=Align.C)
            pdf.cell(w[3], 6, str(c.rhs), align=Align.C)
            pdf.ln(6)
        
        pdf.ln(5)

    def _build_solucion_optima(self, pdf: 'ReporteAcademico') -> None:
        """Construye la seccion de solucion optima."""
        
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "SOLUCION OPTIMA", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(45, 7, "Estado de la solucion: ", align=Align.L)
        
        if self.solution.status == 'OPTIMAL':
            pdf.set_text_color(0, 128, 0)
            pdf.cell(0, 7, "OPTIMA", new_x=XPos.LEFT, new_y=YPos.NEXT)
        else:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 7, self.solution.status, new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.ln(3)
        
        if self.solution.objective_value is not None:
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(0, 0, 150)
            pdf.cell(40, 10, "Valor optimo:")
            pdf.cell(0, 10, f"Z* = {self.solution.objective_value:,.4f}", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.ln(5)
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, "Valores de las variables:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
        
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(58.6, 7, "Variable", align=Align.C, fill=True)
        pdf.cell(58.6, 7, "Valor Optimo", align=Align.C, fill=True)
        pdf.cell(58.7, 7, "Costo Reducido", align=Align.C, fill=True)
        pdf.ln(7)
        
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        
        for var, value in self.solution.variables.items():
            reduced_cost = self.solution.reduced_costs.get(var, 0) if self.solution.reduced_costs else 0
            pdf.cell(58.6, 6, str(var), align=Align.C)
            pdf.cell(58.6, 6, f"{value:.4f}", align=Align.C)
            pdf.cell(58.7, 6, f"{reduced_cost:.4f}", align=Align.C)
            pdf.ln(6)
        
        pdf.ln(5)

    def _build_holgura_dual(self, pdf: 'ReporteAcademico') -> None:
        """Construye el analisis de holgura y precios sombra."""
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "ANALISIS DE HOLGURA Y PRECIOS SOMBRA", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.3)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 6, "Holgura (Slack): cantidad de recurso no utilizado en la restriccion.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.cell(0, 6, "Precio Sombra (Shadow Price): valor marginal de relajar la restriccion por una unidad.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
        
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(255, 255, 255)
        w = [18, 50, 25, 25, 25, 32, 32]
        headers = ["#", "Restriccion", "Lado Der.", "Sentido", "Holgura", "Precio Sombra", "Estado"]
        
        for i, h in enumerate(headers):
            pdf.cell(w[i], 7, h, align=Align.C, fill=True)
        pdf.ln(7)
        
        pdf.set_font('Helvetica', '', 8)
        
        for i, c in enumerate(self.problem.constraints):
            cstr = self._format_constraint_short(c)
            
            if self.solution.variables:
                value = sum(
                    c.coefficients.get(var, 0) * self.solution.variables.get(var, 0)
                    for var in self.problem.variables
                )
                
                if c.sense == '<=':
                    slack = c.rhs - value
                elif c.sense == '>=':
                    slack = value - c.rhs
                else:
                    slack = 0
                
                if abs(slack) < 1e-6:
                    estado = "ACTIVA"
                    pdf.set_text_color(200, 0, 0)
                elif slack > 0:
                    estado = "NO ACTIVA"
                    pdf.set_text_color(0, 128, 0)
                else:
                    estado = "VIOLADA"
                    pdf.set_text_color(200, 0, 0)
                
                dual_value = self.solution.dual_values.get(f"c{i+1}", 0) if self.solution.dual_values else 0
                slack_str = f"{slack:.4f}"
                dual_str = f"{dual_value:.4f}"
            else:
                slack_str = "-"
                dual_str = "-"
                estado = "-"
                pdf.set_text_color(100, 100, 100)
            
            pdf.cell(w[0], 6, str(i + 1), align=Align.C)
            pdf.cell(w[1], 6, cstr[:25], align=Align.L)
            pdf.cell(w[2], 6, f"{c.rhs:.1f}", align=Align.R)
            pdf.cell(w[3], 6, c.sense, align=Align.C)
            pdf.cell(w[4], 6, slack_str, align=Align.R)
            pdf.cell(w[5], 6, dual_str, align=Align.R)
            pdf.cell(w[6], 6, estado, align=Align.C)
            pdf.ln(6)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    def _build_costos_reducidos(self, pdf: 'ReporteAcademico') -> None:
        """Construye el analisis de costos reducidos."""
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "ANALISIS DE COSTOS REDUCIDOS", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.3)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 6, "Costo Reducido: cantidad que el objetivo mejoraria si la variable aumenta en una unidad.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.cell(0, 6, "Variables con costo reducido = 0 estan en su valor optimo.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        has_reduced = self.solution.reduced_costs and any(
            abs(v) > 1e-6 for v in self.solution.reduced_costs.values()
        ) if self.solution.reduced_costs else False
        
        if has_reduced:
            pdf.set_fill_color(0, 51, 102)
            pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
            
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(255, 255, 255)
            w = [50, 45, 45, 45]
            headers = ["Variable", "Valor Optimo", "Costo Reducido", "Interpretacion"]
            
            for i, h in enumerate(headers):
                pdf.cell(w[i], 7, h, align=Align.C, fill=True)
            pdf.ln(7)
            
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(0, 0, 0)
            
            for var, value in self.solution.variables.items():
                reduced_cost = self.solution.reduced_costs.get(var, 0) if self.solution.reduced_costs else 0
                
                if abs(reduced_cost) > 1e-6:
                    if self.problem.sense.lower() == "max":
                        if reduced_cost > 0:
                            interp = "Aumentar beneficia objetivo"
                        else:
                            interp = "Variable en limite"
                    else:
                        if reduced_cost < 0:
                            interp = "Aumentar beneficia objetivo"
                        else:
                            interp = "Variable en limite"
                    pdf.set_text_color(0, 0, 150)
                else:
                    interp = "Variable optima"
                    pdf.set_text_color(0, 100, 0)
                
                pdf.cell(w[0], 6, var, align=Align.C)
                pdf.cell(w[1], 6, f"{value:.4f}", align=Align.R)
                pdf.cell(w[2], 6, f"{reduced_cost:.4f}", align=Align.R)
                pdf.cell(w[3], 6, interp, align=Align.L)
                pdf.ln(6)
        else:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 6, "Todas las variables estan en su valor optimo (costo reducido = 0).", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    def _build_analisis_sensibilidad(self, pdf: 'ReporteAcademico') -> None:
        """Construye el analisis de sensibilidad general."""
        
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "ANALISIS DE SENSIBILIDAD", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 6, "El analisis de sensibilidad muestra como cambios en los parametros afectan la solucion optima.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(8)
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "Interpretacion de Resultados:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(3)
        
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(0, 6, "* Restricciones ACTIVAS (holgura = 0): Utilizan completamente el recurso.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 6, "* Restricciones NO ACTIVAS (holgura > 0): Recurso disponible sin usar.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 6, "* Precio Sombra > 0: Aumentar el RHS mejora el valor objetivo.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 6, "* Precio Sombra = 0: La restriccion no limita el problema.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 6, "* Costo Reducido != 0: La variable no esta en su valor optimo.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(8)
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "Recomendaciones para Analisis Adicional:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(3)
        
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(0, 6, "1. Verificar si los precios sombra son economicamente significativos.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 6, "2. Considerar la precision de los datos antes de interpretar precios sombra.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 6, "3. Analizar el rango donde el precio sombra permanece valido.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 6, "4. Evaluar si las restricciones activas son realistas.", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.ln(10)

    def _build_grafico(self, pdf: 'ReporteAcademico') -> None:
        """Construye la seccion del grafico de region factible."""
        
        pdf.ln(5)
        
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "REGION FACTIBLE", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 7, f"Grafico de region factible para problema con variables: "
                 f"{self.problem.variables[0]}, {self.problem.variables[1]}", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.patches import Polygon
            
            fig, ax = plt.subplots(figsize=(6, 4.5))
            
            var_x = self.problem.variables[0]
            var_y = self.problem.variables[1]
            
            x_max, y_max = 10, 10
            for c in self.problem.constraints:
                a = c.coefficients.get(var_x, 0)
                b = c.coefficients.get(var_y, 0)
                rhs = c.rhs
                
                if abs(b) < 1e-10 and abs(a) > 1e-10:
                    x_max = max(x_max, abs(rhs / a) * 1.5)
                elif abs(a) < 1e-10 and abs(b) > 1e-10:
                    y_max = max(y_max, abs(rhs / b) * 1.5)
                else:
                    if abs(b) > 1e-10:
                        x_max = max(x_max, abs(rhs / b) * 1.5)
                    if abs(a) > 1e-10:
                        y_max = max(y_max, abs(rhs / a) * 1.5)
            
            colors = ['#1E90FF', '#FF6347', '#32CD32', '#9370DB', '#FF8C00']
            x_vals = np.linspace(0, x_max, 100)
            
            for i, c in enumerate(self.problem.constraints):
                a = c.coefficients.get(var_x, 0)
                b = c.coefficients.get(var_y, 0)
                rhs = c.rhs
                
                if abs(b) < 1e-10:
                    if abs(a) > 1e-10:
                        x_const = rhs / a
                        y_vals = np.linspace(0, 100, 100)
                        x_line = np.full_like(y_vals, x_const)
                        ax.plot(x_line, y_vals, color=colors[i % len(colors)], 
                                linewidth=2, label=f"R{i+1}")
                else:
                    y_vals = (rhs - a * x_vals) / b
                    ax.plot(x_vals, y_vals, color=colors[i % len(colors)], 
                            linewidth=2, label=f"R{i+1}")
            
            from ..core import LinearConstraint
            constraints = self.problem.constraints.copy()
            bounds = self.problem.bounds
            
            x_bound = bounds.get(var_x)
            if x_bound is None or x_bound.lower is None or x_bound.lower < 0:
                constraints.append(LinearConstraint(coefficients={var_x: 1}, rhs=0, sense=">="))
            y_bound = bounds.get(var_y)
            if y_bound is None or y_bound.lower is None or y_bound.lower < 0:
                constraints.append(LinearConstraint(coefficients={var_y: 1}, rhs=0, sense=">="))
            
            vertices = []
            for i, c1 in enumerate(constraints):
                for c2 in constraints[i+1:]:
                    intersection = self._find_intersection(c1, c2, var_x, var_y)
                    if intersection and self._is_point_feasible(intersection[0], intersection[1], constraints, var_x, var_y):
                        vertices.append(intersection)
            
            if self._is_point_feasible(0, 0, constraints, var_x, var_y):
                vertices.append((0, 0))
            
            if len(vertices) >= 3:
                import math
                cx = sum(v[0] for v in vertices) / len(vertices)
                cy = sum(v[1] for v in vertices) / len(vertices)
                vertices.sort(key=lambda v: math.atan2(v[1] - cy, v[0] - cx))
                
                polygon = Polygon(vertices, closed=True, alpha=0.3, 
                                 facecolor='#90EE90', edgecolor='#228B22', linewidth=2)
                ax.add_patch(polygon)
            
            if self.solution.variables:
                x = self.solution.variables.get(var_x, 0)
                y = self.solution.variables.get(var_y, 0)
                ax.scatter([x], [y], color='red', s=200, zorder=10, marker='*')
                ax.annotate(f'Optimo\n({x:.2f}, {y:.2f})', (x, y), 
                           textcoords="offset points", xytext=(10, 10), fontsize=9)
            
            ax.set_xlim(-x_max * 0.05, x_max * 1.1)
            ax.set_ylim(-y_max * 0.05, y_max * 1.1)
            ax.set_xlabel(var_x, fontsize=11, fontweight='bold')
            ax.set_ylabel(var_y, fontsize=11, fontweight='bold')
            ax.set_title(f'Region Factible - {self.problem.sense.upper()}', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.axhline(y=0, color='black', linewidth=1)
            ax.axvline(x=0, color='black', linewidth=1)
            ax.legend(loc='upper right', fontsize=8)
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                plt.savefig(tmp.name, dpi=120, bbox_inches='tight')
                tmp_path = tmp.name
            
            plt.close()
            
            if os.path.exists(tmp_path):
                img_width = 110
                x_pos = (PAGE_WIDTH - img_width) / 2
                pdf.image(tmp_path, x=x_pos, w=img_width)
                os.unlink(tmp_path)
                
        except Exception as e:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(150, 0, 0)
            pdf.cell(0, 10, f"No se pudo generar el grafico: {str(e)}", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
            pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)

    def _find_intersection(self, c1, c2, var_x, var_y):
        """Encuentra la interseccion de dos restricciones."""
        a1 = c1.coefficients.get(var_x, 0)
        b1 = c1.coefficients.get(var_y, 0)
        r1 = c1.rhs
        
        a2 = c2.coefficients.get(var_x, 0)
        b2 = c2.coefficients.get(var_y, 0)
        r2 = c2.rhs
        
        det = a1 * b2 - a2 * b1
        
        if abs(det) < 1e-10:
            return None
        
        x = (r1 * b2 - r2 * b1) / det
        y = (a1 * r2 - a2 * r1) / det
        
        return (x, y)

    def _is_point_feasible(self, x, y, constraints, var_x, var_y) -> bool:
        """Verifica si un punto es factible."""
        for c in constraints:
            value = c.coefficients.get(var_x, 0) * x + c.coefficients.get(var_y, 0) * y
            
            if c.sense == "<=":
                if value > c.rhs + 1e-10:
                    return False
            elif c.sense == ">=":
                if value < c.rhs - 1e-10:
                    return False
            elif c.sense == "=":
                if abs(value - c.rhs) > 1e-10:
                    return False
        
        return True

    def _format_objective(self) -> str:
        """Formatea la funcion objetivo."""
        terms = []
        for var in self.problem.variables:
            coeff = self.problem.objective.get(var, 0)
            if coeff != 0:
                terms.append(f"{coeff:+}{var}")
        obj_str = " ".join(terms)
        if obj_str.startswith("+"):
            obj_str = obj_str[1:]
        return obj_str

    def _format_constraint(self, c) -> str:
        """Formatea una restriccion."""
        terms = []
        for var in self.problem.variables:
            coeff = c.coefficients.get(var, 0)
            if coeff != 0:
                terms.append(f"{coeff:+}{var}")
        constraint_str = " ".join(terms)
        if constraint_str.startswith("+"):
            constraint_str = constraint_str[1:]
        return f"{constraint_str} {c.sense} {c.rhs}"

    def _format_constraint_short(self, c) -> str:
        """Formatea una restriccion de forma corta."""
        terms = []
        for var in self.problem.variables:
            coeff = c.coefficients.get(var, 0)
            if coeff != 0:
                terms.append(f"{coeff:+}{var}")
        constraint_str = " ".join(terms)
        if constraint_str.startswith("+"):
            constraint_str = constraint_str[1:]
        return constraint_str


class ReporteAcademico(FPDF):
    """Clase PDF academica personalizada."""
    
    def header(self):
        pass
    
    def footer(self):
        self.set_y(-20)
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.5)
        self.line(MARGIN, self.get_y(), PAGE_WIDTH - MARGIN, self.get_y())
        self.ln(4)

        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(80, 4, "Solucion de Programa Lineal")
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 4, f"Fecha: {fecha}", align=Align.R)
        self.ln(4)
        self.cell(0, 4, f"Pagina {self.page_no()}", align=Align.C)