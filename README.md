# Gurobipy-simplex-general-solver

Un resolvedor de problemas de Programación Lineal (LP) que parsea archivos de texto, construye una representación interna utilizando **Polars** y resuelve el problema mediante optimización con **Gurobi**.

## 📋 Descripción

Este proyecto implementa un solver de Programación Lineal que:

1. **Parsea** problemas LP definidos en archivos de texto plano
2. **Construye** una representación matricial eficiente usando Polars
3. **Resuelve** el problema usando Gurobi (optimizador de alto rendimiento)

### Características

- Soporte para problemas de maximización y minimización
- Restricciones con operadores `<=`, `>=`, y `=`
- Variables con límites inferiores y superiores
- Variables libres (unrestricted)
- Comentarios en archivos LP (líneas que empiezan con `#`)
- Validación completa de entrada

## 🛠️ Instalación

### Requisitos

- Python 3.14+
- Gurobi Optimizer 13.0+
- Polars 1.39+

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone <repositorio-url>
   cd gurobipy-simplex-general-solver
   ```

2. **Instalar dependencias**
   ```bash
   pip install gurobipy polars
   ```

   O si usas Poetry:
   ```bash
   poetry install
   ```

3. **Configurar licencia de Gurobi**
   
   Obtén una licencia gratuita en [gurobi.com](https://www.gurobi.com/downloads/).

## 📖 Formato de Archivo LP

El archivo de entrada debe seguir este formato:

```
max: 3000x + 5000y

# restricciones
2x + 3y <= 120
x + 3y <= 90

# bounds
x >= 0
y >= 0
```

### Estructura del Archivo

| Sección | Descripción | Ejemplo |
|---------|-------------|---------|
| **Función objetivo** | Primera línea: `max:` o `min:` seguido de expresión lineal | `max: 3000x + 5000y` |
| **Restricciones** | Expresiones lineales con operador y valor RHS | `2x + 3y <= 120` |
| **Bounds** | Límites de variables | `x >= 0`, `0 <= y <= 100` |

### Operadores Soportados

- `<=` : Menor o igual que
- `>=` : Mayor o igual que
- `=`  : Igual a

### Formatos de Bounds

```lp
x >= 0          # Límite inferior
x <= 10         # Límite superior
0 <= x <= 10    # Límites doble
x free          # Variable libre (sin restricciones)
x unrestricted  # Variable libre (sin restricciones)
```

### Notas

- Las líneas que empiezan con `#` son comentarios
- Los espacios en blanco son ignorados
- Las variables pueden tener nombres alfanuméricos: `x`, `y`, `var1`, `x1_2`
- Los coeficientes pueden ser positivos o negativos, enteros o decimales

## 🚀 Uso

### Ejecución Básica

```bash
python main.py data/problem.txt
```

### Ejemplo de Salida

```
Valor óptimo: 30000.00
x = 30.00
y = 20.00
```

### Usando como Librería

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
SolverLP(lp).solve()
```

## 📁 Estructura del Proyecto

```
gurobipy-simplex-general-solver/
├── main.py                  # Punto de entrada CLI
├── pyproject.toml           # Configuración del proyecto
├── README.md                # Documentación
├── LICENSE                  # Licencia MIT
├── data/
│   └── problem.txt          # Ejemplo de problema LP
├── src/
│   ├── __init__.py          # Exports públicos
│   ├── parser/
│   │   ├── __init__.py
│   │   └── lp_parser.py     # Parser de archivos LP
│   ├── core/
│   │   ├── __init__.py
│   │   ├── problem.py       # Modelo del problema
│   │   ├── constraint.py    # Representación de restricciones
│   │   ├── bound.py         # Representación de límites
│   │   └── solution.py      # Representación de soluciones
│   ├── matrix/
│   │   ├── __init__.py
│   │   ├── builder.py       # Constructor de matrices Polars
│   │   └── matrix.py        # Tipos de matrices
│   └── solver/
│       ├── __init__.py
│       └── solver.py        # Integración con Gurobi
├── legacy/
│   └── Simplex.py           # Implementación legacy (Simplex manual)
└── test_parser.py           # Tests del parser
```

## 📦 Dependencias

| Paquete | Versión | Descripción |
|---------|---------|-------------|
| `gurobipy` | >=13.0.1 | Optimizador comercial de Programación Lineal/Entera |
| `polars` | >=1.39.0 | DataFrame library para manipulación eficiente de datos |

## ⚠️ Estados de Solución

El solver puede retornar los siguientes estados:

| Estado | Descripción |
|--------|-------------|
| `OPTIMAL` | Se encontró la solución óptima |
| `INFEASIBLE` | El problema no tiene solución factible |
| `UNBOUNDED` | La función objetivo puede mejorarse indefinidamente |
| `OTHER` | Otro estado (consultar código de Gurobi) |

## 📝 Licencia

MIT License - ver archivo [LICENSE](LICENSE)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

---

Desarrollado con ❤️ usando Gurobi y Polars
