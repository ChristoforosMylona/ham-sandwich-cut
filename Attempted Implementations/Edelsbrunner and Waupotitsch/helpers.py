from enum import Enum
from typing import List, Tuple, Union
import matplotlib.pyplot as plt
import numpy as np
import math
from shapely.geometry import LineString, Point as ShapelyPoint

class Position(Enum):
    ABOVE = 1
    ON = 0
    BELOW = -1


class Correct_Halfplane(Enum):
    LEFT = -1
    FINISHED = 0
    RIGHT = 1


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x},{self.y})"

    def dual_line(self, x_vals):
        return self.x * x_vals - self.y



class Line:
    def __init__(self, slope: float, intercept: float):
        self.slope = slope
        self.intercept = intercept

    def __str__(self):
        return f"y = {self.slope}x + {self.intercept}"

    def __repr__(self):
        return f"y = {self.slope}x +{self.intercept}"

    def __getitem__(self, index: int):
        if index == 1:
            return self.slope
        elif index == 2:
            return self.intercept
        else:
            raise IndexError("Index out of range. Use 0 for slope and 1 for intercept.")

    def compute(self, x: float) -> float:
        """Computes the value of the line at a given x."""
        return self.slope * x + self.intercept

    def intersection(self, other):
        if self.slope == other.slope:
            if self.intercept == other.intercept:
                return print("The lines are coincident (infinitely many intersection points).")
            else:
                print ("The lines are parallel (no intersection).")
            raise ValueError("The lines do not intersect.")
        else:
            x = (other.intercept - self.intercept) / (self.slope - other.slope)
            y = self.slope * x + self.intercept
            return Point(x, y)

    def perpendicular_distance(self, point: Point) -> float:
        """Calculate the perpendicular distance from the line to the point."""
        A = -self.slope
        B = 1
        C = -self.intercept
        return (A * point.x + B * point.y + C) / np.sqrt(A**2 + B**2)
    
    def y_values(self, x):
        return self.slope * x + self.intercept
    
    def intersection_with_vertical_line(self, x_val: float):
        """Returns the point of intersection of this line with a vertical line x = x_val."""
        # The y-value is computed by plugging x_val into the line's equation: y = mx + b
        y_val = self.slope * x_val + self.intercept
        return Point(x_val, y_val)
    

    # a method which returns if a given point is on, below, or above the line
    def position_of_point(self, point: Point) -> Position:
        """Determine if a point is above, on, or below the line."""
        line_value = self.compute(point.x)
        if point.y > line_value:
            return Position.ABOVE
        elif point.y < line_value:
            return Position.BELOW
        else:
            return Position.ON

class Pair:

    def __init__(self, line1: Line, line2: Line):
        self.line1 = line1
        self.line2 = line2

    def __repr__(self):
        return f"Line1: y = {self.line1.slope}x + {self.line1.intercept}\tLine2: y = {self.line2.slope}x + {self.line2.intercept}"

    def get_intercept(self):
        x = (self.line2.intercept - self.line1.intercept) / (
            self.line1.slope - self.line2.slope
        )
        y = self.line1.slope * x + self.line1.intercept

        return Point(x, y)


def count_line_positions(point: Point, lines: List[Line]):
    """
    Counts the number of lines below, on, and above a given point.
    """
    below, on, above = 0, 0, 0
    for line in lines:
        y_at_x = line.compute(point.x)
        if point.y < y_at_x:
            below += 1
        elif point.y > y_at_x:
            above += 1
        else:
            on += 1
    return below, on, above


def k_level(G: List[Line], k: int):
    """
    Computes the k_i-level for a set of lines G and an integer k.
    Returns the set of points that satisfy the k_i-level condition.
    """
    # Find all intersection points of the lines
    intersection_points = []
    m = len(G)

    for i in range(m):
        for j in range(i + 1, m):
            intersection = G[i].intersection(G[j])
            if intersection is not None:
                intersection_points.append(intersection)

    # Check each intersection point against the k_i-level condition
    k_level_points = []
    for point in intersection_points:
        below, on, above = count_line_positions(point, G)

        if below < k - 1 and above < m - k and (on == 1 or on == 2):
            k_level_points.append(point)

    return k_level_points


