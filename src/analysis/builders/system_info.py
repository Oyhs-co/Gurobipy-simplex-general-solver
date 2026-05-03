"""
Sección de información del sistema para reportes.
"""

from ..base import ReportBuilder
from ..styles import FONTS, COLORS, LAYOUT
from ..utils import get_system_info, format_number


class SystemInfoBuilder(ReportBuilder):
    """Builder for the system information section."""
    
    def build(self) -> None:
        """Build system info section."""
        report = self.report
        
        # Add section title
        report.add_element({
            "type": "title",
            "text": "System Information",
            "fontsize": 16,
            "spacer": 0.3,
        })
        
        # Get system info
        try:
            from ..utils import get_system_info
            info = get_system_info()
            
            lines = [
                f"OS: {info.get('os', 'Unknown')}",
                f"OS Version: {info.get('os_version', 'Unknown')}",
                f"Python Version: {info.get('python_version', 'Unknown')}",
                f"CPU: {info.get('cpu', 'Unknown')}",
                f"Generated: {info.get('timestamp', 'Unknown')}",
            ]
        except:
            lines = ["System information not available."]
        
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
