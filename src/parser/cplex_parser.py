"""
Parser para formato LP (CPLEX).
"""

import re
from ..core import LinearProblem, LinearConstraint, VariableBound


class CPLEXParser:
    """
    Parser para formato LP (CPLEX/GLPK).

    Formato LP estándar:
    \\ Problem name:  name
    Maximize/Minimize
      objective
    Subject To
      constraints
    Bounds
      bounds
    General/Integer/Binary
      variables
    End
    """

    def __init__(self, txt: str) -> None:
        """Inicializa el parser con texto en formato LP."""
        self.txt = txt

    def parse(self) -> LinearProblem:
        """Parsea el problema en formato LP."""
        lines = self.txt.strip().splitlines()
        
        problem_name = "LPProblem"
        sense = "max"
        objective = {}
        constraints = []
        variables = set()
        bounds = {}

        current_section = None
        in_objective = False

        for line in lines:
            line = line.strip()
            
            if not line or line.startswith("\\"):
                continue

            line_lower = line.lower()

            if "problem name" in line_lower:
                match = re.search(r"name:\s*(\S+)", line_lower)
                if match:
                    problem_name = match.group(1)
                continue

            if "maximize" in line_lower:
                sense = "max"
                in_objective = True
                current_section = "objective"
                continue

            if "minimize" in line_lower:
                sense = "min"
                in_objective = True
                current_section = "objective"
                continue

            if line_lower == "subject to":
                in_objective = False
                current_section = "constraints"
                continue

            if line_lower == "bounds":
                current_section = "bounds"
                continue

            if line_lower == "end":
                break

            if in_objective and current_section == "objective":
                obj_expr = self._parse_expression(line)
                for var, coeff in obj_expr.items():
                    if coeff != 0:
                        objective[var] = coeff
                        variables.add(var)

            elif current_section == "constraints":
                if ":" in line:
                    line = line.split(":", 1)[1].strip()
                
                if "<=" in line:
                    lhs, rhs = line.split("<=", 1)
                    coeff = self._parse_expression(lhs)
                    for var in coeff:
                        variables.add(var)
                    constraints.append(LinearConstraint(
                        coefficients=coeff,
                        rhs=float(rhs.strip()),
                        sense="<="
                    ))
                elif ">=" in line:
                    lhs, rhs = line.split(">=", 1)
                    coeff = self._parse_expression(lhs)
                    for var in coeff:
                        variables.add(var)
                    constraints.append(LinearConstraint(
                        coefficients=coeff,
                        rhs=float(rhs.strip()),
                        sense=">="
                    ))
                elif "=" in line:
                    lhs, rhs = line.split("=", 1)
                    coeff = self._parse_expression(lhs)
                    for var in coeff:
                        variables.add(var)
                    constraints.append(LinearConstraint(
                        coefficients=coeff,
                        rhs=float(rhs.strip()),
                        sense="="
                    ))

            elif current_section == "bounds":
                line_clean = line.replace(" ", "")
                
                if ">=" in line_clean:
                    var, val = line_clean.split(">=")
                    var = var.strip()
                    val = float(val)
                    
                    if var in bounds:
                        bounds[var].lower = val
                    else:
                        bounds[var] = VariableBound(var, lower=val)
                
                elif "<=" in line_clean:
                    var, val = line_clean.split("<=")
                    var = var.strip()
                    val = float(val)
                    
                    if var in bounds:
                        bounds[var].upper = val
                    else:
                        bounds[var] = VariableBound(var, upper=val)
                
                elif "<=" in line_clean and ">=" in line_clean:
                    parts = re.split(r"<=|>=", line_clean)
                    lower = float(parts[0])
                    var = parts[1].strip()
                    upper = float(parts[2])
                    
                    bounds[var] = VariableBound(var, lower=lower, upper=upper)

        sorted_vars = sorted(variables)

        return LinearProblem(
            objective=objective,
            sense=sense,
            constraints=constraints,
            variables=sorted_vars,
            bounds=bounds,
            name=problem_name
        )

    def _parse_expression(self, expr: str) -> dict[str, float]:
        """Parsea una expresión lineal."""
        expr = expr.replace(" ", "").replace("-", "+-")
        
        if expr.startswith("+"):
            expr = expr[1:]
        
        terms = expr.split("+")
        coefficients = {}

        for term in terms:
            term = term.strip()
            if not term:
                continue

            var_match = re.match(r"([+-]?\d*\.?\d*)([a-zA-Z][a-zA-Z0-9_]*)", term)
            if var_match:
                coeff_str, var = var_match.groups()
                
                if coeff_str == "" or coeff_str == "+":
                    coeff = 1.0
                elif coeff_str == "-":
                    coeff = -1.0
                else:
                    coeff = float(coeff_str)
                
                coefficients[var] = coefficients.get(var, 0) + coeff

        return coefficients


def parse_lp_file(filepath: str) -> LinearProblem:
    """Parsea un archivo en formato LP."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return CPLEXParser(content).parse()