def find_intersections(
    test_line: Line, vertical_line: bool, lines: List[Line]
) -> List[Union[Point, None]]:
    """
    Finds the intersection points between the test_line and the list of lines.

    Args:
        test_line: Line to test for intersections.
        vertical_line: A boolean indicating whether the test_line is vertical (True if vertical).
        lines: A list of lines to check for intersections.

    Returns:
        A list of points where the test_line intersects with the given lines. None if no intersection.
    """
    intersections = []

    if vertical_line:
        # The test_line is vertical: x = test_line.intercept
        x_value = test_line.intercept
        for line in lines:
            # Find y for each line at x = test_line.intercept
            y_value = line.compute(x_value)
            intersections.append(Point(x_value, y_value))
    else:
        # The test_line is not vertical: y = mx + b
        for line in lines:
            intersection = test_line.intersection(line)
            intersections.append(intersection)

    return intersections


def is_point_between(p: Point, a: Point, b: Point) -> bool:
    """Checks if point p is between points a and b (inclusive)."""
    return min(a.x, b.x) <= p.x <= max(a.x, b.x) and min(a.y, b.y) <= p.y <= max(
        a.y, b.y
    )


def edge_intersects_line(
    p1: Point, p2: Point, test_line: Line, vertical_line: bool
) -> bool:
    """
    Determines if the edge formed by points p1 and p2 intersects with the test_line.
    Handles both vertical and non-vertical test_line cases.
    """
    if vertical_line:
        # The test_line is vertical: x = test_line.intercept
        x_value = test_line.intercept
        # Check if the vertical line at x = x_value intersects the edge [p1, p2]
        if min(p1.x, p2.x) <= x_value <= max(p1.x, p2.x):
            # Compute y for the vertical line, interpolate y between p1 and p2
            if p1.x != p2.x:  # Prevent division by zero for vertical polygon edges
                slope_edge = (p2.y - p1.y) / (p2.x - p1.x)
                y_at_x_value = slope_edge * (x_value - p1.x) + p1.y
                return min(p1.y, p2.y) <= y_at_x_value <= max(p1.y, p2.y)
    else:
        # The test_line is not vertical: use line-line intersection
        # The edge is treated as a line segment between p1 and p2
        edge_line_slope = (
            (p2.y - p1.y) / (p2.x - p1.x) if p1.x != p2.x else float("inf")
        )
        edge_line = Line(edge_line_slope, p1.y - edge_line_slope * p1.x)
        intersection_point = test_line.intersection(edge_line)
        if intersection_point is not None:
            return is_point_between(intersection_point, p1, p2)

    return False


def does_line_intersect_polygon(
    polygon: List[Point], test_line: Line, vertical_line: bool
) -> bool:
    """
    Determines if the test_line intersects with the polygon.

    Args:
        polygon: List of Points representing the polygon vertices.
        test_line: Line to check for intersection with the polygon.
        vertical_line: Boolean indicating if the test_line is vertical.

    Returns:
        True if the line intersects the polygon, False otherwise.
    """
    num_points = len(polygon)

    # Check each edge of the polygon
    for i in range(num_points):
        p1 = Point(polygon[i][0], polygon[i][1])
        p2 = Point(
            polygon[(i + 1) % num_points][0], polygon[(i + 1) % num_points][1]
        )  # Connect the last point to the first

        if edge_intersects_line(p1, p2, test_line, vertical_line):
            return True

    return False


def plot_points(set1, set2):
    # Extract the x and y coordinates for the points in set1
    x1 = [p.x for p in set1]
    y1 = [p.y for p in set1]

    # Extract the x and y coordinates for the points in set2
    x2 = [p.x for p in set2]
    y2 = [p.y for p in set2]

    # Plot the first set of points in red
    plt.scatter(x1, y1, color="red", label="Set 1")

    # Plot the second set of points in blue
    plt.scatter(x2, y2, color="blue", label="Set 2")

    # Add labels and a legend
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Plot of Two Sets of Points")
    plt.legend()

    # Show the plot
    plt.show()


