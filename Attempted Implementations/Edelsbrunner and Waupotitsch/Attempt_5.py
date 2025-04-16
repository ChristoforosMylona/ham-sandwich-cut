from shapely.geometry import Point
from shapely.geometry.polygon import orient
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from typing import List, Tuple, Optional
import random
import time

class Line:
    """
    Represents a line in 2D space using the form ax + by + c = 0
    """
    def __init__(self, a: float, b: float, c: float):
        self.a = a
        self.b = b
        self.c = c
        
    @classmethod
    def from_points(cls, p1: Tuple[float, float], p2: Tuple[float, float]):
        """Create a line passing through two points"""
        # If points are vertical
        if p1[0] == p2[0]:
            return cls(1, 0, -p1[0])
        
        # Calculate slope
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        # Calculate y-intercept
        b = p1[1] - m * p1[0]
        # Convert to ax + by + c = 0 form
        return cls(-m, 1, -b)
    
    def slope(self) -> Optional[float]:
        """Return the slope of the line"""
        if self.b == 0:  # Vertical line
            return float('inf')
        return -self.a / self.b
    
    def intercept(self) -> Optional[float]:
        """Return the y-intercept of the line"""
        if self.b == 0:  # Vertical line has no y-intercept
            return None
        return -self.c / self.b
    
    def evaluate_point(self, point: Tuple[float, float]) -> float:
        """
        Evaluate ax + by + c for a given point (x, y)
        Positive value means point is on one side of the line,
        negative means it's on the other side, zero means it's on the line
        """
        x, y = point
        return self.a * x + self.b * y + self.c
    
    def is_above(self, point: Tuple[float, float]) -> bool:
        """Check if a point is above the line"""
        # For a horizontal line, "above" is determined by sign of b
        if self.a == 0:
            return (self.b > 0 and self.evaluate_point(point) < 0) or \
                   (self.b < 0 and self.evaluate_point(point) > 0)
        
        # For non-horizontal lines
        if self.b == 0:  # Vertical line
            return (self.a > 0 and point[0] < -self.c / self.a) or \
                   (self.a < 0 and point[0] > -self.c / self.a)
            
        # General case
        # We need to solve for y in ax + by + c = 0
        # y = -(ax + c)/b
        y_on_line = -(self.a * point[0] + self.c) / self.b
        return point[1] > y_on_line
    
    def is_below(self, point: Tuple[float, float]) -> bool:
        """Check if a point is below the line"""
        return not self.is_above(point) and not self.is_on(point)
    
    def is_on(self, point: Tuple[float, float], epsilon=1e-9) -> bool:
        """Check if a point is on the line"""
        return abs(self.evaluate_point(point)) < epsilon
    
    def intersection(self, other: 'Line') -> Optional[Tuple[float, float]]:
        """Find the intersection point with another line"""
        det = self.a * other.b - other.a * self.b
        if abs(det) < 1e-9:  # Lines are parallel
            return None
        
        x = (self.b * other.c - other.b * self.c) / det
        y = (other.a * self.c - self.a * other.c) / det
        return (x, y)
    
    def __repr__(self) -> str:
        return f"Line({self.a}x + {self.b}y + {self.c} = 0)"


def step1_find_median_slope(G1: List[Line], G2: List[Line]) -> Line:
    """
    Determine line g* in G with median slope.
    Returns the line with the median slope and splits the lines into G+ and G-.
    """
    G = G1 + G2
    slopes = [line.slope() for line in G]
    
    # Find the median slope
    median_idx = len(slopes) // 2
    median_slope = sorted(slopes)[median_idx]
    
    # Find a line with the median slope
    for line in G:
        if line.slope() == median_slope:
            g_star = line
            break
    
    # Split lines into G+ (at least as steep) and G- (less steep)
    G_plus = [line for line in G if line.slope() >= median_slope]
    G_minus = [line for line in G if line.slope() < median_slope]
    
    return g_star, G_plus, G_minus

    
def step2_match_lines(G_plus: List[Line], G_minus: List[Line]) -> List[Tuple[Point, Line, Line]]:
    """
    Match each line in G- with a unique line in G+.
    Returns a list of intersection points between matched lines.
    """
    # Ensure we have enough lines in G+ to match all lines in G-
    assert len(G_plus) >= len(G_minus), "G+ must have at least as many lines as G-"
    
    # Match each line in G- with a unique line in G+
    matched_pairs = []
    for i, line_minus in enumerate(G_minus):
        line_plus = G_plus[i]
        intersection_pt = line_minus.intersection(line_plus)
        
        # Skip if lines are parallel (shouldn't happen with general position assumption)
        if intersection_pt is not None:
            # Store the intersection point and the two lines
            matched_pairs.append((Point(intersection_pt), line_minus, line_plus))
    
    return matched_pairs



