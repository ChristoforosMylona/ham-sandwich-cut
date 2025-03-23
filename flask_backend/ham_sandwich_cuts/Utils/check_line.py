def check_line(m, c, A, B, eps=1e-4):
    """
    Given a line y = m*x + c and two sets of points A and B,
    prints the number of points above, on, and below the line for each set.
    Also checks that at most half of the points in each set are above and
    at most half are below the line.

    Parameters:
        m, c: Line parameters.
        A, B: Lists of points, where each point is a tuple (x, y).
        eps: Tolerance to determine if a point is exactly on the line.
    """
    
    def count_points(points):
        above = 0
        on = 0
        below = 0
        for x, y in points:
            diff = y - (m * x + c)
            if diff > eps:
                above += 1
            elif diff < -eps:
                below += 1
            else:
                on += 1
        return above, on, below

    # Count for set A.
    above_A, on_A, below_A = count_points(A)
    n_A = len(A)
    half_A = n_A // 2  # maximum allowed above or below
    cond_A = (above_A <= half_A, below_A <= half_A)

    # Count for set B.
    above_B, on_B, below_B = count_points(B)
    n_B = len(B)
    half_B = n_B // 2  # maximum allowed above or below
    cond_B = (above_B <= half_B, below_B <= half_B)

    # Print results for set A.
    print("Set A:")
    print(f"  Total points: {n_A}")
    print(f"  Above: {above_A}")
    print(f"  On:    {on_A}")
    print(f"  Below: {below_A}")
    print(f"  Condition: at most {half_A} points above: {'satisfied' if cond_A[0] else 'not satisfied'}, "
          f"at most {half_A} points below: {'satisfied' if cond_A[1] else 'not satisfied'}\n")

    # Print results for set B.
    print("Set B:")
    print(f"  Total points: {n_B}")
    print(f"  Above: {above_B}")
    print(f"  On:    {on_B}")
    print(f"  Below: {below_B}")
    print(f"  Condition: at most {half_B} points above: {'satisfied' if cond_B[0] else 'not satisfied'}, "
          f"at most {half_B} points below: {'satisfied' if cond_B[1] else 'not satisfied'}\n")

    # Optionally return a summary of the conditions
    return {
        "A": {"above": above_A, "on": on_A, "below": below_A, "max_allowed": half_A,
              "above_ok": cond_A[0], "below_ok": cond_A[1]},
        "B": {"above": above_B, "on": on_B, "below": below_B, "max_allowed": half_B,
              "above_ok": cond_B[0], "below_ok": cond_B[1]}
    }



def check_line_not_verbose(m, c, A, B, eps=1e-4):
    def count(points):
        above = below = 0
        for x, y in points:
            diff = y - (m * x + c)
            if diff > eps:
                above += 1
            elif diff < -eps:
                below += 1
        return above, below

    above_A, below_A = count(A)
    above_B, below_B = count(B)

    return (above_A <= len(A) // 2 and below_A <= len(A) // 2 and
            above_B <= len(B) // 2 and below_B <= len(B) // 2)
