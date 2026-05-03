"""
Unified sensitivity analysis module for LP solvers.
Provides common interface for sensitivity analysis across different solvers.
"""
from typing import Optional, Any
from dataclasses import dataclass, field
import polars as pl

# Import solver-specific constants if available
GRB = None
HIGHS = None

try:
    from gurobipy import GRB
except ImportError:
    pass

try:
    import highspy
    HIGHS = highspy
except ImportError:
    pass


@dataclass
class SensitivityRange:
    """Range for a parameter in sensitivity analysis."""
    current_value: float
    allowable_decrease: float
    allowable_increase: float
    
    def is_at_limit(self, tolerance: float = 1e-6) -> bool:
        """Check if current value is at the limit of the range."""
        return (
            abs(self.current_value - (self.current_value - self.allowable_decrease)) < tolerance or
            abs(self.current_value - (self.current_value + self.allowable_increase)) < tolerance
        )


@dataclass
class SensitivityAnalysis:
    """Complete sensitivity analysis for an LP."""
    objective_ranges: dict[str, SensitivityRange] = field(default_factory=dict)  # Variable -> range
    rhs_ranges: dict[str, SensitivityRange] = field(default_factory=dict)      # Constraint -> range
    basis_status: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'objective_ranges': {
                var: {
                    'current': r.current_value,
                    'decrease': r.allowable_decrease,
                    'increase': r.allowable_increase,
                }
                for var, r in self.objective_ranges.items()
            },
            'rhs_ranges': {
                constr: {
                    'current': r.current_value,
                    'decrease': r.allowable_decrease,
                    'increase': r.allowable_increase,
                }
                for constr, r in self.rhs_ranges.items()
            },
        }
    
    def to_dataframes(self) -> tuple[Optional[pl.DataFrame], Optional[pl.DataFrame]]:
        """Convert to Polars DataFrames."""
        obj_df = None
        rhs_df = None
        
        if self.objective_ranges:
            obj_data = [
                {
                    'variable': var,
                    'current': r.current_value,
                    'min': r.current_value - r.allowable_decrease,
                    'max': r.current_value + r.allowable_increase,
                    'decrease': r.allowable_decrease,
                    'increase': r.allowable_increase,
                }
                for var, r in self.objective_ranges.items()
            ]
            obj_df = pl.DataFrame(obj_data)
        
        if self.rhs_ranges:
            rhs_data = [
                {
                    'constraint': constr,
                    'current': r.current_value,
                    'min': r.current_value - r.allowable_decrease,
                    'max': r.current_value + r.allowable_increase,
                    'decrease': r.allowable_decrease,
                    'increase': r.allowable_increase,
                }
                for constr, r in self.rhs_ranges.items()
            ]
            rhs_df = pl.DataFrame(rhs_data)
        
        return obj_df, rhs_df


def extract_gurobi_sensitivity(model) -> Optional[SensitivityAnalysis]:
    """Extract sensitivity analysis from Gurobi model."""
    if GRB is None:
        return None
    
    try:
        analysis = SensitivityAnalysis()
        
        for var in model.getVars():
            try:
                sa_obj_low = var.getAttr("SAObjLow")
                sa_obj_up = var.getAttr("SAObjUp")
                current = var.getAttr("Obj")
                analysis.objective_ranges[var.getAttr("VarName")] = SensitivityRange(
                    current_value=current,
                    allowable_decrease=current - sa_obj_low,
                    allowable_increase=sa_obj_up - current,
                )
            except:
                pass
        
        for constr in model.getConstrs():
            try:
                sa_rhs_low = constr.getAttr("SARHSLow")
                sa_rhs_up = constr.getAttr("SARHSUp")
                current = constr.getAttr("RHS")
                analysis.rhs_ranges[constr.getAttr("ConstrName")] = SensitivityRange(
                    current_value=current,
                    allowable_decrease=current - sa_rhs_low,
                    allowable_increase=sa_rhs_up - current,
                )
            except:
                pass
        
        return analysis if analysis.objective_ranges or analysis.rhs_ranges else None
    except:
        return None


def extract_highs_sensitivity(hp) -> Optional[SensitivityAnalysis]:
    """Extract sensitivity analysis from HiGHS solver."""
    if HIGHS is None:
        return None
    
    try:
        # HiGHS has getRanging() method in newer versions
        if not hasattr(hp, 'getRanging'):
            return None
        
        try:
            ranging = hp.getRanging()
        except:
            return None
            
        if not ranging:
            return None
        
        analysis = SensitivityAnalysis()
        
        # Objective coefficients ranging
        if hasattr(ranging, 'col_cost_down') and hasattr(ranging, 'col_cost_up'):
            try:
                solution = hp.getSolution()
                for i, var_name in enumerate(hp.getVars()):
                    try:
                        current = solution.col_value[i]
                        low = ranging.col_cost_down[i]
                        up = ranging.col_cost_up[i]
                        analysis.objective_ranges[var_name] = SensitivityRange(
                            current_value=current,
                            allowable_decrease=current - low,
                            allowable_increase=up - current,
                        )
                    except:
                        pass
            except:
                pass
        
        # RHS ranging
        if hasattr(ranging, 'row_rhs_down') and hasattr(ranging, 'row_rhs_up'):
            try:
                rows = hp.getRows()
                for i, constr_name in enumerate(rows):
                    try:
                        current = rows.rhs[i]
                        low = ranging.row_rhs_down[i]
                        up = ranging.row_rhs_up[i]
                        analysis.rhs_ranges[constr_name] = SensitivityRange(
                            current_value=current,
                            allowable_decrease=current - low,
                            allowable_increase=up - current,
                        )
                    except:
                        pass
            except:
                pass
        
        return analysis if analysis.objective_ranges or analysis.rhs_ranges else None
    except:
        return None


def extract_glpk_sensitivity(prob, variables_list: list, constraints: list) -> Optional[SensitivityAnalysis]:
    """Extract sensitivity analysis from GLPK solver."""
    try:
        import swiglpk
        analysis = SensitivityAnalysis()
        
        # This requires GLPK's glp_analyze_bound and glp_analyze_coef
        # which are not directly accessible via swiglpk
        # Placeholder for future implementation
        
        return analysis if analysis.objective_ranges or analysis.rhs_ranges else None
    except:
        return None
