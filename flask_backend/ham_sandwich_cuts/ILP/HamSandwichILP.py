import random
import pulp

import sys
import os

# Get the parent directory and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now you can import from the parent directory's Utils folder
from Utils.check_line import check_line_not_verbose

def generate_random_points(n, lower=-10, upper=10):
    """Generate n random points with coordinates in [lower, upper]."""
    points = []
    for _ in range(n):
        x = random.uniform(lower, upper)
        y = random.uniform(lower, upper)
        # Round the values for nicer printing
        points.append((round(x, 2), round(y, 2)))
    return points


def find_line_through_points_with_dual_intersection(A, B, M=1e5, eps=1e-4):
    """
    Finds a line y = m*x + c satisfying the ham-sandwich constraints and,
    in addition, forces the dual point (m,c) to lie on an intersection
    between a dual line from set A and a dual line from set B.
    
    Parameters:
      A, B: lists of tuples (x, y)
      M: big-M constant.
      eps: tolerance for strict inequalities.
      
    Returns:
      (m, c) if a feasible line is found; else None.
    """
    # Create the MILP model.
    prob = pulp.LpProblem("Find_Line", pulp.LpMinimize)
    
    # Decision variables for the line.
    m_var = pulp.LpVariable("m", lowBound=-1000, upBound=1000, cat="Continuous")
    c_var = pulp.LpVariable("c", lowBound=-1000, upBound=1000, cat="Continuous")
    
    # --- Classification variables for each point (as before) ---
    # For set A:
    delta_A = [pulp.LpVariable(f"delta_A_{i}", cat="Binary") for i in range(len(A))]
    above_A = [pulp.LpVariable(f"above_A_{i}", cat="Binary") for i in range(len(A))]
    below_A = [pulp.LpVariable(f"below_A_{i}", cat="Binary") for i in range(len(A))]
    
    # For set B:
    delta_B = [pulp.LpVariable(f"delta_B_{j}", cat="Binary") for j in range(len(B))]
    above_B = [pulp.LpVariable(f"above_B_{j}", cat="Binary") for j in range(len(B))]
    below_B = [pulp.LpVariable(f"below_B_{j}", cat="Binary") for j in range(len(B))]
    
    # Dummy objective.
    prob += 0, "DummyObjective"
    
    # At least one point from each set must lie exactly on the line.
    prob += pulp.lpSum(delta_A) >= 1, "At_least_one_on_line_A"
    prob += pulp.lpSum(delta_B) >= 1, "At_least_one_on_line_B"
    
    # Classification constraints for set A.
    for i, (x, y) in enumerate(A):
        prob += delta_A[i] + above_A[i] + below_A[i] == 1, f"Classification_A_{i}"
        prob += (y - m_var*x - c_var) <= M*(1 - delta_A[i]), f"A_on_upper_{i}"
        prob += -(y - m_var*x - c_var) <= M*(1 - delta_A[i]), f"A_on_lower_{i}"
        prob += (y - m_var*x - c_var) >= eps - M*(1 - above_A[i]), f"A_above_{i}"
        prob += (y - m_var*x - c_var) <= -eps + M*(1 - below_A[i]), f"A_below_{i}"
    
    # Classification constraints for set B.
    for j, (x, y) in enumerate(B):
        prob += delta_B[j] + above_B[j] + below_B[j] == 1, f"Classification_B_{j}"
        prob += (y - m_var*x - c_var) <= M*(1 - delta_B[j]), f"B_on_upper_{j}"
        prob += -(y - m_var*x - c_var) <= M*(1 - delta_B[j]), f"B_on_lower_{j}"
        prob += (y - m_var*x - c_var) >= eps - M*(1 - above_B[j]), f"B_above_{j}"
        prob += (y - m_var*x - c_var) <= -eps + M*(1 - below_B[j]), f"B_below_{j}"
    
    # Global constraints: at most half the points in each set are strictly above/below.
    prob += pulp.lpSum(above_A) <= len(A) // 2, "Max_above_A"
    prob += pulp.lpSum(below_A) <= len(A) // 2, "Max_below_A"
    prob += pulp.lpSum(above_B) <= len(B) // 2, "Max_above_B"
    prob += pulp.lpSum(below_B) <= len(B) // 2, "Max_below_B"
    
    # --- Additional dual-intersection constraints ---
    # Introduce binary variables gamma_{ij} for each pair (i in A, j in B).
    gamma = {}
    for i in range(len(A)):
        for j in range(len(B)):
            gamma[(i,j)] = pulp.LpVariable(f"gamma_{i}_{j}", cat="Binary")
    
    # Enforce that exactly one pair (i,j) is chosen.
    prob += pulp.lpSum(gamma[(i,j)] for i in range(len(A)) for j in range(len(B))) == 1, "Choose_one_intersection"
    
    # For each candidate pair (i,j), if gamma_{ij} = 1, then enforce:
    #   c = y_i - m*x_i  and  c = y_j - m*x_j.
    # We add big-M constraints for each.
    for i, (x_i, y_i) in enumerate(A):
        for j, (x_j, y_j) in enumerate(B):
            prob += c_var - (y_i - m_var*x_i) <= M*(1 - gamma[(i,j)]), f"DualA_upper_{i}_{j}"
            prob += -(c_var - (y_i - m_var*x_i)) <= M*(1 - gamma[(i,j)]), f"DualA_lower_{i}_{j}"
            prob += c_var - (y_j - m_var*x_j) <= M*(1 - gamma[(i,j)]), f"DualB_upper_{i}_{j}"
            prob += -(c_var - (y_j - m_var*x_j)) <= M*(1 - gamma[(i,j)]), f"DualB_lower_{i}_{j}"
    
    # Suppress solver logging.
    solver = pulp.PULP_CBC_CMD(msg=False, options=['-firstFeasible'])

    prob.solve(solver)
    
    if pulp.LpStatus[prob.status] == "Optimal":
        return pulp.value(m_var), pulp.value(c_var)
    else:
        return None