def bisect_remaining_points(outside_points: List[Point], median_line: Line) -> Line:
    """
    Find a parallel line w* to the median line g* that bisects the set of points
    outside of the previously found half-plane.
    """
    # Use binary search or other geometric methods to find a parallel line w*
    # that bisects the set of outside points. Assume outside_points is sorted.

    # Find the mid-point in the outside points
    median_idx = len(outside_points) // 2
    bisecting_point = outside_points[median_idx]

    # Create the parallel line w* through the bisecting point, parallel to g*
    slope = median_line.slope  # Use the slope of the median line
    w_star = Line(bisecting_point.x, bisecting_point.y, slope=slope)  # Line equation

    return w_star


def update_polygon_and_sets(
    P: List[Point],
    G1: List[Line],
    G2: List[Line],
    k1: int,
    k2: int,
    v: Line,
    w: Line,
    w_prime: Line,
    w_double_prime: Line,
):
    """
    Update the polygon P and the sets of lines G1 and G2, along with their k-levels based on
    new half-planes (v, w, w_prime, w_double_prime).

    Args:
        P (List[Point]): The current polygon.
        G1 (List[Line]): Set of lines G1.
        G2 (List[Line]): Set of lines G2.
        k1 (int): Current k-level for G1.
        k2 (int): Current k-level for G2.
        v (Line): The vertical half-plane dividing the polygon.
        w (Line): A half-plane parallel to the median line.
        w_prime (Line): A vertical half-plane for refining G1 and G2.
        w_double_prime (Line): Another vertical half-plane for refining G1 and G2.

    Returns:
        Tuple: New polygon and updated G1, G2, k1, k2.
    """

    # Step 1: Restrict P by the intersection of the half-planes defined by v, w, w_prime, and w_double_prime
    new_P = intersect_polygon_with_halfplanes(P, [v, w, w_prime, w_double_prime])

    # Step 2: Update the sets of lines G1 and G2 to include only those intersecting the new polygon P
    new_G1 = [line for line in G1 if intersects_polygon(polygon=new_P, line=line)]
    new_G2 = [line for line in G2 if intersects_polygon(polygon=new_P, line=line)]

    # Step 3: Update the k-levels based on the restrictions (use their sizes)
    if w.slope > 0:  # If w bounds from below
        new_k1 = k1
        new_k2 = k2
    else:  # If w bounds from above
        new_k1 = k1 - (len(G1) - len(new_G1))
        new_k2 = k2 - (len(G2) - len(new_G2))

    return new_P, new_G1, new_G2, new_k1, new_k2


def check_termination(G_plus: List[Line], G_minus: List[Line]):
    """
    Check if the number of lines in G1 and G2 is reduced to 1 in each set. If so, return the intersection point.
    """
    if len(G_plus) + len(G_minus) == 2:
        intersection_point = G_plus[0].intersection(G_minus[0])
        return intersection_point
    return None


def intersect_polygon_with_halfplanes(
    polygon: List[Point], lines: List[Line]
) -> List[Point]:
    """
    Intersect the polygon with the half-planes bounded by the provided lines.
    Returns the resulting polygon after clipping.
    """

    def position_of_point(line: Line, point: Point) -> Position:
        """Determine if a point is above, on, or below the line."""
        line_value = line.slope * point.x + line.intercept
        if point.y > line_value:
            return Position.ABOVE
        elif point.y < line_value:
            return Position.BELOW
        else:
            return Position.ON

    def intersect_edge_with_line(p1: Point, p2: Point, line: Line) -> Point:
        """Find the intersection point between a polygon edge and a clipping line."""
        edge_line = Line(
            slope=(p2.y - p1.y) / (p2.x - p1.x) if p2.x != p1.x else float("inf"),
            intercept=(
                p1.y - (p1.x * ((p2.y - p1.y) / (p2.x - p1.x)))
                if p2.x != p1.x
                else p1.y
            ),
        )
        return edge_line.intersection(line)

    for line in lines:
        new_polygon = []
        n = len(polygon)

        for i in range(n):
            if type(polygon[i]) == type(Point(0, 0)):
                current_point = polygon[i]
                next_point = polygon[(i + 1) % n]
            else:
                current_point = Point(polygon[i][0], polygon[i][1])
                next_point = Point(polygon[(i + 1) % n][0], polygon[(i + 1) % n][1])

            current_pos = position_of_point(line, current_point)
            next_pos = position_of_point(line, next_point)

            if current_pos != Position.BELOW:
                new_polygon.append(current_point)

            if current_pos != next_pos:
                intersection = intersect_edge_with_line(current_point, next_point, line)
                if isinstance(intersection, Point):
                    new_polygon.append(intersection)

        polygon = new_polygon  # update polygon after processing this line

    return polygon


