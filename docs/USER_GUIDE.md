# Guía de Usuario - Gurobipy-Simplex-General-Solver

Esta guía es para **usuarios finales** que quieren resolver problemas de Programación Lineal.

## ¿Qué es Este Proyecto?

Esta es una herramienta que resuelve problemas de Programación Lineal (PL). Defines un problema con un objetivo a maximizar o minimizar, sujeto a restricciones, y la herramienta encuentra la solución óptima.

## Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install gurobipy polars matplotlib numpy fpdf2 reportlab
```

### 2. Crear un Archivo de Problema

Crea un archivo de texto (ej., `miproblema.txt`) con tu problema:

```lp
max profit = 3000x + 5000y

2x + 3y <= 120
x + 3y <= 90

x >= 0
y >= 0
```

### 3. Ejecutar el Solucionador

```bash
python main.py miproblema.txt
```

### 4. Ver Resultados

```
Optimal value: 190000.00
x = 30.00
y = 20.00
```

## Formato de Problemas

### Función Objetivo

Comenzar con `max:` o `min:` seguido de la expresión:

```
max: 3000x + 5000y
min: 2x + 3y + 5z
```

### Restricciones

Usar `<=` (menor o igual), `>=` (mayor o igual), o `=` (igual):

```
x + y <= 100
2x + 3y >= 50
x + y = 75
```

### Límites de Variables

Definir límites para las variables:

```
x >= 0         # límite inferior
y <= 50        # límite superior
x free         # sin límites
0 <= x <= 100   # ambos límites
```

### Comentarios

Usar `#` para comentarios:

```
# Esto es un comentario
max: 3x + 2y

# Restricción de producción
x + y <= 10
```

## Opciones CLI

### Opciones Básicas

| Opción | Descripción |
|--------|-------------|
| `--visualize` | Generar gráfico de región factible |
| `--pdf` | Generar informe PDF |
| `--verbose` | Mostrar salida detallada |

### Comandos de Ejemplo

```bash
# Solo resolver
python main.py miproblema.txt

# Con gráfico
python main.py miproblema.txt --visualize

# Con informe PDF
python main.py miproblema.txt --pdf

# Todo
python main.py miproblema.txt --visualize --pdf --verbose
```

## Múltiples Problemas

Puedes resolver múltiples problemas en un archivo usando `---` como delimitador:

```lp
max: x + 2y
x + y <= 10
x >= 0; y >= 0

---

min: 3x + y
x - y >= 5
x >= 0; y >= 0
```

Ejecutar con:

```bash
python main.py misproblemas.txt --multi
```

## Entendiendo los Resultados

### Solución Óptima

Cuando el solucionador encuentra una solución óptima:

```
Status: OPTIMAL
Optimal value: 190000.00
x = 30.00
y = 20.00
```

### Problema Infactible

Cuando ninguna solución satisface todas las restricciones:

```
Status: INFEASIBLE
```

Esto significa que tus restricciones se contradicen entre sí.

### Problema No Acotado

Cuando el objetivo puede mejorar indefinidamente:

```
Status: UNBOUNDED
```

Esto significa que necesitas restricciones adicionales.

## Informe PDF

El informe PDF contiene un analisis academico completo con las siguientes secciones:

### Contenido del Informe

1. **Portada**: Tipo de problema, numero de variables/restricciones, fecha
2. **Resumen Ejecutivo**: Estado de la solucion, valor optimo
3. **Datos del Problema**: Variables, funcion objetivo, tabla de restricciones
4. **Solucion Optima**: Valores de variables con costos reducidos
5. **Analisis de Holgura y Precios Sombra**: Tabla con holgura, precio sombra y estado
6. **Analisis de Costos Reducidos**: Tabla con interpretacion
7. **Analisis de Sensibilidad**: Interpretacion de resultados y recomendaciones
8. **Region Factible**: Grafico visual (solo para 2 variables)

### Analisis de Sensibilidad

El informe incluye interpretacion de:

- **Holgura (Slack)**: Cantidad de recurso no utilizado en cada restriccion
- **Precio Sombra**: Valor marginal de relajar una restriccion por una unidad
- **Costos Reducidos**: Cantidad que el objetivo mejoraria si una variable aumenta

### Ejemplo de Uso

```bash
# Generar informe PDF con grafico
python main.py problema.txt --pdf --visualize

# Generar informe para multiples problemas
python main.py problemas.txt --multi --pdf
```

## Solucion de Problemas

### "Problema es infactible"

Tus restricciones no pueden satisfacerse al mismo tiempo. Verificar:
- Restricciones contradictorias (ej., `x >= 5` y `x <= 3`)
- Errores en coeficientes
- Usar diagnostico IIS: `solver.diagnose_infeasibility()`

### "Problema es no acotado"

Tu objetivo puede aumentar sin limite. Agregar limites superiores a las variables.

### Resultados incorrectos

- Asegurar que los coeficientes sean correctos
- Verificar direcciones de restricciones (`<=` vs `>=`)
- Usar validacion: `validate_problem(problem)`

---

Para detalles tecnicos, ver [README.md](../README.md).