"""
Cover page builder for LP analysis reports.
"""
from datetime import datetime
from ..base import ReportBuilder, BaseReport


class CoverBuilder(ReportBuilder):
    """Builder for the cover page."""
    
    def build(self) -> None:
        """Build cover page elements."""
        report = self.report
        
        # Add title
        title_text = f"LP Analysis Report"
        report.add_element({
            "type": "title",
            "text": title_text,
            "fontsize": 24,
            "spacer": 0.5,
        })
        
        # Add problem information
        summary = report.get_summary_data()
        
        info_lines = [
            f"Problem: {summary['problem_name']}",
            f"Type: {'MILP' if summary['is_mip'] else 'LP'}",
            f"Sense: {summary['sense'].upper()}",
            f"Variables: {summary['num_variables']}",
            f"Constraints: {summary['num_constraints']}",
            f"Status: {summary['status']}",
        ]
        
        if summary['objective_value'] is not None:
            info_lines.append(f"Objective Value: {summary['objective_value']:.6f}")
        
        info_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        report.add_element({
            "type": "text_block",
            "lines": info_lines,
            "fontsize": 12,
            "spacer": 0.3,
        })
        
        # Add separator
        report.add_element({
            "type": "spacer",
            "height": 0.5,
        })