def get_points_outside_of_halfplane(polygon: List[Point], line: Line) -> List[Point]:
    """
    Get all points of the polygon that lie outside (below) the half-plane defined by the line.

    Args:
        polygon (List[Point]): List of points representing the polygon.
        line (Line): The line defining the half-plane (consider points below as outside).

    Returns:
        List[Point]: A list of points that lie outside the half-plane.
    """

    def position_of_point(line: Line, point: Point) -> Position:
        """Determine if a point is above, on, or below the line."""
        line_value = line.slope * point.x + line.intercept
        if point.y > line_value:
            return Position.ABOVE
        elif point.y < line_value:
            return Position.BELOW
        else:
            return Position.ON

    outside_points = []
    for point in polygon:
        if position_of_point(line, point) == Position.BELOW:
            outside_points.append(point)

    return outside_points


def find_vertical_bisectors(points: List[Point]) -> Tuple[Line, Line]:
    """
    Finds two vertical lines (w_prime, w_double_prime) that bisect a set of points.

    Args:
        points (List[Point]): List of intersection points.

    Returns:
        Tuple[Line, Line]: Vertical lines that bisect the set of points.
    """
    # Sort points by x-coordinates
    sorted_points = sorted(points, key=lambda p: p.x)

    # Find the bisectors: roughly the middle x-coordinates of the sorted points
    median_idx = len(sorted_points) // 2
    w_prime_x = sorted_points[median_idx - 1].x
    w_double_prime_x = sorted_points[median_idx].x

    # Return vertical lines at these x-coordinates
    return Line(slope=float("inf"), intercept=w_prime_x), Line(
        slope=float("inf"), intercept=w_double_prime_x
    )


def find_parallel_bisector(median_line: Line, points: List[Point]) -> Line:
    """
    Finds a line parallel to the median line that bisects the intersection points.
    """
    sorted_points = sorted(points, key=lambda p: p.y)
    median_idx = len(sorted_points) // 2
    median_point = sorted_points[median_idx]
    parallel_intercept = median_line.slope * median_point.x + median_point.y
    return Line(median_line.slope, parallel_intercept)


def find_vertical_bisectors(points: List[Point]) -> Tuple[Line, Line]:
    """
    Finds two vertical lines (w_prime, w_double_prime) that bisect a set of points.

    Args:
        points (List[Point]): List of intersection points.

    Returns:
        Tuple[Line, Line]: Vertical lines that bisect the set of points.
    """
    # Sort points by x-coordinates
    sorted_points = sorted(points, key=lambda p: p.x)

    # Find the bisectors: roughly the middle x-coordinates of the sorted points
    median_idx = len(sorted_points) // 2
    w_prime_x = sorted_points[median_idx - 1].x
    w_double_prime_x = sorted_points[median_idx].x

    # Return vertical lines at these x-coordinates
    return Line(slope=float("inf"), intercept=w_prime_x), Line(
        slope=float("inf"), intercept=w_double_prime_x
    )


def intersects_polygon(line: Line, polygon: List[Point]) -> bool:
    """
    Check if a given line intersects any edge of the polygon.
    The polygon is represented as a list of points, and each edge is a line segment
    between two consecutive points.
    """
    n = len(polygon)

    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]  # wrap around to the first point for the last edge

        # Check if line intersects the edge (p1, p2)
        edge_line = Line(
            slope=(p2.y - p1.y) / (p2.x - p1.x) if p2.x != p1.x else float("inf"),
            intercept=(
                p1.y - (p1.x * ((p2.y - p1.y) / (p2.x - p1.x)))
                if p2.x != p1.x
                else p1.y
            ),
        )

        # Find intersection point between the test line and the edge line
        intersection_point = line.intersection(edge_line)

        # If intersection is within the bounds of the edge, return True
        if isinstance(intersection_point, Point):
            if min(p1.x, p2.x) <= intersection_point.x <= max(p1.x, p2.x) and min(
                p1.y, p2.y
            ) <= intersection_point.y <= max(p1.y, p2.y):
                return True

    return False


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

