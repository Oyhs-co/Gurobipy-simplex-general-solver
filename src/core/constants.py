"""
Centralized numerical constants for LP solving.
Use these constants throughout the codebase to ensure consistent numerical behavior.
"""

# Tolerance for feasibility checks (constraint satisfaction)
FEASIBILITY_TOLERANCE = 1e-6

# Tolerance for optimality checks
OPTIMALITY_TOLERANCE = 1e-6

# Tolerance for bound checks
BOUND_TOLERANCE = 1e-9

# Tolerance for numerical comparisons in parsing
PARSING_TOLERANCE = 1e-10

# Default infinity value (use solver-specific when possible)
DEFAULT_INFINITY = 1e30

# Solver-specific infinity fallbacks
HIGHS_INFINITY = 1e30  # Should use highspy.kInf when possible
GLPK_INFINITY = 1e30
CBC_INFINITY = 1e30
