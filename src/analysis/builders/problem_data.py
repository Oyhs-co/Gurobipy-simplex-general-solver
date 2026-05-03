"""
Problem data section builder for LP analysis reports.
"""
from ..base import ReportBuilder


class ProblemDataBuilder(ReportBuilder):
    """Builder for the problem data section."""
    
    def build(self) -> None:
        """Build problem data section."""
        report = self.report
        
        # Add section title
        report.add_element({
            "type": "title",
            "text": "Problem Data",
            "fontsize": 16,
            "spacer": 0.3,
        })
        
        # Add problem information
        problem = report.problem
        solution = report.solution
        
        lines = [
            f"Problem Name: {problem.name or 'Unnamed'}",
            f"Objective Sense: {problem.sense.upper()}",
            f"Number of Variables: {len(problem.variables)}",
            f"Number of Constraints: {len(problem.constraints)}",
            f"Problem Type: {'MILP' if problem.is_mip else 'LP'}",
        ]
        
        if solution.objective_value is not None:
            lines.append(f"Objective Value: {solution.objective_value:.6f}")
        
        lines.append(f"Solution Status: {solution.status}")
        
        report.add_element({
            "type": "text_block",
            "lines": lines,
            "fontsize": 11,
            "spacer": 0.3,
        })
        
        # Add separator
        report.add_element({
            "type": "separator",
            "spacer": 0.2,
        })