# def calculate_k_level(lines: list[Line], k: int) -> list[Point]:
#     """Calculate the k-level points of a set of lines in general position."""
#     # Step 1: Compute all unique intersections between lines
#     intersections = []
#     for i in range(len(lines)):
#         for j in range(i + 1, len(lines)):
#             point = lines[i].intersection(lines[j])
#             if isinstance(point, Point):  # Only add valid intersection points
#                 intersections.append(point)

#     # # Step 2: Sort intersections by y descending, then by x ascending
#     # intersections.sort(key=lambda p: (-p.y, p.x))

#     # # Step 3: Sweep through sorted intersections to find the k-level points
#     # k_level_points = []
#     # for point in intersections:
#     #     x, y = point.x, point.y
#     #     lines_above = sum(1 for line in lines if line.compute(x) > y)
        
#     #     if lines_above == k:
#     #         k_level_points.append(point)

#     # return k_level_points

#     k_level_points = []
#     # is a k level point if :
#     # the number of lines that p is below <= k - 1
#     # the number of lines that p is above >= len(lines) - k
    
#     for point in intersections:
#         x,y = point.x, point.y
#         lines_above = len([line for line in lines if line.compute(x) > y])
#         lines_below = len([line for line in lines if line.compute(x) < y])
        
#         if lines_above <= k - 1 and lines_below >= len(lines) - k:
#             k_level_points.append(point)
        
#     return k_level_points    


def test_against_vertical_line(
    k_level_1: List[Point],
    k_level_2: List[Point],
    test_line: float,
    P: List[Point],
):
    # treat k_levels as shapely linesegment
    # check if the leftmost point in k_level_1 is above k_level_2
    
    k_level_1_linesegment = LineString([ ShapelyPoint(p.x, p.y) for p in k_level_1])
    k_level_2_linesegment = LineString([ShapelyPoint(p.x, p.y) for p in k_level_2])
    
    # leftmost_k_level_1 = min(k_level_1, key=lambda p: p.x)
    
    # if leftmost_k_level_1.y > k_l
    intersection = k_level_1_linesegment.intersection(k_level_2_linesegment)
    
    print(intersection)    
    
