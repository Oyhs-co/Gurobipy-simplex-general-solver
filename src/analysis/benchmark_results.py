"""
Visualizacion y exportacion de resultados de benchmarking.
Genera graficos comparativos y reportes visuales.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
import json

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime

from src.solver.benchmark import BenchmarkRunner, BenchmarkResult


@dataclass
class PlotStyle:
    """Estilos para los graficos."""
    primary_color: str = "#003366"
    secondary_color: str = "#0066CC"
    success_color: str = "#228B22"
    error_color: str = "#DC143C"
    warning_color: str = "#FF8C00"
    grid_alpha: float = 0.3
    figure_size: tuple = (10, 6)
    font_size: int = 10


class BenchmarkVisualizer:
    """
    Genera visualizaciones para resultados de benchmarking.
    """
    
    def __init__(self, runner: BenchmarkRunner, style: Optional[PlotStyle] = None):
        self.runner = runner
        self.style = style or PlotStyle()
        self.results = runner.results
        self.summary = runner.get_summary()
    
    def plot_times_comparison(self, save_path: Optional[Path] = None) -> None:
        """Grafica comparacion de tiempos por solver y problema."""
        if not self.results:
            return
        
        solvers = list(self.summary["by_solver"].keys())
        problems = list(self.summary["by_problem"].keys())
        
        fig, ax = plt.subplots(figsize=self.style.figure_size)
        
        x = np.arange(len(problems))
        width = 0.8 / max(len(solvers), 1)
        
        colors = plt.cm.Set2(np.linspace(0, 1, len(solvers)))
        
        for i, solver in enumerate(solvers):
            times = []
            for problem in problems:
                found = False
                for r in self.results:
                    if r.solver_name == solver and r.problem_name == problem:
                        times.append(r.total_time * 1000)
                        found = True
                        break
                if not found:
                    times.append(0)
            
            offset = (i - len(solvers)/2 + 0.5) * width
            bars = ax.bar(x + offset, times, width, label=solver, color=colors[i])
        
        ax.set_xlabel('Problemas', fontsize=self.style.font_size)
        ax.set_ylabel('Tiempo (ms)', fontsize=self.style.font_size)
        ax.set_title('Comparacion de Tiempos de Resolucion', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(problems, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=self.style.grid_alpha, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_success_rate(self, save_path: Optional[Path] = None) -> None:
        """Grafica tasa de exito por solver."""
        if not self.results:
            return
        
        fig, ax = plt.subplots(figsize=self.style.figure_size)
        
        solvers = list(self.summary["by_solver"].keys())
        total = []
        successful = []
        
        for solver in solvers:
            total.append(self.summary["by_solver"][solver]["runs"])
            successful.append(self.summary["by_solver"][solver]["successful"])
        
        x = np.arange(len(solvers))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, total, width, label='Total', color=self.style.secondary_color)
        bars2 = ax.bar(x + width/2, successful, width, label='Exitosos', color=self.style.success_color)
        
        ax.set_xlabel('Solver', fontsize=self.style.font_size)
        ax.set_ylabel('Numero de Pruebas', fontsize=self.style.font_size)
        ax.set_title('Tasa de Exito por Solver', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(solvers)
        ax.legend()
        ax.grid(True, alpha=self.style.grid_alpha, linestyle='--', axis='y')
        
        for bar in bars2:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_performance_profile(self, save_path: Optional[Path] = None) -> None:
        """Grafica perfil de rendimiento (tiempo relativo al mas rapido)."""
        if not self.results:
            return
        
        problems = list(self.summary["by_problem"].keys())
        solvers = list(self.summary["by_solver"].keys())
        
        fig, ax = plt.subplots(figsize=self.style.figure_size)
        
        for i, solver in enumerate(solvers):
            ratios = []
            for problem in problems:
                times = []
                for r in self.results:
                    if r.problem_name == problem and r.solution.is_optimal():
                        times.append(r.total_time)
                
                if times:
                    min_time = min(times)
                    for r in self.results:
                        if r.solver_name == solver and r.problem_name == problem and r.solution.is_optimal():
                            ratios.append(r.total_time / min_time if min_time > 0 else 1)
                            break
                else:
                    ratios.append(np.nan)
            
            ax.plot(problems, ratios, 'o-', label=solver, markersize=8)
        
        ax.set_xlabel('Problema', fontsize=self.style.font_size)
        ax.set_ylabel('Ratio de Tiempo (vs. mas rapido)', fontsize=self.style.font_size)
        ax.set_title('Perfil de Rendimiento', fontsize=14, fontweight='bold')
        ax.set_xticklabels(problems, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=self.style.grid_alpha, linestyle='--')
        ax.axhline(y=1, color='gray', linestyle=':', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_summary_dashboard(self, save_path: Optional[Path] = None) -> None:
        """Genera un dashboard con todas las metricas."""
        if not self.results:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        title = f"Dashboard de Benchmarking\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        ax1 = axes[0, 0]
        solvers = list(self.summary["by_solver"].keys())
        avg_times = [self.summary["by_solver"][s]["avg_time"] * 1000 for s in solvers]
        bars = ax1.barh(solvers, avg_times, color=self.style.primary_color)
        ax1.set_xlabel('Tiempo Promedio (ms)')
        ax1.set_title('Tiempo Promedio por Solver')
        ax1.grid(True, alpha=self.style.grid_alpha, axis='x')
        for bar, time in zip(bars, avg_times):
            ax1.text(time + 0.1, bar.get_y() + bar.get_height()/2, f'{time:.2f}ms', 
                    va='center', fontsize=9)
        
        ax2 = axes[0, 1]
        total = [self.summary["by_solver"][s]["runs"] for s in solvers]
        successful = [self.summary["by_solver"][s]["successful"] for s in solvers]
        x = np.arange(len(solvers))
        ax2.bar(x - 0.2, total, 0.4, label='Total', color=self.style.secondary_color)
        ax2.bar(x + 0.2, successful, 0.4, label='Exitosos', color=self.style.success_color)
        ax2.set_xticks(x)
        ax2.set_xticklabels(solvers)
        ax2.set_title('Tasa de Exito')
        ax2.legend()
        ax2.grid(True, alpha=self.style.grid_alpha, axis='y')
        
        ax3 = axes[1, 0]
        problems = list(self.summary["by_problem"].keys())
        problem_times = {}
        for problem in problems:
            problem_times[problem] = []
            for r in self.results:
                if r.problem_name == problem and r.solution.is_optimal():
                    problem_times[problem].append(r.total_time * 1000)
        
        ax3.boxplot([problem_times[p] for p in problems], labels=problems)
        ax3.set_ylabel('Tiempo (ms)')
        ax3.set_title('Distribucion de Tiempos por Problema')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=self.style.grid_alpha, axis='y')
        
        ax4 = axes[1, 1]
        categories = ['Total', 'Exitosos', 'Fallidos']
        values = [
            self.summary['total_benchmarks'],
            self.summary['successful'],
            self.summary['failed']
        ]
        colors = [self.style.secondary_color, self.style.success_color, self.style.error_color]
        wedges, texts, autotexts = ax4.pie(values, labels=categories, colors=colors, 
                                          autopct='%1.1f%%', startangle=90)
        ax4.set_title('Resumen General')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def generate_all_plots(self, output_dir: Path, prefix: str = "benchmark") -> Dict[str, Path]:
        """Genera todos los graficos y los guarda."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        paths = {}
        
        paths['times'] = output_dir / f"{prefix}_times.png"
        self.plot_times_comparison(paths['times'])
        
        paths['success'] = output_dir / f"{prefix}_success.png"
        self.plot_success_rate(paths['success'])
        
        paths['profile'] = output_dir / f"{prefix}_profile.png"
        self.plot_performance_profile(paths['profile'])
        
        paths['dashboard'] = output_dir / f"{prefix}_dashboard.png"
        self.plot_summary_dashboard(paths['dashboard'])
        
        return paths


