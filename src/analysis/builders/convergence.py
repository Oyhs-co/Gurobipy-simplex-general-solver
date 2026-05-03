"""
Convergence section builder for LP analysis reports.
"""
from ..base import ReportBuilder


class ConvergenceBuilder(ReportBuilder):
    """Builder for the convergence section."""
    
    def build(self) -> None:
        """Build convergence section."""
        report = self.report
        solution = report.solution
        
        if not hasattr(solution, 'progress_log') or not solution.progress_log:
            return
        
        # Add section title
        report.add_element({
            "type": "title",
            "text": "Convergence History",
            "fontsize": 16,
            "spacer": 0.3,
        })
        
        # Plot convergence
        try:
            import matplotlib.pyplot as plt
            
            iterations = [p.iteration for p in solution.progress_log]
            objectives = [p.objective for p in solution.progress_log]
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(iterations, objectives, 'b-', linewidth=2)
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Objective Value')
            ax.set_title('Convergence History')
            ax.grid(True, alpha=0.3)
            
            report.add_element({
                "type": "figure",
                "figure": fig,
                "spacer": 0.3,
            })
        except:
            # Fallback to text
            lines = ["Convergence data available but plotting failed."]
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
