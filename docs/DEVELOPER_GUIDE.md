# Guía del Desarrollador - Gurobipy-Simplex-General-Solver

Esta guía es para **desarrolladores** que quieren extender o integrar este proyecto.

## Visión General de la Arquitectura

### Estructura de Módulos

```
src/
├── core/                    # Clases base de datos
│   ├── problem.py           # LinearProblem
│   ├── constraint.py      # LinearConstraint
│   ├── bound.py          # VariableBound
│   ├── solution.py       # Solution
│   └── exceptions.py     # Excepciones personalizadas
├── parser/                 # Analizadores sintácticos
│   ├── lp_parser.py       # Formato texto personalizado
│   ├── cplex_parser.py  # Formato CPLEX/LP
│   └── multi_parser.py   # Multi-problema
├── matrix/                 # Estructuras de datos
│   ├── builder.py       # Constructor Polars
│   └── matrix.py       # Clase PolarsLP
├── solver/                # Optimización
│   ├── solver.py        # Solucionador Gurobi
│   ├── multi_solver.py # Multi-problema
│   └── __init__.py    # Exports SolverConfig
├── analysis/              # Generación PDFs
│   ├── analysis.py      # Problema individual
│   └── multi_analysis.py # Multi-problema
├── visualization/        # Visualización gráfica
│   └── visualization.py # Gráficos Matplotlib
└── utils/                # Utilidades
    ├── validation.py   # Validación de entrada
    ├── exporter.py  # Exportación LP
    └── logging.py  # Sistema de logging
```

## Uso Básico

### Parsear y Resolver

```python
from src.parser import LPParser
from src.matrix import LPBuilder
from src.solver import SolverLP

# Parsear
problem = LPParser(texto).parse()

# Construir
lp = LPBuilder(problem).build()

# Resolver
solution = SolverLP(lp).solve()

# Resultados
print(solution.objective_value)
print(solution.variables)
```

### Con Configuración

```python
from src.solver import SolverConfig

config = SolverConfig(
    verbose=True,
    time_limit=30.0,
    threads=4
)
solver = SolverLP(lp, config=config)
```

### Con Validación

```python
from src.utils.validation import validate_problem

validation = validate_problem(problem)
if not validation.is_valid:
    print(validation.summary())
```

## Extendiendo el Proyecto

### Agregar un Nuevo Parser

1. Crear una nueva clase parser en `src/parser/`
2. Implementar el método `parse()` retornando `LinearProblem`
3. Importar en `src/parser/__init__.py`

Ejemplo:

```python
# src/parser/mi_parser.py
from ..core import LinearProblem

class MiParser:
    def __init__(self, texto: str):
        self.texto = texto
    
    def parse(self) -> LinearProblem:
        # Lógica de parseo aquí
        return LinearProblem(...)
```

### Agregar un Nuevo Solucionador

1. Crear clase solver en `src/solver/`
2. Implementar método `solve()` retornando `Solution`
3. Exportar en `src/solver/__init__.py`

### Agregar Validación

Agregar códigos de validación en `src/utils/validation.py`:

```python
# Códigos de error
issues.append(ValidationIssue(
    severity="ERROR",
    code="NUEVO001",
    message="Mensaje de error personalizado",
    location="contexto"
))
```

## Opciones de Configuración

### Parámetros de SolverConfig

```python
config = SolverConfig(
    verbose=False,      # Imprimir salida
    time_limit=60.0,   # Segundos
    mip_gap=0.0001,  # Gap MIP
    threads=4,        # Hilos de CPU
    method=-1,        # -1=auto, 0=primal, 1=dual, 2=barrier
    presolve=1         # 0=off, 1=on
)
```

## Patrones Comunes

### Manejo de Errores

```python
from src.core.exceptions import LPError

try:
    problem = LPParser(texto).parse()
except LPError as e:
    print(f"Error de parseo: {e}")
```

### Verificar Solución

```python
solution = solver.solve()

if solution.is_optimal():
    print(f"Óptimo: {solution.objective_value}")
elif solution.is_infeasible():
    iis = solver.diagnose_infeasibility()
    print(f"IIS: {iis}")
elif solution.is_unbounded():
    print("Problema no acotado")
```

---

Para referencia de API, ver [README.md](../README.md).