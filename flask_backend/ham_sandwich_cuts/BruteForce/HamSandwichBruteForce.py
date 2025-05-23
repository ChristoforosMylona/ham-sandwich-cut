import numpy as np
import itertools


def find_line_through_points_with_dual_intersection_brute_no_numpy(A, B, eps=1e-4):
    """
    Brute force version to find a line satisfying:
    1. It passes through at least one point from A and one from B.
    2. It satisfies the ham-sandwich constraints.

    Parameters:
      A, B: lists of tuples (x, y) representing points.
      eps: small tolerance to prevent strict inequalities.

    Returns:
      ("vertical", k) if a vertical line x = k is found.
      ("non-vertical", m, c) if a non-vertical line y = m*x + c is found.
      None if no valid line is found.
    """

    for (x1, y1), (x2, y2) in itertools.product(A, B):
        if abs(x1 - x2) < eps:  # Handle vertical line case
            median_x = (x1 + x2) / 2  # Midpoint as dividing line

            left_A = sum(1 for x, _ in A if x < median_x - eps)
            right_A = sum(1 for x, _ in A if x > median_x + eps)

            left_B = sum(1 for x, _ in B if x < median_x - eps)
            right_B = sum(1 for x, _ in B if x > median_x + eps)

            if (
                left_A <= len(A) // 2
                and right_A <= len(A) // 2
                and left_B <= len(B) // 2
                and right_B <= len(B) // 2
            ):
                return "vertical", median_x  # Vertical line at x = median_x

        else:  # Non-vertical line case
            m = (y2 - y1) / (x2 - x1)
            c = y1 - m * x1

            above_A = sum(1 for x, y in A if y - (m * x + c) > eps)
            below_A = sum(1 for x, y in A if y - (m * x + c) < -eps)

            above_B = sum(1 for x, y in B if y - (m * x + c) > eps)
            below_B = sum(1 for x, y in B if y - (m * x + c) < -eps)

            if (
                above_A <= len(A) // 2
                and below_A <= len(A) // 2
                and above_B <= len(B) // 2
                and below_B <= len(B) // 2
            ):
                return "non-vertical", (m, c)  # Found a valid line

    return None  # No valid line found


def find_line_through_points_with_dual_intersection_brute(A, B, eps=1e-4):
    """
    Optimized version using NumPy to find a line satisfying:
    1. It passes through at least one point from A and one from B.
    2. It satisfies the ham-sandwich constraints.

    Parameters:
      A, B: lists of tuples (x, y) representing points.
      eps: small tolerance to prevent strict inequalities.

    Returns:
      ("vertical", k) if a vertical line x = k is found.
      ("non-vertical", m, c) if a non-vertical line y = m*x + c is found.
      None if no valid line is found.
    """
    A = np.array(A)
    B = np.array(B)

    # Precompute the lengths and half-lengths of A and B
    len_A = len(A)
    len_B = len(B)
    half_len_A = len_A // 2
    half_len_B = len_B // 2

    for (x1, y1), (x2, y2) in itertools.product(A, B):
        if abs(x1 - x2) < eps:  # Handle vertical line case
            median_x = (x1 + x2) / 2  # Midpoint as dividing line

            # Use NumPy's boolean indexing for efficient counting
            left_A = np.sum(A[:, 0] < median_x - eps)
            right_A = len_A - left_A - np.sum(A[:, 0] <= median_x + eps)

            left_B = np.sum(B[:, 0] < median_x - eps)
            right_B = len_B - left_B - np.sum(B[:, 0] <= median_x + eps)

            if (
                left_A <= half_len_A
                and right_A <= half_len_A
                and left_B <= half_len_B
                and right_B <= half_len_B
            ):
                return "vertical", median_x  # Vertical line at x = median_x

        else:  # Non-vertical line case
            m = (y2 - y1) / (x2 - x1)
            c = y1 - m * x1

            # Precompute the line equation for all points
            line_A = A[:, 1] - (m * A[:, 0] + c)
            line_B = B[:, 1] - (m * B[:, 0] + c)

            # Vectorized above/below comparisons
            above_A = np.sum(line_A > eps)
            below_A = np.sum(line_A < -eps)

            above_B = np.sum(line_B > eps)
            below_B = np.sum(line_B < -eps)

            if (
                above_A <= half_len_A
                and below_A <= half_len_A
                and above_B <= half_len_B
                and below_B <= half_len_B
            ):
                return "non-vertical", (m, c)  # Found a valid line

    return None  # No valid line found
