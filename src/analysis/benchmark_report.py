"""
Reporte de benchmark multi-solver.
Genera PDF con comparacion de multiples solvers.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any
import tempfile
import os

from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

from ..solver import BenchmarkRunner

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
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.3)
        self.line(MARGIN, self.get_y(), PAGE_WIDTH - MARGIN, self.get_y())
        self.ln(3)

        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(100, 100, 100)
        self.cell(80, 4, "Benchmark Report")
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 4, f"Fecha: {fecha} | Pagina {self.page_no()}", align=Align.R)


class BenchmarkReport:
    """Genera reportes PDF para benchmarking multi-solver."""
    
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
        self._summary(pdf)
        
        pdf.add_page()
        self._detailed(pdf)
        
        pdf.add_page()
        self._charts(pdf)
        
        if self.system_info:
            pdf.add_page()
            self._system(pdf)
        
        pdf.output(output_path)
    
    def _cover(self, pdf: BenchmarkPDF) -> None:
        """Pagina de portada."""
        pdf.set_font('Helvetica', 'B', 22)
        pdf.set_text_color(0, 51, 102)
        pdf.ln(40)
        pdf.cell(0, 12, "REPORTE DE BENCHMARK", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(10)
        pdf.set_font('Helvetica', 'I', 12)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, "Comparacion Multi-Solver de Solvers de Programacion Lineal", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(30)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(60, 60, 60)
        
        summary = self.runner.get_summary()
        pdf.cell(0, 8, f"Total de pruebas: {summary['total_benchmarks']}", align=Align.C, new_y=YPos.NEXT)
        pdf.ln(5)
        pdf.cell(0, 8, f"Exitosas: {summary['successful']}", align=Align.C, new_y=YPos.NEXT)
        pdf.ln(5)
        pdf.cell(0, 8, f"Fallidas: {summary['failed']}", align=Align.C, new_y=YPos.NEXT)
        
        solvers = ", ".join(summary.get("by_solver", {}).keys())
        pdf.ln(5)
        pdf.cell(0, 8, f"Solvers: {solvers}", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(30)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(100, 100, 100)
        fecha = datetime.now().strftime("%d de %B de %Y")
        pdf.cell(0, 8, f"Fecha de generacion: {fecha}", align=Align.C, new_y=YPos.NEXT)
        
        pdf.ln(15)
        pdf.set_draw_color(0, 51, 102)
        pdf.set_line_width(1)
        pdf.line(PAGE_WIDTH/2 - 25, pdf.get_y(), PAGE_WIDTH/2 + 25, pdf.get_y())
        
        pdf.set_text_color(0, 0, 0)
    
    def _summary(self, pdf: BenchmarkPDF) -> None:
        """Resumen por solver."""
        self._header(pdf, "RESUMEN POR SOLVER")
        
        summary = self.runner.get_summary()
        
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, "Resultados por Solver:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.ln(5)
        
        w = [45, 20, 20, 20, 30, 30, 35, 30]
        total_w = sum(w)
        x_start = MARGIN + (CONTENT_WIDTH - total_w) / 2
        
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(x_start, pdf.get_y(), total_w, 5, 'F')
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_text_color(255, 255, 255)
        
        pdf.set_x(x_start)
        pdf.cell(w[0], 5, "Solver", align=Align.C)
        pdf.cell(w[1], 5, "Pruebas", align=Align.C)
        pdf.cell(w[2], 5, "Exito", align=Align.C)
        pdf.cell(w[3], 5, "Fallo", align=Align.C)
        pdf.cell(w[4], 5, "Tiempo prom.", align=Align.C)
        pdf.cell(w[5], 5, "Tiempo total", align=Align.C)
        pdf.cell(w[6], 5, "Memoria prom.", align=Align.C)
        pdf.cell(w[7], 5, "Memoria peak", align=Align.C)
        pdf.ln(5)
        
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(0, 0, 0)
        
        for solver, data in summary.get("by_solver", {}).items():
            failed = data.get("runs", 0) - data.get("successful", 0)
            pdf.set_x(x_start)
            pdf.cell(w[0], 5, solver, align=Align.C)
            pdf.cell(w[1], 5, str(data.get("runs", 0)), align=Align.C)
            pdf.cell(w[2], 5, str(data.get("successful", 0)), align=Align.C)
            pdf.cell(w[3], 5, str(failed), align=Align.C)
            avg_time = data.get("avg_time", 0) * 1000
            pdf.cell(w[4], 5, f"{avg_time:.2f}ms", align=Align.C)
            total_time = data.get("total_time", 0) * 1000
            pdf.cell(w[5], 5, f"{total_time:.2f}ms", align=Align.C)
            avg_mem = data.get("avg_memory", 0)
            pdf.cell(w[6], 5, f"{avg_mem:.2f} MB", align=Align.C)
            peak_mem = data.get("peak_memory", 0)
            pdf.cell(w[7], 5, f"{peak_mem:.2f} MB", align=Align.C)
            pdf.ln(5)
        
        pdf.ln(8)
    
    def _detailed(self, pdf: BenchmarkPDF) -> None:
        """Resultados detallados."""
        self._header(pdf, "RESULTADOS DETALLADOS")
        
        pdf.ln(3)
        
        w = [30, 28, 22, 22, 18, 12, 12, 20, 20]
        total_w = sum(w)
        x_start = MARGIN + (CONTENT_WIDTH - total_w) / 2
        
        pdf.set_fill_color(0, 51, 102)
        pdf.rect(x_start, pdf.get_y(), total_w, 5, 'F')
        pdf.set_font('Helvetica', 'B', 6)
        pdf.set_text_color(255, 255, 255)
        
        pdf.set_x(x_start)
        pdf.cell(w[0], 5, "Problema", align=Align.C)
        pdf.cell(w[1], 5, "Solver", align=Align.C)
        pdf.cell(w[2], 5, "Estado", align=Align.C)
        pdf.cell(w[3], 5, "Valor Obj", align=Align.C)
        pdf.cell(w[4], 5, "Tiempo", align=Align.C)
        pdf.cell(w[5], 5, "Iter", align=Align.C)
        pdf.cell(w[6], 5, "Nodos", align=Align.C)
        pdf.cell(w[7], 5, "Memoria", align=Align.C)
        pdf.cell(w[8], 5, "Peak Mem", align=Align.C)
        pdf.ln(5)
        
        pdf.set_font('Helvetica', '', 6)
        pdf.set_text_color(0, 0, 0)
        
        for r in self.runner.results:
            pdf.set_x(x_start)
            pdf.cell(w[0], 4, r.problem_name[:15], align=Align.L)
            pdf.cell(w[1], 4, r.solver_name[:12], align=Align.L)
            status = r.solution.status[:6] if r.solution else "N/A"
            pdf.cell(w[2], 4, status, align=Align.C)
            obj = f"{r.solution.objective_value:.2f}" if r.solution and r.solution.objective_value else "-"
            pdf.cell(w[3], 4, obj, align=Align.R)
            pdf.cell(w[4], 4, f"{r.total_time*1000:.1f}ms", align=Align.R)
            iters = r.stats.iterations if r.stats else 0
            pdf.cell(w[5], 4, str(iters), align=Align.C)
            nodes = r.stats.nodes if r.stats else 0
            pdf.cell(w[6], 4, str(nodes), align=Align.C)
            mem = r.memory_used_mb if r.memory_used_mb else 0
            pdf.cell(w[7], 4, f"{mem:.1f}MB", align=Align.R)
            peak = r.peak_memory_mb if r.peak_memory_mb else 0
            pdf.cell(w[8], 4, f"{peak:.1f}MB", align=Align.R)
            pdf.ln(4)
    
    def _charts(self, pdf: BenchmarkPDF) -> None:
        """Graficos comparativos."""
        self._header(pdf, "GRAFICOS COMPARATIVOS")
        
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        
        summary = self.runner.get_summary()
        solvers = list(summary.get("by_solver", {}).keys())
        
        if not solvers:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 6, "No hay suficientes datos para graficar.", new_x=XPos.LEFT, new_y=YPos.NEXT)
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        fig.suptitle('Analisis Comparativo de Solvers', fontsize=14, fontweight='bold')
        
        x_pos = np.arange(len(solvers))
        
        times = [summary["by_solver"][s].get("avg_time", 0) * 1000 for s in solvers]
        colors = ['#003366', '#1E90FF', '#228B22', '#8B0000', '#4B0082'][:len(solvers)]
        axes[0, 0].bar(x_pos, times, color=colors)
        axes[0, 0].set_xticks(x_pos)
        axes[0, 0].set_xticklabels(solvers, rotation=45, ha='right')
        axes[0, 0].set_ylabel('Tiempo (ms)')
        axes[0, 0].set_title('Tiempo Promedio por Solver')
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        success = [summary["by_solver"][s].get("successful", 0) for s in solvers]
        runs = [summary["by_solver"][s].get("runs", 1) for s in solvers]
        success_rate = [s/r*100 if r > 0 else 0 for s, r in zip(success, runs)]
        axes[0, 1].bar(x_pos, success_rate, color=colors)
        axes[0, 1].set_xticks(x_pos)
        axes[0, 1].set_xticklabels(solvers, rotation=45, ha='right')
        axes[0, 1].set_ylabel('Tasa de Exito (%)')
        axes[0, 1].set_title('Tasa de Exito por Solver')
        axes[0, 1].set_ylim(0, 110)
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        total_times = [summary["by_solver"][s].get("total_time", 0) * 1000 for s in solvers]
        axes[1, 0].bar(x_pos, total_times, color=colors)
        axes[1, 0].set_xticks(x_pos)
        axes[1, 0].set_xticklabels(solvers, rotation=45, ha='right')
        axes[1, 0].set_ylabel('Tiempo Total (ms)')
        axes[1, 0].set_title('Tiempo Total por Solver')
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        iterations = []
        for s in solvers:
            data = summary["by_solver"][s]
            iters = data.get("total_iterations", 0)
            runs = data.get("runs", 1)
            iterations.append(iters / runs if runs > 0 else 0)
        axes[1, 1].bar(x_pos, iterations, color=colors)
        axes[1, 1].set_xticks(x_pos)
        axes[1, 1].set_xticklabels(solvers, rotation=45, ha='right')
        axes[1, 1].set_ylabel('Iteraciones')
        axes[1, 1].set_title('Iteraciones Promedio')
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                plt.savefig(tmp.name, dpi=150, bbox_inches='tight', facecolor='white')
                tmp_path = tmp.name
            plt.close()
            
            if os.path.exists(tmp_path):
                pdf.image(tmp_path, x=MARGIN, w=PAGE_WIDTH - 2*MARGIN)
                os.unlink(tmp_path)
        except Exception as e:
            pdf.ln(5)
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(150, 0, 0)
            pdf.cell(0, 5, f"No se pudieron generar los graficos: {str(e)}", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_text_color(0, 0, 0)
    
    def _system(self, pdf: BenchmarkPDF) -> None:
        """Informacion del sistema."""
        self._header(pdf, "INFORMACION DEL SISTEMA")
        
        pdf.ln(3)
        p = self.system_info.get("platform", {})
        
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, "Plataforma:", new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 6, f"{p.get('system', 'N/A')} {p.get('release', '')}", new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.ln(8)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(50, 6, "Maquina:", new_x=XPos.LEFT)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 6, p.get('machine', 'N/A'), new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.cell(50, 6, "Procesador:", new_x=XPos.LEFT)
        pdf.cell(0, 6, p.get('processor', 'N/A')[:60], new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.cell(50, 6, "Python:", new_x=XPos.LEFT)
        pdf.cell(0, 6, p.get('python_version', 'N/A'), new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.cell(50, 6, "Hostname:", new_x=XPos.LEFT)
        pdf.cell(0, 6, self.system_info.get('hostname', 'N/A'), new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.cell(50, 6, "Fecha:", new_x=XPos.LEFT)
        pdf.cell(0, 6, self.system_info.get('timestamp', 'N/A')[:19], new_x=XPos.LEFT, new_y=YPos.NEXT)
        
        pdf.set_text_color(0, 0, 0)
    
    def _header(self, pdf: BenchmarkPDF, title: str) -> None:
        """Encabezado de seccion."""
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 8, title, align=Align.C, new_y=YPos.NEXT)
        pdf.ln(4)
        pdf.set_line_width(0.5)
        pdf.set_draw_color(0, 51, 102)
        pdf.line(MARGIN, pdf.get_y(), PAGE_WIDTH - MARGIN, pdf.get_y())
        pdf.ln(4)