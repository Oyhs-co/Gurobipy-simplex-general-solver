"""
Sección de análisis de sensibilidad para reportes LP.
"""

from ..base import ReportBuilder
from ..styles import FONTS, COLORS, LAYOUT
from ..utils import format_number


class SensitivityAnalysisBuilder(ReportBuilder):
    """Builder for the sensitivity analysis section."""
    
    def build(self) -> None:
        """Build sensitivity analysis section."""
        report = self.report
        solution = report.solution
        
        # Add section title
        report.add_element({
            "type": "title",
            "text": "Sensitivity Analysis",
            "fontsize": 16,
            "spacer": 0.3,
        })
        
        if not solution.sensitivity:
            report.add_element({
                "type": "text_block",
                "lines": ["Sensitivity analysis not available for this solver."],
                "fontsize": 11,
                "spacer": 0.3,
            })
            report.add_element({
                "type": "separator",
                "spacer": 0.2,
            })
            return
        
        # Objective coefficients sensitivity
        if hasattr(solution.sensitivity, 'objective_ranges') and solution.sensitivity.objective_ranges:
            lines = ["Objective Coefficients Sensitivity:"]
            for var, rng in solution.sensitivity.objective_ranges.items():
                lines.append(
                    f"  {var}: Current={rng.current_value:.4f}, "
                    f"Allowable Decrease={rng.allowable_decrease:.4f}, "
                    f"Allowable Increase={rng.allowable_increase:.4f}"
                )
            
            report.add_element({
                "type": "text_block",
                "lines": lines,
                "fontsize": 10,
                "spacer": 0.3,
            })
        
        # RHS sensitivity
        if hasattr(solution.sensitivity, 'rhs_ranges') and solution.sensitivity.rhs_ranges:
            lines = ["RHS Sensitivity:"]
            for constr, rng in solution.sensitivity.rhs_ranges.items():
                lines.append(
                    f"  {constr}: Current={rng.current_value:.4f}, "
                    f"Allowable Decrease={rng.allowable_decrease:.4f}, "
                    f"Allowable Increase={rng.allowable_increase:.4f}"
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
