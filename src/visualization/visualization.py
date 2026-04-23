"""
Módulo de visualización para problemas de programación lineal.

Este módulo proporciona herramientas para visualizar:
- Las rectas que representan las restricciones
- Las intersecciones entre restricciones
- La región factible del problema
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from typing import Optional
import math

from ..core import LinearProblem, LinearConstraint, Solution


class LinearVisualization:
    """
    Clase para visualizar problemas de programación lineal en 2D.
    
    ### attributes:
    - problem: LinearProblem - El problema de programación lineal.
    - solution: Solution - La solución óptima (opcional).
    """
    
    def __init__(self, problem: LinearProblem, solution: Optional[Solution] = None):
        """
        Inicializa el visualizador con un problema de programación lineal.
        
        ### parameters:
        - problem: LinearProblem - El problema de programación lineal a visualizar.
        - solution: Solution - La solución óptima (opcional).
        """
        self.problem = problem
        self.solution = solution
        
        # Verificar que el problema tenga exactly 2 variables
        if len(problem.variables) != 2:
            raise ValueError(
                f"La visualización solo funciona con 2 variables. "
                f"El problema tiene {len(problem.variables)} variables: {problem.variables}"
            )
        
        self.var_x = problem.variables[0]
        self.var_y = problem.variables[1]
    
    def find_intersection(self, c1: LinearConstraint, c2: LinearConstraint) -> Optional[tuple[float, float]]:
        """
        Encuentra la intersección entre dos restricciones lineales.
        
        Para dos restricciones de la forma:
        a1*x + b1*y = r1
        a2*x + b2*y = r2
        
        Usamos la regla de Cramer para resolver el sistema.
        
        ### parameters:
        - c1: LinearConstraint - Primera restricción.
        - c2: LinearConstraint - Segunda restricción.
        
        ### returns:
        - tuple[float, float] | None - Las coordenadas (x, y) de la intersección, o None si no hay intersección.
        """
        # Extraer coeficientes
        a1 = c1.coefficients.get(self.var_x, 0)
        b1 = c1.coefficients.get(self.var_y, 0)
        r1 = c1.rhs
        
        a2 = c2.coefficients.get(self.var_x, 0)
        b2 = c2.coefficients.get(self.var_y, 0)
        r2 = c2.rhs
        
        # Calcular determinante
        det = a1 * b2 - a2 * b1
        
        if abs(det) < 1e-10:
            return None  # Rectas paralelas
        
        # Regla de Cramer
        x = (r1 * b2 - r2 * b1) / det
        y = (a1 * r2 - a2 * r1) / det
        
        return (x, y)
    
    def is_point_feasible(self, x: float, y: float, constraints: list[LinearConstraint]) -> bool:
        """
        Verifica si un punto satisface todas las restricciones.
        
        ### parameters:
        - x: float - Coordenada x del punto.
        - y: float - Coordenada y del punto.
        - constraints: list[LinearConstraint] - Lista de restricciones.
        
        ### returns:
        - bool - True si el punto es factible, False en caso contrario.
        """
        for c in constraints:
            value = 0
            value += c.coefficients.get(self.var_x, 0) * x
            value += c.coefficients.get(self.var_y, 0) * y
            
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
    
    def get_constraint_line_x(self, c: LinearConstraint, x_range: tuple[float, float]) -> tuple[np.ndarray, np.ndarray]:
        """
        Obtiene los puntos (x, y) para graficar una restricción como línea.
        
        Resuelve para y en términos de x: y = (rhs - a*x) / b
        
        ### parameters:
        - c: LinearConstraint - La restricción.
        - x_range: tuple[float, float] - Rango de x para graficar.
        
        ### returns:
        - tuple[np.ndarray, np.ndarray] - Arrays de x e y para la línea.
        """
        a = c.coefficients.get(self.var_x, 0)
        b = c.coefficients.get(self.var_y, 0)
        rhs = c.rhs
        
        x_vals = np.linspace(x_range[0], x_range[1], 100)
        
        if abs(b) < 1e-10:
            # Si b = 0, la restricción es a*x = rhs (línea vertical)
            if abs(a) < 1e-10:
                return np.array([]), np.array([])  # Restricción inválida
            x_const = rhs / a
            return np.full_like(x_vals, x_const), x_vals
        else:
            y_vals = (rhs - a * x_vals) / b
            return x_vals, y_vals
    
    def find_feasible_vertices(self) -> list[tuple[float, float]]:
        """
        Encuentra los vértices de la región factible.
        
        ### returns:
        - list[tuple[float, float]] - Lista de vértices factibles.
        """
        # Recopilar todas las restricciones
        constraints = self.problem.constraints.copy()
        
        bounds = self.problem.bounds
        x_bound = bounds.get(self.var_x)
        if x_bound is None or x_bound.lower is None or x_bound.lower < 0:
            constraints.append(LinearConstraint(
                coefficients={self.var_x: 1},
                rhs=0,
                sense=">="
            ))
        y_bound = bounds.get(self.var_y)
        if y_bound is None or y_bound.lower is None or y_bound.lower < 0:
            constraints.append(LinearConstraint(
                coefficients={self.var_y: 1},
                rhs=0,
                sense=">="
            ))
        
        vertices: list[tuple[float, float]] = []
        
        # Intersecciones entre todas las restricciones
        for i, c1 in enumerate(constraints):
            for c2 in constraints[i+1:]:
                intersection = self.find_intersection(c1, c2)
                if intersection is not None:
                    x, y = intersection
                    if self.is_point_feasible(x, y, constraints):
                        # Verificar que no sea un duplicado
                        if not any(math.isclose(x, v[0], abs_tol=1e-6) and math.isclose(y, v[1], abs_tol=1e-6) for v in vertices):
                            vertices.append((x, y))
        
        # Intersecciones con los ejes si son factibles
        # Eje x (y = 0)
        for c in constraints:
            value_at_x_axis = c.coefficients.get(self.var_x, 0)
            coeff_y = c.coefficients.get(self.var_y, 0)
            if abs(coeff_y) > 1e-10:
                x_at_y0 = c.rhs / coeff_y
                if self.is_point_feasible(x_at_y0, 0, constraints):
                    if not any(math.isclose(x_at_y0, v[0], abs_tol=1e-6) and math.isclose(0, v[1], abs_tol=1e-6) for v in vertices):
                        vertices.append((x_at_y0, 0))
        
        # Eje y (x = 0)
        for c in constraints:
            coeff_x = c.coefficients.get(self.var_x, 0)
            value_at_y_axis = c.coefficients.get(self.var_y, 0)
            if abs(coeff_x) > 1e-10:
                y_at_x0 = c.rhs / coeff_x
                if self.is_point_feasible(0, y_at_x0, constraints):
                    if not any(math.isclose(0, v[0], abs_tol=1e-6) and math.isclose(y_at_x0, v[1], abs_tol=1e-6) for v in vertices):
                        vertices.append((0, y_at_x0))
        
        # Origen siempre es un vértice factible si x >= 0 e y >= 0
        if self.is_point_feasible(0, 0, constraints):
            if not any(v[0] == 0 and v[1] == 0 for v in vertices):
                vertices.append((0, 0))
        
        return vertices
    
    def plot(self, save_path: Optional[str] = None, show: bool = True) -> None:
        """
        Genera la visualización completa del problema.

        Parameters:
            save_path: Ruta para guardar la imagen (opcional).
            show: Si True, muestra el gráfico.
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Determinar el rango del gráfico (permite valores negativos)
        (x_min, x_max), (y_min, y_max) = self._calculate_plot_range()

        # Graficar las rectas de las restricciones
        self._plot_constraints(ax, (x_min, x_max))

        # Encontrar y graficar la región factible
        self._plot_feasible_region(ax, (x_min, x_max), (y_min, y_max))

        # Graficar las intersecciones
        self._plot_intersections(ax)

        # Graficar la solución óptima si existe
        if self.solution:
            self._plot_solution(ax)

        # Configurar el gráfico con plano cartesiano completo
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel(self.var_x, fontsize=12)
        ax.set_ylabel(self.var_y, fontsize=12)
        ax.set_title(f"Region Factible - {self.problem.sense.upper()} {self._format_objective()}", fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linewidth=0.5)
        ax.axvline(x=0, color='k', linewidth=0.5)
        ax.legend(loc='upper right')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        if show:
            plt.show()

        plt.close()
    
    def _calculate_plot_range(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Calcula el rango apropiado para el gráfico, permitiendo valores negativos.

        Returns:
            tuple de rangos (x_min, x_max), (y_min, y_max).
        """
        x_min = -10
        x_max = 10
        y_min = -10
        y_max = 10

        # Usar la solución óptima para determinar el centro del gráfico
        if self.solution:
            sol_x = self.solution.variables.get(self.var_x, 0)
            sol_y = self.solution.variables.get(self.var_y, 0)

            # Expandir según la solución
            x_max = max(x_max, sol_x * 2 if sol_x > 0 else abs(sol_x) * 0.5)
            x_min = min(x_min, sol_x * 2 if sol_x < 0 else -abs(sol_x) * 0.5)
            y_max = max(y_max, sol_y * 2 if sol_y > 0 else abs(sol_y) * 0.5)
            y_min = min(y_min, sol_y * 2 if sol_y < 0 else -abs(sol_y) * 0.5)

        for c in self.problem.constraints:
            a = c.coefficients.get(self.var_x, 0)
            b = c.coefficients.get(self.var_y, 0)
            rhs = c.rhs

            if abs(b) < 1e-10 and abs(a) > 1e-10:
                x_val = abs(rhs / a)
                x_max = max(x_max, x_val * 1.5)
                x_min = min(x_min, -x_val * 0.5)
            elif abs(a) < 1e-10 and abs(b) > 1e-10:
                y_val = abs(rhs / b)
                y_max = max(y_max, y_val * 1.5)
                y_min = min(y_min, -y_val * 0.5)
            else:
                if abs(b) > 1e-10:
                    x_int = rhs / b
                    x_max = max(x_max, x_int * 1.5)
                    x_min = min(x_min, x_int * 0.5 if x_int > 0 else x_int * 1.5)
                if abs(a) > 1e-10:
                    y_int = rhs / a
                    y_max = max(y_max, y_int * 1.5)
                    y_min = min(y_min, y_int * 0.5 if y_int > 0 else y_int * 1.5)

        # Asegurar un rango mínimo
        x_range = x_max - x_min
        y_range = y_max - y_min
        if x_range < 5:
            mid = (x_max + x_min) / 2
            x_min = mid - 2.5
            x_max = mid + 2.5
        if y_range < 5:
            mid = (y_max + y_min) / 2
            y_min = mid - 2.5
            y_max = mid + 2.5

        return (x_min, x_max), (y_min, y_max)
    
    def _plot_constraints(self, ax, x_range: tuple[float, float]) -> None:
        """
        Grafica las rectas de las restricciones.
        
        ### parameters:
        - ax: matplotlib.axes.Axes - Ejes donde graficar.
        - x_range: tuple[float, float] - Rango de x.
        """
        from matplotlib.colors import TABLEAU_COLORS as TAB10_COLORS
        colors = list(TAB10_COLORS)
        
        for i, c in enumerate(self.problem.constraints):
            x_vals, y_vals = self.get_constraint_line_x(c, x_range)
            
            # Determinar el estilo de línea según el tipo de restricción
            if c.sense == "<=":
                linestyle = '-'
                label = f"{self._format_constraint(c)} (<=)"
            elif c.sense == ">=":
                linestyle = '--'
                label = f"{self._format_constraint(c)} (>=)"
            else:
                linestyle = ':'
                label = f"{self._format_constraint(c)} (=)"
            
            ax.plot(x_vals, y_vals, 
                   linestyle=linestyle, 
                   color=colors[i % len(colors)],
                   linewidth=2,
                   label=label)
    
    def _plot_feasible_region(self, ax, x_range: tuple[float, float], y_range: tuple[float, float]) -> None:
        """
        Grafica la región factible.
        
        ### parameters:
        - ax: matplotlib.axes.Axes - Ejes donde graficar.
        - x_range: tuple[float, float] - Rango de x.
        - y_range: tuple[float, float] - Rango de y.
        """
        # Encontrar vértices de la región factible
        vertices = self.find_feasible_vertices()
        
        if not vertices:
            # Si no hay vértices, la región puede ser vacía o no acotada
            # Intentamos una región de prueba
            print("Advertencia: No se pudieron encontrar vertices de la region factible.")
            return
        
        # Ordenar los vértices en sentido antihorario
        if len(vertices) >= 3:
            # Calcular el centroide
            cx = sum(v[0] for v in vertices) / len(vertices)
            cy = sum(v[1] for v in vertices) / len(vertices)
            
            # Ordenar por ángulo desde el centroide
            vertices.sort(key=lambda v: math.atan2(v[1] - cy, v[0] - cx))
        
        # Crear el polígono de la región factible
        polygon = Polygon(vertices, closed=True, alpha=0.3, facecolor='green', 
                         edgecolor='darkgreen', linewidth=2)
        ax.add_patch(polygon)
    
    def _plot_intersections(self, ax) -> None:
        """
        Grafica los puntos de intersección entre restricciones.
        
        ### parameters:
        - ax: matplotlib.axes.Axes - Ejes donde graficar.
        """
        # Encontrar todas las intersecciones
        intersections = []
        
        constraints = self.problem.constraints.copy()
        
        for i, c1 in enumerate(constraints):
            for c2 in constraints[i+1:]:
                intersection = self.find_intersection(c1, c2)
                if intersection is not None:
                    x, y = intersection
                    if self.is_point_feasible(x, y, constraints):
                        intersections.append((x, y))
        
        # Graficar las intersecciones
        if intersections:
            x_vals = [p[0] for p in intersections]
            y_vals = [p[1] for p in intersections]
            ax.scatter(x_vals, y_vals, color='red', s=100, zorder=5, 
                      edgecolors='black', linewidths=1.5,
                      label='Intersecciones')
            
            # Etiquetar las intersecciones
            for i, (x, y) in enumerate(intersections):
                ax.annotate(f'P{i+1}\n({x:.2f}, {y:.2f})', 
                           (x, y), 
                           textcoords="offset points", 
                           xytext=(5, 10),
                           fontsize=8,
                           ha='left')
    
    def _plot_solution(self, ax) -> None:
        """
        Grafica la solución óptima.
        
        ### parameters:
        - ax: matplotlib.axes.Axes - Ejes donde graficar.
        """
        if not self.solution:
            return
        
        x = self.solution.variables.get(self.var_x, 0)
        y = self.solution.variables.get(self.var_y, 0)
        
        # Graficar el punto óptimo
        ax.scatter([x], [y], color='blue', s=200, zorder=6, 
                  marker='*', edgecolors='black', linewidths=1.5,
                  label=f'Optimo (x={x:.2f}, y={y:.2f})')
        
        # Etiquetar el punto óptimo
        ax.annotate(f'Optimo\n({x:.2f}, {y:.2f})', 
                   (x, y), 
                   textcoords="offset points", 
                   xytext=(10, 10),
                   fontsize=10,
                   fontweight='bold',
                   ha='left',
                   color='blue')
        
        # Si hay función objetivo, graficar líneas de nivel
        self._plot_objective_contour(ax, x, y)
    
    def _plot_objective_contour(self, ax, opt_x: float, opt_y: float) -> None:
        """
        Grafica las líneas de nivel de la función objetivo.
        
        ### parameters:
        - ax: matplotlib.axes.Axes - Ejes donde graficar.
        - opt_x: float - Coordenada x de la solución óptima.
        - opt_y: float - Coordenada y de la solución óptima.
        """
        # Obtener coeficientes de la función objetivo
        obj = self.problem.objective
        a = obj.get(self.var_x, 0)
        b = obj.get(self.var_y, 0)
        
        if abs(b) < 1e-10 and abs(a) < 1e-10:
            return
        
        # Calcular el valor óptimo
        opt_value = a * opt_x + b * opt_y
        
        # Graficar líneas de nivel alrededor del óptimo
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Crear una línea de nivel para el valor óptimo
        x_vals = np.linspace(xlim[0], xlim[1], 100)
        
        if abs(b) > 1e-10:
            y_vals = (opt_value - a * x_vals) / b
            ax.plot(x_vals, y_vals, 'b--', alpha=0.5, linewidth=1.5,
                   label=f'Funcion objetivo (z={opt_value:.2f})')
        elif abs(a) > 1e-10:
            x_const = opt_value / a
            ax.axvline(x_const, color='b', linestyle='--', alpha=0.5, linewidth=1.5,
                      label=f'Funcion objetivo (z={opt_value:.2f})')
    
    def _format_objective(self) -> str:
        """
        Formatea la función objetivo como string.
        
        ### returns:
        - str - La función objetivo formateada.
        """
        terms = []
        for var in self.problem.variables:
            coeff = self.problem.objective.get(var, 0)
            if coeff != 0:
                if coeff >= 0:
                    terms.append(f"+{coeff}{var}")
                else:
                    terms.append(f"{coeff}{var}")
        
        obj_str = " ".join(terms)
        if obj_str.startswith("+"):
            obj_str = obj_str[1:]
        
        return obj_str
    
    def _format_constraint(self, c: LinearConstraint) -> str:
        """
        Formatea una restricción como string.
        
        ### parameters:
        - c: LinearConstraint - La restricción a formatear.
        
        ### returns:
        - str - La restricción formateada.
        """
        terms = []
        for var in self.problem.variables:
            coeff = c.coefficients.get(var, 0)
            if coeff != 0:
                if coeff >= 0:
                    terms.append(f"+{coeff}{var}")
                else:
                    terms.append(f"{coeff}{var}")
        
        constraint_str = " ".join(terms)
        if constraint_str.startswith("+"):
            constraint_str = constraint_str[1:]
        
        return f"{constraint_str} {c.sense} {c.rhs}"
