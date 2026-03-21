"""
Interfaz principal del Solver con Gurobi.

Para ejecutar desde la linea de comando:
    python main.py data/problem.txt
    python main.py data/problem.txt --visualize
    python main.py data/problem.txt --pdf
    python main.py data/problem.txt --visualize --pdf

Para múltiples problemas:
    python main.py data/problem.txt --multi
    python main.py data/problem.txt --multi --pdf
"""

import sys
import time
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ExecutionTimes:
    """Almacena los tiempos de ejecución del programa."""
    parse_time: float = 0.0
    build_time: float = 0.0
    solve_time: float = 0.0
    visualize_time: float = 0.0
    pdf_time: float = 0.0
    total_time: float = 0.0


def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]

    # Verificar argumentos
    visualize = "--visualize" in argv or "-v" in argv
    pdf = "--pdf" in argv or "-p" in argv
    help_flag = "--help" in argv or "-h" in argv
    show_times = "--times" in argv or "-t" in argv
    multi_flag = "--multi" in argv or "-m" in argv

    if help_flag:
        print("Uso: python main.py <ruta_al_archivo_lp> [opciones]")
        print("Opciones:")
        print("  --multi, -m       : Resolver multiples problemas")
        print("  --visualize, -v  : Mostrar grafica de la region factible")
        print("  --pdf, -p        : Generar reporte PDF")
        print("  --times, -t      : Mostrar tiempos de ejecucion")
        print("  --help, -h       : Mostrar esta ayuda")
        sys.exit(0)

    if not argv or ("--" in argv[0] and not Path(argv[0]).exists()):
        print("Uso: python main.py <archivo> [--opciones]")
        sys.exit(1)

    path = Path(argv[0])
    if not path.exists():
        print(f"El archivo no existe: {path}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")

    if multi_flag:
        _run_multi(text, path, visualize, pdf, show_times)
    else:
        _run_single(text, path, visualize, pdf, show_times)


def _run_multi(text: str, path: Path, visualize: bool,
                   pdf: bool, show_times: bool) -> None:
    """Ejecuta el modo multi-problema."""
    from src.parser import MultiLPParser
    from src.solver import MultiSolver
    from src.analysis import MultiLPAnalysis

    # Importaciones base
    total_start = time.perf_counter()

    # Contar problemas
    num_problems = MultiLPParser.count_problems(text)
    print(f"\n{'='*50}")
    print("MODO MULTI-PROBLEMA")
    print(f"{'='*50}")
    print(f"Problemas encontrados: {num_problems}")

    if num_problems == 0:
        print("No se encontraron problemas en el archivo.")
        sys.exit(1)

    # Resolver todos los problemas
    print("\nResolviendo problemas...\n")
    result = MultiSolver.solve_from_text(text)

    # Mostrar resultados y generar visualizaciones
    print(f"\n{'='*50}")
    print("RESULTADOS")
    print(f"{'='*50}")

    for i, res in enumerate(result.results):
        problem_name = res.problem.name or f"Problema {i+1}"
        print(f"\n--- {problem_name} ---")
        print(f"Estado: {res.solution.status}")
        if res.solution.objective_value is not None:
            print(f"Valor óptimo: {res.solution.objective_value:.4f}")
        if res.error:
            print(f"Error: {res.error}")
        print(f"Tiempo: {res.total_time*1000:.2f} ms")

        # Generar visualización si se solicita y es problema de 2 variables
        if visualize and len(res.problem.variables) == 2 and not res.error:
            try:
                from src.visualization import LinearVisualization

                print(f"Generando gráfica para {problem_name}...")
                viz = LinearVisualization(res.problem, res.solution)
                # Usar nombre del problema para el archivo
                safe_name = problem_name.replace(" ", "_").lower()
                output_img = path.parent / f"{path.stem}_{safe_name}.png"
                viz.plot(save_path=str(output_img), show=False)
                print(f"Gráfica guardada en: {output_img}")
            except Exception as e:
                print(f"Error al generar visualización: {e}")

    # Generar PDF si se solicita
    pdf_time = 0.0
    if pdf:
        print("\nGenerando reporte PDF...")
        pdf_start = time.perf_counter()
        try:
            analysis = MultiLPAnalysis(result)
            output_pdf = path.with_suffix('.pdf')
            analysis.generate_pdf(str(output_pdf))
            print(f"PDF guardado en: {output_pdf}")
        except Exception as e:
            print(f"Error al generar PDF: {e}")
        pdf_time = time.perf_counter() - pdf_start
        result.total_time += pdf_time

    total_time = time.perf_counter() - total_start

    # Mostrar tiempos si se solicita
    if show_times:
        print("\n" + "=" * 50)
        print("TIEMPOS DE EJECUCION")
        print("=" * 50)
        print(f"Parseo de problemas:    {result.total_parse_time*1000:.2f} ms")
        print(f"Construccion de LP:     {result.total_build_time*1000:.2f} ms")
        print(f"Resolucion (Gurobi):   {result.total_solve_time*1000:.2f} ms")
        if pdf:
            print(f"Generacion PDF:        {pdf_time*1000:.2f} ms")
        print("-" * 50)
        print(f"TOTAL:                  {total_time*1000:.2f} ms")
        print("=" * 50)

    exito = len(result.get_successful_results())
    total = len(result.results)
    print(f"\nProblemas resueltos: {exito}/{total}")


