import numpy as np
import scipy.stats as stats
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)

class StatsUtil:
    """
    Tool for statistical calculations and analysis
    """

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute statistical operation
        """
        operation = parameters.get("operation", "describe")
        data = parameters.get("data", [])

        try:
            if operation == "describe":
                return self.descriptive_stats(data)
            elif operation == "correlation":
                return self.correlation_analysis(parameters)
            elif operation == "hypothesis_test":
                return self.hypothesis_test(parameters)
            elif operation == "trend_analysis":
                return self.trend_analysis(parameters)
            else:
                raise ValueError(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def descriptive_stats(self, data: List[float]) -> Dict[str, Any]:
        """
        Calculate descriptive statistics
        """
        if not data:
            return {"status": "error", "error": "No data provided"}

        arr = np.array(data)

        return {
            "status": "success",
            "count": len(data),
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "mode": float(stats.mode(arr, keepdims=False).mode) if len(data) > 0 else None,
            "std_dev": float(np.std(arr)),
            "variance": float(np.var(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "range": float(np.max(arr) - np.min(arr)),
            "percentiles": {
                "25": float(np.percentile(arr, 25)),
                "50": float(np.percentile(arr, 50)),
                "75": float(np.percentile(arr, 75))
            },
            "skewness": float(stats.skew(arr)),
            "kurtosis": float(stats.kurtosis(arr)),
            "timestamp": datetime.now().isoformat()
        }

    def correlation_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform correlation analysis
        """
        x_data = parameters.get("x_data", [])
        y_data = parameters.get("y_data", [])
        method = parameters.get("method", "pearson")

        if len(x_data) != len(y_data):
            return {
                "status": "error",
                "error": "Data arrays must have same length"
            }

        if len(x_data) < 3:
            return {
                "status": "error",
                "error": "Need at least 3 data points"
            }

        x_arr = np.array(x_data)
        y_arr = np.array(y_data)

        if method == "pearson":
            corr, p_value = stats.pearsonr(x_arr, y_arr)
        elif method == "spearman":
            corr, p_value = stats.spearmanr(x_arr, y_arr)
        elif method == "kendall":
            corr, p_value = stats.kendalltau(x_arr, y_arr)
        else:
            return {"status": "error", "error": f"Unknown method: {method}"}

        # Calculate R-squared
        r_squared = corr ** 2

        # Interpret correlation
        interpretation = self._interpret_correlation(corr)

        return {
            "status": "success",
            "method": method,
            "correlation": float(corr),
            "p_value": float(p_value),
            "r_squared": float(r_squared),
            "interpretation": interpretation,
            "significant": p_value < 0.05,
            "sample_size": len(x_data),
            "timestamp": datetime.now().isoformat()
        }

    def hypothesis_test(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform hypothesis testing
        """
        test_type = parameters.get("test_type", "t_test")
        data1 = parameters.get("data1", [])
        data2 = parameters.get("data2", [])
        alpha = parameters.get("alpha", 0.05)

        if test_type == "t_test":
            # Two-sample t-test
            if not data2:
                # One-sample t-test
                pop_mean = parameters.get("population_mean", 0)
                t_stat, p_value = stats.ttest_1samp(data1, pop_mean)
                test_name = "One-sample t-test"
            else:
                t_stat, p_value = stats.ttest_ind(data1, data2)
                test_name = "Two-sample t-test"

            result = {
                "test_statistic": float(t_stat),
                "p_value": float(p_value)
            }

        elif test_type == "chi_square":
            # Chi-square test
            observed = np.array(data1)
            if data2:
                expected = np.array(data2)
            else:
                expected = np.ones_like(observed) * np.mean(observed)

            chi2, p_value = stats.chisquare(observed, expected)
            test_name = "Chi-square test"
            result = {
                "test_statistic": float(chi2),
                "p_value": float(p_value)
            }

        elif test_type == "anova":
            # One-way ANOVA
            groups = parameters.get("groups", [data1, data2])
            f_stat, p_value = stats.f_oneway(*groups)
            test_name = "One-way ANOVA"
            result = {
                "test_statistic": float(f_stat),
                "p_value": float(p_value)
            }

        else:
            return {"status": "error", "error": f"Unknown test type: {test_type}"}

        # Determine if we reject null hypothesis
        reject_null = p_value < alpha

        return {
            "status": "success",
            "test": test_name,
            **result,
            "alpha": alpha,
            "reject_null_hypothesis": reject_null,
            "conclusion": f"{'Reject' if reject_null else 'Fail to reject'} null hypothesis at {alpha} significance level",
            "timestamp": datetime.now().isoformat()
        }

    def trend_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trends in time series data
        """
        values = parameters.get("values", [])
        timestamps = parameters.get("timestamps", list(range(len(values))))

        if len(values) < 2:
            return {"status": "error", "error": "Need at least 2 data points"}

        x = np.array(timestamps)
        y = np.array(values)

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # Calculate predictions
        predictions = slope * x + intercept

        # Calculate residuals
        residuals = y - predictions
        mse = np.mean(residuals ** 2)
        rmse = np.sqrt(mse)

        # Determine trend direction
        if abs(slope) < std_err:
            trend = "no significant trend"
        elif slope > 0:
            trend = "upward"
        else:
            trend = "downward"

        # Calculate percentage change
        if values[0] != 0:
            pct_change = ((values[-1] - values[0]) / values[0]) * 100
        else:
            pct_change = None

        return {
            "status": "success",
            "trend": trend,
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_value ** 2),
            "p_value": float(p_value),
            "std_error": float(std_err),
            "rmse": float(rmse),
            "percentage_change": float(pct_change) if pct_change else None,
            "forecast_next": float(slope * (len(values)) + intercept),
            "timestamp": datetime.now().isoformat()
        }

    def _interpret_correlation(self, corr: float) -> str:
        """
        Interpret correlation coefficient
        """
        abs_corr = abs(corr)
        if abs_corr < 0.1:
            strength = "negligible"
        elif abs_corr < 0.3:
            strength = "weak"
        elif abs_corr < 0.5:
            strength = "moderate"
        elif abs_corr < 0.7:
            strength = "strong"
        else:
            strength = "very strong"

        direction = "positive" if corr > 0 else "negative"
        return f"{strength} {direction} correlation"

    def get_description(self) -> str:
        """
        Get tool description
        """
        return "Perform statistical calculations and analysis"

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get tool parameters schema
        """
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["describe", "correlation", "hypothesis_test", "trend_analysis"],
                    "description": "Statistical operation to perform"
                },
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Data array for analysis"
                },
                "data1": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "First data array"
                },
                "data2": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Second data array"
                },
                "x_data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "X values for correlation"
                },
                "y_data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Y values for correlation"
                },
                "method": {
                    "type": "string",
                    "enum": ["pearson", "spearman", "kendall"],
                    "description": "Correlation method"
                },
                "test_type": {
                    "type": "string",
                    "enum": ["t_test", "chi_square", "anova"],
                    "description": "Type of hypothesis test"
                },
                "alpha": {
                    "type": "number",
                    "description": "Significance level"
                }
            },
            "required": ["operation"]
        }