SOME_THRESHOLDS = (
    (1.0, 0),
    (5.0, 1),
    (float("inf"), 2),
)

SOME_300_THRESHOLDS = (
    (0.5, 0),
    (2.0, 1),
    (float("inf"), 2),
)

FULL_THRESHOLDS = (
    (0.5, 0),
    (1.0, 1),
    (float("inf"), 2),
)

FULL_300_THRESHOLDS = (
    (0.1, 0),
    (0.5, 1),
    (float("inf"), 2),
)

CPU_AVG10_THRESHOLDS = (
    (1.0, 0),
    (5.0, 1),
    (float("inf"), 2),
)

CPU_AVG60_THRESHOLDS = (
    (1.0, 0),
    (3.0, 1),
    (float("inf"), 2),
)

CPU_AVG300_THRESHOLDS = (
    (0.5, 0),
    (1.0, 1),
    (float("inf"), 2),
)

CPU_HEALTH_THRESHOLDS = (
    (80.0, 2),   # <=80 → critical
    (90.0, 1),   # <=90 → warning
    (float("inf"), 0),  # >90 → good
)