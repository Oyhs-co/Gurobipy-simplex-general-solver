from dataclasses import dataclass


@dataclass
class LinearConstraint:
    """
    Represents a linear constraint in the form of:

    a1*x1 + a2*x2 + ... + an*xn (<=, >=, =) b

    ### attributes:
        -  coefficients: List[float] - Coefficients of the variables
        in the constraint.
        - rhs: float - Right-hand side value of the constraint.
        - sense: str - Type of constraint ("<=", ">=", "=").
    """

    coefficients: dict[str, float]
    rhs: float
    sense: str  # "<=", ">=", "="