def test_against_a_line(
    P: List[Line],
    G_plus: List[Line],
    G_minus: List[Line],
    k_plus: int,
    k_minus: int,
    test_line: Line,
    test_line_vertical: bool,
    points: List[Point] = None,
):
    """
    Returns whether test_line contains an intersection with the k levels of G_plus and G_minus, or which halfplane bounded by t has an odd number of intersections
    """

    G_plus_intersections = sorted(find_intersections(test_line, test_line_vertical, G_plus), key= lambda p : p.x)
    G_minus_intersections = sorted(find_intersections(test_line, test_line_vertical, G_minus), key= lambda p : p.x)

    leftmost_G_plus = min(G_plus_intersections, key=lambda x: x.x).y
    leftmost_G_minus = min(G_minus_intersections, key=lambda x: x.x).y

    above = leftmost_G_plus > leftmost_G_minus

    intersects_polygon = does_line_intersect_polygon(
        polygon=P, test_line=test_line, vertical_line=test_line_vertical
    )


    print("test_line intersects polygon: ", intersects_polygon)

    # firstly, consider the case when test_line is vertical
    if test_line_vertical:
        if not intersects_polygon:
            # Determine which half-plane contains the polygon
            polygon_x_min = min(vertex.x for line in P for vertex in [line.start, line.end])
            polygon_x_max = max(vertex.x for line in P for vertex in [line.start, line.end])

            if polygon_x_max < test_line.x:
                return Correct_Halfplane.LEFT
            elif polygon_x_min > test_line.x:
                return Correct_Halfplane.RIGHT

            raise ValueError(
                "Unexpected case: test line doesn't intersect the polygon, but polygon spans both sides."
            )

        # print("k_level G plus:", k_level(G_plus, k_plus))
        # print("k_level G minus:", k_level(G_minus, k_minus))

        # print()
        # print("G plus intersections with test line: ", G_plus_intersections)
        # print()
        # print("G minus intersections with test line: ", G_minus_intersections)

        # TODO
        # find the intersection point with the ki-largest y-coordinate
        # also look into using heapq or sliding window approach (might be faster)
        # If NOT faster than numpy, change everything to use numpy so casting to numpy array not necessary
        # and change does_line_intersect_polygon to return only the y coordinates, not the points

        # print()
        # print("k_plus:", k_plus)
        # print("k_minus:", k_minus)
        # print()

        # print("calculated k level plus: ", calculate_k_level(lines=G_plus, k=k_plus))
        # print("calculated k level minus: ", calculate_k_level(lines=G_minus, k=k_minus))

        k_largest_plus = np.partition(
            [point.y for point in calculate_k_level(lines=G_plus, k=k_plus)], int(-k_plus)
        )[int(-k_plus)]
        k_largest_minus = np.partition(
            [point.y for point in calculate_k_level(lines=G_minus, k=k_minus)], int(-k_minus)
        )[int(-k_minus)]
        # k_largest_plus = np.partition(
        #     [point.y for point in G_plus_intersections], int(-k_plus)
        # )[int(-k_plus)]
        # k_largest_minus = np.partition(
        #     [point.y for point in G_minus_intersections], int(-k_minus)
        # )[int(-k_minus)]

        # print()

        # print("K largest for G+:", k_largest_plus)
        # print("K largest for G-:", k_largest_minus)

        contains_intersection = False
        
        for point in calculate_k_level(lines=G_plus, k=k_plus):
            for point_minus in calculate_k_level(lines=G_minus, k=k_minus):
                if math.isclose(point.x, point_minus.x) and math.isclose(point.y, point_minus.y):
                    contains_intersection = True
    
        # TODO: cehck if math.isClose is more appropriate
        if contains_intersection:
            # in this case we are finished
            return Correct_Halfplane.FINISHED
        elif k_largest_plus > k_largest_minus:
            if not above:
                return Correct_Halfplane.LEFT
        else:
            if above:
                return Correct_Halfplane.LEFT

        return Correct_Halfplane.RIGHT

    
    
    
    # if test line is not vertical
    
    # TODO: decide if there is a point in kG1 that intersects (is the same) as a point in kG2. In this case we are finished
        
    print(G_plus_intersections)
    print()
    print("k level G+: ", k_level_plus := calculate_k_level(lines=G_plus, k=k_plus))
    print("k level G-: ", k_level_minus := calculate_k_level(lines=G_minus, k=k_minus))
    
    print()
    
    # Carry out a binary search to find an index j where:
    # The region G_plus_intersection at j and and G_plus_intersection at j + 1 contain an odd number of points from k_level_intersects = k_level_plus + k_level_minus
    
    def binary_search_intervals(G_plus_intersections: List[Point], k_level_plus: List[Point], k_level_minus: List[Point]):
        low, high = 0, len(G_plus_intersections) - 1
        
        while low <= high:
            if low == -math.inf:
                j = high // 2
            elif high == math.inf:
                j = (len(G_plus_intersections) - 1 + low ) // 2
            else:
                j = (low + high) // 2
            
            if j < 0:
                mid = -math.inf
            else:
                mid = G_plus_intersections[j].x
            
            
            if j == len(G_plus_intersections):
                mid_plus = math.inf
            else:
                mid_plus = G_plus_intersections[j + 1].x
            
            
            
            k_level_intersects = 0
            
            # TODO: w is defined as an open half plane so might not be inclusive
            for p in k_level_plus:
                if p.x >= mid and p.x <= mid_plus:
                    k_level_intersects += 1
            
            for p in k_level_minus:
                if p.x >= mid and p.x <= mid_plus:
                    k_level_intersects += 1
            
            if k_level_intersects % 2 == 1:
                return mid, mid_plus
            
            # count the number of intersects left and right of the interval
            left_intersects_count = 0
            right_intersects_count = 0
            
            # TODO: figure out if should be inclusive (described as open halfplane)
            for intersection in G_plus_intersections:
                if intersection.x < mid:
                    left_intersects_count += 1
                elif intersection.x > mid_plus:
                    right_intersects_count += 1
            
            if left_intersects_count % 2  == 1 & left_intersects_count != 0:
                high = mid
            elif right_intersects_count % 2 == 1 & right_intersects_count != 0:
                low = mid_plus
            else:
                print("Neither left nor right have odd half planes??")
                break
            
            # print ("mid", mid)
            # print("mid_plus", mid_plus)
            # break
        
        print("Could not find mid,mid_plus before end of binary search")
        return 0, 0
    
    mid, mid_plus = binary_search_intervals(G_plus_intersections=G_plus_intersections, k_level_plus=k_level_plus, k_level_minus=k_level_minus)
    if mid == 0 and mid_plus == 0:
        print("FAILED RUN, STILL NEED TO FIGURE OUT WHICH DIRECTION THE BINARY SEARCH SHOULD GO")
    
    print("mid: ", mid)
    print("mid plus: ", mid_plus)
    print()
    if mid != 0 and mid_plus != 0:
        plot_test_against_a_line (P, G_plus_intersections, k_level_plus, k_level_minus, test_line)
        
    
    # TODO: figure out which direction the binary search should go
    if mid == 0 and mid_plus == 0:
        print("FAILED RUN, STILL NEED TO FIGURE OUT WHICH DIRECTION THE BINARY SEARCH SHOULD GO")
        return 0, 0
    
    return mid, mid_plus
    
    
    
    
    
    