class ConvexPolygon:
    """
    Represents an open convex polygon, potentially unbounded.
    """
    def __init__(self, half_planes=None):
        # A list of half-planes (represented as lines)
        # A point is in the polygon if it satisfies all half-plane constraints
        self.half_planes = half_planes if half_planes else []
        self.is_empty = False
    
    def intersect_half_plane(self, line: Line, positive_side: bool):
        """
        Intersect the polygon with a half-plane defined by a line.
        The half-plane is the positive or negative side of the line.
        """
        if self.is_empty:
            return
        
        if positive_side:
            self.half_planes.append((line, True))
        else:
            self.half_planes.append((line, False))
    
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """Check if the polygon contains a given point"""
        if self.is_empty:
            return False
            
        for line, positive_side in self.half_planes:
            value = line.evaluate_point(point)
            if positive_side and value < 0:
                return False
            if not positive_side and value > 0:
                return False
        return True


def find_vertical_bisector(matched_pairs: List[Tuple[Point, Line, Line]]) -> Line:
    """
    Find a vertical line that bisects the set of intersection points.
    """
    # Extract x-coordinates of intersection points
    x_coords = [point.x for point, _, _ in matched_pairs]
    
    # Find the median x-coordinate
    median_x = sorted(x_coords)[len(x_coords) // 2]
    
    # Create a vertical line through the median x
    vertical_line = Line(1, 0, -median_x)  # x = median_x
    
    return vertical_line


def test_line_against_levels(G1: List[Line], G2: List[Line], k1: int, k2: int, 
                            P: ConvexPolygon, test_line: Line, above: bool, matched_pairs) -> Tuple[bool, bool, Optional[str]]:
    """
    Determine whether test_line contains an intersection of Lk1(G1) and Lk2(G2) in P,
    and if not, which open halfplane contains an odd number of intersections.
    
    This is a simplified version for now - in a real implementation, we would need to:
    1. Find the k-level of line arrangements
    2. Determine intersections between these levels
    3. Test which side of the line contains an odd number of intersections
    
    Returns:
    - (contains_intersection, above_has_odd, below_has_odd)
    """
    # This is a placeholder implementation
    # In a full implementation, we would implement the algorithm described in Section 3
    
    # For vertical lines, we can use the simpler approach mentioned in the paper
    if abs(test_line.a) > 0 and abs(test_line.b) < 1e-9:  # Vertical line
        # TODO: Implement full algorithm from Section 3
        # For now, returning a placeholder result
        
        intersection_points_1 = []
        intersection_points_2 = []
        
        for p in matched_pairs:
            point, line1, line2 = p
            
            
        
        return False, True, False
    
    # For non-vertical lines, we need the binary search approach
    # TODO: Implement full algorithm from Section 3
    return False, False, True  # Placeholder


def step3_find_vertical_bisector(G1: List[Line], G2: List[Line], k1: int, k2: int, 
                                P: ConvexPolygon, matched_pairs: List[Tuple[Point, Line, Line]], above: bool):
    """
    Find a vertical line v* that bisects the matched pairs,
    and determine which halfplane contains odd number of intersections.
    """
    v_star = find_vertical_bisector(matched_pairs)
    
    # Test whether v* contains an intersection or which halfplane does
    contains_intersection, left_has_odd, right_has_odd = test_line_against_levels(
        G1, G2, k1, k2, P, v_star, above, matched_pairs
    )
    
    if contains_intersection:
        return v_star, None  # We found the ham-sandwich cut!
    
    # Create the halfplane v
    if left_has_odd:
        v = ConvexPolygon()
        v.intersect_half_plane(v_star, False)  # Left side of v*
        return v_star, v
    else:
        v = ConvexPolygon()
        v.intersect_half_plane(v_star, True)  # Right side of v*
        return v_star, v


def create_parallel_line(original_line: Line, point: Tuple[float, float]) -> Line:
    """Create a line parallel to original_line passing through point"""
    if original_line.b == 0:  # Vertical line
        return Line(1, 0, -point[0])
    
    if original_line.a == 0:  # Horizontal line
        return Line(0, 1, -point[1])
    
    # For general lines (ax + by + c = 0)
    # The slope is -a/b
    slope = original_line.slope()
    
    # Using point-slope form: y - y1 = m(x - x1)
    # Convert to general form: -m*x + y - (-m*x1 + y1) = 0
    # which is: -m*x + y + (m*x1 - y1) = 0
    x1, y1 = point
    a = -slope
    b = 1
    c = slope * x1 - y1
    
    return Line(a, b, c)


def find_points_in_halfplane(matched_pairs: List[Tuple[Point, Line, Line]], 
                            halfplane: ConvexPolygon) -> List[Tuple[Point, Line, Line]]:
    """Find the points from matched_pairs that lie in the given halfplane"""
    result = []
    for point_data in matched_pairs:
        point, line1, line2 = point_data
        if halfplane.contains_point((point.x, point.y)):
            result.append(point_data)
    return result


def find_bisector_parallel_to_line(points_data: List[Tuple[Point, Line, Line]], 
                                 reference_line: Line) -> Line:
    """
    Find a line parallel to reference_line that bisects the given points.
    """
    if not points_data:
        raise ValueError("Empty points list")
    
    # If reference_line is vertical, we need to bisect y-coordinates
    if abs(reference_line.a) > 0 and abs(reference_line.b) < 1e-9:
        y_values = [point.y for point, _, _ in points_data]
        median_y = sorted(y_values)[len(y_values) // 2]
        return Line(0, 1, -median_y)  # y = median_y
    
    # If reference_line is horizontal, we need to bisect x-coordinates
    if abs(reference_line.a) < 1e-9 and abs(reference_line.b) > 0:
        x_values = [point.x for point, _, _ in points_data]
        median_x = sorted(x_values)[len(x_values) // 2]
        return Line(1, 0, -median_x)  # x = median_x
    
    # For general lines, project points onto a line perpendicular to reference_line
    # and find the median of these projections
    slope = reference_line.slope()
    perpendicular_slope = -1 / slope if slope != 0 else float('inf')
    
    # Function to project a point onto the perpendicular direction
    def project_point(p):
        # For simplicity, we project to a coordinate value that increases
        # as we move perpendicular to the reference line
        # The perpendicular direction vector is (-b, a) for line ax + by + c = 0
        return -reference_line.b * p.x + reference_line.a * p.y
    
    # Get projections
    projections = [(project_point(point), point) for point, _, _ in points_data]
    
    # Find median projection
    sorted_projections = sorted(projections, key=lambda x: x[0])
    median_idx = len(sorted_projections) // 2
    _, median_point = sorted_projections[median_idx]
    
    # Create a line through this point parallel to reference_line
    return create_parallel_line(reference_line, (median_point.x, median_point.y))


def step4_find_parallel_bisector(G1: List[Line], G2: List[Line], k1: int, k2: int,
                               P: ConvexPolygon, g_star: Line, v: ConvexPolygon,
                               matched_pairs: List[Tuple[Point, Line, Line]], above: bool):
    """
    Find a line w* parallel to g* that bisects the matched pairs outside of v.
    Determine which halfplane contains an odd number of intersections.
    """
    # Find points that are outside the halfplane v
    points_outside_v = [pair for pair in matched_pairs 
                       if not v.contains_point((pair[0].x, pair[0].y))]
    
    if not points_outside_v:
        # If all points are in v, we can pick any line parallel to g*
        # For simplicity, use g* itself
        w_star = g_star
    else:
        # Find a line parallel to g* that bisects points outside of v
        w_star = find_bisector_parallel_to_line(points_outside_v, g_star)
    
    # Test whether w* contains an intersection or which halfplane does
    contains_intersection, above_has_odd, below_has_odd = test_line_against_levels(
        G1, G2, k1, k2, P, w_star, above
    )
    
    if contains_intersection:
        return w_star, None, None, None  # Found the ham-sandwich cut!
    
    # Create halfplane w based on which side has odd intersections
    if above_has_odd:
        w = ConvexPolygon()
        w.intersect_half_plane(w_star, True)  # Above w*
    else:
        w = ConvexPolygon()
        w.intersect_half_plane(w_star, False)  # Below w*
    
    # Create vertical lines w' and w" for restricting the region
    # These are described but not explicitly defined in the paper
    # For now, using the min and max x-values of points in v ∩ w
    points_in_v = find_points_in_halfplane(matched_pairs, v)
    points_in_v_and_w = find_points_in_halfplane(points_in_v, w)
    
    if points_in_v_and_w:
        x_values = [point.x for point, _, _ in points_in_v_and_w]
        min_x = min(x_values)
        max_x = max(x_values)
        
        # Create vertical lines at these x-coordinates
        w_prime = Line(1, 0, -min_x)  # x = min_x
        w_double_prime = Line(1, 0, -max_x)  # x = max_x
    else:
        # If no points, use some defaults
        w_prime = None
        w_double_prime = None
    
    return w_star, w, w_prime, w_double_prime


def step5_update_polygon_and_sets(G1: List[Line], G2: List[Line], k1: int, k2: int,
                                P: ConvexPolygon, v: ConvexPolygon, w: ConvexPolygon,
                                w_prime: Optional[Line], w_double_prime: Optional[Line],
                                w_star: Line):
    """
    Update the polygon P and the sets G1 and G2.
    Returns new polygon P, new sets G1' and G2', and new k1' and k2'.
    """
    # Update polygon P = P ∩ v ∩ w ∩ w' ∩ w"
    new_P = ConvexPolygon(P.half_planes.copy())
    
    for halfplane, is_positive in v.half_planes:
        new_P.intersect_half_plane(halfplane, is_positive)
    
    for halfplane, is_positive in w.half_planes:
        new_P.intersect_half_plane(halfplane, is_positive)
    
    if w_prime:
        # We want the right side of w_prime (x > min_x)
        new_P.intersect_half_plane(w_prime, True)
    
    if w_double_prime:
        # We want the left side of w_double_prime (x < max_x)
        new_P.intersect_half_plane(w_double_prime, False)
    
    # Update the sets G1 and G2
    # In a full implementation, we would need to determine which lines intersect the new polygon
    # For simplicity, we'll just filter based on basic criteria
    # Note: This is a simplification; the actual implementation would be more complex
    
    G1_prime = [line for line in G1 if line_intersects_polygon(line, new_P)]
    G2_prime = [line for line in G2 if line_intersects_polygon(line, new_P)]
    
    # Update k1 and k2 based on the side of w*
    # If w* bounds w from below, k1' = k1, k2' = k2
    # Otherwise, k1' = k1 - |G1| + |G1'|, k2' = k2 - |G2| + |G2'|
    if w.half_planes[0][1]:  # If w is the upper half-plane (w* bounds w from below)
        k1_prime = k1
        k2_prime = k2
    else:
        k1_prime = k1 - len(G1) + len(G1_prime)
        k2_prime = k2 - len(G2) + len(G2_prime)
    
    return new_P, G1_prime, G2_prime, k1_prime, k2_prime


def line_intersects_polygon(line: Line, polygon: ConvexPolygon) -> bool:
    """
    Check if a line intersects the polygon.
    This is a simplified version; in reality, we'd need to compute actual intersections.
    """
    # For simplicity, we'll check if the line might intersect the polygon
    # In a full implementation, we would compute the actual intersection
    return True  # Placeholder


def ham_sandwich_cut(H1: List[Line], H2: List[Line]) -> Line:
    """
    Find a ham-sandwich cut for two sets of lines H1 and H2.
    """
    # Ensure lines are in general position and n1 ≤ n2
    n1 = len(H1)
    n2 = len(H2)
    
    if n1 > n2:
        H1, H2 = H2, H1
        n1, n2 = n2, n1
    
    # Make n1 and n2 odd (as required by the algorithm)
    if n1 % 2 == 0:
        H1 = H1[:-1]
        n1 -= 1
    
    if n2 % 2 == 0:
        H2 = H2[:-1]
        n2 -= 1
    
    # Initialize algorithm parameters
    G1 = H1.copy()
    G2 = H2.copy()
    k1 = (n1 + 1) // 2
    k2 = (n2 + 1) // 2
    P = ConvexPolygon()  # Initially the entire plane
    above = True  # Initial value doesn't matter as we haven't restricted P yet
    
    max_iterations = 100  # Safety check to avoid infinite loops
    iteration = 0
    
    while iteration < max_iterations and (len(G1) + len(G2) > 10):  # Arbitrary threshold
        iteration += 1
        
        # Step 1: Find median slope line
        g_star, G_plus, G_minus = step1_find_median_slope(G1, G2)
        
        # Step 2: Match lines in G- with lines in G+
        matched_pairs = step2_match_lines(G_plus, G_minus)
        
        # Step 3: Find vertical bisector
        v_star, v = step3_find_vertical_bisector(G1, G2, k1, k2, P, matched_pairs, above)
        
        if v is None:
            return v_star  # Found the ham-sandwich cut
        
        # Step 4: Find parallel bisector
        w_star, w, w_prime, w_double_prime = step4_find_parallel_bisector(
            G1, G2, k1, k2, P, g_star, v, matched_pairs, above
        )
        
        if w is None:
            return w_star  # Found the ham-sandwich cut
        
        # Step 5: Update polygon and sets
        P, G1, G2, k1, k2 = step5_update_polygon_and_sets(
            G1, G2, k1, k2, P, v, w, w_prime, w_double_prime, w_star
        )
        
        # Update 'above' for the next iteration
        # In a full implementation, we would determine this based on the leftmost point of Lk1(G1) in P
        # For now, using a placeholder
        above = not above
    
    # If we reach here, we have a small problem remaining
    # We can solve it using brute force or a simpler method
    # For simplicity, let's find all intersections of levels and test each
    
    # This would be the final fallback implementation
    # In practice, we would implement a proper brute force solution here
    # For now, return the most recent w_star as a placeholder
    return w_star



if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    import random
    
    # Import classes and functions from previous modules
    # Assume all code from previous artifacts is in the same file or imported
    
    # Generate two sets of random points
    def generate_random_points(n, x_range=(-100, 100), y_range=(-100, 100)):
        points = []
        for _ in range(n):
            x = random.uniform(*x_range)
            y = random.uniform(*y_range)
            points.append((x, y))
        return points
    
    # Convert points to lines using point-line duality
    # In the standard dual, a point (a, b) maps to the line y = ax - b
    # or in the form ax - y - b = 0
    def points_to_dual_lines(points):
        lines = []
        for x, y in points:
            # Line corresponding to point (x, y) is: y' = x*x' - y
            # In ax + by + c = 0 form: x*x' - y' - y = 0
            lines.append(Line(x, -1, -y))
        return lines
    
    # Convert a line back to a point in the dual space
    # A line ax + by + c = 0 with b != 0 corresponds to the point (-a/b, -c/b)
    def line_to_dual_point(line):
        if abs(line.b) < 1e-9:
            # Vertical line case, map to point at infinity
            return None
        return (-line.a / line.b, -line.c / line.b)
    
    # Generate two sets of points
    n1 = 11  # Odd number for simplicity
    n2 = 15  # Odd number
    points_set1 = generate_random_points(n1, (-5, 5), (-5, 5))
    points_set2 = generate_random_points(n2, (-5, 5), (-5, 5))
    
    # Convert points to dual lines
    H1 = points_to_dual_lines(points_set1)
    H2 = points_to_dual_lines(points_set2)
    
    print(f"Generated {len(points_set1)} points for set 1")
    print(f"Generated {len(points_set2)} points for set 2")
    
    # Find ham sandwich cut
    print("Running ham sandwich algorithm...")
    ham_sandwich_line = ham_sandwich_cut(H1, H2)
    print(f"Ham sandwich cut: {ham_sandwich_line}")
    
    # Plot the points and the ham sandwich line
    plt.figure(figsize=(10, 8))
    
    # Plot points from set 1
    x1, y1 = zip(*points_set1)
    plt.scatter(x1, y1, color='blue', label='Set 1')
    
    # Plot points from set 2
    x2, y2 = zip(*points_set2)
    plt.scatter(x2, y2, color='red', label='Set 2')
    
    # Plot the ham sandwich cut line
    if ham_sandwich_line:
        # Create points for the line to plot
        x_min, x_max = plt.xlim()
        if abs(ham_sandwich_line.b) < 1e-9:  # Vertical line
            x_line = [-ham_sandwich_line.c / ham_sandwich_line.a] * 2
            y_line = [plt.ylim()[0], plt.ylim()[1]]
        else:
            x_line = [x_min, x_max]
            # Convert ax + by + c = 0 to y = mx + b
            # y = -ax/b - c/b
            y_line = [(-ham_sandwich_line.a * x - ham_sandwich_line.c) / ham_sandwich_line.b 
                     for x in x_line]
        
        plt.plot(x_line, y_line, 'g-', label='Ham Sandwich Cut')
    
    # Count points on each side of the line
    def count_points_relative_to_line(points, line):
        above = 0
        on = 0
        below = 0
        for p in points:
            if line.is_above(p):
                above += 1
            elif line.is_on(p):
                on += 1
            else:
                below += 1
        return above, on, below
    
    above1, on1, below1 = count_points_relative_to_line(points_set1, ham_sandwich_line)
    above2, on2, below2 = count_points_relative_to_line(points_set2, ham_sandwich_line)
    
    print(f"Set 1: {above1} points above, {on1} points on, {below1} points below")
    print(f"Set 2: {above2} points above, {on2} points on, {below2} points below")
    
    # Add this information to the plot title
    plt.title(f"Ham Sandwich Cut\nSet 1: {above1} above, {on1} on, {below1} below | Set 2: {above2} above, {on2} on, {below2} below")
    
    plt.grid(True)
    plt.legend()
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('ham_sandwich_result.png')
    plt.show()