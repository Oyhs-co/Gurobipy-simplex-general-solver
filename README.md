# ISLA LP Benchmark v1.0.0

## Resumen del Proyecto

ISLA LP Benchmark es una plataforma profesional de benchmarking para comparar múltiples solvers de Programación Lineal (LP). El sistema permite ejecutar y comparar el rendimiento de diferentes optimizadores bajo condiciones controladas, generando métricas detalladas y reportes comparativos.

Esta herramienta está diseñada para uso educativo, investigación y evaluación de algoritmos de optimización lineal.

---

## Tabla de Contenidos

1. [Características Principales](#1-características-principales)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Solvers Disponibles](#3-solvers-disponibles)
4. [Requisitos del Sistema](#4-requisitos-del-sistema)
5. [Instalación](#5-instalación)
6. [Uso desde Línea de Comandos](#6-uso-desde-línea-de-comandos)
7. [Modo Benchmark](#7-modo-benchmark)
8. [Formato de Archivos de Problemas](#8-formato-de-archivos-de-problemas)
9. [Estructura del Proyecto](#9-estructura-del-proyecto)
10. [API de Solvers](#10-api-de-solvers)
11. [Reportes y Métricas](#11-reportes-y-métricas)
12. [Docker](#12-docker)
13. [Licencia](#13-licencia)
14. [Versión](#14-versión)

---

## 1. Características Principales

| Característica | Descripción |
|-------------|-----------|
| Múltiples Solvers | Comparativa de HiGHS, GLPK, CBC y Gurobi |
| Métricas Detalladas | Tiempo, iteraciones, memoria, nodos |
| Warmup | Ejecuciones de calentamiento para fair benchmarking |
| Modo Fair | Configuración uniforme entre solvers |
| Reportes PDF | Comparaciones visuales con gráficos |
| Exportación | CSV, JSON, Markdown |
| CLI Modular | Flags configurables |
| Registro de Solvers | Detección automática de disponibilidad |
| Docker | Imagen Alpine ligera |

---

## 2. Arquitectura del Sistema

```
src/
├── cli/
│   ├── __main__.py      # Punto de entrada CLI
│   ├── benchmark.py   # Handler benchmark
│   ├── solve.py    # Handler resolución single
│   └── __init__.py  # Utilidades del sistema
├── solver/
│   ├── base.py          # BaseSolver, SolverRegistry
│   ├── gurobi.py       # Solver Gurobi
│   ├── highs_solver.py  # Solver HiGHS (native)
│   ├── glpk_solver.py # Solver GLPK (native)
│   ├── cbc.py       # Solver CBC (via PuLP)
│   ├── benchmark.py   # BenchmarkRunner
│   └── __init__.py
├── analysis/
│   ├── analysis.py        # Reporte single
│   ├── benchmark_report.py # Reporte PDF benchmark
│   ├── benchmark_results.py # Visualización
│   └── __init__.py
├── parser/
│   ├── lp_parser.py     # Parser LP
│   ├── cplex_parser.py # Parser CPLEX
│   └── __init__.py
├── core/
│   ├── problem.py    # LinearProblem
│   ├── constraint.py # LinearConstraint
│   ├── bound.py    # VariableBound
│   ├── solution.py # Solution
│   └── __init__.py
├── matrix/
│   ├── builder.py   # LPBuilder
│   ├── matrix.py   # PolarsLP
│   └── __init__.py
├── visualization/
│   ├── visualization.py
│   └── __init__.py
└── utils/
    ├── validation.py
    ├── exporter.py
    ├── logging.py
    └── __init__.py
```

### Flujo de Datos

```
Archivo LP → Parser → LinearProblem → LPBuilder → PolarsLP → Solver → Solution
                                                            ↓
                                              BenchmarkRunner → Métricas → Reportes (PDF/CSV/JSON)
```

---

## 3. Solvers Disponibles

| Solver | Paquete | Estado | Notas |
|--------|--------|--------|-------|
| **HiGHS** | highspy | ✅ Disponible | Optimizador open-source de HiGHS |
| **GLPK** | swiglpk | ✅ Disponible | GNU Linear Programming Kit |
| **CBC** | pulp | ✅ Disponible | COIN-OR Branch and Cut |
| **Gurobi** | gurobipy | ⚠️ Requiere licencia | Optimizador comercial |

### CLI

```bash
# Listar solvers disponibles
python main.py --list-solvers

# Salida:
# === Solvers Disponibles ===
#   gurobi: DISPONIBLE
#   highs: DISPONIBLE
#   glpk: DISPONIBLE
#   cbc: DISPONIBLE
```

---

## 4. Requisitos del Sistema

| Requisito | Versión Mínima | Descripción |
|----------|---------------|-------------|
| Python | 3.14 | Lenguaje de programación |
| Memoria RAM | 4 GB | Para ejecución de solvers |
| Espacio disco | 500 MB | Dependencias |

### Dependencias

| Paquete | Versión | Propósito |
|---------|---------|----------|
| polars | >=1.39.0 | DataFrames |
| matplotlib | >=3.9.0 | Gráficos |
| numpy | >=2.4.3 | Computación numérica |
| fpdf2 | >=2.7.0 | PDFs |
| reportlab | >=4.4.10 | PDFs avanzados |
| psutil | >=7.2.2 | Métricas de memoria |
| highspy | >=1.14.0 | Solver HiGHS |
| swiglpk | >=5.0.13 | Solver GLPK |
| pulp | >=3.3.0 | Solver CBC |

---

## 5. Instalación

### Usando Poetry (recomendado)

```bash
# Clonar repositorio
git clone <repo-url>
cd isla-lp-benchmark

# Instalar dependencias
poetry install

# Activar entorno virtual
poetry shell
```

### Usando pip

```bash
pip install -r requirements.txt
```

### Requisitos

- Python 3.14+
- Gurobi (opcional, para solver comercial)

---

## 6. Uso desde Línea de Comandos

### Comandos Básicos

| Comando | Descripción |
|--------|------------|
| `python main.py problema.txt` | Resolver problema |
| `python main.py problema.txt --pdf` | Generar reporte PDF |
| `python main.py problema.txt --visualize` | Graficar región factible |
| `python main.py problema.txt --times` | Mostrar tiempos |
| `python main.py --list-solvers` | Listar solvers disponibles |
| `python main.py -- benchmark problema.txt` | Modo benchmark |

### Flags CLI

| Flag | Alias | Descripción |
|------|-------|------------|
| `--solver` | `-s` | Solver a usar |
| `--benchmark` | `-b` | Modo benchmark |
| `--solvers` | | Lista de solvers |
| `--repetitions` | `-r` | Repeticiones |
| `--pdf` | `-p` | Generar PDF |
| `--visualize` | `-v` | Visualización |
| `--plot-comparison` | | Gráficos comparativos |
| `--verbose` | | Salida detallada |
| `--times` | `-t` | Tiempos de ejecución |
| `--output-csv` | | Exportar CSV |
| `--output-dir` | | Directorio de salida |
| `--list-solvers` | | Listar solvers |

### Ejemplos

```bash
# Resolver un problema simple
python main.py data/problem.txt

# Generar reporte PDF
python main.py data/problem.txt --pdf

# Modo benchmark con multiple solvers
python main.py --benchmark --solvers highs glpk cbc --repetitions 3 data/problem.txt

# Benchmark con gráficos comparativos
python main.py --benchmark --solvers highs glpk --plot-comparison --pdf data/problem.txt
```

---

## 7. Modo Benchmark

### Descripción

El modo benchmark permite comparar múltiples solvers bajo condiciones controladas:

- **Warmup**: Ejecuciones iniciales para JVM/hotspot warmup
- **Fair Config**: Misma configuración para todos los solvers
- **Métricas**: Tiempo, iteraciones, memoria, nodos

### Configuración

```python
from src.solver import BenchmarkRunner, BenchmarkConfig

config = BenchmarkConfig(
    warmup_runs=1,           # Ejecuciones de warmup
    runs_per_problem=1,       # Repeticiones
    verbose=False,            # Salida detallada
    collect_detailed_stats=True, # Métricas completas
    collect_memory=True,       # Memoria
    output_dir=None,          # Directorio de salida
    fairness_mode=True,       # Modo fair
    randomize_order=True     # Orden aleatorio
)

runner = BenchmarkRunner(config)
results = runner.run(problems, solvers)
```

### Métricas Recolectadas

| Métrica | Descripción |
|---------|-----------|
| parse_time | Tiempo de parsing |
| build_time | Tiempo de construcción |
| solve_time | Tiempo de resolución |
| total_time | Tiempo total |
| memory_used_mb | Memoria utilizada |
| peak_memory_mb | Pico de memoria |
| iterations | Iteraciones del solver |
| nodes | Nodos explorados |

### Salida

```
============================================================
BENCHMARK SUMMARY
============================================================
Total de pruebas: 9
Exitosas: 9
Fallidas: 0

Por Solver:
------------------------------------------------------------
Solver          Runs     Exitosos   Tiempo Promedio
------------------------------------------------------------
gurobi          3        3          54.32ms
highs           3        3          48.15ms
glpk            3        3          42.87ms
============================================================
```

### Exportación

```bash
# CSV
python main.py --benchmark --solvers highs glpk --output-csv results.csv

# PDF con gráficos
python main.py --benchmark --solvers highs glpk --plot-comparison --pdf
```

---

## 8. Formato de Archivos de Problemas

### Función Objetivo

```
max: 3000x + 5000y
min: 2x + 3y + 5z
```

### Restricciones

```
x + y <= 100         (menor o igual)
2x + 3y >= 50       (mayor o igual)  
x + y = 75           (igual)
```

### Límites de Variables

```
x >= 0                (límite inferior)
y <= 50               (límite superior)
x free                (variable libre)
0 <= x <= 100         (ambos límites)
```

### Múltiples Problemas

```
max: 3x + 2y

x + y <= 10
2x + y <= 15

x >= 0
y >= 0

---

max: 4x + 3y

x <= 5
y <= 8

x >= 0
y >= 0
```

---

## 9. Estructura del Proyecto

```
isla-lp-benchmark/
├── main.py                    # Punto de entrada
├── pyproject.toml             # Configuración Poetry
├── Dockerfile               # Imagen Docker
├── docker-compose.yml        # Orquestación Docker
├── README.md               # Documentación
├── data/
│   ├── problem.txt          # Problema de ejemplo
│   ├── problem_multi.txt  # Múltiples problemas
│   └── benchmark_output/ # Resultados benchmark
├── src/
│   ├── cli/              # Interfaz CLI
│   ├── solver/           # Implementaciones de solvers
│   ├── analysis/        # Análisis y reportes
│   ├── parser/         # Parsing de archivos
│   ├── core/           # Modelos de datos
│   ├── matrix/         # Construcción Polars
│   ├── visualization/  # Gráficos
│   └── utils/          # Utilidades
└── docs/
    └── Evolucion.md      # Planificación
```

---

## 10. API de Solvers

### Registro de Solvers

```python
from src.solver import SolverRegistry

# Listar solvers disponibles
solvers = SolverRegistry.list_solvers()
print(solvers)  # ['gurobi', 'highs', 'glpk', 'cbc']

# Obtener clase de solver
solver_class = SolverRegistry.get('highs')

# Información de solver
info = SolverRegistry.get_info('glpk')
print(info)  # {'name': 'glpk', 'available': True, 'error': None}
```

### Implementar Nuevo Solver

```python
from src.solver import BaseSolver, SolverStats, register_solver
from src.core import Solution

@register_solver("mi_solver")
class MiSolver(BaseSolver):
    """Implementación de solver personalizado."""
    
    @property
    def solver_name(self) -> str:
        return "mi_solver"
    
    @property
    def solver_version(self) -> str:
        return "1.0.0"
    
    @property
    def is_available(self) -> bool:
        # Verificar disponibilidad
        return True
    
    def solve(self) -> Solution:
        # Resolver problema
        return Solution(
            status="OPTIMAL",
            objective_value=42.0,
            variables={"x": 1.0}
        )
    
    def get_stats(self) -> SolverStats:
        return SolverStats(iterations=2, nodes=0)
```

---

## 11. Reportes y Métricas

### PDF Benchmark

El reporte PDF incluye:

1. **Portada**: Información del benchmark
2. **Resumen**: Tabla de resultados por solver
3. **Gráficos Comparativos**:
   - Tiempo de ejecución
   - Uso de memoria
   - Iteraciones
4. **Detalles por Solver**: Estado, valor óptimo, variables

### Exportación

| Formato | Archivo | Descripción |
|--------|--------|-----------|
| CSV | `benchmark_results.csv` | Datos tabulares |
| JSON | `benchmark_results.json` | Datos estructurados |
| PDF | `benchmark_report.pdf` | Reporte visual |
| Markdown | `benchmark_report.md` | Documentación |

---

## 12. Docker

### Build

```bash
docker build -t lp-solver .
```

### Run

```bash
# Listar solvers
docker run lp-solver --list-solvers

# Benchmark
docker run lp-solver --benchmark --solvers highs glpk --repetitions 1 data/problem.txt

# Con compose
docker compose run list-solvers
docker compose run benchmark
```

### docker-compose.yml

```yaml
services:
  lp-solver:
    build: .
    volumes:
      - ./data:/app/data:ro

  benchmark:
    build: .
    command: python main.py --benchmark --solvers highs glpk --repetitions 1 /app/data/problem.txt
    volumes:
      - ./data:/app/data
      - ./output:/app/output
```

### Imagen

- **Base**: Python 3.14 Alpine
- **Tamaño**: ~150MB (dependencias compiladas)
- **Usuario**: No-root (security)

---

## 13. Licencia

MIT License

Copyright (c) 2026 ISLA LP Benchmark

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 14. Versión

**Versión actual: 1.0.0**

### Changelog v1.0.0

- ✅ Plataforma de benchmark multi-solver
- ✅ Solvers: HiGHS (native), GLPK (native), CBC (PuLP), Gurobi
- ✅ Métricas: tiempo, iteraciones, memoria, nodos
- ✅ Warmup para fair benchmarking
- ✅ Reportes PDF con gráficos comparativos
- ✅ Exportación: CSV, JSON, Markdown
- ✅ CLI con --list-solvers
- ✅ Docker Alpine
- ✅ Limpieza de código duplicado

---

<div align="center">

**ISLA LP Benchmark** - Plataforma de Benchmarking para Programación Lineal

Desarrollado con Python, Polars, Matplotlib y fpdf2

</div>