def split_points_by_halfplane(vertical_line_x: float, halfplane: Correct_Halfplane, points: list[Point]) -> tuple[list[Point], list[Point]]:
    """
    Split points into those inside and outside the halfplane.
    
    Args:
    - vertical_line_x (float): The x-coordinate that defines the vertical line.
    - halfplane (Correct_Halfplane): Enum to specify which half-plane to consider.
    - points (list[Point]): List of points to split.
    
    Returns:
    - tuple: (points_in_halfplane, points_not_in_halfplane)
    """
    if halfplane == Correct_Halfplane.FINISHED:
        # If 'FINISHED', there is no halfplane restriction, so all points are in the "in halfplane" list
        return points, []

    points_in_halfplane = []
    points_not_in_halfplane = []

    for point in points:
        if halfplane == Correct_Halfplane.LEFT:
            if point.x < vertical_line_x:
                points_in_halfplane.append(point)
            else:
                points_not_in_halfplane.append(point)
        elif halfplane == Correct_Halfplane.RIGHT:
            if point.x > vertical_line_x:
                points_in_halfplane.append(point)
            else:
                points_not_in_halfplane.append(point)

    return points_in_halfplane, points_not_in_halfplane



def find_bisecting_line(line: Line, points: list[Point]) -> Line:
    # Step 1: Calculate signed perpendicular distances for each point
    distances = [line.perpendicular_distance(point) for point in points]
    
    # Step 2: Find the median of these distances
    median_distance = np.median(distances)
    
    # Step 3: Adjust the intercept to create a parallel line at the median distance
    new_intercept = line.intercept + median_distance * np.sqrt(1 + line.slope**2)
    return Line(line.slope, new_intercept)





