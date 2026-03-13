from src.parser import LPParser

problem_text = """
max u = 3x + 5y - 2z

# restricciones
2x + y <= 18
2x + 3y >= 10
x + y = 5

# bounds
x >= 0
y <= 10
z free
"""
parser = LPParser(problem_text)
problem = parser.parse()

print(problem)

print("SENSE:")
print(problem.sense)

print("\nOBJECTIVE:")
print(problem.objective)

print("\nVARIABLES:")
print(problem.variables)

print("\nCONSTRAINTS:")
for c in problem.constraints:
    print(c)

print("\nBOUNDS:")
for k, v in problem.bounds.items():
    print(k, v)
