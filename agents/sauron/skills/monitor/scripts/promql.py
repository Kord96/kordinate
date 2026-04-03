"""
PromQL query parsing utilities.

Extracted from nokrashi-tools (Kord96/nokrashi-tools, archived).
"""

import re


def extract_metrics_from_promql(queries: list[str]) -> set[str]:
    """Extract metric names from PromQL queries.

    Args:
        queries: List of PromQL query strings

    Returns:
        Set of metric names found in queries

    Example:
        extract_metrics_from_promql([
            'rate(http_requests_total[5m])',
            'sum(cpu_usage) by (instance)',
        ])
        # Returns: {'http_requests_total', 'cpu_usage'}
    """
    metrics = set()

    # Pattern to match metric names in PromQL
    # Metric names: [a-zA-Z_:][a-zA-Z0-9_:]*
    # They appear before { or [ or ( or whitespace or operators
    metric_pattern = re.compile(
        r"(?<![a-zA-Z0-9_:])([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\s*[{\[(]|\s*(?:by|without|on|ignoring|group_left|group_right)\s*\(|$)"
    )

    # Functions to exclude (PromQL functions, not metrics)
    promql_functions = {
        "abs",
        "absent",
        "absent_over_time",
        "avg",
        "avg_over_time",
        "bottomk",
        "ceil",
        "changes",
        "clamp",
        "clamp_max",
        "clamp_min",
        "count",
        "count_over_time",
        "count_values",
        "day_of_month",
        "day_of_week",
        "days_in_month",
        "delta",
        "deriv",
        "exp",
        "floor",
        "group",
        "histogram_quantile",
        "holt_winters",
        "hour",
        "idelta",
        "increase",
        "irate",
        "label_join",
        "label_replace",
        "last_over_time",
        "ln",
        "log10",
        "log2",
        "max",
        "max_over_time",
        "min",
        "min_over_time",
        "minute",
        "month",
        "predict_linear",
        "quantile",
        "quantile_over_time",
        "rate",
        "resets",
        "round",
        "scalar",
        "sgn",
        "sort",
        "sort_desc",
        "sqrt",
        "stddev",
        "stddev_over_time",
        "stdvar",
        "stdvar_over_time",
        "sum",
        "sum_over_time",
        "time",
        "timestamp",
        "topk",
        "vector",
        "year",
        "present_over_time",
        "by",
        "without",
        "on",
        "ignoring",
        "group_left",
        "group_right",
        "bool",
        "offset",
    }

    for query in queries:
        if not query:
            continue
        # Find all potential metric names
        for match in metric_pattern.finditer(query):
            name = match.group(1)
            if name.lower() not in promql_functions:
                metrics.add(name)

    return metrics
