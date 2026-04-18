"""Project-wide constants and paths."""

from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
STAGE1_DIR = REPO_ROOT / "outputs" / "stage1"
STAGE2_V2_DIR = REPO_ROOT / "outputs" / "stage2_v2"
STAGE3_V2_DIR = REPO_ROOT / "outputs" / "stage3_v2"
VALIDATION_DIR = REPO_ROOT / "outputs" / "validation"

# Action space (primary: 3-action)
N_ACTIONS_PRIMARY = 3
ACTIONS_PRIMARY = [0, 1, 2]
ACTION_LABELS = {
    0: "No intervention",
    1: "SMS reminder",
    2: "CHW home visit",
    3: "Facility recall",
    4: "Conditional incentive",
}
ACTION_COSTS_POINT = {0: 0, 1: 50, 2: 500, 3: 1500, 4: 800}

# RRR literature ranges (central, low, high)
RRR_RANGES = {
    0: (0.00, 0.00, 0.00),
    1: (0.10, 0.05, 0.15),
    2: (0.20, 0.15, 0.25),
    3: (0.25, 0.20, 0.30),
    4: (0.14, 0.09, 0.22),
}

# Cost CoV for Gamma priors
COST_COV = 0.25

# Reward function constants (unchanged from CLAUDE.md)
REWARD_COMPLETION = 1.0
REWARD_NEXT_DOSE = 0.3
COST_LAMBDA = 0.001
GAMMA_DISCOUNT = 0.95

# Microsimulation defaults
N_POP_DEFAULT = 10_000
N_BOOTSTRAP_DEFAULT = 1_000
CHILDREN_PER_LGA = 3_000

# Validation
CALIBRATION_TOLERANCE = 0.01
SUBGROUP_CALIBRATION_FLAG = 0.03
