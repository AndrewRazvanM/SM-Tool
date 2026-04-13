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

PRESSURE_HEALTH_THRESHOLDS = (
    (80.0, 2),   # <=80 → critical
    (90.0, 1),   # <=90 → warning
    (float("inf"), 0),  # >90 → good
)

GPU_TEMP_THRESHOLDS = (
    (70, 0),    # <= 70 → good
    (80, 1),    #<= 80 → warning
    (150, 2) #>80 → critical. 150 degress should be impossible to get, so should be safe to use
)

CPU_TEMP_THRESHOLDS = (
    (70, 0),    # <= 70 → good
    (80, 1),    #<= 80 → warning
    (150, 2) #>90 → critical
)

GPU_LOAD_THRESHOLDS = (
    (50, 0),    # <= 70 → good
    (80, 1),    #<= 80 → warning
    (150, 2)    #>80 → critical #memory load cannot go over 100%. This should be safe
)

IO_PRESSURE_THRESHOLDS = (
    (1.0, 0),
    (5.0, 1),
    (float("inf"), 2),
)