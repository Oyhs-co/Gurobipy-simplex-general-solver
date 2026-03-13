""""
Interfaz principal del Solver con Gurobi.

Para ejecutar desde la línea de comando:
    python main.py data/problem.txt
"""

from src.parser import LPParser
from src.matrix import LPBuilder
from src.solver import SolverLP
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> None:
    argv = argv or sys.argv[1:]

    if not argv:
        print("Uso: python main.py <ruta_al_archivo_lp>")
        sys.exit(1)

    path = Path(argv[0])
    if not path.exists():
        print(f"El archivo no existe: {path}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")

    problem = LPParser(text).parse()
    lp = LPBuilder(problem).build()

    SolverLP(lp).solve()


if __name__ == "__main__":
    main()
