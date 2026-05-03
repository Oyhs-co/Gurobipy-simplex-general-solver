"""
IIS (Irreducible Infeasible Subsystem) section builder for LP analysis reports.
"""
from ..base import ReportBuilder


class IISSectionBuilder(ReportBuilder):
    """Builder for the IIS section."""
    
    def build(self) -> None:
        """Build IIS section."""
        report = self.report
        solution = report.solution
        
        if not solution.iis:
            return
        
        # Add section title
        report.add_element({
            "type": "title",
            "text": "IIS Analysis",
            "fontsize": 16,
            "spacer": 0.3,
        })
        
        lines = [
            "The following constraints/variables form an Irreducible Infeasible Subsystem:",
            ""
        ]
        
        for i, item in enumerate(solution.iis):
            lines.append(f"  {i+1}. {item}")
        
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
