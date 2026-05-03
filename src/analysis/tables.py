"""
Table drawing utilities for PDF reports.
Uses matplotlib table and Polars DataFrames.
"""
import polars as pl
from typing import Optional, Any


def draw_dataframe_table(
    df: pl.DataFrame,
    title: str = "",
    figsize: tuple = (8, 4),
    header_color: str = "#4472C4",
    row_colors: list = ["#f2f2f2", "#d0d0d0"],
    text_color: str = "#000000",
    fontsize: int = 9,
) -> Any:
    """
    Draw a matplotlib table from a Polars DataFrame.
    Returns matplotlib Figure or None if df is empty.
    """
    if df is None or len(df) == 0:
        return None
    
    import matplotlib.pyplot as plt
    from matplotlib.table import Table
    
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    
    if title:
        ax.set_title(title, fontsize=12, pad=15)
    
    # Convert to list of lists
    headers = df.columns
    rows = df.to_numpy().tolist()
    
    # Create table
    table = Table(ax, bbox=[0, 0, 1, 1])
    
    # Add headers
    for col_idx, header in enumerate(headers):
        table.add_cell(0, col_idx, width=1.0/len(headers), height=0.1,
                       text=header, loc='center', 
                       facecolor=header_color, edgecolor='#000000',
                       text_color='#ffffff', fontsize=fontsize)
    
    # Add rows
    for row_idx, row in enumerate(rows):
        color = row_colors[row_idx % len(row_colors)]
        for col_idx, cell in enumerate(row):
            table.add_cell(row_idx + 1, col_idx, width=1.0/len(headers), height=0.1,
                           text=str(cell), loc='center',
                           facecolor=color, edgecolor='#cccccc',
                           text_color=text_color, fontsize=fontsize)
    
    ax.add_table(table)
    return fig


def format_numeric_column(df: pl.DataFrame, column: str, precision: int = 4) -> pl.DataFrame:
    """Format numeric columns to fixed precision."""
    if column not in df.columns:
        return df
    return df.with_columns(pl.col(column).round(precision))


def highlight_optimal_solution(
    df: pl.DataFrame, 
    optimal_value: Optional[float] = None
) -> pl.DataFrame:
    """Highlight rows where variable value matches optimal (within tolerance)."""
    if optimal_value is None or "value" not in df.columns:
        return df
    tolerance = 1e-6
    return df.with_columns(
        pl.when(pl.col("value").is_between(optimal_value - tolerance, optimal_value + tolerance))
        .then(pl.lit(True))
        .otherwise(pl.lit(False))
        .alias("_highlight")
    )
