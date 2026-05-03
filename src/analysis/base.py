"""
Base classes for analysis and reporting.
Provides common interface for report generation.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from ..core import Solution, LinearProblem


class BaseReport(ABC):
    """Abstract base class for report generators."""
    
    def __init__(self, problem: LinearProblem, solution: Solution, 
                 output_path: str = "report.pdf"):
        self.problem = problem
        self.solution = solution
        self.output_path = output_path
        self.elements = []  # PDF elements
    
    @abstractmethod
    def build(self) -> None:
        """Build the report structure."""
        pass
    
    @abstractmethod
    def save(self) -> None:
        """Save the report to file."""
        pass
    
    def generate(self) -> None:
        """Generate the complete report."""
        self.build()
        self.save()
    
    def add_element(self, element: Any) -> None:
        """Add an element to the report."""
        self.elements.append(element)
    
    def get_summary_data(self) -> dict:
        """Get common summary data for reports."""
        return {
            "problem_name": self.problem.name or "Unnamed",
            "sense": self.problem.sense,
            "status": self.solution.status,
            "objective_value": self.solution.objective_value,
            "is_optimal": self.solution.is_optimal(),
            "is_mip": self.problem.is_mip,
            "num_variables": len(self.problem.variables),
            "num_constraints": len(self.problem.constraints),
        }


class ReportBuilder(ABC):
    """Builder for a specific section of a report."""
    
    def __init__(self, report: BaseReport):
        self.report = report
    
    @abstractmethod
    def build(self) -> None:
        """Build this section of the report."""
        pass
