"""
Summary section builder for LP analysis reports.
"""
from ..base import ReportBuilder


class SummaryBuilder(ReportBuilder):
    """Builder for the summary section."""
    
    def build(self) -> None:
        """Build summary section."""
        report = self.report
        summary = report.get_summary_data()
        
        # Add section title
        report.add_element({
            "type": "title",
            "text": "Problem Summary",
            "fontsize": 16,
            "spacer": 0.3,
        })
        
        # Add summary information
        lines = [
            f"Problem Name: {summary['problem_name']}",
            f"Problem Type: {'MILP' if summary['is_mip'] else 'LP'}",
            f"Optimization Sense: {summary['sense'].upper()}",
            f"Number of Variables: {summary['num_variables']}",
            f"Number of Constraints: {summary['num_constraints']}",
        ]
        
        if summary['objective_value'] is not None:
            lines.append(f"Objective Value: {summary['objective_value']:.6f}")
        
        lines.append(f"Solution Status: {summary['status']}")
        
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
