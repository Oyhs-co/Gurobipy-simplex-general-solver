""""
Interfaz principal del Solver con Gurobi.
Aquí se pueden definir las funciones y clases que los usuarios del paquete
puedan utilizar para resolver problemas de programación lineal utilizando el
método Simplex con Gurobi.
"""

from .solver import SolverLP

__all__ = ["SolverLP"]
