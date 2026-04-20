"""
Main CLI interface for the LP Solver with Gurobi.

Usage:
    python main.py data/problem.txt
    python main.py data/problem.txt --verbose
    python main.py data/problem.txt --visualize
    python main.py data/problem.txt --pdf
    python main.py data/problem.txt --visualize --pdf

For multiple problems:
    python main.py data/problem.txt --multi
    python main.py data/problem.txt --multi --pdf
"""

import sys
import time
from pathlib import Path
from src.analysis.analysis import ExecutionTimes


def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]

    visualize = "--visualize" in argv or "-v" in argv
    pdf = "--pdf" in argv or "-p" in argv
    help_flag = "--help" in argv or "-h" in argv
    show_times = "--times" in argv or "-t" in argv
    multi_flag = "--multi" in argv or "-m" in argv
    verbose = "--verbose" in argv or "-V" in argv

    if help_flag:
        print("Usage: python main.py <path_to_lp_file> [options]")
        print("Options:")
        print("  --multi, -m       : Solve multiple problems")
        print("  --visualize, -v   : Show feasible region graph")
        print("  --pdf, -p         : Generate PDF report")
        print("  --times, -t       : Show execution times")
        print("  --verbose, -V     : Show detailed solver output")
        print("  --help, -h        : Show this help")
        sys.exit(0)

    if not argv or ("--" in argv[0] and not Path(argv[0]).exists()):
        print("Usage: python main.py <file> [options]")
        sys.exit(1)

    path = Path(argv[0])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")

    if multi_flag:
        _run_multi(text, path, visualize, pdf, show_times, verbose)
    else:
        _run_single(text, path, visualize, pdf, show_times, verbose)


def _run_multi(
    text: str, path: Path, visualize: bool,
    pdf: bool, show_times: bool, verbose: bool
) -> None:
    """Execute multi-problem mode."""
    from src.parser import MultiLPParser
    from src.solver import MultiSolver
    from src.analysis import MultiLPAnalysis

    total_start = time.perf_counter()

    num_problems = MultiLPParser.count_problems(text)
    print(f"\n{'='*50}")
    print("MULTI-PROBLEM MODE")
    print(f"{'='*50}")
    print(f"Problems found: {num_problems}")

    if num_problems == 0:
        print("No problems found in file.")
        sys.exit(1)

    print("\nSolving problems...\n")
    result = MultiSolver.solve_from_text(text)

    print(f"\n{'='*50}")
    print("RESULTS")
    print(f"{'='*50}")

    for i, res in enumerate(result.results):
        problem_name = res.problem.name or f"Problem {i+1}"
        print(f"\n--- {problem_name} ---")
        print(f"Status: {res.solution.status}")

        if res.solution.objective_value is not None:
            if verbose:
                print(res.solution.print_summary(verbose=True))
            else:
                print(f"Optimal value: {res.solution.objective_value:.4f}")
                vars_str = ", ".join(
                    f"{k}={v:.2f}" for k, v in sorted(res.solution.variables.items())
                )
                print(f"Variables: {vars_str}")

        if res.error:
            print(f"Error: {res.error}")

        print(f"Time: {res.total_time*1000:.2f} ms")

        if visualize and len(res.problem.variables) == 2 and not res.error:
            try:
                from src.visualization import LinearVisualization

                print(f"Generating graph for {problem_name}...")
                viz = LinearVisualization(res.problem, res.solution)
                safe_name = problem_name.replace(" ", "_").lower()
                output_img = path.parent / f"{path.stem}_{safe_name}.png"
                viz.plot(save_path=str(output_img), show=False)
                print(f"Graph saved to: {output_img}")
            except Exception as e:
                print(f"Error generating visualization: {e}")

    pdf_time = 0.0
    if pdf:
        print("\nGenerating PDF report...")
        pdf_start = time.perf_counter()
        try:
            analysis = MultiLPAnalysis(result)
            output_pdf = path.with_suffix('.pdf')
            analysis.generate_pdf(str(output_pdf))
            print(f"PDF saved to: {output_pdf}")
        except Exception as e:
            print(f"Error generating PDF: {e}")
        pdf_time = time.perf_counter() - pdf_start
        result.total_time += pdf_time

    total_time = time.perf_counter() - total_start

    if show_times:
        print("\n" + "=" * 50)
        print("EXECUTION TIMES")
        print("=" * 50)
        print(f"Parsing:            {result.total_parse_time*1000:.2f} ms")
        print(f"Building LP:        {result.total_build_time*1000:.2f} ms")
        print(f"Solving (Gurobi):  {result.total_solve_time*1000:.2f} ms")
        if pdf:
            print(f"PDF generation:     {pdf_time*1000:.2f} ms")
        print("-" * 50)
        print(f"TOTAL:              {total_time*1000:.2f} ms")
        print("=" * 50)

    success = len(result.get_successful_results())
    total = len(result.results)
    print(f"\nProblems solved: {success}/{total}")


