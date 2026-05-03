"""
Style constants for PDF reports.
Centralizes colors, fonts, and layout parameters.
"""
# Color palette
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff7f0e",
    "info": "#17becf",
    "light": "#f8f9fa",
    "dark": "#343a40",
    "white": "#ffffff",
    "black": "#000000",
    "grey": "#6c757d",
}

# Table colors
TABLE_HEADER_BG = "#4472C4"
TABLE_HEADER_TEXT = "#ffffff"
TABLE_ROW_ALTERNATE = "#f2f2f2"
TABLE_BORDER = "#d0d0d0"

# Chart colors (categorical)
CHART_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", 
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"
]

# Font sizes
FONTS = {
    "title": 18,
    "subtitle": 14,
    "heading": 12,
    "normal": 10,
    "small": 8,
    "table_header": 10,
    "table_cell": 9,
}

# Layout
LAYOUT = {
    "page_margin": 36,  # 0.5 inch
    "section_spacing": 12,
    "table_padding": 6,
    "chart_figsize": (6, 4),
}

# Line styles
LINESTYLES = {
    "solid": "-",
    "dashed": "--",
    "dotted": ":",
    "dash_dot": "-.",
}

# Marker styles
MARKERS = ["o", "s", "^", "D", "v", "<", ">", "p", "*"]
