# Gurobipy-Simplex-General-Solver

## Resolvedor Profesional de Programación Lineal con Método Simplex y Optimización Gurobi

---

<div align="center">

**Un sistema completo de resolución de problemas de Programación Lineal (LP) que combina la robustez del método Simplex con el poder computacional del optimizador comercial Gurobi, incluyendo visualización gráfica de regiones factibles y generación de reportes académicos profesionales en formato PDF.**

*Desarrollado en Python con integración nativa de Gurobi, Polars, Matplotlib y fpdf2*

</div>

---

## Tabla de Contenidos

1. [Descripción del Proyecto](#1-descripción-del-proyecto)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Instalación](#3-instalación)
4. [Estructura del Proyecto](#4-estructura-del-proyecto)
5. [Descripción Técnica de Módulos](#5-descripción-técnica-de-módulos)
6. [Uso y Comandos](#6-uso-y-comandos)
7. [Formato de Archivos de Entrada](#7-formato-de-archivos-de-entrada)
8. [Módulo de Visualización](#8-módulo-de-visualización)
9. [Módulo de Análisis Multi-Problema](#9-módulo-de-análisis-multi-problema)
10. [Algoritmos y Complejidad](#10-algoritmos-y-complejidad)
11. [Referencias Técnicas](#11-referencias-técnicas)
12. [Licencia y Contribuciones](#12-licencia-y-contribuciones)

---

## 1. Descripción del Proyecto

### 1.1 Propósito del Sistema

El **Gurobipy-Simplex-General-Solver** es un sistema de optimización matemática de propósito general diseñado para resolver problemas de **Programación Lineal (LP)** mediante la integración de dos enfoques complementarios: el clásico **Método Simplex** de George Dantzig y el optimizador comercial de alto rendimiento **Gurobi**.

Este proyecto proporciona una solución completa que abarca desde el parseo de problemas definidos en archivos de texto hasta la generación de visualizaciones gráficas y reportes académicos profesionales, soportando tanto problemas mono-objetivo como múltiples problemas simultáneos.

### 1.2 Funcionalidades Principales

| Funcionalidad | Descripción |
|---------------|-------------|
| **Resolución de Problemas LP** | Soluciona problemas de programación lineal con restricciones de <=, >=, y = |
| **Modo Multi-Problema** | Resuelve múltiples problemas desde un único archivo mediante flag `--multi` |
| **Optimización Gurobi** | Utiliza el optimizador comercial Gurobi para soluciones exactas y eficientes |
| **Visualización Gráfica** | Genera gráficos de regiones factibles en 2D con plano cartesiano completo (soporta valores negativos) |
| **Reportes PDF** | Crea informes académicos profesionales con análisis detallados |
| **Análisis de Sensibilidad** | Calcula holguras, precios sombra y análisis de factibilidad |
| **Soporte de Variables** | Maneja variables no negativas, límites superiores, inferiores y variables libres |
| **Medición de Rendimiento** | Registra tiempos de ejecución de cada fase del proceso |

### 1.3 Características Avanzadas

- **Parsers dualessimplex**: Parser para formato LP estándar y formato personalizado
- **Constructor matricial**: Construcción eficiente de matrices usando Polars DataFrames
- **Validación completa**: Verificación exhaustiva de entrada con mensajes de error claros
- **Manejo de errores robusto**: Continúa procesando múltiples problemas incluso si algunos fallan
- **Flexibilidad de delimitadores**: Soporta múltiples separadores (`---`, `===`, `___`) para múltiples problemas

---

## 2. Arquitectura del Sistema

### 2.1 Visión General de la Arquitectura

El sistema sigue una **arquitectura orientada a componentes** con las siguientes capas:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAPA DE PRESENTACIÓN                      │
│                    (main.py - Interfaz CLI)                     │
├─────────────────────────────────────────────────────────────────┤
│                     CAPA DE VISUALIZACIÓN                       │
│              (visualization.py - Gráficos matplotlib)            │
├─────────────────────────────────────────────────────────────────┤
│                       CAPA DE ANÁLISIS                          │
│       (analysis.py / multi_analysis.py - Reportes PDF)          │
├─────────────────────────────────────────────────────────────────┤
│                      CAPA DE SOLUCIÓN                           │
│              (solver.py / multi_solver.py - Gurobi)             │
├─────────────────────────────────────────────────────────────────┤
│                     CAPA DE CONSTRUCCIÓN                        │
│                 (matrix/builder.py - Polars)                   │
├─────────────────────────────────────────────────────────────────┤
│                       CAPA DE PARSING                           │
│        (parser/lp_parser.py / multi_parser.py)                 │
├─────────────────────────────────────────────────────────────────┤
│                        CAPA CORE                                │
│     (core/problem.py, constraint.py, bound.py, solution.py)     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Diseño Orientado a Objetos

El proyecto implementa los siguientes patrones de diseño:

| Patrón | Aplicación |
|--------|------------|
| **Data Class** | `LinearProblem`, `Solution`, `ProblemResult`, `MultiSolverResult` |
| **Factory** | `LPBuilder` construye objetos `PolarsLP` |
| **Strategy** | Selección entre modo single y multi-problema |
| **Template Method** | `MultiLPAnalysis` define estructura de reportes |

### 2.3 Flujo de Datos

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Archivo LP  │────▶│   Parser     │────▶│  Problema   │
│  (.txt)      │     │ (lp_parser)  │     │ (LinearProb)│
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Visualiz.  │◀────│  Solución    │◀────│ Constructor │
│ (.png)      │     │ (Solution)   │     │ (LPBuilder) │
└──────────────┘     └──────────────┘     └──────────────┘
        │                                       │
        ▼                                       ▼
┌──────────────┐                        ┌──────────────┐
│   Reporte    │                        │   Gurobi    │
│   PDF        │                        │  Optimizer   │
└──────────────┘                        └──────────────┘
```

---

## 3. Instalación

### 3.1 Requisitos del Sistema

| Requisito | Versión Mínima | Descripción |
|-----------|-----------------|-------------|
| **Sistema Operativo** | Windows 10+, Linux, macOS | Compatible con Windows 11, Ubuntu 20.04+, macOS 12+ |
| **Python** | 3.14+ | Requiere Python 3.14 o superior |
| **Gurobi Optimizer** | 13.0+ | Licencia comercial o académica |
| **Memoria RAM** | 4 GB mínimo | 8 GB recomendado |
| **Espacio en Disco** | 500 MB | Para dependencias y datos |

### 3.2 Dependencias del Entorno

El proyecto utiliza las siguientes librerías principales:

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `gurobipy` | >=13.0.1 | Optimizador comercial de Programación Lineal/Entera Mixta (MILP) |
| `polars` | >=1.39.0 | Biblioteca de DataFrames de alto rendimiento para manipulación de datos |
| `matplotlib` | >=3.9.0 | Generación de gráficos y visualizaciones 2D |
| `numpy` | >=2.4.3 | Computación numérica y operaciones matriciales |
| `fpdf2` | >=2.7.0 | Generación de documentos PDF |
| `reportlab` | >=4.4.10 | Generación avanzada de PDFs |

### 3.3 Pasos de Instalación

#### Paso 1: Clonar el Repositorio

```bash
git clone <repositorio-url>
cd gurobipy-simplex-general-solver
```

#### Paso 2: Instalar Poetry (si no está disponible)

**En Windows:**
```powershell
pip install poetry
```

**En Linux/macOS:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### Paso 3: Instalar Dependencias

```bash
poetry install
```

Opcionalmente, si prefieres pip:

```bash
pip install gurobipy polars matplotlib numpy fpdf2 reportlab
```

#### Paso 3.4: Configurar Licencia de Gurobi

El optimizador Gurobi requiere una licencia válida. Hay varias opciones:

1. **Licencia Gratuita Academica**: Obtén una en [gurobi.com/academic](https://www.gurobi.com/downloads/)
2. **Licencia Comercial**: Contacta a Gurobi para una licencia de evaluación
3. **WLS (Web License Service)**: Configura el servicio de licencias web

```bash
# Configurar licencia (ejemplo)
grbgetkey <licencia-key>
```

---

## 4. Estructura del Proyecto

```
gurobipy-simplex-general-solver/
├── main.py                           # Punto de entrada CLI
├── pyproject.toml                    # Configuración del proyecto (Poetry)
├── README.md                         # Documentación principal
├── LICENSE                           # Licencia MIT
├── data/
│   ├── problem.txt                   # Ejemplo de problema LP simple
│   ├── problem_multi.txt             # Ejemplo de múltiples problemas
│   ├── problem.png                   # Imagen de problema de ejemplo
│   └── problem.pdf                   # Reporte PDF de ejemplo
├── src/
│   ├── __init__.py                   # Exports públicos del paquete
│   ├── parser/
│   │   ├── __init__.py              # Exports del módulo parser
│   │   ├── lp_parser.py             # Parser de archivos LP
│   │   └── multi_parser.py          # Parser multi-problema
│   ├── core/
│   │   ├── __init__.py              # Exports del módulo core
│   │   ├── problem.py               # Modelo de problema LP
│   │   ├── constraint.py            # Representación de restricciones
│   │   ├── bound.py                 # Representación de límites de variables
│   │   └── solution.py              # Representación de soluciones
│   ├── matrix/
│   │   ├── __init__.py              # Exports del módulo matrix
│   │   ├── builder.py               # Constructor de matrices Polars
│   │   └── matrix.py                # Definición de tipos PolarsLP
│   ├── solver/
│   │   ├── __init__.py              # Exports del módulo solver
│   │   ├── solver.py                # Integración con Gurobi
│   │   └── multi_solver.py          # Solver multi-problema
│   ├── analysis/
│   │   ├── __init__.py              # Exports del módulo analysis
│   │   ├── analysis.py              # Análisis y reportes PDF (single)
│   │   └── multi_analysis.py        # Análisis y reportes PDF (multi)
│   └── visualization/
│       ├── __init__.py              # Exports del módulo visualization
│       └── visualization.py          # Visualización gráfica 2D
├── legacy/
│   ├── Simplex.py                   # Implementación legacy (Simplex manual)
│   └── Opinion.md                   # Documento de opiniones legacy
└── test_parser.py                   # Tests del parser
```

---

## 5. Descripción Técnica de Módulos

### 5.1 Módulo Principal (`main.py`)

**Ubicación**: `main.py`

**Propósito**: Punto de entrada de la aplicación CLI que gestiona los argumentos de línea de comandos y coordina la ejecución en modo single o multi-problema.

**Clase Principal**: No aplica (funciones globales)

**Funciones**:

| Función | Firma | Descripción |
|---------|-------|-------------|
| `main` | `main(argv: list[str] \| None = None) -> None` | Función principal que parsea argumentos y ejecuta el flujo apropiado |
| `_run_multi` | `_run_multi(text: str, path: Path, visualize: bool, pdf: bool, show_times: bool) -> None` | Ejecuta el modo multi-problema |
| `_run_single` | `_run_single(text: str, path: Path, visualize: bool, pdf: bool, show_times: bool) -> None` | Ejecuta el modo single-problema |

**Flags CLI Disponibles**:

| Flag | Alias | Descripción |
|------|-------|-------------|
| `--multi` | `-m` | Activa el modo multi-problema |
| `--visualize` | `-v` | Genera visualización gráfica de la región factible |
| `--pdf` | `-p` | Genera reporte académico en PDF |
| `--times` | `-t` | Muestra tiempos de ejecución |
| `--help` | `-h` | Muestra la ayuda |

### 5.2 Módulo de Parsing (`src/parser/`)

#### 5.2.1 Parser LP Individual (`lp_parser.py`)

**Ubicación**: `src/parser/lp_parser.py`

**Propósito**: Parsea problemas de programación lineal definidos en texto plano a objetos `LinearProblem`.

**Clase Principal**: [`LPParser`](src/parser/lp_parser.py:13)

**Atributos**:

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `txt` | `str` | Texto con la definición del problema LP |
| `bounds` | `dict[str, VariableBound]` | Diccionario de límites de variables |

**Métodos**:

| Método | Firma | Complejidad |
|--------|-------|-------------|
| `parse` | `parse() -> LinearProblem` | O(n×m) donde n=líneas, m=variables |
| `_parse_objective` | `_parse_objective(line: str) -> tuple[str, dict[str, float]]` | O(m) |
| `_parse_constraint` | `_parse_constraint(line: str) -> LinearConstraint` | O(m) |
| `_parse_linear_expression` | `_parse_linear_expression(expr: str) -> dict[str, float]` | O(m) |
| `_is_bound` | `_is_bound(line: str) -> bool` | O(1) |
| `_parse_bound` | `_parse_bound(line: str) -> None` | O(1) |
| `_extract_variables` | `_extract_variables(...) -> list[str]` | O(n×m) |

**Excepciones**: `ValueError` para formato inválido

#### 5.2.2 Parser Multi-Problema (`multi_parser.py`)

**Ubicación**: `src/parser/multi_parser.py`

**Propósito**: Parsea múltiples problemas de LP desde un único archivo usando delimitadores.

**Clase Principal**: [`MultiLPParser`](src/parser/multi_parser.py:11)

**Constantes**:

```python
DELIMITERS = ['---', '===', '___']
```

**Métodos**:

| Método | Firma | Descripción |
|--------|-------|-------------|
| `parse_all` | `parse_all() -> List[LinearProblem]` | Parsea todos los problemas encontrados |
| `_split_by_delimiter` | `_split_by_delimiter(txt: str) -> List[str]` | Divide el texto usando regex |
| `count_problems` | `count_problems(txt: str) -> int` [staticmethod] | Cuenta problemas sin parsear |

### 5.3 Módulo Core (`src/core/`)

#### 5.3.1 Modelo de Problema (`problem.py`)

**Ubicación**: `src/core/problem.py`

**Clase Principal**: [`LinearProblem`](src/core/problem.py:7) (dataclass)

**Atributos**:

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `objective` | `dict[str, float]` | Coeficientes de la función objetivo |
| `sense` | `str` | Dirección de optimización ("max" o "min") |
| `constraints` | `list[LinearConstraint]` | Lista de restricciones lineales |
| `variables` | `list[str]` | Lista de nombres de variables |
| `bounds` | `dict[str, VariableBound]` | Límites de cada variable |
| `name` | `str` | Nombre opcional del problema |

#### 5.3.2 Restricciones (`constraint.py`)

**Ubicación**: `src/core/constraint.py`

**Clase Principal**: [`LinearConstraint`](src/core/constraint.py:6) (dataclass)

**Atributos**:

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `coefficients` | `dict[str, float]` | Coeficientes de las variables |
| `rhs` | `float` | Lado derecho de la restricción |
| `sense` | `str` | Tipo de restricción ("<=", ">=", "=") |

#### 5.3.3 Límites de Variables (`bound.py`)

**Ubicación**: `src/core/bound.py`

**Clase Principal**: [`VariableBound`](src/core/bound.py:5) (dataclass)

**Atributos**:

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `variable` | `str` | Nombre de la variable |
| `lower` | `float \| None` | Límite inferior |
| `upper` | `float \| None` | Límite superior |

#### 5.3.4 Solución (`solution.py`)

**Ubicación**: `src/core/solution.py`

**Clase Principal**: [`Solution`](src/core/solution.py:5) (dataclass)

**Atributos**:

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `status` | `str` | Estado de la solución ("OPTIMAL", "INFEASIBLE", "UNBOUNDED") |
| `objective_value` | `float \| None` | Valor óptimo de la función objetivo |
| `variables` | `dict[str, float]` | Valores de las variables en la solución |

### 5.4 Módulo Matrix (`src/matrix/`)

#### 5.4.1 Constructor de Matrices (`builder.py`)

**Ubicación**: `src/matrix/builder.py`

**Propósito**: Construye estructuras de datos Polars (DataFrames) para representar el problema LP.

**Clase Principal**: [`LPBuilder`](src/matrix/builder.py:10)

**Métodos**:

| Método | Firma | Descripción |
|--------|-------|-------------|
| `build` | `build() -> PolarsLP` | Construye el objeto PolarsLP con DataFrames |

#### 5.4.2 Tipos de Matrices (`matrix.py`)

**Ubicación**: `src/matrix/matrix.py`

**Clase Principal**: [`PolarsLP`](src/matrix/matrix.py:8) (dataclass)

**Atributos**:

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `objective` | `pl.DataFrame` | DataFrame con coeficientes objetivo |
| `constraints` | `pl.DataFrame` | DataFrame con restricciones |
| `coefficients` | `pl.DataFrame` | DataFrame con matriz de coeficientes |
| `bounds` | `pl.DataFrame` | DataFrame con límites de variables |
| `sense` | `str` | Sentido de optimización |

### 5.5 Módulo Solver (`src/solver/`)

#### 5.5.1 Solver Gurobi (`solver.py`)

**Ubicación**: `src/solver/solver.py`

**Propósito**: Resuelve problemas LP utilizando el optimizador Gurobi.

**Clase Principal**: [`SolverLP`](src/solver/solver.py:8)

**Métodos**:

| Método | Firma | Complejidad |
|--------|-------|-------------|
| `solve` | `solve() -> Solution` | O(n³) típico de métodos simplex |

**Estados de Solución**:

| Estado | Descripción |
|--------|-------------|
| `OPTIMAL` | Solución óptima encontrada |
| `INFEASIBLE` | El problema no tiene región factible |
| `UNBOUNDED` | La función objetivo puede crecer sin límite |
| `STATUS_*` | Otro estado de Gurobi |

#### 5.5.2 Solver Multi-Problema (`multi_solver.py`)

**Ubicación**: `src/solver/multi_solver.py`

**Clases Principales**:

| Clase | Descripción |
|-------|-------------|
| [`ProblemResult`](src/solver/multi_solver.py:15) | Dataclass para resultado de un problema |
| [`MultiSolverResult`](src/solver/multi_solver.py:27) | Dataclass para resultados múltiples |
| [`MultiSolver`](src/solver/multi_solver.py:45) | Solver para múltiples problemas |

**Métodos de MultiSolver**:

| Método | Firma | Descripción |
|--------|-------|-------------|
| `solve_all` | `solve_all(problems: List[LinearProblem]) -> MultiSolverResult` | Resuelve todos los problemas |
| `_solve_single` | `_solve_single(problem: LinearProblem, index: int) -> ProblemResult` | Resuelve un problema individual |
| `solve_from_text` | `solve_from_text(text: str) -> MultiSolverResult` [staticmethod] | Parsea y resuelve desde texto |

### 5.6 Módulo de Análisis (`src/analysis/`)

#### 5.6.1 Análisis Single (`analysis.py`)

**Ubicación**: `src/analysis/analysis.py`

**Clases**:

| Clase | Descripción |
|-------|-------------|
| `ReporteAcademico` | Clase base FPDF para reportes |
| `LPAnalysis` | Generador de reportes PDF para un problema |

#### 5.6.2 Análisis Multi-Problema (`multi_analysis.py`)

**Ubicación**: `src/analysis/multi_analysis.py`

**Clases**:

| Clase | Descripción |
|-------|-------------|
| `ReporteAcademicoMulti` | Clase base FPDF para reportes multi-problema |
| `MultiLPAnalysis` | Generador de reportes PDF para múltiples problemas |

**Constantes de Estilo**:

```python
PAGE_WIDTH = 215.9   # mm (carta)
PAGE_HEIGHT = 279.4  # mm
MARGIN = 20           # mm
COLOR_PRIMARY = (0, 51, 102)       # Azul oscuro
COLOR_SUCCESS = (0, 128, 0)        # Verde
COLOR_ERROR = (200, 0, 0)          # Rojo
COLOR_WARNING = (200, 128, 0)      # Naranja
```

### 5.7 Módulo de Visualización (`src/visualization/`)

**Ubicación**: `src/visualization/visualization.py`

**Clase Principal**: [`LinearVisualization`](src/visualization/visualization.py:21)

**Atributos**:

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `problem` | `LinearProblem` | El problema de programación lineal |
| `solution` | `Solution \| None` | La solución óptima |
| `var_x` | `str` | Nombre de la primera variable |
| `var_y` | `str` | Nombre de la segunda variable |

**Métodos**:

| Método | Firma | Descripción |
|--------|-------|-------------|
| `find_intersection` | `find_intersection(c1, c2) -> Optional[tuple[float, float]]` | Encuentra intersección entre dos restricciones |
| `is_point_feasible` | `is_point_feasible(x, y, constraints) -> bool` | Verifica factibilidad de un punto |
| `get_constraint_line_x` | `get_constraint_line_x(c, x_range) -> tuple[np.ndarray, np.ndarray]` | Obtiene puntos para graficar restricción |
| `find_feasible_vertices` | `find_feasible_vertices() -> list[tuple[float, float]]` | Encuentra vértices de la región factible |
| `plot` | `plot(save_path: Optional[str] = None, show: bool = True) -> None` | Genera la visualización completa |
| `_calculate_plot_range` | `_calculate_plot_range() -> tuple[tuple[float, float], tuple[float, float]]` | Calcula rango del gráfico (soporta negativos) |
| `_plot_constraints` | `_plot_constraints(ax, x_range) -> None` | Grafica las rectas de restricciones |
| `_plot_feasible_region` | `_plot_feasible_region(ax, x_range, y_range) -> None` | Grafica la región factible |
| `_plot_intersections` | `_plot_intersections(ax) -> None` | Grafica puntos de intersección |
| `_plot_solution` | `_plot_solution(ax) -> None` | Grafica la solución óptima |
| `_plot_objective_contour` | `_plot_objective_contour(ax, opt_x, opt_y) -> None` | Grafica líneas de nivel de la función objetivo |

---

## 6. Uso y Comandos

### 6.1 Ejecución Básica

#### Resolver un problema simple

```bash
python main.py data/problem.txt
```

#### Mostrar ayuda

```bash
python main.py --help
# o
python main.py -h
```

### 6.2 Flags Disponibles

| Comando | Descripción |
|---------|-------------|
| `python main.py <archivo>` | Resuelve un problema LP |
| `python main.py <archivo> --visualize` | Resuelve y genera gráfico |
| `python main.py <archivo> --pdf` | Resuelve y genera reporte PDF |
| `python main.py <archivo> -v -p` | Resuelve, grafica y genera PDF |
| `python main.py <archivo> --times` | Muestra tiempos de ejecución |
| `python main.py <archivo> --multi` | Resuelve múltiples problemas |
| `python main.py <archivo> -m -p` | Resuelve múltiples y genera PDF |

### 6.3 Ejemplos de Uso

#### Ejemplo 1: Resolución Simple

```bash
python main.py data/problem.txt
```

**Salida esperada:**
```
Valor optimo: 30000.00
x = 30.00
y = 20.00
```

#### Ejemplo 2: Con Visualización

```bash
python main.py data/problem.txt --visualize
```

**Salida esperada:**
```
Valor optimo: 30000.00
x = 30.00
y = 20.00

Generando visualizacion...
Grafica guardada en: data/problem.png
```

#### Ejemplo 3: Con Reporte PDF

```bash
python main.py data/problem.txt --pdf
```

**Salida esperada:**
```
Valor optimo: 30000.00
x = 30.00
y = 20.00

Generando reporte PDF...
PDF guardado en: data/problem.pdf
```

#### Ejemplo 4: Múltiples Problemas

```bash
python main.py data/problem_multi.txt --multi
```

**Salida esperada:**
```
==================================================
MODO MULTI-PROBLEMA
==================================================
Problemas encontrados: 2

--- Problema 1 ---
Estado: OPTIMAL
Valor óptimo: 11.4286 (x=-1.14, y=2.57)
Tiempo: 15.23 ms

--- Problema 2 ---
Estado: OPTIMAL
Valor óptimo: 36.0000 (x=2.00, y=6.00)
Tiempo: 12.45 ms

Problemas resueltos: 2/2
```

#### Ejemplo 5: Combinación Completa

```bash
python main.py data/problem_multi.txt --multi --visualize --pdf --times
```

### 6.4 Uso como Librería

```python
from src.parser import LPParser
from src.matrix import LPBuilder
from src.solver import SolverLP

# Definir problema en texto
lp_text = """
max: 3x + 2y

x + y <= 10
2x + y <= 15
x >= 0
y >= 0
"""

# Parsear, construir y resolver
problem = LPParser(lp_text).parse()
lp = LPBuilder(problem).build()
solution = SolverLP(lp).solve()

print(f"Valor óptimo: {solution.objective_value}")
print(f"Solución: {solution.variables}")
```

---

## 7. Formato de Archivos de Entrada

### 7.1 Formato Estándar LP

El archivo de entrada debe seguir este formato:

```lp
max: 3000x + 5000y

# restricciones
2x + 3y <= 120
x + 3y <= 90

# bounds
x >= 0
y >= 0
```

### 7.2 Estructura del Archivo

| Sección | Descripción | Ejemplo |
|---------|-------------|---------|
| **Función objetivo** | Primera línea: `max:` o `min:` seguido de expresión lineal | `max: 3000x + 5000y` |
| **Restricciones** | Expresiones lineales con operador y valor RHS | `2x + 3y <= 120` |
| **Bounds** | Límites de variables | `x >= 0`, `0 <= y <= 100` |

### 7.3 Operadores Soportados

| Operador | Descripción |
|----------|-------------|
| `<=` | Menor o igual que |
| `>=` | Mayor o igual que |
| `=` | Igual a |

### 7.4 Formatos de Bounds

```lp
x >= 0          # Límite inferior
x <= 10         # Límite superior
0 <= x <= 10    # Límites doble
x free          # Variable libre (sin restricciones)
x unrestricted  # Variable libre (sin restricciones)
```

### 7.5 Múltiples Problemas

Para definir múltiples problemas en un archivo, use delimitadores:

```lp
# Problema 1: Maximización

max Z = -x + 4y

# restricciones
-3x + y <= 6
x + 2y <= 4

# bounds
x free
y >= -3

---

# Problema 2: Maximización

max Z = 3x + 5y

# restricciones
x <= 4
2y <= 12
3x + 2y = 18

# bounds
x >= 0
y >= 0
```

### 7.6 Notas Adicionales

- Las líneas que empiezan con `#` son comentarios
- Los espacios en blanco son ignorados
- Las variables pueden tener nombres alfanuméricos: `x`, `y`, `var1`, `x1_2`
- Los coeficientes pueden ser positivos o negativos, enteros o decimales
- Delimitadores reconocidos: `---`, `===`, `___`

---

## 8. Módulo de Visualización

### 8.1 Descripción General

El módulo de visualización (`LinearVisualization`) proporciona herramientas completas para graficar problemas de programación lineal en 2D. Las características principales incluyen:

- **Plano Cartesiano Completo**: Soporta valores negativos en ambos ejes
- **Región Factible**: Identificación y graficación del polígono factible
- **Restricciones como Rectas**: Visualización de cada restricción como línea
- **Puntos de Intersección**: Marcado de intersecciones entre restricciones
- **Solución Óptima**: Resaltado del punto óptimo con estrella
- **Líneas de Nivel**: Graficación de la función objetivo

### 8.2 Algoritmo de Cálculo de Rango

El método [`_calculate_plot_range`](src/visualization/visualization.py:262) determina automáticamente el rango del gráfico:

1. **Inicialización**: Comienza con rango base de [-10, 10]
2. **Expansión por solución**: Si existe solución óptima, expande el rango basándose en sus valores
3. **Expansión por restricciones**: Analiza cada restricción para encontrar intersecciones con ejes
4. **Mínimo garantizado**: Asegura un rango mínimo de 5 unidades

```python
def _calculate_plot_range(self) -> tuple[tuple[float, float], tuple[float, float]]:
    """Calcula el rango apropiado para el gráfico, permitiendo valores negativos."""
    x_min, x_max = -10, 10
    y_min, y_max = -10, 10
    
    # Usar la solución óptima para determinar el centro del gráfico
    if self.solution:
        sol_x = self.solution.variables.get(self.var_x, 0)
        sol_y = self.solution.variables.get(self.var_y, 0)
        # Expandir según la solución...
    
    return (x_min, x_max), (y_min, y_max)
```

### 8.3 Algoritmo de Región Factible

El método [`find_feasible_vertices`](src/visualization/visualization.py:147) encuentra los vértices de la región factible:

1. **Recopilación de restricciones**: Incluye restricciones originales y de no negatividad
2. **Intersecciones pairwise**: Calcula intersección entre cada par de restricciones
3. **Verificación de factibilidad**: Descarta puntos que violan alguna restricción
4. **Intersecciones con ejes**: Considera puntos donde las restricciones cruzan x=0 o y=0
5. **Ordenamiento**: Ordena vértices en sentido antihorario para graficación

### 8.4 Salida Gráfica

El método [`plot`](src/visualization/visualization.py:215) genera:

- Gráfico en formato PNG con resolución 150 DPI
- Leyenda con todas las restricciones
- Ejes cartesianos completos con líneas en x=0 e y=0
- Región factible sombreada en verde
- Puntos de intersección marcados en rojo
- Solución óptima marcada con estrella azul

---

## 9. Módulo de Análisis Multi-Problema

### 9.1 Estructura del Reporte PDF

El módulo [`MultiLPAnalysis`](src/analysis/multi_analysis.py:82) genera reportes profesionales con la siguiente estructura:

1. **Portada**: Título, información del sistema, fecha
2. **Resumen Ejecutivo**: Estadísticas generales, tabla de resultados
3. **Páginas Individuales**: Un página por problema con:
   - Función objetivo
   - Tabla de restricciones con holguras
   - Solución óptima
   - Gráfico de región factible (para 2 variables)
   - Análisis de tiempos
4. **Resumen de Tiempos**: Tiempos totales de ejecución

### 9.2 Clases de Estilo

```python
class ReporteAcademicoMulti(FPDF):
    """Clase base para reportes multi-problema."""
    
    def header(self):
        """No mostrar header en todas las páginas."""
        pass
    
    def footer(self):
        """Pie de página completo."""
        # Información de página, marca de agua, etc.
```

### 9.3 Generación de Gráficos en PDF

El método [`_build_grafico`](src/analysis/multi_analysis.py:560) integra visualizaciones en el PDF:

1. Genera el gráfico temporalmente usando `LinearVisualization`
2. Convierte la imagen a formato soportado por fpdf2
3. Inserta la imagen en el PDF con posicionamiento adecuado
4. Limpia archivos temporales

### 9.4 Análisis de Holguras

El método [`_calcular_holguras`](src/analysis/multi_analysis.py:620) calcula:

- **Holgura (Slack)**: Diferencia entre el lado izquierdo y derecho de restricciones `<=`
- **Exceso (Surplus)**: Diferencia para restricciones `>=`
- **Restricciones Activas**: Aquellas con holgura cero

---

## 10. Algoritmos y Complejidad

### 10.1 Método Simplex

El sistema utiliza el método Simplex implementado en Gurobi, que incluye:

#### Simplex Revisado
- Optimización del método simplex original
- Mantiene solo las columnas relevantes en cada iteración
- Complejidad: O(n³) en el caso promedio

#### Simplex de Dos Fases
- Fase I: Encuentra solución factible básica
- Fase II: Optimiza desde la solución factible

#### Método de la M Grande
- Penaliza variables artificiales en la función objetivo
- Parameter M suficientemente grande

### 10.2 Complejidad Computacional

| Operación | Complejidad | Descripción |
|-----------|-------------|-------------|
| Parsing | O(n×m) | n=líneas del archivo, m=variables |
| Construcción LP | O(m×r) | m=variables, r=restricciones |
| Optimización Gurobi | O(n³) promedio | Depende del tamaño del problema |
| Visualización | O(r² + v) | r=restricciones, v=vértices |
| Generación PDF | O(k) | k=número de problemas |

### 10.3 Estructuras de Datos

| Estructura | Uso | Ventajas |
|------------|-----|----------|
| Polars DataFrame | Matrices sparse | Eficiente en memoria, operaciones vectorizadas |
| Dict[str, float] | Coeficientes | Búsqueda O(1) por variable |
| List[LinearConstraint] | Restricciones | Iteración secuencial eficiente |
| Polygon (matplotlib) | Región factible | Rendering optimizado |

### 10.4 Patrones de Diseño Aplicados

| Patrón | Módulo | Beneficio |
|--------|--------|-----------|
| Data Class | core/* | Inmutabilidad, comparabilidad |
| Factory | matrix/builder.py | Creación de objetos PolarsLP |
| Strategy | main.py | Selección de algoritmos de resolución |
| Template Method | analysis/* | Estructura de reportes definida |

---

## 11. Referencias Técnicas

### 11.1 Teoría de Programación Lineal

- **George Dantzig** (1947): Inventor del método Simplex
- **Referencia**: Dantzig, G. B. & Thapa, M. N. (1997). *Linear Programming*. Springer.

### 11.2 Método Simplex

- **Variantes**: Simplex primal, Simplex dual, Simplex revisado
- **Complejidad**: Polinomial en promedio, exponencial en peor caso
- **Avances**: Método del elipsoide (Khachiyan), punto interior (Karmarkar)

### 11.3 Dualidad en Programación Lineal

- **Teorema de dualidad fuerte**: Valores óptimos de primal y dual son iguales
- **Teorema de dualidad débil**: Cualquier solución factible del dual acota el primal
- **Precios sombra**: Variables duales representan el valor marginal de recursos

### 11.4 Optimización con Gurobi

- **Documentación**: [Gurobi Optimizer Reference Manual](https://www.gurobi.com/documentation/)
- **API Python**: [Gurobi Python API](https://www.gurobi.com/documentation/9.0/quickstart_mac/py_quickstart.html)
- **Algoritmos**: Simplex, barrera, recocido simulado, métodos híbridos

### 11.5 Análisis de Sensibilidad

- **Holguras (Slack)**: Recursos no utilizados en restricciones `<=`
- **Precios Sombra**: Valor marginal de recursos adicionales
- **Rango de optimalidad**: Rango donde la solución permanece óptima
- **Rango de factibilidad**: Rango donde la solución permanece factible

### 11.6 Funciones Objetivo Múltiples

- **Weighted Sum Method**: Agregación de objetivos con ponderaciones
- **ε-constraint Method**: Optimiza un objetivo sujetando otros
- **Pareto Optimality**: Soluciones no dominadas

### 11.7 Bibliotecas Relacionadas

| Biblioteca | Propósito | Referencia |
|------------|-----------|------------|
| Gurobi | Optimización | gurobipy |
| Polars | DataFrames | polars |
| Matplotlib | Visualización | matplotlib.org |
| NumPy | Computación numérica | numpy.org |
| fpdf2 | PDF | pypi.org/project/fpdf2 |

---

## 12. Licencia y Contribuciones

### 12.1 Licencia

Este proyecto está licenciado bajo la **MIT License**.

```
MIT License

Copyright (c) 2026 Gurobipy-Simplex-General-Solver

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 12.2 Autores y Contribuidores

| Nombre | Rol | Contacto |
|--------|-----|-----------|
| **Oyhs-co** | Desarrollador Principal | oyhsotelo@gmail.com |

### 12.3 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. **Fork** el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un **Pull Request**

### 12.4 Cómo Reportar Issues

Si encuentras algún problema o tienes sugerencias:

1. Verifica que el issue no haya sido reportado anteriormente
2. Proporciona pasos detallados para reproducir el problema
3. Incluye información de tu entorno (SO, Python, versiones de dependencias)
4. Adjunta archivos de prueba si es posible

---

<div align="center">

## Desarrollado con ❤️ usando Gurobi, Polars, Matplotlib y fpdf2

*Versión del proyecto: 0.1.0*

</div>
