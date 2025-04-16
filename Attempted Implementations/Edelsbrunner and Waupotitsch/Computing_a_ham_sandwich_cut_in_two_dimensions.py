from matplotlib import pyplot as plt
import numpy as np
from typing import List, Tuple
import random
import math
from icecream import ic
from helpers import (
    Position,
    Correct_Halfplane,
    Point,
    Line,
    Pair,
    split_points_by_halfplane,
    test_against_a_line,
    find_bisecting_line,
    plot_points_and_line,
    plot_step_4_lines,
    test_against_vertical_line,
)

ic.configureOutput(includeContext=False, argToStringFunction=str)
def generate_points(size) -> np.ndarray:
    # Generate 4 points with positive x-values and random y-values
    positive_x_points = np.column_stack(
        (
            np.random.uniform(low=0.1, high=10.0, size=size),  # Positive x-values
            np.random.uniform(low=-10.0, high=10.0, size=size),  # Random y-values
        )
    )

    # Generate 4 points with negative x-values and random y-values
    negative_x_points = np.column_stack(
        (
            np.random.uniform(low=-10.0, high=-0.1, size=size),  # Negative x-values
            np.random.uniform(low=-10.0, high=10.0, size=size),  # Random y-values
        )
    )

    # Concatenate both sets of points
    points = np.vstack((positive_x_points, negative_x_points))

    print(f"Generated Points ({size} with +ve x, {size} with -ve x):")
    print(points)

    return points


def generate_int_points(n) -> np.ndarray:
    # Generate n integer points with both x and y values between -10 and 10
    points = np.column_stack(
        (
            np.random.randint(low=-10, high=11, size=n),  # x-values between -10 and 10
            np.random.randint(low=-10, high=11, size=n),  # y-values between -10 and 10
        )
    )

    # print(f"Generated {n} Integer Points (x, y values between -10 and 10):")
    # print(points)
    points_objects = np.array([Point(x, y) for x, y in points])
    return points_objects


# return the median line of the set of lines
def find_median_line(lines):

    # Sort slopes
    sorted_lines = sorted(lines, key=lambda line: line.slope)
    m = len(sorted_lines)

    # Find the median slope
    if m % 2 == 1:  # Odd number of lines
        median_index = m // 2
    else:  # Even number of lines
        median_index = m // 2 - 1

    median_line = sorted_lines[median_index]

    # Partition the lines into G+ and G-
    # G_plus = [line for line in lines if line.slope >= median_line.slope]
    # G_minus = [line for line in lines if line.slope < median_line.slope]

    G_plus = sorted_lines[median_index + 1 :]
    G_minus = sorted_lines[:median_index]

    if len(G_plus) > 1 and len(G_plus) % 2 == 0:
        G_plus = G_plus[1:]

    if len(G_minus) > 1 and len(G_minus) % 2 == 0:
        G_minus = G_minus[1:]

    return median_line, G_plus, G_minus


def partition(points: List[Point], low: int, high: int, pivot_index: int) -> int:
    pivot_value = points[pivot_index].x
    points[pivot_index], points[high] = (
        points[high],
        points[pivot_index],
    )  # Move pivot to end
    store_index = low
    for i in range(low, high):
        if points[i].x < pivot_value:
            points[store_index], points[i] = points[i], points[store_index]
            store_index += 1
    points[store_index], points[high] = (
        points[high],
        points[store_index],
    )  # Move pivot to its final place
    return store_index


def quickselect(points: List[Point], low: int, high: int, k: int) -> float:
    if low == high:  # If the list contains only one element
        return points[low].x

    pivot_index = random.randint(low, high)
    pivot_index = partition(points, low, high, pivot_index)

    if k == pivot_index:  # The pivot is the k-th smallest element
        return points[k].x
    elif k < pivot_index:
        return quickselect(points, low, pivot_index - 1, k)
    else:
        return quickselect(points, pivot_index + 1, high, k)


