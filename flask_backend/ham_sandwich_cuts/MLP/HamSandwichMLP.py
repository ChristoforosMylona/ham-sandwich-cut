import math
import os
import random
import sys
import timeit
import numpy as np
from ortools.linear_solver import pywraplp
from tabulate import tabulate

# Get the parent directory and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now you can import from the parent directory's Utils folder
from Utils.check_line import check_line_not_verbose


def find_line_through_points_ortools_extended(A, B, M=1e5, eps=1e-4):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return None

    # Set solver parameters to limit the solver to 1 solution
    solver.SetSolverSpecificParametersAsString("limits/solutions=1")

    # Convert A and B to NumPy arrays for efficient computation
    A = np.array(A)
    B = np.array(B)

    # Compute bounds for x and y.
    min_x = min(np.min(A[:, 0]), np.min(B[:, 0]))
    max_x = max(np.max(A[:, 0]), np.max(B[:, 0]))
    min_y = min(np.min(A[:, 1]), np.min(B[:, 1]))
    max_y = max(np.max(A[:, 1]), np.max(B[:, 1]))

    # Compute slope (m) bounds using broadcasting over all pairs (A, B)
    xA = A[:, 0][:, np.newaxis]  # shape (nA, 1)
    yA = A[:, 1][:, np.newaxis]  # shape (nA, 1)
    xB = B[:, 0]                # shape (nB,)
    yB = B[:, 1]                # shape (nB,)

    dx = xB - xA  # (nA, nB) differences in x
    dy = yB - yA  # (nA, nB) differences in y

    # Compute slopes, ignoring divisions by zero.
    with np.errstate(divide='ignore', invalid='ignore'):
        slopes = dy / dx

    # Only consider non-vertical pairs.
    m_min = np.min(slopes[dx != 0])
    m_max = np.max(slopes[dx != 0])

    # Compute candidate intercepts for all points in A∪B using both extreme slopes.
    points = np.vstack([A, B])
    candidate_cs_m_min = points[:, 1] - m_min * points[:, 0]
    candidate_cs_m_max = points[:, 1] - m_max * points[:, 0]
    c_min = min(np.min(candidate_cs_m_min), np.min(candidate_cs_m_max))
    c_max = max(np.max(candidate_cs_m_min), np.max(candidate_cs_m_max))

    # For vertical line (x = k), k is between min_x and max_x.
    k_min = min_x
    k_max = max_x

    # Binary variable: 0 for non-vertical, 1 for vertical.
    is_vertical = solver.BoolVar("is_vertical")
    
    # Variables for non-vertical line: y = m*x + c.
    m_var = solver.NumVar(math.floor(m_min), math.ceil(m_max), "m")
    c_var = solver.NumVar(math.floor(c_min), math.ceil(c_max), "c")
    # Variable for vertical line: x = k.
    k_var = solver.NumVar(math.floor(k_min), math.ceil(k_max), "k")

    nA, nB = len(A), len(B)
    
    # For non-vertical mode, classify each point in A and B:
    delta_A = [solver.BoolVar(f"delta_A_{i}") for i in range(nA)]
    above_A = [solver.BoolVar(f"above_A_{i}") for i in range(nA)]
    below_A = [solver.BoolVar(f"below_A_{i}") for i in range(nA)]
    
    delta_B = [solver.BoolVar(f"delta_B_{j}") for j in range(nB)]
    above_B = [solver.BoolVar(f"above_B_{j}") for j in range(nB)]
    below_B = [solver.BoolVar(f"below_B_{j}") for j in range(nB)]
    
    # For vertical mode, we use left/right/on.
    left_A  = [solver.BoolVar(f"left_A_{i}") for i in range(nA)]
    right_A = [solver.BoolVar(f"right_A_{i}") for i in range(nA)]
    on_A    = [solver.BoolVar(f"on_A_{i}") for i in range(nA)]
    
    left_B  = [solver.BoolVar(f"left_B_{j}") for j in range(nB)]
    right_B = [solver.BoolVar(f"right_B_{j}") for j in range(nB)]
    on_B    = [solver.BoolVar(f"on_B_{j}") for j in range(nB)]
    
    # For each point, enforce that exactly one classification holds in each mode.
    for i in range(nA):
        solver.Add(delta_A[i] + above_A[i] + below_A[i] == 1)
        solver.Add(on_A[i] + left_A[i] + right_A[i] == 1)
    for j in range(nB):
        solver.Add(delta_B[j] + above_B[j] + below_B[j] == 1)
        solver.Add(on_B[j] + left_B[j] + right_B[j] == 1)

    # At least one point must lie exactly on the line in each set.
    solver.Add(solver.Sum(delta_A) >= 1 - M * is_vertical)
    solver.Add(solver.Sum(delta_B) >= 1 - M * is_vertical)
    solver.Add(solver.Sum(on_A) >= 1 - M * (1 - is_vertical))
    solver.Add(solver.Sum(on_B) >= 1 - M * (1 - is_vertical))

    # NON-VERTICAL MODE CONSTRAINTS (active when is_vertical==0):
    for i, (x, y) in enumerate(A):
        solver.Add(y - m_var * x - c_var <= M*(1 - delta_A[i]) + M*is_vertical)
        solver.Add(-(y - m_var * x - c_var) <= M*(1 - delta_A[i]) + M*is_vertical)
        solver.Add(y - m_var * x - c_var >= eps - M*(1 - above_A[i]) - M*is_vertical)
        solver.Add(y - m_var * x - c_var <= -eps + M*(1 - below_A[i]) + M*is_vertical)
    for j, (x, y) in enumerate(B):
        solver.Add(y - m_var * x - c_var <= M*(1 - delta_B[j]) + M*is_vertical)
        solver.Add(-(y - m_var * x - c_var) <= M*(1 - delta_B[j]) + M*is_vertical)
        solver.Add(y - m_var * x - c_var >= eps - M*(1 - above_B[j]) - M*is_vertical)
        solver.Add(y - m_var * x - c_var <= -eps + M*(1 - below_B[j]) + M*is_vertical)

    # VERTICAL MODE CONSTRAINTS (active when is_vertical==1):
    for i, (x, y) in enumerate(A):
        # If the point is classified as "on", enforce |x - k| <= eps.
        solver.Add(x - k_var <= eps + M*(1 - on_A[i]) + M*(1 - is_vertical))
        solver.Add(-(x - k_var) <= eps + M*(1 - on_A[i]) + M*(1 - is_vertical))
        # If the point is to the left, enforce x - k <= -eps.
        solver.Add(x - k_var <= -eps + M*(1 - left_A[i]) + M*(1 - is_vertical))
        # If the point is to the right, enforce x - k >= eps.
        solver.Add(x - k_var >= eps - M*(1 - right_A[i]) - M*(1 - is_vertical))
    for j, (x, y) in enumerate(B):
        solver.Add(x - k_var <= eps + M*(1 - on_B[j]) + M*(1 - is_vertical))
        solver.Add(-(x - k_var) <= eps + M*(1 - on_B[j]) + M*(1 - is_vertical))
        solver.Add(x - k_var <= -eps + M*(1 - left_B[j]) + M*(1 - is_vertical))
        solver.Add(x - k_var >= eps - M*(1 - right_B[j]) - M*(1 - is_vertical))

    
    # GLOBAL CLASSIFICATION CONSTRAINTS:
    solver.Add(solver.Sum(above_A) <= (nA // 2) + M * is_vertical)
    solver.Add(solver.Sum(below_A) <= (nA // 2) + M * is_vertical)
    solver.Add(solver.Sum(above_B) <= (nB // 2) + M * is_vertical)
    solver.Add(solver.Sum(below_B) <= (nB // 2) + M * is_vertical)
    solver.Add(solver.Sum(left_A) <= (nA // 2) + M * (1 - is_vertical))
    solver.Add(solver.Sum(right_A) <= (nA // 2) + M * (1 - is_vertical))
    solver.Add(solver.Sum(left_B) <= (nB // 2) + M * (1 - is_vertical))
    solver.Add(solver.Sum(right_B) <= (nB // 2) + M * (1 - is_vertical))

    # Dummy objective (we only care about feasibility).
    objective = solver.Objective()
    objective.SetCoefficient(m_var, 0)
    objective.SetCoefficient(c_var, 0)
    objective.SetCoefficient(k_var, 0)
    objective.SetCoefficient(is_vertical, 0)
    objective.SetMinimization()

    status = solver.Solve()

    if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
        if is_vertical.solution_value() > 0.5:
            return "vertical", k_var.solution_value()
        else:
            return "non-vertical", (m_var.solution_value(), c_var.solution_value())
    else:
        return None


def generate_random_points(n, lower=-10, upper=10):
    """Generate n random points with coordinates in [lower, upper]."""
    points = []
    for _ in range(n):
        x = random.uniform(lower, upper)
        y = random.uniform(lower, upper)
        # Round the values for nicer printing
        points.append((round(x, 2), round(y, 2)))
    return points


def generate_random_points(n, lower=-10, upper=10):
    """Generate n random points with coordinates in [lower, upper]."""
    points = [
        (round(random.uniform(lower, upper), 2), round(random.uniform(lower, upper), 2))
        for _ in range(n)
    ]
    return points


if __name__ == "__main__":
    n_A = 100
    n_B = 100
    A = generate_random_points(n_A, lower=-10, upper=10)
    B = generate_random_points(n_B, lower=-10, upper=10)

    result = find_line_through_points_ortools_extended(A, B)
    if result:
        mode, params = result
        if mode == "vertical":
            print(f"Found vertical line: x = {params:.4f}")
        else:
            m_val, c_val = params
            print(f"Found non-vertical line: y = {m_val:.4f} * x + {c_val:.4f}")
            print("Line is ham sandwich cut: ", check_line_not_verbose(m_val, c_val, A, B))
    else:
        print("No feasible line found.")