def plot_points_and_line(points: list[Point], line: Line, title="Bisecting Line and Points"):
    """
    Plot a set of points and a line on a 2D plane.
    
    Args:
    - points (list of Point): The list of points to plot.
    - line (Line): The line to plot.
    - title (str): The title of the plot.
    """
    # Extract x and y coordinates of the points
    x_vals = [point.x for point in points]
    y_vals = [point.y for point in points]

    # Create a range of x values for plotting the line
    x_range = np.linspace(min(x_vals) - 1, max(x_vals) + 1, 100)
    
    # Calculate corresponding y values using the line equation
    y_line = line.slope * x_range + line.intercept
    
    # Plot the points
    plt.scatter(x_vals, y_vals, color='blue', label="Points Outside Halfplane")

    # Plot the line
    plt.plot(x_range, y_line, color='red', label=f"Line: y = {line.slope}x + {line.intercept}")

    # Labeling and title
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_test_against_a_line(
    P, G_plus_intersections, k_level_plus, k_level_minus, test_line
):
    plt.figure(figsize=(10, 8))
    
    # Plot each point in P
    P_x = [point[0] for point in P]
    P_y = [point[1] for point in P]
    plt.scatter(P_x, P_y, color='gray', marker='.', label='Points in P', alpha=0.6)
    
    # Plot intersections of G_plus with test_line
    G_plus_x = [point.x for point in G_plus_intersections]
    G_plus_y = [point.y for point in G_plus_intersections]
    plt.scatter(G_plus_x, G_plus_y, color='blue', marker='o', label='G+ Intersections')
    
    # Plot k_level_plus as individual points
    if k_level_plus:
        k_level_plus_x = [point.x for point in k_level_plus]
        k_level_plus_y = [point.y for point in k_level_plus]
        plt.scatter(k_level_plus_x, k_level_plus_y, color='green', marker='x', label=f'k-Level G+ (k={len(k_level_plus)})')
    
    # Plot k_level_minus as individual points
    if k_level_minus:
        k_level_minus_x = [point.x for point in k_level_minus]
        k_level_minus_y = [point.y for point in k_level_minus]
        plt.scatter(k_level_minus_x, k_level_minus_y, color='red', marker='x', label=f'k-Level G- (k={len(k_level_minus)})')
    
    min_x = min(min(k_level_minus_x), min (k_level_plus_x), min(P_x))
    min_y = min(min(k_level_minus_y), min (k_level_plus_y), max(P_x))
    
    max_x = max(max(k_level_minus_x), max (k_level_plus_x))
    max_y = max(max(k_level_minus_y), max (k_level_plus_y))
    
    # Plot the test line
    x_vals = np.linspace(-10, 10, 400)  
    y_vals = test_line.slope * x_vals + test_line.intercept
    plt.plot(x_vals, y_vals, color='purple', linewidth=1.5, label='Test Line')

    # Set plot limits
    plt.xlim(min_x - 10, max_x + 10)
    plt.ylim(min_y + 10, max_y + 10)

    # Labels and legend
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Plot of Points P, G+ Intersections, k-Level G+, k-Level G-, and Test Line")
    plt.legend()
    plt.grid(True)
    
    # Show plot
    plt.show()

def plot_step_4_lines(v: float, w: Line, w_prime: float, w_double_prime: float, P: list[Line]):
    # Dynamically determine the x-range
    all_x = [v, w_prime, w_double_prime]  # Start with vertical line positions
    for line in P:
        # Estimate significant x-values based on line intercepts
        intercept_x = -line.intercept / line.slope if line.slope != 0 else 0
        all_x.append(intercept_x)

    # Use the range of all_x values to define linspace
    x_min = min(all_x) - 5
    x_max = max(all_x) + 5
    x = np.linspace(x_min, x_max, 400)

    # Plot the non-vertical line 'w'
    plt.plot(x, w.y_values(x), label=f"Line w: y = {w.slope}x + {w.intercept}", color='blue')

    # Plot each line in the set P
    for i, line in enumerate(P, start=1):
        plt.plot(x, line.y_values(x), label=f"Line P[{i}]: y = {line.slope}x + {line.intercept}")

    # Plot the vertical line at 'v'
    plt.axvline(x=v, color='red', linestyle='--', label=f"Vertical line v = {v}")

    # Plot the vertical line at 'w_prime'
    plt.axvline(x=w_prime, color='green', linestyle='--', label=f"Vertical line w' = {w_prime}")

    # Plot the vertical line at 'w_double_prime'
    plt.axvline(x=w_double_prime, color='purple', linestyle='--', label=f"Vertical line w'' = {w_double_prime}")

    # Set labels and title
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Plot of Vertical and Non-Vertical Lines")
    plt.legend()

    # Display the plot
    plt.grid(True)
    plt.show()