def find_vertical_bisector(points: List[Point]) -> float:
    n = len(points)
    if n % 2 == 1:  # If odd, find the median directly
        return quickselect(points, 0, n - 1, n // 2)
    else:  # If even, find the average of the two medians
        left_median = quickselect(points, 0, n - 1, n // 2 - 1)
        right_median = quickselect(points, 0, n - 1, n // 2)
        return (left_median + right_median) / 2


def plot_points_and_bisector(points: List[Point], bisector_x: float) -> None:
    # Extract x and y coordinates for plotting
    x_coords = [point.x for point in points]
    y_coords = [point.y for point in points]

    # Create a scatter plot for the points
    plt.scatter(x_coords, y_coords, color="blue", label="Points")

    # Draw the bisector line
    plt.axvline(
        x=bisector_x,
        color="red",
        linestyle="--",
        label=f"Bisector Line x = {bisector_x}",
    )

    # Adding titles and labels
    plt.title("Points and their Vertical Bisector")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.legend()

    # Show grid
    plt.grid()

    # Separate points left and right of the bisector
    points_left = [point for point in points if point.x < bisector_x]
    points_right = [point for point in points if point.x > bisector_x]

    # Print points on the left and right of the bisector
    print(f"Points to the left of the bisector: {points_left}")
    print(f"Points to the right of the bisector: {points_right}")

    # Show the plot
    plt.show()


def intersects_vertical_line_polygon(v_star, vertices):
    """
    Determine if a vertical line v_star intersects a polygon.

    Args:
        v_star (float): The x-coordinate of the vertical line.
        vertices (list of Point): List of vertices representing the polygon.

    Returns:
        bool: True if v_star intersects the polygon, False otherwise.
    """
    n = len(vertices)
    for i in range(n):
        # Get the current edge's vertices
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n]  # Wrap around to the first vertex

        # Check if the edge is vertical
        if p1.x == p2.x and p1.x == v_star:
            # The edge itself lies on the vertical line
            return True

        # Check if v_star is between p1.x and p2.x
        if (p1.x <= v_star <= p2.x) or (p2.x <= v_star <= p1.x):
            # Calculate the y-coordinate of the intersection
            if p1.x != p2.x:  # Avoid division by zero for vertical edges
                t = (v_star - p1.x) / (p2.x - p1.x)
                y_intersect = p1.y + t * (p2.y - p1.y)

                # Check if the y-coordinate lies within the edge's y-range
                if min(p1.y, p2.y) <= y_intersect <= max(p1.y, p2.y):
                    return True

    # No intersection found
    return False


def count_inversions(arr: List[float]) -> int:
    """Counts the number of inversions in an array using Merge Sort."""
    if len(arr) < 2:
        return 0

    mid = len(arr) // 2
    left = arr[:mid]
    right = arr[mid:]

    inv_count = count_inversions(left) + count_inversions(right)

    # Merge step with inversion count
    i = j = k = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # No inversion
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            inv_count += len(left) - i  # Remaining elements in left are all greater
            j += 1
        k += 1

    # Copy remaining elements
    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1
    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1

    return inv_count


# def count_intersections(points_set1: List[Point], points_set2: List[Point], x_min: float, x_max: float) -> int:
#     """Returns the number of times two sets of points intersect between two vertical lines."""

#     # Filter points within the vertical range
#     filtered1 = sorted([p for p in points_set1 if x_min <= p.x <= x_max], key=lambda p: p.x)
#     filtered2 = sorted([p for p in points_set2 if x_min <= p.x <= x_max], key=lambda p: p.x)

#     if len(filtered1) != len(filtered2):
#         raise ValueError("The two sets must have the same number of points for a meaningful intersection count.")

#     # Extract y-values in the order of x-coordinates
#     y_values1 = [p.y for p in filtered1]
#     y_values2 = [p.y for p in filtered2]

#     # Count inversions in the y-value order (this gives intersection count)
#     return count_inversions(list(zip(y_values1, y_values2)))


def line_intersection(p1: Point, p2: Point, q1: Point, q2: Point) -> Tuple[bool, Point]:
    """Checks if two line segments (p1-p2 and q1-q2) intersect and returns intersection point."""

    # Line equations: y = m1 * x + b1  and  y = m2 * x + b2
    def get_line_coefficients(p1, p2):
        """Returns slope and intercept of the line through points p1 and p2."""
        if p1.x == p2.x:  # Vertical line case
            return None, p1.x  # Special case: vertical line x = c
        slope = (p2.y - p1.y) / (p2.x - p1.x)
        intercept = p1.y - slope * p1.x
        return slope, intercept

    m1, b1 = get_line_coefficients(p1, p2)
    m2, b2 = get_line_coefficients(q1, q2)

    if m1 == m2:  # Parallel or coincident lines (no intersection)
        return False, None

    # Find intersection
    if m1 is None:  # First segment is vertical: x = constant
        x_int = b1
        y_int = m2 * x_int + b2
    elif m2 is None:  # Second segment is vertical
        x_int = b2
        y_int = m1 * x_int + b1
    else:
        x_int = (b2 - b1) / (m1 - m2)
        y_int = m1 * x_int + b1

    # Check if intersection is within both segments' x-ranges
    if min(p1.x, p2.x) <= x_int <= max(p1.x, p2.x) and min(q1.x, q2.x) <= x_int <= max(
        q1.x, q2.x
    ):
        return True, Point(x_int, y_int)

    return False, None


def count_intersections(
    lk1: List[Point], lk2: List[Point], x_min: float, x_max: float
) -> int:
    """Counts the number of times two polylines (lk1 and lk2) intersect between x_min and x_max."""

    intersections = 0

    # Iterate through consecutive points in both sets
    for i in range(len(lk1) - 1):
        for j in range(len(lk2) - 1):
            p1, p2 = lk1[i], lk1[i + 1]
            q1, q2 = lk2[j], lk2[j + 1]

            # Check if the segments overlap in x-range
            if max(p1.x, p2.x) < x_min or min(p1.x, p2.x) > x_max:
                continue  # Skip if completely outside the region
            if max(q1.x, q2.x) < x_min or min(q1.x, q2.x) > x_max:
                continue

            # Find if they intersect
            does_intersect, intersection_point = line_intersection(p1, p2, q1, q2)

            if does_intersect and x_min <= intersection_point.x <= x_max:
                intersections += 1

    return intersections


def find_odd_intersection_index(
    q1m: List[float], lk1: List[Point], lk2: List[Point]
) -> int:
    """Finds index j where lk1 and lk2 intersect an odd number of times between q1m[j] and q1m[j+1]."""

    # Step 1: Sort q1m while keeping track of original indices
    indexed_q1m = sorted(
        enumerate(q1m), key=lambda x: x[1].x
    )  # (original_index, value)
    sorted_q1m = [x[1] for x in indexed_q1m]  # Extract sorted values

    # Step 2: Perform binary search
    left, right = 0, len(sorted_q1m) - 1

    while left < right:
        mid = (left + right) // 2
        x_min, x_max = sorted_q1m[mid], (
            sorted_q1m[mid + 1] if mid + 1 < len(sorted_q1m) else float("inf")
        )

        if count_intersections(lk1, lk2, x_min, x_max) % 2 == 1:
            right = mid  # Move left to find the first odd intersection
        else:
            left = mid + 1

    # Step 3: Handle points at infinity if needed
    if left >= len(sorted_q1m) - 1:
        return len(sorted_q1m) - 1  # Use the last valid index

    # Step 4: Return the original index of q1m[j]
    return indexed_q1m[left][0]


def main_old():

    # IMPORTANT: THIS CURRENTNLY ONLY WORKS WITH ODD NUMBER OF POINTS -> N MUST ODD!!!!!!
    n = 5
    P = math.inf
    points: np.ndarray = generate_int_points(n)
    G = []

    # points_obj = [(10,0), (5,-8), (-10,1), (6,-4), (-6,1), (9,-9)]
    # points = np.array([Point(x, y) for x, y in points_obj])

    for p in points:
        G.append(Line(p.x, -p.y))

    G: List[Line] = sorted(G, key=lambda x: x.slope)
    stop: bool = False

    n1 = n // 2
    n2 = n - n1

    G_shuffled = random.sample(G, len(G))
    G1 = G_shuffled[:n1]  # First n1 elements
    G2 = G_shuffled[n1:]

    k1 = (n1 + 1) / 2
    k2 = (n2 + 1) / 2

    while not stop:
        # TODO: remove this stop once fully implemented
        stop = True

        ###STEP 1###
        # Determine median slope g*
        # slope is floor (m/2) - smallest among all m1 + m2

        # PROBLEM ASSUMTION the paper takes into account 0 indexing??
        median_index = math.floor((n1 + n2) / 2)
        G: List[Line] = G1 + G2
        G: List[Line] = sorted(G, key=lambda x: x.slope)
        g_star = G[median_index]

        # determine G+ and G-

        # PROBLEM? SAYS SHOULD BE floor m/2 smallest line but then takes into account steepness which looks at the ABSOLUTE value of the slope
        # This means that it can be split differently to expected (expects sizes of G_plus and G_minus to be equal or G_plus = G_minus + 1 if n is odd)
        # example:
        # median slope would be: y = 2x + -4
        # G = [y = 0x +1, y = 2x +-4, y = 2x +0, y = 3x +-9, y = 6x +5]
        # G+ = [y = 2x +-4, y = 2x +0, y = 3x +-9, y = 6x +5]
        # G- = [y = 0x +1]
        # ??? Maybe this will never happen because it's always odd number of point, and odd + odd = even ???

        # G_plus = [line for line in G if abs(line.slope) >= abs(g_star.slope)]
        # G_minus = [line for line in G if abs(line.slope) < abs(g_star.slope)]

        G_minus: List[Line] = G[:median_index]
        G_plus: List[Line] = G[median_index:]

        ###STEP 2###
        # Match each line in G+ with an arbitrary line in G-
        # Let M be the intersection points of these lines

        pair_lines = [Pair(l_minus, l_plus) for l_minus, l_plus in zip(G_minus, G_plus)]

        M = [pair.get_intercept() for pair in pair_lines]
        # ic(G, G_plus, G_minus, g_star, pair_lines, M)
        # print(len(G_plus), len(G_minus))
        # print(g_star)
        # print(G)
        # print(G_plus)
        # print(G_minus)
        # print(len(pair_lines))
        # print(len(M))

        ###STEP 3###
        # Determine a vertical line v* that bisects M

        sorted_x_coords_of_M_intercept = [
            point.x for point in sorted(M, key=lambda x: x.x)
        ]
        len_sorted_M = len(sorted_x_coords_of_M_intercept)

        if len_sorted_M % 2 == 1:
            v_star = sorted_x_coords_of_M_intercept[len_sorted_M // 2]
        else:
            v_star = (
                sorted_x_coords_of_M_intercept[len_sorted_M // 2 - 1]
                + sorted_x_coords_of_M_intercept[len_sorted_M // 2]
            ) / 2
        # ic(sorted_x_coords_of_M_intercept, len_sorted_M, v_star, M)

        # Decide wether v* contains an intersection of Lk1(G1) and Lk2(G2) in P -> finished
        # or find the halfplane that has an odd number of these intersections

        # if t (v_star) does not intersect P, then the side with P in it is needed
        # if it does (at the start it does since P is the whole plane) then:
        # Let the lines in Gi intersect t in points q_i_m for 1 <= m <= mi and i=1,2
        # Then the ki-level of Gi intersects t in point qi, with the k largest y-coordinate amongt these points

        # calculate  Lk1(G1) and Lk2(G2)

        # line query parameters
        # test_line = v_star
        # G1 = G1
        # G2 = G2
        # k1 = k1
        # k2 = k2

        # lki is a set of points. It intersects t at the ki-largest of the set of points (lki)

        kg1 = set()
        kg2 = set()

        # ic(G1, G2, M)
        # TODO: Determine if M or Points (probably M though)
        for point in M:
            above_1 = 0
            above_2 = 0
            below_1 = 0
            below_2 = 0
            on_1 = 0
            on_2 = 0

            for line in G1:
                y = line.slope * point.x + line.intercept

                if y > point.y:
                    below_1 += 1
                elif y < point.y:
                    above_1 += 1
                else:
                    on_1 += 1

            for line in G2:
                y = line.slope * point.x + line.intercept

                if y > point.y:
                    below_2 += 1
                elif y < point.y:
                    above_2 += 1
                else:
                    on_2 += 1

            if (below_1 <= k1 - 1) and (above_1 <= len(G1) - k1):
                kg1.add(point)

            if (below_2 <= k2 - 1) and (below_2 <= len(G2) - k2):
                kg2.add(point)

        # Returns: the open half plane v that contains the odd number of intersections
        if P == math.inf or intersects_vertical_line_polygon(v_star=v_star, vertices=P):
            # The test line DOES intersect the polygon
            # find the side of the halfplane which contains an odd number of intesections i
            # Use G1 and G2 NOT G+ and G-

            # set_of_points = P
            # if P == math.inf:
            #     set_of_points = points

            # Find the k level:
            # Optimize this

            q1 = [line.intersection_with_vertical_line(v_star) for line in G1]
            q2 = [line.intersection_with_vertical_line(v_star) for line in G2]

            # TODO: Optimise with numpy partition

            q1.sort(key=lambda p: p.y)
            q2.sort(key=lambda p: p.y)

            # account for 0 indexing
            lk1_intercept = q1[int(k1 - 1)]
            lk2_intercept = q2[int(k2 - 1)]

            # ic(k1, k2)
            # ic(lk1_intercept, lk2_intercept)
            # ic(q1)
            # ic(q2)
            # ic(v_star)
            # ic(points)

            if math.isclose(
                lk1_intercept.y, lk2_intercept.y
            ):  # x value is always the same as test line is vertical, so no need to test .x
                print("\n\n\nFINISHED!!!!\n\n\n")
                ic(lk1_intercept, lk2_intercept)
                ic(G)
                ic(points, G, G1, G2, v_star, M)
                print("\n\n\nFINISHED!!!!\n\n\n")
                return

            # Determine above
            # above is true if the leftmost point of lkG1 in P lies above LkG2, false otherwise

            # print(lk2_intercept)

            # ic(on_1, on_2, above_1, above_2, below_1, below_2)

            # ic(kg1, kg2)
            # decide whether the the leftmost point of kg1 in P lies above

            # find leftmost points for kg1 and kg2
            leftmost_kg1 = min(kg1, key=lambda p: p.x)
            leftmost_kg2 = min(kg2, key=lambda p: p.x)

            above = leftmost_kg1.y > leftmost_kg2.y

            if lk1_intercept.y > lk2_intercept.y:
                v_star_correct_halfplane = Correct_Halfplane.LEFT
                if above:
                    v_star_correct_halfplane = Correct_Halfplane.RIGHT
            elif lk1_intercept.y < lk2_intercept.y:
                v_star_correct_halfplane = Correct_Halfplane.RIGHT
                if above:
                    v_star_correct_halfplane = Correct_Halfplane.LEFT

        else:
            # The vertical test line does not intersect the polygon
            v_star_correct_halfplane = Correct_Halfplane.RIGHT

            if points[0].x < v_star:
                v_star_correct_halfplane = Correct_Halfplane.LEFT

        ### STEP 4 ###
        # Determine a line parallel to g* (median slope line) that bisects the set of points M outside of V
        # ic(g_star, M)

        # Find points in M not outside of v

        def points_not_in_halfplane(
            v_star: float, v_star_correct_halfplane: Correct_Halfplane, M: List[Point]
        ) -> List[Point]:
            if v_star_correct_halfplane == Correct_Halfplane.FINISHED:
                return []  # No open half-plane, so no points are outside.

            if v_star_correct_halfplane == Correct_Halfplane.LEFT:
                return [
                    p for p in M if p.x >= v_star
                ]  # Outside the open half-plane (x < v_star)

            if v_star_correct_halfplane == Correct_Halfplane.RIGHT:
                return [
                    p for p in M if p.x <= v_star
                ]  # Outside the open half-plane (x > v_star)

            return []  # Should never reach this point

        M_outside_v = points_not_in_halfplane(
            v_star=v_star, v_star_correct_halfplane=v_star_correct_halfplane, M=M
        )

        def bisecting_parallel_line(g_star: Line, M_outside_v: list) -> Line:
            if not M_outside_v:
                return None  # No points to bisect

            # Compute perpendicular distances
            distances = [g_star.perpendicular_distance(p) for p in M_outside_v]

            # Sort distances and find median
            distances.sort()
            median_distance = distances[len(distances) // 2]  # Median distance

            # Compute new intercept using line equation shift
            shift = median_distance * np.sqrt(1 + g_star.slope**2)

            # Choose whether to shift up or down based on the sign of distances
            if len(distances) % 2 == 0:
                shift = (
                    distances[len(distances) // 2 - 1] + distances[len(distances) // 2]
                ) / 2  # Average if even

            new_intercept = g_star.intercept + shift  # Adjust the y-intercept

            return Line(g_star.slope, new_intercept)

        bisecting_line = bisecting_parallel_line(g_star=g_star, M_outside_v=M_outside_v)

        ic(bisecting_line, M_outside_v, g_star, G1, G2)

        # Find q1m for all intersections of G1 with the bisecting line

        q1m = [line.intersection(bisecting_line) for line in G1]

        # ic (q1m)

        try:
            w_prime, w_d_prime = find_odd_intersection_index(q1m=q1m, lk1=kg1, lk2=kg2)
            ic(w_prime, w_d_prime, len(q1m), q1m)
        except Exception as e:
            stop=False
            # IMPORTANT: THIS CURRENTNLY ONLY WORKS WITH ODD NUMBER OF POINTS -> N MUST ODD!!!!!!
            n = 6
            P = math.inf
            points: np.ndarray = generate_int_points(n)
            G = []

            # points_obj = [(10,0), (5,-8), (-10,1), (6,-4), (-6,1), (9,-9)]
            # points = np.array([Point(x, y) for x, y in points_obj])

            for p in points:
                G.append(Line(p.x, -p.y))

            G: List[Line] = sorted(G, key=lambda x: x.slope)
            stop: bool = False

            n1 = n // 2
            n2 = n - n1

            G_shuffled = random.sample(G, len(G))
            G1 = G_shuffled[:n1]  # First n1 elements
            G2 = G_shuffled[n1:]

            k1 = (n1 + 1) / 2
            k2 = (n2 + 1) / 2
            
        
        


def main_temp():
    n = 5
    points = generate_points(size=n)

    lines = []
    for p in points:
        lines.append(Line(p[0], -p[1]))

    # print()
    # print("lines: ", lines)

    stop = False

    # initial k_i value is (n_i + 1)/2 for i=1,2 (for G1 and G2)
    # ???? if n_i is even, we must delete an arbitrary line from G_i ????
    P = points

    while not stop:
        # median_line, G_plus, G_minus = find_median_line(lines)

        
        median_index = math.floor(len(lines) / 2)
        G: List[Line] = sorted(lines, key=lambda x: x.slope)
        median_line = G[median_index]

        # determine G+ and G-

        # PROBLEM? SAYS SHOULD BE floor m/2 smallest line but then takes into account steepness which looks at the ABSOLUTE value of the slope
        # This means that it can be split differently to expected (expects sizes of G_plus and G_minus to be equal or G_plus = G_minus + 1 if n is odd)
        # example:
        # median slope would be: y = 2x + -4
        # G = [y = 0x +1, y = 2x +-4, y = 2x +0, y = 3x +-9, y = 6x +5]
        # G+ = [y = 2x +-4, y = 2x +0, y = 3x +-9, y = 6x +5]
        # G- = [y = 0x +1]

        # G_plus = [line for line in G if abs(line.slope) >= abs(g_star.slope)]
        # G_minus = [line for line in G if abs(line.slope) < abs(g_star.slope)]

        G_minus: List[Line] = G[:median_index]
        G_plus: List[Line] = G[median_index:]
        
        ic(G_plus, G_minus)
        # print()
        # print("median line: ", median_line)
        # print()
        # print("G+: ", G_plus, "\tlength: ", len(G_plus))
        # print()
        # print("G-: ", G_minus, "\tlenght: ", len(G_minus))
        # print()

        matches: List[Pair] = []
        for l1, l2 in zip(G_plus, G_minus):
            matches.append(Pair(l1, l2))

        intersection_points: List[Point] = [m.get_intercept() for m in matches]

        # print("\nmatches", matches, end="\n\n")

        bisector = find_vertical_bisector(intersection_points)
        # print("bisector:", bisector, end="\n")
        # plot_points_and_bisector(intersection_points, bisector)
        # print("P:", P, end="\n\n")

        # Find the open halfplane bounded by v*

        ## TODO replace k values to be calculate before loop and at end of step 4
        halfplane_result_v = test_against_a_line(
            P=P,
            G_minus=G_minus,
            G_plus=G_plus,
            k_minus=(len(G_minus) + 1) / 2,
            k_plus=(len(G_plus) + 1) / 2,
            test_line=Line(0, bisector),
            test_line_vertical=True,
        )

        if halfplane_result_v == Correct_Halfplane.FINISHED:
            stop = True
            print("\n\n\nFINISHED\n\n\n")
            continue

        # TODO: if not done with vertical test? -> Determine a line parallel to median_line that bisects the set of points in intersection_points outside of the open halfplane returned that contains the odd number of intersections

        print(halfplane_result_v)
        print()

        if type(halfplane_result_v == type(Correct_Halfplane.FINISHED)):

            points_in_halfplane, points_outside_halfplane = split_points_by_halfplane(
                bisector, halfplane_result_v, intersection_points
            )
            # print("points outside halfplane", points_outside_halfplane)
            # print()

            bisecting_line = find_bisecting_line(median_line, points_outside_halfplane)
            # print("bisecting line: ", bisecting_line)
            # print()

            # plot_points_and_line(points_outside_halfplane, bisecting_line)

            # Decide if the line contains an intersection of Lk1(G1) and Lk2(G2) in P (finished)
            # or determine the open halfplane (w) bounded by the parrallel line which there are an odd number of intersection points contained in v (the open half plane returned by test_against_line vertical = true) (run test_against_line; vertical = false)
            # This yields two restricting halfplanes w' and w'' bounded by vertical lines

            ## TODO replace k values to be calculate before loop and at end of step 4
            halfplane_result_w = test_against_a_line(
                P=P,
                G_plus=G_plus,
                G_minus=G_minus,
                k_minus=(len(G_minus) + 1) / 2,
                k_plus=(len(G_plus) + 1) / 2,
                test_line=bisecting_line,
                test_line_vertical=False,
            )

            # print("halfplane result w: ", halfplane_result_w)

        else:
            raise (
                TypeError,
                f"Expected halfplane result of type: {type(Correct_Halfplane.FINISHED)}, got {type(halfplane_result_v)} instead",
            )

        # TODO: Define P' = P (intersection) halfplane bounded by v*  (intersection) w  (intersection) w'  (intersection)  w''
        #  Let all lines in Gi contain all lines that intersect:  halfplane bounded by v*  (intersection) w  (intersection) w'  (intersection)  w''
        # if w* bounds w from below k' = k, else k' = k - card(Gi) + card(Gi')

        # Needed variables to find intersection and what they are:
        # P   -> set of Points (dual lines)
        # v   -> The open half plane bounded by v* (vertical line in  step 2) that contains an odd number of intersections between L_k1(G1) and L_k2(G2) ->  = bisector
        # w   -> The open half plane bounded by w* (line parallel to g* -> line with median slope) that contains an odd number of intersection points bounded in v -> = bisecting_line ?
        # w'  -> vertical line -> = halfpane_result_w[0]
        # w'' -> vertical line -> = halfpane_result_w[1]

        # To decide if w* bounds w from above or below -> Lk1(G1) exists either only above or only below the test line t

        w_prime, w_d_prime = halfplane_result_w[0], halfplane_result_w[1]
        print(
            "step 4 needed planes/lines:",
            bisector,
            halfplane_result_v,
            bisecting_line,
            w_prime,
            w_d_prime,
        )
        plot_step_4_lines(
            v=bisector,
            w=bisecting_line,
            w_prime=w_prime,
            w_double_prime=w_d_prime,
            P=lines,
        )
        if w_prime != 0 and w_d_prime != 0:
            plot_points_and_line([Point(p[0], p[1]) for p in P], bisecting_line)
            stop = True
        # P
        else:
            # TODO: REMOVE THIS ENTIRE ELSE CONDITION ONCE STEP 4 DONE CORRECTLY
            points = generate_points(size=n)

            lines = []
            for p in points:
                lines.append(Line(p[0], -p[1]))

            print()
            print(lines)

            stop = False

            # initial k_i value is (n_i + 1)/2 for i=1,2 (for G1 and G2)
            # ???? if n_i is even, we must delete an arbitrary line from G_i ????
            P = points

        # stop = True


# if __name__ == "__main__":
#     main_temp()


# Determine k_i

# k-level(G) = a(p) <= k - 1, b(p) <= m - k, o(p) = 1 or 2      | for a point p -> TODO: DETERMINE WHERE P COMES FROM (intersections or points????)
# The k level -> if for example  k = 3 (and m1 = 5), then the k-level (three level) would be the set of points where a(p) <= 3 - 1, b(p) <= 5 - 3 and o(p) = 1 | 2


# Might have to find the convex hull of the polygon and remove all the points on its edges


def determine_k_level(points: List[Point], lines: List[Line], k: int):
    # For a point p in points
    # a(p) = number of lines such that p is below
    # o(p) = number of lines such that p is on the line
    # b(p) = number of lines such that p is above
    
    # Return the k-level of the points in the polygon
    # That is, the set of points wher a(P) <= k - 1, b(p) <= m - k, o(p) = 1 or 2
    k_level = []
    
    for p in points:
        a = 0
        b = 0
        o = 0
        
        for line in lines:
            position = line.position_of_point(p)
            
            if position == Position.BELOW:
                a += 1
            if position == Position.ABOVE:
                b += 1
            if position == Position.ON:
                o += 1
        
        if a <= k - 1 and b <= len(lines) - k and o in [1, 2]:
            k_level.append(p)
    
    return k_level

def main():
    n = 25

    # Generate n random points without using any functions
    n_random_points = random.sample(range(-100, 100), n * 2)
    G1_points = [Point(n_random_points[i], n_random_points[i + 1]) for i in range(0, len(n_random_points), 2)]
    G1 = [Line(p.x, -p.y) for p in G1_points]

    n_random_points = random.sample(range(-100, 100), n * 2)
    G2_points = [Point(n_random_points[i], n_random_points[i + 1]) for i in range(0, len(n_random_points), 2)]
    G2 = [Line(p.x, -p.y) for p in G2_points]
    points = G1_points + G2_points
    
    
    lines = G1 + G2
    # for p in points:
    #     lines.append(Line(p[0], -p[1]))

    
    stop = False

    # initial k_i value is (n_i + 1)/2 for i=1,2 (for G1 and G2)
    # ???? if n_i is even, we must delete an arbitrary line from G_i ????
    P = points
    
    k1 = (len(G1) + 1) / 2
    k2 = (len(G2) + 1) / 2
    
    while not stop:
        median_index = math.floor(len(lines) / 2)
        G: List[Line] = sorted(lines, key=lambda x: x.slope)
        median_line = G[median_index]
        
        G_minus: List[Line] = G[:median_index]
        G_plus: List[Line] = G[median_index:]

        matches: List[Pair] = []
        matches_intersections: List[Point] = []
        for l1, l2 in zip(G_plus, G_minus):
            matches.append(Pair(l1, l2))
            matches_intersections.append(l1.intersection(l2))
            
        # Determine a vertical line v* that bisects matches_intersections
        vertical_bisector = find_vertical_bisector(matches_intersections)
        
                
        G1_k_level = determine_k_level(points=G1_points, lines=G1, k=k1)
        G2_k_level = determine_k_level(points=G2_points, lines=G2, k=k2)
        
        test_against_vertical_line(
            k_level_1=G1_k_level,
            k_level_2=G2_k_level,
            test_line=vertical_bisector,
            P=points,
        )
        
        
        # halfplane_result_v = test_against_a_line(
        #     P=P,
        #     G_minus=G_minus,
        #     G_plus=G_plus,
        #     k_minus=(len(G_minus) + 1) / 2,
        #     k_plus=(len(G_plus) + 1) / 2,
        #     test_line=Line(0, vertical_bisector),
        #     test_line_vertical=True,
        # )

        # if halfplane_result_v == Correct_Halfplane.FINISHED:
        #     stop = True
        #     print("\n\n\nFINISHED\n\n\n")
        #     print(halfplane_result_v)
        #     print(vertical_bisector)
        #     print(P)
        #     continue
        
        # points_in_halfplane, points_outside_halfplane = split_points_by_halfplane(
        #     vertical_bisector, halfplane_result_v, matches_intersections
        # )
        
        # #Determine a line parallel to median line which bisects the set of points in intersection_points outside of the open halfplane returned that contains the odd number of intersections
        # bisecting_line = find_bisecting_line(median_line, points_outside_halfplane)
        
        # # # plot the bisecting line, the median line and the points outside halfplane using matplotlib
        # # plot_points_and_line(points_outside_halfplane, bisecting_line)
        
        # G1_k_level = determine_k_level(points=points_in_halfplane, lines=G1, k=k1)
        # G2_k_level = determine_k_level(points=points_in_halfplane, lines=G2, k=k2)
        
        # print("G1 k level: ", G1_k_level)
        # print("G2 k level: ", G2_k_level)
        

        stop = True # TODO Remove
    
    
if __name__== "__main__":
    main()