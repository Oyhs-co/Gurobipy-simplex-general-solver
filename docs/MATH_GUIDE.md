# Guía Matemática - Gurobipy-Simplex-General-Solver

Esta guía es para **matemáticos e investigadores** que quieren entender la teoría detrás del solucionador.

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

El solucionador convierte problemas a forma estándar:

- **Maximización**: Convertir a minimización si es necesario
- **Desigualdades**: Convertir >= a <= multiplicando por -1
- **Variables**: Agregar variables de holgura para restricciones <=

## Métodos de Solución

### Método Simplex

El **Método Simplex** (Dantzig, 1947) es el algoritmo primario:

1. **Solución Factible Básica**: Comenzar en un vértice de la región factible
2. **Operaciones Pivote**: Moverse a vértices adyacentes con mejor valor objetivo
3. **Prueba de Optimalidad**: Detenerse cuando ningún vértice adyacente mejore el objetivo

**Complejidad**: O(mn) por iteración, polinomial en promedio.

### Métodos de Punto Interior

Para problemas grandes, Gurobi usa **Métodos de Barrera**:

1. **Barrera Logarítmica**: Agregar término de barrera al objetivo
2. **Camino Central**: Seguir camino al óptimo
3. **Método de Newton**: Resolver condiciones KKT

### Implementación de Gurobi

El solucionador usa la implementación de Gurobi que incluye:

- **Simplex Primal**: Trabajar en problema primal
- **Simplex Dual**: Trabajar en problema dual
- **Barrera**: Método de punto interior
- **Concurrente**: Ejecutar múltiples métodos en paralelo

## Análisis de Sensibilidad

### Costos Reducidos

Para variable xⱼ en el óptimo:

```
costo_reducido = coeficiente_objetivo - precio_sombra * coeficiente_restricción
```

Si costo_reducido > 0 (problema max): aumentar xⱼ decrease objetivo
Si costo_reducido < 0 (problema max): aumentar xⱼ increase objetivo

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

## Usando el Solucionador

### Acceder a Valores Duales

```python
solution = solver.solve()

# Precios sombra
if solution.dual_values:
    for restriccion, precio in solution.dual_values.items():
        print(f"{restriccion}: {precio:.4f}")

# Costos reducidos
if solution.reduced_costs:
    for variable, costo in solution.reduced_costs.items():
        print(f"{variable}: {costo:.4f}")
```

### Diagnóstico IIS

```python
solver = SolverLP(lp)
solution = solver.solve()

if solution.is_infeasible():
    iis = solver.diagnose_infeasibility()
    print(f"Restricciones en conflicto: {iis['iis_constraints']}")
```

## Selección del Algoritmo

### Cuándo Usar Cada Método

| Método | Mejor Para |
|--------|----------|
| Simplex Primal | Problemas densos, warm starts |
| Simplex Dual | Adiciones de restricciones, análisis de sensibilidad |
| Barrera | Problemas grandes y dispersos |
| Concurrente | Problemas difíciles, rendimiento no confiable |

### Configuración

```python
from src.solver import SolverConfig

# Forzar método específico
config = SolverConfig(method=0)  # Primal
config = SolverConfig(method=1)  # Dual
config = SolverConfig(method=2)  # Barrera
```

## Notas de Rendimiento

### Características del Problema

| Característica | Impacto |
|-------------|--------|
| Variables | Más variables = más columnas |
| Restricciones | Más restricciones = más filas |
| Densidad | Matrices densas son más lentas |
| Degeneración | Puede causar ciclación |

### Parámetros de Gurobi

```python
config = SolverConfig(
    time_limit=300,    # Segundos
    mip_gap=0.0001,   # Gap de optimalidad 0.01%
    threads=8,        # Hilos paralelos
    presolve=1         # Habilitar presolve
)
```

---

## Referencias

1. Dantzig, G. B. (1963). *Linear Programming and Extensions*. Princeton University Press.
2. Bertsimas, D., & Tsitsiklis, J. N. (1997). *Introduction to Linear Optimization*. Athena Scientific.
3. Gurobi Optimization. (2024). *Gurobi Optimizer Reference Manual*.

Para detalles de API, ver [README.md](../README.md).