class ResultsExporter:
    """Exportador de resultados de benchmarking a multiple formatos."""
    
    def __init__(self, runner: BenchmarkRunner):
        self.runner = runner
        self.results = runner.results
        self.summary = runner.get_summary()
    
    def to_markdown(self, path: Path) -> None:
        """Exporta resultados a formato Markdown."""
        lines = [
            "# Reporte de Benchmarking",
            f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n## Resumen",
            f"- Total de pruebas: {self.summary['total_benchmarks']}",
            f"- Exitosas: {self.summary['successful']}",
            f"- Fallidas: {self.summary['failed']}",
            f"\n## Por Solver",
        ]
        
        lines.append(f"\n| Solver | Pruebas | Exitosas | Tiempo Promedio |")
        lines.append(f"|--------|---------|----------|-----------------|")
        
        for solver, data in self.summary["by_solver"].items():
            avg_time = data["avg_time"] * 1000
            lines.append(f"| {solver} | {data['runs']} | {data['successful']} | {avg_time:.2f}ms |")
        
        lines.append(f"\n## Detalle de Resultados")
        
        lines.append(f"\n| Problema | Solver | Estado | Valor Obj. | Tiempo |")
        lines.append(f"|----------|--------|--------|------------|--------|")
        
        for r in self.results:
            status_icon = "OK" if r.solution.is_optimal() else "X"
            obj_val = f"{r.solution.objective_value:.2f}" if r.solution.objective_value else "-"
            lines.append(f"| {r.problem_name} | {r.solver_name} | {status_icon} | {obj_val} | {r.total_time*1000:.2f}ms |")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write("\n".join(lines))
    
    def to_html(self, path: Path, include_plots: bool = True, plots_dir: Optional[Path] = None) -> None:
        """Exporta resultados a formato HTML."""
        plots_html = ""
        if include_plots and plots_dir:
            plots_dir.mkdir(parents=True, exist_ok=True)
            visualizer = BenchmarkVisualizer(self.runner)
            paths = visualizer.generate_all_plots(plots_dir)
            
            plots_html = "\n## Graficos\n"
            for name, plot_path in paths.items():
                plots_html += f'\n![{name}]({plot_path.name})\n'
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Benchmark Report</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #003366; }}
        h2 {{ color: #0066CC; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #003366; color: white; }}
        tr:nth-child(even) {{ background-color: #f8f8f8; }}
        .success {{ color: #228B22; font-weight: bold; }}
        .error {{ color: #DC143C; font-weight: bold; }}
        .summary {{ background-color: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        img {{ max-width: 100%; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Reporte de Benchmarking</h1>
    <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>Resumen</h2>
        <ul>
            <li><strong>Total de pruebas:</strong> {self.summary['total_benchmarks']}</li>
            <li><strong>Exitosas:</strong> {self.summary['successful']}</li>
            <li><strong>Fallidas:</strong> {self.summary['failed']}</li>
        </ul>
    </div>
    
    <h2>Por Solver</h2>
    <table>
        <tr>
            <th>Solver</th>
            <th>Pruebas</th>
            <th>Exitosas</th>
            <th>Tiempo Promedio</th>
        </tr>
        {''.join(f"<tr><td>{solver}</td><td>{data['runs']}</td><td>{data['successful']}</td><td>{data['avg_time']*1000:.2f}ms</td></tr>" for solver, data in self.summary["by_solver"].items())}
    </table>
    
    <h2>Detalle de Resultados</h2>
    <table>
        <tr>
            <th>Problema</th>
            <th>Solver</th>
            <th>Estado</th>
            <th>Valor Obj.</th>
            <th>Tiempo</th>
        </tr>
        {''.join(f"<tr><td>{r.problem_name}</td><td>{r.solver_name}</td><td class=\"{'success' if r.solution.is_optimal() else 'error'}\">{r.solution.status}</td><td>{r.solution.objective_value if r.solution.objective_value else '-'}</td><td>{r.total_time*1000:.2f}ms</td></tr>" for r in self.results)}
    </table>
    
    {plots_html}
</body>
</html>
"""
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(html)
    
    def to_polars_dataframe(self):
        """Convierte resultados a un Polars DataFrame."""
        import polars as pl
        
        data = []
        for r in self.results:
            data.append({
                "problem": r.problem_name,
                "solver": r.solver_name,
                "status": r.solution.status,
                "objective_value": r.solution.objective_value,
                "parse_time_ms": r.parse_time * 1000,
                "build_time_ms": r.build_time * 1000,
                "solve_time_ms": r.stats.solve_time * 1000,
                "total_time_ms": r.total_time * 1000,
                "iterations": r.stats.iterations,
                "nodes": r.stats.nodes,
                "error": r.error
            })
        
        return pl.DataFrame(data)


def export_benchmark_results(
    runner: BenchmarkRunner,
    output_dir: Path,
    formats: List[str] = ["json", "csv", "md", "html"],
    include_plots: bool = True
) -> Dict[str, Path]:
    """
    Exporta todos los resultados de benchmarking.
    
    Args:
        runner: BenchmarkRunner con los resultados
        output_dir: Directorio de salida
        formats: Formatos a exportar (json, csv, md, html)
        include_plots: Si generar graficos
        
    Returns:
        Diccionario con las rutas de archivos generados
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    
    exporter = ResultsExporter(runner)
    
    if "json" in formats:
        paths["json"] = output_dir / "benchmark_results.json"
        runner.export_json(paths["json"])
    
    if "csv" in formats:
        paths["csv"] = output_dir / "benchmark_results.csv"
        runner.export_csv(paths["csv"])
    
    if "md" in formats:
        paths["md"] = output_dir / "benchmark_report.md"
        exporter.to_markdown(paths["md"])
    
    if "html" in formats:
        plots_dir = output_dir / "plots" if include_plots else None
        paths["html"] = output_dir / "benchmark_report.html"
        exporter.to_html(paths["html"], include_plots=include_plots, plots_dir=plots_dir)
    
    return paths