from dataclasses import dataclass
import polars as pl


@dataclass
class PolarsLP:

    objective: pl.DataFrame
    coefficients: pl.DataFrame
    constraints: pl.DataFrame
    bounds: pl.DataFrame
    sense: str
