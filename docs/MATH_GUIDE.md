# Guía Matemática - ISLA LP Benchmark

Esta guía es para **matemáticos e investigadores** que quieren entender la teoría detrás del sistema.

## Fundamento Matemático

### Problema de Programación Lineal

Un problema de Programación Lineal (PL) tiene:

1. **Función Objetivo**: Maximizar o minimizar
   ```
   max/min: c₁x₁ + c₂x₂ + ... + cₙxₙ
   ```

2. **Restricciones**: Desigualdades/igualdades lineales
   ```
   a₁₁x₁ + a₁₂x₂ + ... + a₁ₙxₙ <= b₁
   a₂₁x₁ + a₂₂x₂ + ... + a₂ₙxₙ >= b₂
   ...
   aₘ₁x₁ + aₘ₂x₂ + ... + aₘₙxₙ = bₘ
   ```

3. **Límites**: Límites de variables
   ```
   xᵢ >= ℓᵢ
   xᵢ <= uᵢ
   ```

### Forma Estándar

El sistema convierte problemas a forma estándar:

- **Maximización**: Convertir a minimización si es necesario
- **Desigualdades**: Convertir >= a <= multiplicando por -1
- **Variables**: Agregar variables de holgura para restricciones <=

## Métodos de Solución

### Simplex

El **Método Simplex** (Dantzig, 1947) es el algoritmo primario:

1. **Solución Factible Básica**: Comenzar en un vértice de la región factible
2. **Operaciones Pivote**: Moverse a vértices adyacentes con mejor valor objetivo
3. **Prueba de Optimalidad**: Detenerse cuando ningún vértice adyacente mejore el objetivo

**Complejidad**: O(mn) por iteración, polinomial en promedio.

### Comparación de Solvers

| Solver | Algoritmo | Fortalezas |
|--------|-----------|------------|
| **HiGHS** | Dual Simplex | Rápido para LP densos |
| **GLPK** | Simplex | Open source estable |
| **CBC** | Branch & Cut | Para MIP |
| **Gurobi** | Multi-method | Mejor rendimiento general |

### Métodos de Punto Interior

Para problemas grandes, algunos solvers usan **Métodos de Barrera**:

1. **Barrera Logarítmica**: Agregar término de barrera al objetivo
2. **Camino Central**: Seguir camino al óptimo
3. **Método de Newton**: Resolver condiciones KKT

## Análisis de Sensibilidad

### Costos Reducidos

Para variable xⱼ en el óptimo:

```
costo_reducido = coeficiente_objetivo - precio_sombra * coeficiente_restricción
```

- Si costo_reducido > 0 (max): aumentar xⱼ decrease objetivo
- Si costo_reducido < 0 (max): aumentar xⱼ increase objetivo

### Precios Sombra (Valores Duales)

Para restricción i:

```
precio_sombra = d(valor_óptimo) / d(bi)
```

Interpretación: El valor marginal de relajar la restricción i por una unidad.

### Rangos de Factibilidad

- **Rango RHS**: Rango donde el precio sombra permanece válido
- **Rango Objetivo**: Rango donde la base permanece óptima

## Análisis de Infactibilidad

### IIS (Conjunto Infactible Irreducible)

Cuando un problema es infactible:

1. **Calcular IIS**: Encontrar subconjunto infactible mínimo
2. **Identificar conflictos**: Qué restricciones se contradicen
3. **Sugerir correcciones**: Relajar o eliminar restricciones

### Problema Dual

Todo problema primal tiene un dual:

| Primal | Dual |
|--------|------|
| max cᵀx | min bᵀy |
| Ax <= b | Aᵀy >= c |
| x >= 0 | y >= 0 |

**Dualidad Fuerte**: Si el primal tiene solución óptima, el dual también la tiene con el mismo valor objetivo.

## Benchmark - Fair Comparison

### Warmup

Para comparaciones justas:

```python
config = BenchmarkConfig(
    warmup_runs=1,    # Ejecuciones de calentamiento
    runs_per_problem=3
)
```

El warmup elimina variaciones de JVM/hotspot.

### Métricas de Benchmark

| Métrica | Descripción |
|---------|------------|
| parse_time | Tiempo de parsing |
| build_time | Construcción Polars |
| solve_time | Resolución solver |
| total_time | Tiempo total |
| memory_used_mb | MemoriaDelta |
| peak_memory_mb | Pico de memoria |
| iterations | Iteraciones simplex |
| nodes | Nodos explorados |

### Configuración Uniforme

```python
# Misma configuración para todos los solvers
config = BenchmarkConfig(
    fairness_mode=True,  # Configuración uniforme
    collect_memory=True,
    collect_detailed_stats=True
)
```

## Selección del Algoritmo

### Cuándo Usar Cada Solver

| Solver | Mejor Para |
|--------|----------|
| HiGHS | LP densos, open source |
| GLPK | Portabilidad, open source |
| CBC | MIP simples |
| Gurobi | Mejor rendimiento general |

### Configuración

```python
from src.solver import BenchmarkRunner, BenchmarkConfig

config = BenchmarkConfig(
    warmup_runs=1,
    runs_per_problem=3,
    collect_memory=True,
    fairness_mode=True
)
```

## Notas de Rendimiento

### Características del Problema

| Característica | Impacto |
|-------------|--------|
| Variables | Más variables = más columnas |
| Restricciones | Más restricciones = más filas |
| Densidad | Matrices densas son más lentas |
| Degeneración | Puede causar ciclación |

### Parámetros de Benchmark

```python
config = BenchmarkConfig(
    warmup_runs=2,       # Warmup iterations
    runs_per_problem=5,  # Repeticiones
    time_limit=60,       # Límite por problema
    verbose=False,        # Salida detallada
    collect_memory=True   # Métricas de memoria
)
```

---

## Referencias

1. Dantzig, G. B. (1963). *Linear Programming and Extensions*. Princeton University Press.
2. Bertsimas, D., & Tsitsiklis, J. N. (1997). *Introduction to Linear Optimization*. Athena Scientific.
3. HiGHS Documentation. *Highs Optimization Solver*.
4. GLPK Documentation. *GNU Linear Programming Kit*.

Para detalles de API, ver [README.md](../README.md).