def find_line_through_points_ILP(A, B, M=1e5, eps=1e-4):
    """
    Finds a ham sandwich cut line that separates two point sets (A and B) by
    choosing between a non-vertical line (y = m*x + c) or a vertical line (x = k).
    At least one point from each set must lie exactly on the chosen line.
    In each set, at most half of the points lie strictly on either side.
    
    Returns:
      ("vertical", k) if a vertical line is chosen,
      ("non-vertical", (m, c)) if a non-vertical line is chosen,
      or None if no feasible solution is found.
    """
    # Create the MILP model.
    prob = pulp.LpProblem("Find_Line", pulp.LpMinimize)
    
    # Binary variable: 0 => non-vertical, 1 => vertical.
    is_vertical = pulp.LpVariable("is_vertical", cat="Binary")
    
    # Variables for non-vertical line: y = m*x + c.
    m = pulp.LpVariable("m", lowBound=-1000, upBound=1000, cat="Continuous")
    c = pulp.LpVariable("c", lowBound=-1000, upBound=1000, cat="Continuous")
    
    # Variable for vertical line: x = k.
    k = pulp.LpVariable("k", lowBound=-1000, upBound=1000, cat="Continuous")
    
    nA = len(A)
    nB = len(B)
    
    # For non-vertical mode: classification for each point:
    # delta: point is exactly on the line.
    # above: point is strictly above the line.
    # below: point is strictly below the line.
    delta_A = [pulp.LpVariable(f"delta_A_{i}", cat="Binary") for i in range(nA)]
    above_A = [pulp.LpVariable(f"above_A_{i}", cat="Binary") for i in range(nA)]
    below_A = [pulp.LpVariable(f"below_A_{i}", cat="Binary") for i in range(nA)]
    
    delta_B = [pulp.LpVariable(f"delta_B_{j}", cat="Binary") for j in range(nB)]
    above_B = [pulp.LpVariable(f"above_B_{j}", cat="Binary") for j in range(nB)]
    below_B = [pulp.LpVariable(f"below_B_{j}", cat="Binary") for j in range(nB)]
    
    # For vertical mode: classification for each point:
    # on: point lies exactly on x=k.
    # left: point is strictly to the left.
    # right: point is strictly to the right.
    on_A = [pulp.LpVariable(f"on_A_{i}", cat="Binary") for i in range(nA)]
    left_A = [pulp.LpVariable(f"left_A_{i}", cat="Binary") for i in range(nA)]
    right_A = [pulp.LpVariable(f"right_A_{i}", cat="Binary") for i in range(nA)]
    
    on_B = [pulp.LpVariable(f"on_B_{j}", cat="Binary") for j in range(nB)]
    left_B = [pulp.LpVariable(f"left_B_{j}", cat="Binary") for j in range(nB)]
    right_B = [pulp.LpVariable(f"right_B_{j}", cat="Binary") for j in range(nB)]
    
    # Dummy objective – we only care about feasibility.
    prob += 0, "DummyObjective"
    
    # At least one point in each set must lie exactly on the line.
    # For non-vertical mode, enforce at least one "delta" per set (inactive when vertical).
    prob += pulp.lpSum(delta_A) >= 1 - M * is_vertical, "At_least_one_nonvert_A"
    prob += pulp.lpSum(delta_B) >= 1 - M * is_vertical, "At_least_one_nonvert_B"
    # For vertical mode, enforce at least one "on" per set (inactive when non-vertical).
    prob += pulp.lpSum(on_A) >= 1 - M * (1 - is_vertical), "At_least_one_vert_A"
    prob += pulp.lpSum(on_B) >= 1 - M * (1 - is_vertical), "At_least_one_vert_B"
    
    # For each point in set A:
    for i, (x, y) in enumerate(A):
        # Non-vertical mode: exactly one classification.
        prob += delta_A[i] + above_A[i] + below_A[i] == 1, f"Nonvert_class_A_{i}"
        # Vertical mode: exactly one classification.
        prob += on_A[i] + left_A[i] + right_A[i] == 1, f"Vert_class_A_{i}"
        
        # NON-VERTICAL MODE CONSTRAINTS (active when is_vertical==0)
        # If delta_A[i]==1, force y = m*x + c.
        prob += (y - m * x - c) <= M * (1 - delta_A[i]) + M * is_vertical, f"A_on_upper_{i}"
        prob += -(y - m * x - c) <= M * (1 - delta_A[i]) + M * is_vertical, f"A_on_lower_{i}"
        # If above_A[i]==1, force y - m*x - c >= eps.
        prob += (y - m * x - c) >= eps - M * (1 - above_A[i]) - M * is_vertical, f"A_above_{i}"
        # If below_A[i]==1, force y - m*x - c <= -eps.
        prob += (y - m * x - c) <= -eps + M * (1 - below_A[i]) + M * is_vertical, f"A_below_{i}"
        
        # VERTICAL MODE CONSTRAINTS (active when is_vertical==1)
        # If on_A[i]==1, force x = k.
        prob += (x - k) <= M * (1 - on_A[i]) + M * (1 - is_vertical), f"A_on_vert_upper_{i}"
        prob += -(x - k) <= M * (1 - on_A[i]) + M * (1 - is_vertical), f"A_on_vert_lower_{i}"
        # If left_A[i]==1, force x < k (x - k <= -eps).
        prob += (x - k) <= -eps + M * (1 - left_A[i]) + M * (1 - is_vertical), f"A_left_{i}"
        # If right_A[i]==1, force x > k (x - k >= eps).
        prob += (x - k) >= eps - M * (1 - right_A[i]) - M * (1 - is_vertical), f"A_right_{i}"
    
    # For each point in set B:
    for j, (x, y) in enumerate(B):
        prob += delta_B[j] + above_B[j] + below_B[j] == 1, f"Nonvert_class_B_{j}"
        prob += on_B[j] + left_B[j] + right_B[j] == 1, f"Vert_class_B_{j}"
        
        # NON-VERTICAL MODE CONSTRAINTS
        prob += (y - m * x - c) <= M * (1 - delta_B[j]) + M * is_vertical, f"B_on_upper_{j}"
        prob += -(y - m * x - c) <= M * (1 - delta_B[j]) + M * is_vertical, f"B_on_lower_{j}"
        prob += (y - m * x - c) >= eps - M * (1 - above_B[j]) - M * is_vertical, f"B_above_{j}"
        prob += (y - m * x - c) <= -eps + M * (1 - below_B[j]) + M * is_vertical, f"B_below_{j}"
        
        # VERTICAL MODE CONSTRAINTS
        prob += (x - k) <= M * (1 - on_B[j]) + M * (1 - is_vertical), f"B_on_vert_upper_{j}"
        prob += -(x - k) <= M * (1 - on_B[j]) + M * (1 - is_vertical), f"B_on_vert_lower_{j}"
        prob += (x - k) <= -eps + M * (1 - left_B[j]) + M * (1 - is_vertical), f"B_left_{j}"
        prob += (x - k) >= eps - M * (1 - right_B[j]) - M * (1 - is_vertical), f"B_right_{j}"
    
    # Global constraints: at most half of the points in each set are strictly on one side.
    max_nonvert_A = nA // 2
    max_nonvert_B = nB // 2
    max_vert_A = nA // 2
    max_vert_B = nB // 2
    
    # Non-vertical: limits on strictly above and below.
    prob += pulp.lpSum(above_A) <= max_nonvert_A + M * is_vertical, "Max_above_A"
    prob += pulp.lpSum(below_A) <= max_nonvert_A + M * is_vertical, "Max_below_A"
    prob += pulp.lpSum(above_B) <= max_nonvert_B + M * is_vertical, "Max_above_B"
    prob += pulp.lpSum(below_B) <= max_nonvert_B + M * is_vertical, "Max_below_B"
    
    # Vertical: limits on strictly left and right.
    prob += pulp.lpSum(left_A) <= max_vert_A + M * (1 - is_vertical), "Max_left_A"
    prob += pulp.lpSum(right_A) <= max_vert_A + M * (1 - is_vertical), "Max_right_A"
    prob += pulp.lpSum(left_B) <= max_vert_B + M * (1 - is_vertical), "Max_left_B"
    prob += pulp.lpSum(right_B) <= max_vert_B + M * (1 - is_vertical), "Max_right_B"
    
    # Use CBC solver with option to return the first feasible solution.
    solver = pulp.PULP_CBC_CMD(msg=False, options=['-firstFeasible'])
    prob.solve(solver)
    
    # Return the result depending on the mode.
    if pulp.LpStatus[prob.status] in ["Optimal", "Feasible"]:
        if pulp.value(is_vertical) > 0.5:
            # Vertical line found.
            return "vertical", pulp.value(k)
        else:
            return "non-vertical", (pulp.value(m), pulp.value(c))
    else:
        return None




if __name__ == "__main__":
    # Define two sets of points.
    n_A = 20
    n_B = 10
    A = generate_random_points(n_A, lower=-10, upper=10)
    B = generate_random_points(n_B, lower=-10, upper=10)

    # # Test case for vertical line 
    # A = [(1, 2), (2, 3), (3, 5)]
    # B = [(1, 1), (2, 2), (3, 2)]
    
    result = find_line_through_points_ILP(A, B)
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