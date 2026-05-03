"""
Optimal solution section builder for LP analysis reports.
"""
from ..base import ReportBuilder


class OptimalSolutionBuilder(ReportBuilder):
    """Builder for the optimal solution section."""
    
    def build(self) -> None:
        """Build optimal solution section."""
        report = self.report
        solution = report.solution
        
        if not solution.is_optimal():
            report.add_element({
                "type": "text_block",
                "lines": [f"Solution is not optimal. Status: {solution.status}"],
                "fontsize": 11,
                "spacer": 0.3,
            })
            return
        
        # Add section title
        report.add_element({
            "type": "title",
            "text": "Optimal Solution",
            "fontsize": 16,
            "spacer": 0.3,
        })
        
        # Solution summary
        lines = [
            f"Objective Value: {solution.objective_value:.6f}",
            f"Iterations: {solution.iterations}",
        ]
        
        if solution.nodes > 0:
            lines.append(f"Nodes: {solution.nodes}")
        
        report.add_element({
            "type": "text_block",
            "lines": lines,
            "fontsize": 11,
            "spacer": 0.3,
        })
        
        # Variables table (if available)
        if solution.variables:
            var_lines = ["Variables:"]
            for var, value in sorted(solution.variables.items()):
                var_lines.append(f"  {var} = {value:.4f}")
            
            report.add_element({
                "type": "text_block",
                "lines": var_lines,
                "fontsize": 10,
                "spacer": 0.3,
            })
        
        # Add separator
        report.add_element({
            "type": "separator",
            "spacer": 0.2,
        })
