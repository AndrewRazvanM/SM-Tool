"""
formatter_thresholds.py
-----------------------
All threshold tuples used by classify() and scale_formatter().

Threshold tuple format: ((upper_limit, style_index), ...)
    style_index 0 = green (good)
    style_index 1 = yellow (warning)
    style_index 2 = red (critical)
    style_index 3 = dim (N/A / muted)

classify() picks the FIRST entry whose limit > value, so order matters:
list from lowest limit to highest, last entry is float("inf") as catch-all.

PRESSURE_HEALTH_THRESHOLDS is inverted: lower score = worse health.
"""

# ---------------------------------------------------------------------------
# PSI pressure — CPU averages (some only; CPU has no "full" line)
# ---------------------------------------------------------------------------

# Avg10 / Avg60 for CPU pressure  (higher = worse, same thresholds)
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

# ---------------------------------------------------------------------------
# PSI pressure — Memory and IO "some" averages
# ---------------------------------------------------------------------------

MEM_IO_SOME_AVG10_60_THRESHOLDS = (
    (1.0, 0),
    (5.0, 1),
    (float("inf"), 2),
)

MEM_IO_SOME_AVG300_THRESHOLDS = (
    (0.5, 0),
    (2.0, 1),
    (float("inf"), 2),
)

# ---------------------------------------------------------------------------
# PSI pressure — Memory and IO "full" averages (stricter than "some")
# ---------------------------------------------------------------------------

MEM_IO_FULL_AVG10_60_THRESHOLDS = (
    (0.5, 0),
    (1.0, 1),
    (float("inf"), 2),
)

MEM_IO_FULL_AVG300_THRESHOLDS = (
    (0.1, 0),
    (0.5, 1),
    (float("inf"), 2),
)

# ---------------------------------------------------------------------------
# PSI pressure — IO averages (same values as MEM; aliased for readability)
# ---------------------------------------------------------------------------

IO_PRESSURE_THRESHOLDS = (
    (1.0, 0),
    (5.0, 1),
    (float("inf"), 2),
)

# ---------------------------------------------------------------------------
# PSI health score (0–100, higher = healthier, so thresholds are inverted)
# ---------------------------------------------------------------------------

PRESSURE_HEALTH_THRESHOLDS = (
    (80.0, 2),          # score <= 80  → critical
    (90.0, 1),          # score <= 90  → warning
    (float("inf"), 0),  # score >  90  → good
)

# ---------------------------------------------------------------------------
# Temperature — CPU and GPU share identical limits
# ---------------------------------------------------------------------------

CPU_TEMP_THRESHOLDS = (
    (70, 0),            # <= 70 °C → good
    (80, 1),            # <= 80 °C → warning
    (float("inf"), 2),  # >  80 °C → critical
)

GPU_TEMP_THRESHOLDS = CPU_TEMP_THRESHOLDS   # same limits, aliased

# ---------------------------------------------------------------------------
# Load — GPU core / memory load percentage
# ---------------------------------------------------------------------------

GPU_LOAD_THRESHOLDS = (
    (50, 0),            # <= 50 % → good
    (80, 1),            # <= 80 % → warning
    (float("inf"), 2),  # >  80 % → critical
)

# ---------------------------------------------------------------------------
# Unit scales for scale_formatter()
# Use binary (1024-based) for storage/memory, decimal (1000-based) for network
# ---------------------------------------------------------------------------

BINARY_UNITS_SCALES = (
    (1024 ** 3, "GiB"),
    (1024 ** 2, "MiB"),
    (1024 ** 1, "KiB"),
    (1,         "B"),
)

DECIMAL_UNITS_SCALES = (
    (1000 ** 3, "Gb"),
    (1000 ** 2, "Mb"),
    (1000 ** 1, "Kb"),
    (1,         "b"),
)