def _run_single(
    text: str, path: Path, visualize: bool,
    pdf: bool, show_times: bool, verbose: bool
) -> None:
    """Execute single-problem mode."""
    from src.parser import LPParser
    from src.matrix import LPBuilder
    from src.solver import SolverLP, SolverConfig

    times = ExecutionTimes()

    parse_start = time.perf_counter()
    problem = LPParser(text).parse()
    times.parse_time = time.perf_counter() - parse_start

    build_start = time.perf_counter()
    lp = LPBuilder(problem).build()
    times.build_time = time.perf_counter() - build_start

    solve_start = time.perf_counter()
    config = SolverConfig(verbose=verbose)
    solver = SolverLP(lp, config=config)
    solution = solver.solve()
    times.solve_time = time.perf_counter() - solve_start

    times.total_time = (
        times.parse_time +
        times.build_time +
        times.solve_time
    )

    if verbose:
        print("\n" + solution.print_summary(verbose=True))
    else:
        if solution.objective_value is not None:
            print(f"Optimal value: {solution.objective_value:.2f}")
            for var, value in sorted(solution.variables.items()):
                print(f"{var} = {value:.2f}")

    if visualize:
        visualize_start = time.perf_counter()
        try:
            from src.visualization import LinearVisualization

            if len(problem.variables) == 2:
                print("\nGenerating visualization...")
                viz = LinearVisualization(problem, solution)
                output_image = path.with_suffix('.png')
                viz.plot(save_path=str(output_image), show=False)
                print(f"Graph saved to: {output_image}")
            else:
                print("\nVisualization only for 2 variables.")
        except Exception as e:
            print(f"Error generating visualization: {e}")
        times.visualize_time = time.perf_counter() - visualize_start
        times.total_time += times.visualize_time

    if pdf:
        pdf_start = time.perf_counter()
        try:
            from src.analysis import LPAnalysis

            print("\nGenerating PDF report...")
            analysis = LPAnalysis(problem, solution, times)
            output_pdf = path.with_suffix('.pdf')
            analysis.generate_pdf(str(output_pdf))
            print(f"PDF saved to: {output_pdf}")
        except Exception as e:
            print(f"Error generating PDF: {e}")
        times.pdf_time = time.perf_counter() - pdf_start
        times.total_time += times.pdf_time

    if show_times:
        print("\n" + "=" * 50)
        print("EXECUTION TIMES")
        print("=" * 50)
        print(f"Parsing:            {times.parse_time*1000:.2f} ms")
        print(f"Building LP:        {times.build_time*1000:.2f} ms")
        print(f"Solving (Gurobi):  {times.solve_time*1000:.2f} ms")
        if visualize:
            print(f"Visualization:      {times.visualize_time*1000:.2f} ms")
        if pdf:
            print(f"PDF generation:     {times.pdf_time*1000:.2f} ms")
        print("-" * 50)
        print(f"TOTAL:              {times.total_time*1000:.2f} ms")
        print("=" * 50)


if __name__ == "__main__":
    main()