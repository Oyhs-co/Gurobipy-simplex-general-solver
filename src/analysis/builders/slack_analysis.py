"""
Slack analysis section builder for LP analysis reports.
"""
from ..base import ReportBuilder


class SlackAnalysisBuilder(ReportBuilder):
    """Builder for the slack analysis section."""
    
    def build(self) -> None:
        """Build slack analysis section."""
        report = self.report
        problem = report.problem
        solution = report.solution
        
        if not solution.is_optimal():
            return
        
        # Add section title
        report.add_element({
            "type": "title",
            "text": "Slack Analysis",
            "fontsize": 16,
            "spacer": 0.3,
        })
        
        # Calculate slacks
        slack_data = []
        for i, constr in enumerate(problem.constraints):
            lhs = sum(
                coeff * solution.variables.get(var, 0.0)
                for var, coeff in constr.coefficients.items()
            )
            
            if constr.sense == "<=":
                slack = constr.rhs - lhs
                status = "Inactive" if abs(slack) < 1e-6 else "Active"
            elif constr.sense == ">=":
                slack = lhs - constr.rhs
                status = "Inactive" if abs(slack) < 1e-6 else "Active"
            else:
                slack = abs(lhs - constr.rhs)
                status = "Active" if slack < 1e-6 else "Inactive"
            
            slack_data.append({
                "name": constr.name or f"R{i}",
                "sense": constr.sense,
                "rhs": constr.rhs,
                "lhs": lhs,
                "slack": slack,
                "status": status,
            })
        
        if slack_data:
            lines = ["Constraint Slack Analysis:"]
            for item in slack_data:
                lines.append(
                    f"  {item['name']}: RHS={item['rhs']:.4f}, "
                    f"LHS={item['lhs']:.4f}, Slack={item['slack']:.6f} ({item['status']})"
                )
            
            report.add_element({
                "type": "text_block",
                "lines": lines,
                "fontsize": 10,
                "spacer": 0.3,
            })
        
        # Add separator
        report.add_element({
            "type": "separator",
            "spacer": 0.2,
        })