def _run_single(
    text: str, path: Path, visualize: bool,
    pdf: bool, show_times: bool
) -> None:
    """Ejecuta el modo single-problema (original)."""
    # Importaciones base
    from src.parser import LPParser
    from src.matrix import LPBuilder
    from src.solver import SolverLP

    # Tiempos de ejecución
    times = ExecutionTimes()

    # === FASE 1: Parseo ===
    parse_start = time.perf_counter()
    problem = LPParser(text).parse()
    times.parse_time = time.perf_counter() - parse_start

    # === FASE 2: Construcción ===
    build_start = time.perf_counter()
    lp = LPBuilder(problem).build()
    times.build_time = time.perf_counter() - build_start

    # === FASE 3: Resolución ===
    solve_start = time.perf_counter()
    solver = SolverLP(lp)
    solution = solver.solve()
    times.solve_time = time.perf_counter() - solve_start

    # Calcular tiempo total hasta aqui
    times.total_time = (
        times.parse_time +
        times.build_time +
        times.solve_time
    )

    # Generar visualizacion si se solicita
    if visualize:
        visualize_start = time.perf_counter()
        try:
            from src.visualization import LinearVisualization

            if len(problem.variables) == 2:
                print("\nGenerando visualizacion...")
                viz = LinearVisualization(problem, solution)
                output_image = path.with_suffix('.png')
                viz.plot(save_path=str(output_image), show=False)
                print(f"Grafica guardada en: {output_image}")
            else:
                print("\nVisualizacion solo para 2 variables.")
        except Exception as e:
            print(f"Error al generar visualizacion: {e}")
        times.visualize_time = time.perf_counter() - visualize_start
        times.total_time += times.visualize_time

    # Generar PDF si se solicita
    if pdf:
        pdf_start = time.perf_counter()
        try:
            from src.analysis import LPAnalysis

            print("\nGenerando reporte PDF...")
            analysis = LPAnalysis(problem, solution)
            output_pdf = path.with_suffix('.pdf')
            analysis.generate_pdf(str(output_pdf))
            print(f"PDF guardado en: {output_pdf}")
        except Exception as e:
            print(f"Error al generar PDF: {e}")
        times.pdf_time = time.perf_counter() - pdf_start
        times.total_time += times.pdf_time

    # Mostrar tiempos si se solicita
    if show_times:
        print("\n" + "=" * 50)
        print("TIEMPOS DE EJECUCION")
        print("=" * 50)
        print(f"Parseo del problema:    {times.parse_time*1000:.2f} ms")
        print(f"Construccion del LP:    {times.build_time*1000:.2f} ms")
        print(f"Resolucion (Gurobi):   {times.solve_time*1000:.2f} ms")
        if visualize:
            print(f"Visualizacion:         {times.visualize_time*1000:.2f} ms")
        if pdf:
            print(f"Generacion PDF:        {times.pdf_time*1000:.2f} ms")
        print("-" * 50)
        print(f"TOTAL:                  {times.total_time*1000:.2f} ms")
        print("=" * 50)


if __name__ == "__main__":
    main()
