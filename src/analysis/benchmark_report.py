"""
Reporte de benchmark multi-solver.
Genera PDF con comparación detallada de multiples solvers.
Utiliza BaseReport y builders del módulo analysis.
La visualización de gráficos esta en src.visualization.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any

import tempfile
import os

from fpdf import FPDF
from fpdf.enums import Align, YPos

from ..solver import BenchmarkRunner
from ..visualization import BenchmarkPlotter
from .base import BaseReport, ReportBuilder
from .builders.summary import SummaryBuilder
from .builders.comparison_charts import ComparisonChartsBuilder
from .builders.system_info import SystemInfoBuilder

PAGE_WIDTH = 215.9
PAGE_HEIGHT = 279.4
MARGIN = 15
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN


class BenchmarkPDF(FPDF):
    """Clase PDF para reportes de benchmark."""
    
    def header(self):
        pass
    
    def footer(self):
        self.set_y(-15)
        self.set_x(MARGIN)
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.3)
        self.line(MARGIN, self.get_y(), PAGE_WIDTH - MARGIN, self.get_y())
        self.ln(3)
        
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(100, 100, 100)
        self.cell(80, 4, "ISLA LP Benchmark Report")
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 4, f"Fecha: {fecha} | Pagina {self.page_no()}", align=Align.R)


class BenchmarkReport:
    """Genera reportes PDF detallado para benchmarking."""
    
    def __init__(self, runner: BenchmarkRunner, system_info: Optional[Dict[str, Any]] = None):
        self.runner = runner
        self.system_info = system_info or {}
    
    def generate(self, output_path: str) -> None:
        """Genera el reporte PDF."""
        pdf = BenchmarkPDF()
        pdf.set_margins(MARGIN, MARGIN, MARGIN)
        pdf.set_auto_page_break(auto=True, margin=15)
        
        pdf.add_page()
        self._cover(pdf)
        
        pdf.add_page()
        self._summary_stats(pdf)
        
        pdf.add_page()
        self._solver_comparison(pdf)
        
        pdf.add_page()
        self._detailed_results(pdf)
        
        pdf.add_page()
        self._problem_definitions(pdf)
        
        if self._has_charts():
            pdf.add_page()
            self._charts(pdf)
        
        if self.system_info:
            pdf.add_page()
            self._system(pdf)
        
        pdf.output(output_path)
    
    def _has_charts(self) -> bool:
        return len(self.runner.results) > 0
    
    def _cover(self, pdf: BenchmarkPDF) -> None:
        """Pagina de portada."""
        pdf.set_font('Helvetica', 'B', 24)
        pdf.set_text_color(0, 51, 102)
        pdf.ln(50)
        pdf.cell(0, 14, "ISLA LP BENCHMARK", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 18)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 12, "Reporte de Rendimiento", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(30)
        pdf.set_font('Helvetica', 'I', 12)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, "Comparacion Multi-Solver de Solvers de Programacion Lineal", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(30)
        summary = self.runner.get_summary()
        
        total = summary.get('total_benchmarks', 0)
        successful = summary.get('successful', 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        pdf.set_font('Helvetica', '', 14)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 10, f"Problemas evaluados: {total}", align=Align.C, new_y=YPos.NEXT)
        pdf.ln(5)
        pdf.cell(0, 10, f"Solvers comparados: {len(summary.get('by_solver', {}))}", align=Align.C, new_y=YPos.NEXT)
        pdf.ln(5)
        pdf.cell(0, 10, f"Tasa de exito: {success_rate:.1f}%", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(30)
        fecha = datetime.now().strftime("%d de %B de %Y a las %H:%M")
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 8, f"Generado: {fecha}", align=Align.C, new_y=YPos.NEXT)
        
        pdf.set_text_color(0, 0, 0)
    
    def _summary_stats(self, pdf: BenchmarkPDF) -> None:
        """Resumen estadistico completo."""
        self._header(pdf, "RESUMEN ESTADISTICO")
        
        summary = self.runner.get_summary()
        
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "Metricas Globales:", new_y=YPos.NEXT)
        pdf.ln(3)
        
        col_w = CONTENT_WIDTH / 4
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        
        data = [
            ("Total de pruebas", str(summary.get('total_benchmarks', 0))),
            ("Exitosas", str(summary.get('successful', 0))),
            ("Fallidas", str(summary.get('failed', 0))),
            ("Tasa de exito", f"{(summary.get('successful', 0) / max(summary.get('total_benchmarks', 1), 1) * 100):.1f}%"),
        ]
        
        pdf.set_x(MARGIN)
        y_start = pdf.get_y()
        for i, (label, value) in enumerate(data):
            pdf.set_fill_color(245, 245, 245)
            x_col = MARGIN + (i % 4) * col_w
            pdf.rect(x_col, y_start, col_w - 2, 14, 'F')
            pdf.set_xy(x_col + 2, y_start + 2)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.cell(col_w - 4, 4, label, align='C')
            pdf.set_xy(x_col + 2, y_start + 7)
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(col_w - 4, 4, value, align='C')
            if (i + 1) % 4 == 0:
                pdf.ln(16)
                pdf.set_x(MARGIN)
                y_start += 16
        
        if len(data) % 4 != 0:
            pdf.ln(16)
        
        pdf.ln(15)
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "Ranking por Velocidad (tiempo promedio):", new_y=YPos.NEXT)
        pdf.ln(3)
        
        solver_times = []
        for solver, data in summary.get("by_solver", {}).items():
            if data.get("successful", 0) > 0:
                solver_times.append((solver, data.get("avg_time", 0) * 1000))
        
        solver_times.sort(key=lambda x: x[1])
        
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(MARGIN)
        for rank, (solver, time_ms) in enumerate(solver_times, 1):
            if rank == 1:
                pdf.set_text_color(0, 128, 0)
            elif rank == len(solver_times):
                pdf.set_text_color(200, 0, 0)
            else:
                pdf.set_text_color(0, 0, 0)
            
            pdf.cell(15, 7, f"{rank}.", align=Align.R)
            pdf.cell(60, 7, solver)
            pdf.cell(50, 7, f"{time_ms:.2f} ms", align=Align.R)
            
            if rank == 1:
                pdf.cell(0, 7, "(Mas rapido)", new_y=YPos.NEXT)
            elif rank == len(solver_times):
                pdf.cell(0, 7, "(Mas lento)", new_y=YPos.NEXT)
            else:
                pdf.ln(7)
            pdf.set_x(MARGIN)
        
        pdf.ln(10)
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, "Tabla Comparativa:", new_y=YPos.NEXT)
        pdf.ln(3)
        
        w = [40, 25, 25, 25, 35, 35]
        cols = ["Solver", "Pruebas", "Exito", "Tiempo prom.", "Tiempo total", "Memoria peak"]
        
        pdf.set_fill_color(0, 51, 102)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_text_color(255, 255, 255)
        
        x_start = MARGIN + (CONTENT_WIDTH - sum(w)) / 2
        pdf.rect(x_start, pdf.get_y(), sum(w), 5, 'F')
        
        pdf.set_x(x_start)
        for i, col in enumerate(cols):
            pdf.cell(w[i], 5, col, align=Align.C)
        pdf.ln(5)
        
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(0, 0, 0)
        
        for solver, data in summary.get("by_solver", {}).items():
            pdf.set_x(x_start)
            success_rate = data.get("successful", 0) / max(data.get("runs", 1), 1) * 100
            
            pdf.cell(w[0], 5, solver, align=Align.L)
            pdf.cell(w[1], 5, str(data.get("runs", 0)), align=Align.C)
            
            if success_rate >= 100:
                pdf.set_text_color(0, 128, 0)
            elif success_rate >= 50:
                pdf.set_text_color(200, 140, 0)
            else:
                pdf.set_text_color(200, 0, 0)
            pdf.cell(w[2], 5, f"{success_rate:.0f}%", align=Align.C)
            pdf.set_text_color(0, 0, 0)
            
            pdf.cell(w[3], 5, f"{data.get('avg_time', 0) * 1000:.2f}ms", align=Align.R)
            pdf.cell(w[4], 5, f"{data.get('total_time', 0) * 1000:.2f}ms", align=Align.R)
            pdf.cell(w[5], 5, f"{data.get('peak_memory', 0):.1f} MB", align=Align.R)
            pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
    
    def _solver_comparison(self, pdf: BenchmarkPDF) -> None:
        """Comparacion detallada entre solvers."""
        self._header(pdf, "COMPARACION DETALLADA POR SOLVER")
        
        summary = self.runner.get_summary()
        
        pdf.ln(5)
        
        for solver, data in summary.get("by_solver", {}).items():
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 8, solver.upper(), new_y=YPos.NEXT)
            pdf.ln(2)
            
            pdf.set_line_width(0.5)
            pdf.set_draw_color(0, 51, 102)
            pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
            pdf.ln(5)
            
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(0, 0, 0)
            
            runs = data.get("runs", 0)
            success = data.get("successful", 0)
            
            pdf.cell(50, 6, "Ejecuciones:")
            pdf.cell(0, 6, str(runs), new_y=YPos.NEXT)
            pdf.set_x(MARGIN)
            
            pdf.cell(50, 6, "Exitosas:")
            if success == runs:
                pdf.set_text_color(0, 128, 0)
            elif success == 0:
                pdf.set_text_color(200, 0, 0)
            else:
                pdf.set_text_color(200, 140, 0)
            pdf.cell(0, 6, f"{success} ({success/runs*100:.1f}%)" if runs > 0 else "N/A", new_y=YPos.NEXT)
            pdf.set_x(MARGIN)
            pdf.set_text_color(0, 0, 0)
            
            avg_time = data.get("avg_time", 0) * 1000
            pdf.cell(50, 6, "Tiempo promedio:")
            pdf.cell(0, 6, f"{avg_time:.3f} ms", new_y=YPos.NEXT)
            pdf.set_x(MARGIN)
            
            min_time = data.get("min_time", 0) * 1000
            pdf.cell(50, 6, "Tiempo minimo:")
            pdf.cell(0, 6, f"{min_time:.3f} ms", new_y=YPos.NEXT)
            pdf.set_x(MARGIN)
            
            max_time = data.get("max_time", 0) * 1000
            pdf.cell(50, 6, "Tiempo maximo:")
            pdf.cell(0, 6, f"{max_time:.3f} ms", new_y=YPos.NEXT)
            pdf.set_x(MARGIN)
            
            std_time = data.get("std_time", 0) * 1000
            pdf.cell(50, 6, "Desv. estandar:")
            pdf.cell(0, 6, f"{std_time:.3f} ms", new_y=YPos.NEXT)
            pdf.set_x(MARGIN)
            
            pdf.cell(50, 6, "Memoria promedio:")
            pdf.cell(0, 6, f"{data.get('avg_memory', 0):.2f} MB", new_y=YPos.NEXT)
            pdf.set_x(MARGIN)
            
            pdf.cell(50, 6, "Memoria peak:")
            pdf.cell(0, 6, f"{data.get('peak_memory', 0):.2f} MB", new_y=YPos.NEXT)
            
            pdf.ln(8)
        
        pdf.set_text_color(0, 0, 0)
    
    def _detailed_results(self, pdf: BenchmarkPDF) -> None:
        """Resultados detallados por problema."""
        self._header(pdf, "RESULTADOS DETALLADOS")
        
        pdf.ln(5)
        
        problems = sorted(set(r.problem_name for r in self.runner.results))
        
        for problem in problems:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 7, f"Problema: {problem}", new_y=YPos.NEXT)
            pdf.ln(2)
            
            w = [35, 25, 25, 30, 25, 20, 20]
            cols = ["Solver", "Estado", "Valor Obj", "Tiempo", "Memoria", "Iter", "Nodos"]
            
            pdf.set_fill_color(0, 51, 102)
            pdf.set_font('Helvetica', 'B', 6)
            pdf.set_text_color(255, 255, 255)
            
            x_start = MARGIN + (CONTENT_WIDTH - sum(w)) / 2
            pdf.rect(x_start, pdf.get_y(), sum(w), 4, 'F')
            
            pdf.set_x(x_start)
            for i, col in enumerate(cols):
                pdf.cell(w[i], 4, col, align=Align.C)
            pdf.ln(4)
            
            pdf.set_font('Helvetica', '', 6)
            pdf.set_text_color(0, 0, 0)
            
            solvers_in_problem = [r for r in self.runner.results if r.problem_name == problem]
            
            for r in solvers_in_problem:
                pdf.set_x(x_start)
                pdf.cell(w[0], 4, r.solver_name, align=Align.L)
                
                status = r.solution.status if r.solution else "N/A"
                if status == "OPTIMAL":
                    pdf.set_text_color(0, 128, 0)
                elif status.startswith("ERROR"):
                    pdf.set_text_color(200, 0, 0)
                else:
                    pdf.set_text_color(200, 140, 0)
                pdf.cell(w[1], 4, status[:10], align=Align.C)
                pdf.set_text_color(0, 0, 0)
                
                obj = f"{r.solution.objective_value:.2f}" if r.solution and r.solution.objective_value else "-"
                pdf.cell(w[2], 4, obj, align=Align.R)
                pdf.cell(w[3], 4, f"{r.total_time*1000:.2f}ms", align=Align.R)
                
                mem = f"{r.memory_used_mb:.1f}MB" if r.memory_used_mb else "-"
                pdf.cell(w[4], 4, mem, align=Align.R)
                
                iters = str(r.stats.iterations) if r.stats and r.stats.iterations else "-"
                pdf.cell(w[5], 4, iters, align=Align.C)
                
                nodes = str(r.stats.nodes) if r.stats and r.stats.nodes else "-"
                pdf.cell(w[6], 4, nodes, align=Align.C)
                pdf.ln(4)
            
            pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
    
    def _problem_definitions(self, pdf: BenchmarkPDF) -> None:
        """Definiciones de problemas evaluados."""
        self._header(pdf, "DEFINICIONES DE PROBLEMAS")
        
        pdf.ln(5)
        
        problems = {}
        for r in self.runner.results:
            if r.problem_name not in problems and r.problem_text:
                problems[r.problem_name] = r.problem_text
        
        for problem_name, problem_text in problems.items():
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 7, f"Problema: {problem_name}", new_y=YPos.NEXT)
            pdf.set_x(MARGIN)
            pdf.ln(3)
            
            pdf.set_font('Courier', '', 7)
            pdf.set_text_color(0, 0, 0)
            pdf.set_fill_color(248, 248, 248)
            
            lines = problem_text.strip().split('\n')[:12]
            for line in lines:
                pdf.cell(0, 4, line, new_y=YPos.NEXT)
                pdf.set_x(MARGIN)
            
            pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
    
    def _charts(self, pdf: BenchmarkPDF) -> None:
        """Graficos comparativos usando el modulo de visualizacion."""
        self._header(pdf, "GRAFICOS COMPARATIVOS")
        
        try:
            # Usar BenchmarkPlotter del modulo visualization
            plotter = BenchmarkPlotter(self.runner)
            
            # Generar graficos y guardar temporalmente
            tmp_files = []
            
            # Tiempo promedio
            tmp_times = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            tmp_files.append(tmp_times.name)
            plotter.plot_times_comparison(Path(tmp_times.name))
            
            # Tasa de exito
            tmp_success = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            tmp_files.append(tmp_success.name)
            plotter.plot_success_rate(Path(tmp_success.name))
            
            # Perfil de rendimiento
            tmp_profile = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            tmp_files.append(tmp_profile.name)
            plotter.plot_performance_profile(Path(tmp_profile.name))
            
            # Dashboard
            tmp_dashboard = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            tmp_files.append(tmp_dashboard.name)
            plotter.plot_summary_dashboard(Path(tmp_dashboard.name))
            
            # Agregar al PDF
            for tmp_path in tmp_files:
                if os.path.exists(tmp_path):
                    pdf.image(tmp_path, x=MARGIN, w=CONTENT_WIDTH)
                    pdf.ln(5)
                    os.unlink(tmp_path)
                    
        except Exception as e:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(150, 0, 0)
            pdf.cell(0, 5, f"No se pudieron generar los graficos: {str(e)}", new_y=YPos.NEXT)
        
        pdf.set_text_color(0, 0, 0)
    
    def _system(self, pdf: BenchmarkPDF) -> None:
        """Informacion del sistema."""
        self._header(pdf, "INFORMACION DEL SISTEMA")
        
        pdf.ln(5)
        p = self.system_info.get("platform", {})
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        fields = [
            ("Sistema", f"{p.get('system', 'N/A')} {p.get('release', '')}"),
            ("Maquina", p.get('machine', 'N/A')),
            ("Procesador", p.get('processor', 'N/A')[:60]),
            ("Python", p.get('python_version', 'N/A')),
            ("Hostname", self.system_info.get('hostname', 'N/A')),
            ("Fecha", self.system_info.get('timestamp', 'N/A')[:19]),
        ]
        
        for label, value in fields:
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(40, 6, label + ":")
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(0, 6, value, new_y=YPos.NEXT)
            pdf.set_x(MARGIN)
        
        pdf.set_text_color(0, 0, 0)
    
    def _header(self, pdf: BenchmarkPDF, title: str) -> None:
        """Encabezado de seccion."""
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, title, align=Align.C, new_y=YPos.NEXT)
        pdf.ln(2)
        pdf.set_line_width(0.5)
        pdf.set_draw_color(0, 51, 102)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(5)