"""
Módulo de análisis para problemas de programación lineal.
Reporte académico profesional usando fpdf2.
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


# Configuración de página carta
PAGE_WIDTH = 215.9  # mm (carta)
PAGE_HEIGHT = 279.4  # mm
MARGIN = 20  # mm


@dataclass
class ExecutionTimes:
    """Almacena los tiempos de ejecución del programa."""
    parse_time: float = 0.0
    build_time: float = 0.0
    solve_time: float = 0.0
    visualize_time: float = 0.0
    pdf_time: float = 0.0
    total_time: float = 0.0


class LPAnalysis:
    """Genera reportes académicos profesionales para problemas de programación lineal."""

    def __init__(self, problem: LinearProblem, solution: Solution, 
                 times: Optional[ExecutionTimes] = None):
        self.problem = problem
        self.solution = solution
        self.times = times or ExecutionTimes()
        self.page_count = 0

    def generate_pdf(self, output_path: str) -> None:
        """Genera un reporte académico completo."""
        pdf = ReporteAcademico()
        pdf.set_margins(MARGIN, MARGIN, MARGIN)
        
        # Portada
        pdf.add_page()
        self.page_count += 1
        self._build_portada(pdf)
        
        # Página 1: Datos del problema y solución
        pdf.add_page()
        self.page_count += 1
        self._build_header(pdf)
        self._build_resumen_ejecutivo(pdf)
        self._build_detalles_tecnicos(pdf)
        self._build_datos_problema(pdf)
        self._build_funcion_objetivo(pdf)
        self._build_restricciones_tabla(pdf)
        self._build_solucion_optima(pdf)
        self._build_variables_holgura(pdf)
        
        # Página 2: Análisis de restricciones y sensibilidad
        if len(self.problem.variables) == 2:
            pdf.add_page()
            self.page_count += 1
            self._build_header(pdf)
            self._build_analisis_restricciones(pdf)
            self._build_sensibilidad(pdf)
            self._build_grafico(pdf)
        else:
            # Si no es problema de 2 variables, mostrar análisis de sensibilidad en página 2
            pdf.add_page()
            self.page_count += 1
            self._build_header(pdf)
            self._build_sensibilidad(pdf)
        
        pdf.output(output_path)

    def _build_header(self, pdf: 'ReporteAcademico') -> None:
        """Construye el encabezado."""
        # Título
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "SOLUCIÓN DE PROGRAMA LINEAL", align=Align.C,
                 new_y=YPos.NEXT)
        
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(3, 8, "Método Simplex - Solucionador con Gurobi",
                 align=Align.C, new_y=YPos.NEXT, center=True)
        
        pdf.ln(5)
        
        # Línea separadora
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.8)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)

    def _build_portada(self, pdf: 'ReporteAcademico') -> None:
        """Construye la portada del reporte."""
        # Título principal
        pdf.set_font('Helvetica', 'B', 24)
        pdf.set_text_color(0, 51, 102)
        pdf.ln(40)
        pdf.cell(0, 12, "SOLUCIÓN DE PROGRAMA LINEAL", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(10)
        
        # Subtítulo
        pdf.set_font('Helvetica', 'I', 14)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, "Reporte Académico de Optimización", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(30)
        
        # Información del problema
        pdf.set_font('Helvetica', '', 12)
        pdf.set_text_color(60, 60, 60)
        
        tipo = "Maximización" if self.problem.sense.lower() == "max" else "Minimización"
        pdf.cell(0, 8, f"Tipo de problema: {tipo}", align=Align.C, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 8, f"Número de variables: {len(self.problem.variables)}", align=Align.C, new_y=YPos.NEXT)
        pdf.ln(5)
        
        pdf.cell(0, 8, f"Número de restricciones: {len(self.problem.constraints)}", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(30)
        
        # Fecha
        pdf.set_font('Helvetica', 'I', 11)
        pdf.set_text_color(100, 100, 100)
        fecha = datetime.now().strftime("%d de %B de %Y")
        pdf.cell(0, 8, f"Fecha de generación: {fecha}", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(10)
        
        # Línea decorativa
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(1)
        pdf.line(PAGE_WIDTH/2 - 40, pdf.get_y(), PAGE_WIDTH/2 + 40, pdf.get_y())
        
        pdf.set_text_color(0, 0, 0)

    def _build_resumen_ejecutivo(self, pdf: 'ReporteAcademico') -> None:
        """Construye el resumen ejecutivo del problema."""
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "Resumen Ejecutivo", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.3)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(2)
        
        # Fondo para el resumen
        pdf.set_fill_color(245, 250, 255)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 28, 'F')
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        
        # Tipo de problema
        tipo = "MAXIMIZACIÓN" if self.problem.sense.lower() == "max" else "MINIMIZACIÓN"
        pdf.cell(40, 6, f"Tipo:")
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(60, 6, tipo)
        pdf.set_font('Helvetica', '', 10)
        pdf.ln(6)
        
        # Variables y restricciones
        pdf.cell(40, 6, f"Variables:")
        pdf.cell(60, 6, f"{len(self.problem.variables)}")
        pdf.ln(6)
        
        pdf.cell(40, 6, f"Restricciones:")
        pdf.cell(60, 6, f"{len(self.problem.constraints)}")
        pdf.ln(6)
        
        # Estado y valor óptimo
        pdf.cell(40, 6, f"Estado:")
        if self.solution.status == 'OPTIMAL':
            pdf.set_text_color(0, 128, 0)
            pdf.cell(60, 6, "ÓPTIMA")
        else:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(60, 6, self.solution.status)
        pdf.ln(6)
        
        pdf.set_text_color(0, 0, 0)
        pdf.cell(40, 6, f"Valor óptimo (Z*):")
        pdf.set_text_color(0, 0, 150)
        pdf.set_font('Helvetica', 'B', 10)
        if self.solution.objective_value is not None:
            pdf.cell(60, 6, f"{self.solution.objective_value:,.4f}")
        else:
            pdf.cell(60, 6, "No disponible")
        
        pdf.ln(8)
        pdf.set_text_color(0, 0, 0)

    def _build_detalles_tecnicos(self, pdf: 'ReporteAcademico') -> None:
        """Construye la sección de detalles técnicos del entorno."""
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "Información del Sistema", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.3)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(2)
        
        # Información técnica
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(60, 60, 60)
        
        # Primera fila
        pdf.cell(90, 5, f"Python: {sys.version.split()[0]}")
        pdf.cell(90, 5, f"Sistema: {platform.system()} {platform.release()}")
        pdf.ln(4)
        
        # Segunda fila
        pdf.cell(90, 5, f"Procesador: {platform.processor()}", fill=True)
        pdf.cell(90, 5, f"Arquitectura: {platform.machine()}")
        pdf.ln(4)
        
        # Tercera fila
        pdf.cell(90, 5, f"Hostname: {platform.node()}", fill=True)
        fecha_gen = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.cell(90, 5, f"Fecha generación: {fecha_gen}")
        pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
        
        # Sección de análisis de tiempos
        self._build_analisis_tiempos(pdf)
    
    def _build_analisis_tiempos(self, pdf: 'ReporteAcademico') -> None:
        """Construye la sección de análisis de tiempos de ejecución."""
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 7, "Análisis de Tiempos de Ejecución", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.3)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(2)
        
        # Encabezado de tabla
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 6, 'F')
        
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(87.95, 6, "Etapa", align=Align.C, fill=True)
        pdf.cell(87.95, 6, "Tiempo (s)", align=Align.C, fill=True)
        pdf.ln(6)
        
        # Datos de tiempos
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 0, 0)
        
        times_data = [
            ("Análisis Léxico/Sintáctico", self.times.parse_time),
            ("Construcción del modelo", self.times.build_time),
            ("Resolución (Gurobi)", self.times.solve_time),
            ("Generación de visualizaciones", self.times.visualize_time),
            ("Generación del reporte PDF", self.times.pdf_time),
        ]
        
        for stage, time_val in times_data:
            pdf.cell(87.95, 5, stage, align=Align.L)
            pdf.cell(87.95, 5, f"{time_val:.4f}", align=Align.R)
            pdf.ln(5)
        
        # Total
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN + 5, pdf.get_y(), PAGE_WIDTH - MARGIN - 5, pdf.get_y())
        pdf.ln(2)
        
        pdf.cell(87.95, 5, "TIEMPO TOTAL DE EJECUCIÓN", align=Align.L)
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
        
        # Tabla de variables
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, "Variables del problema:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        # Encabezado de tabla
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
        
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(58.6, 7, "Variable", align=Align.C, fill=True)
        pdf.cell(58.6, 7, "Límite Inferior", align=Align.C, fill=True)
        pdf.cell(58.7, 7, "Límite Superior", align=Align.C, fill=True)
        pdf.ln(7)
        
        # Datos de variables
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
        """Construye la sección de función objetivo."""
        
        pdf.ln(3)
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, "Función Objetivo:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        # Tipo
        sense = "MAXIMIZAR" if self.problem.sense.lower() == "max" else "MINIMIZAR"
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(30, 7, f"Tipo: {sense}")
        pdf.ln()
        
        # Expresión
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
        
        # Encabezado
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
        
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(255, 255, 255)
        
        w = [20, 95.9, 25, 35]
        headers = ["#", "Expresión", "Tipo", "RHS"]
        
        for i, h in enumerate(headers):
            pdf.cell(w[i], 7, h, align=Align.C, fill=True)
        pdf.ln(7)
        
        # Datos
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
        """Construye la sección de solución óptima."""
        
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "SOLUCIÓN ÓPTIMA", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        # Estado
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(45, 7, "Estado de la solución: ", align=Align.L)
        
        if self.solution.status == 'OPTIMAL':
            pdf.set_text_color(0, 128, 0)
            pdf.cell(0, 7, "ÓPTIMA", new_x=XPos.LEFT, new_y=YPos.NEXT)
        else:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 7, self.solution.status, new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.ln(3)
        
        # Valor óptimo
        if self.solution.objective_value is not None:
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(0, 0, 150)
            pdf.cell(40, 10, "Valor óptimo:")
            pdf.cell(0, 10, f"Z* = {self.solution.objective_value:,.4f}", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.ln(5)
        
        # Tabla de valores
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, "Valores de las variables:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        # Encabezado
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
        
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(58.6, 7, "Variable", align=Align.C, fill=True)
        pdf.cell(58.6, 7, "Valor Óptimo", align=Align.C, fill=True)
        pdf.cell(58.7, 7, "Costo Reducido", align=Align.C, fill=True)
        pdf.ln(7)
        
        # Datos
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        
        for var, value in self.solution.variables.items():
            pdf.cell(58.6, 6, str(var), align=Align.C)
            pdf.cell(58.6, 6, f"{value:.4f}", align=Align.C)
            pdf.cell(58.7, 6, "0.0000", align=Align.C)
            pdf.ln(6)
        
        pdf.ln(5)

    def _build_variables_holgura(self, pdf: 'ReporteAcademico') -> None:
        """Construye el análisis de holgura."""
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, "Análisis de Holgura:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        # Encabezado
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
        
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(255, 255, 255)
        
        w = [20, 95.9, 30, 30]
        headers = ["#", "Restricción", "Holgura", "Estado"]
        
        for i, h in enumerate(headers):
            pdf.cell(w[i], 7, h, align=Align.C, fill=True)
        pdf.ln(7)
        
        # Datos
        pdf.set_font('Helvetica', '', 9)
        
        for i, c in enumerate(self.problem.constraints):
            cstr = self._format_constraint(c)
            
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
                
                slack_str = f"{slack:.4f}"
            else:
                slack_str = "-"
                estado = "-"
                pdf.set_text_color(100, 100, 100)
            
            pdf.cell(w[0], 6, str(i + 1), align=Align.C)
            pdf.cell(w[1], 6, cstr[:35], align=Align.C)
            pdf.cell(w[2], 6, slack_str, align=Align.C)
            pdf.cell(w[3], 6, estado, align=Align.C)
            pdf.ln(6)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    def _build_analisis_restricciones(self, pdf: 'ReporteAcademico') -> None:
        """Construye el análisis detallado de restricciones."""
        
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "ANÁLISIS DE RESTRICCIONES", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        # Análisis para cada restricción
        pdf.set_font('Helvetica', '', 9)
        
        for i, c in enumerate(self.problem.constraints):
            cstr = self._format_constraint(c)
            
            # Fondo para cada restricción
            pdf.set_fill_color(245, 245, 245)
            pdf.rect(MARGIN, pdf.get_y(), 175.9, 20, 'F')
            
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 6, f"Restricción {i+1}: {cstr}", new_x=XPos.LEFT, new_y=YPos.NEXT)
            
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
                
                pdf.set_font('Helvetica', '', 9)
                pdf.cell(35, 5, f"Valor actual: {value:.4f}")
                pdf.cell(35, 5, f"RHS: {c.rhs}")
                pdf.cell(35, 5, f"Holgura: {slack:.4f}")
                
                if abs(slack) < 1e-6:
                    pdf.set_text_color(200, 0, 0)
                    pdf.cell(50, 5, "Tipo: ACTIVA")
                elif slack > 0:
                    pdf.set_text_color(0, 128, 0)
                    pdf.cell(50, 5, "Tipo: NO ACTIVA")
                else:
                    pdf.set_text_color(200, 0, 0)
                    pdf.cell(50, 5, "Tipo: VIOLADA")
                
                pdf.set_text_color(0, 0, 0)
            
            pdf.ln(8)

    def _build_sensibilidad(self, pdf: 'ReporteAcademico') -> None:
        """Construye el análisis de sensibilidad."""
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "ANÁLISIS DE SENSIBILIDAD", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        # Verificar si hay datos de sensibilidad disponibles
        has_dual = hasattr(self.solution, 'dual_values') and self.solution.dual_values is not None
        has_reduced = hasattr(self.solution, 'reduced_costs') and self.solution.reduced_costs is not None
        
        if not has_dual and not has_reduced:
            # Mostrar mensaje informativo
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 8, "Nota: Los datos de sensibilidad (precios sombra, costos reducidos) no están", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
            pdf.cell(0, 8, "disponibles en la solución actual. Estos datos requieren que el modelo de Gurobi", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
            pdf.cell(0, 8, "preserve la información de sensibilidad (atributos Pi y RC en el modelo).", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
            pdf.ln(5)
            
            # Información alternativa: calcular precios sombra manualmente para restricciones
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, "Análisis de Restricciones (Información Disponible):", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
            pdf.ln(3)
            
            # Tabla de restricciones con información calculada
            pdf.set_fill_color(0, 51, 102)
            pdf.rect(MARGIN, pdf.get_y(), 175.9, 7, 'F')
            
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(255, 255, 255)
            w = [25, 55, 35, 30, 30.9]
            headers = ["#", "Restricción", "Holgura", "Estado", "Shadow"]
            
            for i, h in enumerate(headers):
                pdf.cell(w[i], 7, h, align=Align.C, fill=True)
            pdf.ln(7)
            
            # Datos
            pdf.set_font('Helvetica', '', 8)
            pdf.set_text_color(0, 0, 0)
            
            for i, c in enumerate(self.problem.constraints):
                cstr = self._format_constraint(c)
                
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
                        shadow = f"{abs(c.rhs - value):.2f}" if c.sense == '=' else "-"
                    elif slack > 0:
                        estado = "NO ACTIVA"
                        shadow = "0.00"
                    else:
                        estado = "VIOLADA"
                        shadow = "-"
                else:
                    slack = 0
                    estado = "-"
                    shadow = "-"
                
                pdf.cell(w[0], 6, str(i + 1), align=Align.C)
                pdf.cell(w[1], 6, cstr[:25], align=Align.L)
                pdf.cell(w[2], 6, f"{slack:.4f}", align=Align.R)
                pdf.cell(w[3], 6, estado, align=Align.C)
                pdf.cell(w[4], 6, shadow, align=Align.R)
                pdf.ln(6)
        else:
            # Si hay datos de sensibilidad, mostrarlos
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, "Datos de sensibilidad disponibles en la solución.", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.ln(5)

    def _build_grafico(self, pdf: 'ReporteAcademico') -> None:
        """Construye la sección del gráfico de región factible."""
        
        pdf.ln(5)
        
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "REGIÓN FACTIBLE", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(0.5)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(3)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 7, f"Gráfico de región factible para problema con variables: "
                 f"{self.problem.variables[0]}, {self.problem.variables[1]}", 
                 new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        # Generar gráfico con matplotlib
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.patches import Polygon
            
            fig, ax = plt.subplots(figsize=(6, 4.5))
            
            var_x = self.problem.variables[0]
            var_y = self.problem.variables[1]
            
            # Calcular rango
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
            
            # Dibujar restricciones
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
            
            # Región factible
            from ..core import LinearConstraint
            constraints = self.problem.constraints.copy()
            bounds = self.problem.bounds
            
            if var_x not in bounds or bounds[var_x].lower is None or bounds[var_x].lower < 0:
                constraints.append(LinearConstraint(coefficients={var_x: 1}, rhs=0, sense=">="))
            if var_y not in bounds or bounds[var_y].lower is None or bounds[var_y].lower < 0:
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
            
            # Punto óptimo
            if self.solution.variables:
                x = self.solution.variables.get(var_x, 0)
                y = self.solution.variables.get(var_y, 0)
                ax.scatter([x], [y], color='red', s=200, zorder=10, marker='*')
                ax.annotate(f'Óptimo\n({x:.2f}, {y:.2f})', (x, y), 
                           textcoords="offset points", xytext=(10, 10), fontsize=9)
            
            ax.set_xlim(-x_max * 0.05, x_max * 1.1)
            ax.set_ylim(-y_max * 0.05, y_max * 1.1)
            ax.set_xlabel(var_x, fontsize=11, fontweight='bold')
            ax.set_ylabel(var_y, fontsize=11, fontweight='bold')
            ax.set_title(f'Región Factible - {self.problem.sense.upper()}', fontsize=12)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.axhline(y=0, color='black', linewidth=1)
            ax.axvline(x=0, color='black', linewidth=1)
            ax.legend(loc='upper right', fontsize=8)
            
            # Guardar imagen
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                plt.savefig(tmp.name, dpi=120, bbox_inches='tight')
                tmp_path = tmp.name
            
            plt.close()
            
            # Insertar imagen en PDF (mas pequena y centrada)
            if os.path.exists(tmp_path):
                # Ancho de imagen: 110mm (mas pequeno)
                img_width = 110
                # Centrar: (ancho pagina - ancho imagen) / 2
                x_pos = (PAGE_WIDTH - img_width) / 2
                pdf.image(tmp_path, x=x_pos, w=img_width)
                os.unlink(tmp_path)
                
        except Exception as e:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(150, 0, 0)
            pdf.cell(0, 10, f"No se pudo generar el gráfico: {str(e)}", 
                     new_x=XPos.LEFT, new_y=YPos.NEXT)
            pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)

    def _find_intersection(self, c1, c2, var_x, var_y):
        """Encuentra la intersección de dos restricciones."""
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
        """Formatea la función objetivo."""
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
        """Formatea una restricción."""
        terms = []
        for var in self.problem.variables:
            coeff = c.coefficients.get(var, 0)
            if coeff != 0:
                terms.append(f"{coeff:+}{var}")
        constraint_str = " ".join(terms)
        if constraint_str.startswith("+"):
            constraint_str = constraint_str[1:]
        return f"{constraint_str} {c.sense} {c.rhs}"


class ReporteAcademico(FPDF):
    """Clase PDF académica personalizada."""
    
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
        # Primera línea: título y fecha
        self.cell(80, 4, "Solución de Programa Lineal")
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 4, f"Fecha: {fecha}", align=Align.R)
        self.ln(4)
        # Segunda línea: número de página centrado
        self.cell(0, 4, f"Página {self.page_no()}", align=Align.C)
