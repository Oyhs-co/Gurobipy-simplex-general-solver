"""
Sección de gráficos comparativos para reportes de benchmark.
"""

from ..base import ReportBuilder
from ..styles import FONTS, CHART_COLORS, LAYOUT


class ComparisonChartsBuilder(ReportBuilder):
    """Builder for the comparison charts section."""
    
    def build(self) -> None:
        """Build comparison charts section."""
        report = self.report
        
        # Add section title
        report.add_element({
            "type": "title",
            "text": "Comparison Charts",
            "fontsize": 16,
            "spacer": 0.3,
        })
        
        # Placeholder for solver comparison
        # This would be used in benchmark reports
        lines = [
            "Solver comparison charts would be displayed here.",
            "This section is used in benchmark reports.",
        ]
        
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
