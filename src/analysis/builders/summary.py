"""
Sección de resumen para reportes de análisis LP.

"""

from ..base import ReportBuilder
from ..styles import FONTS, COLORS, LAYOUT
from ..utils import format_number, format_percent

class SummaryBuilder(ReportBuilder):
    """Builder para la sección de resumen."""
    
    def build(self) -> None:
        """Construye la sección de resumen."""
        report = self.report
        summary = report.get_summary_data()
        
        # Título de sección
        report.add_element({
            "type": "title",
            "text": "Resumen del Problema",
            "fontsize": FONTS["heading"],
            "spacer": LAYOUT["section_spacing"],
        })
        
        # Información del problema
        lines = [
            f"Nombre: {summary['problem_name']}",
            f"Tipo: {'MILP' if summary['is_mip'] else 'LP'}",
            f"Sentido: {summary['sense'].upper()}",
            f"Variables: {summary['num_variables']}",
            f"Restricciones: {summary['num_constraints']}",
            f"Estado: {summary['status']}",
        ]
        
        if summary['objective_value'] is not None:
            lines.append(f"Valor óptimo: {format_number(summary['objective_value'], 6)}")
        
        report.add_element({
            "type": "text_block",
            "lines": lines,
            "fontsize": FONTS["normal"],
            "spacer": LAYOUT["section_spacing"],
        })
        
        # Separador
        report.add_element({
            "type": "separator",
            "spacer": LAYOUT["section_spacing"],
        })
