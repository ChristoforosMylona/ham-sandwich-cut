import random
import numpy as np
from pprint import pprint
import math


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
        return f"y = {self.slope}x +{self.intercept})"

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
                return "The lines are coincident (infinitely many intersection points)."
            else:
                return "The lines are parallel (no intersection)."
        else:
            x = (other.intercept - self.intercept) / (self.slope - other.slope)
            y = self.slope * x + self.intercept
            return Point(x, y)


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


def quickselect_median_line(lines, pivot_fn=random.choice):
    if len(lines) % 2 == 1:
        return quickselect_line(lines, len(lines) // 2, pivot_fn)
    else:
        return 0.5 * (
            quickselect_line(lines, len(lines) // 2 - 1, pivot_fn).slope
            + quickselect_line(lines, len(lines) // 2, pivot_fn).slope
        )


def quickselect_line(lines, k, pivot_fn):
    """
    Select the kth element in lines (0 based), based on slope
    :param lines: List of Line objects
    :param k: Index
    :param pivot_fn: Function to choose a pivot, defaults to random.choice
    :return: The kth element (based on slope) of lines
    """
    if len(lines) == 1:
        assert k == 0
        return lines[0]

    # Choose a pivot based on the slope of the Line objects
    pivot = pivot_fn(lines)

    # Partition the lines into those with slope less than, greater than, or equal to the pivot's slope
    lows = [line for line in lines if line.slope < pivot.slope]
    highs = [line for line in lines if line.slope > pivot.slope]
    pivots = [line for line in lines if line.slope == pivot.slope]

    if k < len(lows):
        return quickselect_line(lows, k, pivot_fn)
    elif k < len(lows) + len(pivots):
        # We found the pivot as the median
        return pivots[0]
    else:
        return quickselect_line(highs, k - len(lows) - len(pivots), pivot_fn)


def quickselect_median(l, pivot_fn=random.choice):
    if len(l) % 2 == 1:
        return quickselect(l, len(l) // 2, pivot_fn)
    else:
        return 0.5 * (
            quickselect(l, len(l) / 2 - 1, pivot_fn)
            + quickselect(l, len(l) / 2, pivot_fn)
        )


def quickselect(l, k, pivot_fn):
    """
    Select the kth element in l (0 based)
    :param l: List of numerics
    :param k: Index
    :param pivot_fn: Function to choose a pivot, defaults to random.choice
    :return: The kth element of l
    """
    if len(l) == 1:
        assert k == 0
        return l[0]

    pivot = pivot_fn(l)

    lows = [el for el in l if el < pivot]
    highs = [el for el in l if el > pivot]
    pivots = [el for el in l if el == pivot]

    if k < len(lows):
        return quickselect(lows, k, pivot_fn)
    elif k < len(lows) + len(pivots):
        # We got lucky and guessed the median
        return pivots[0]
    else:
        return quickselect(highs, k - len(lows) - len(pivots), pivot_fn)


# Setp 1

# Set P_t with postitive slopes
P_k_set = [
    Line(np.clip(slope, a_min=0.1, a_max=999), np.random.uniform(-10, 10))
    for slope in np.random.uniform(1, 5, 5)
]

# Set Q_t with negative slopes
Q_t_set = [
    Line(np.clip(slope, a_max=-0.1, a_min=-999), np.random.uniform(-10, 10))
    for slope in np.random.uniform(-5, -1, 5)
]

active = P_k_set + Q_t_set

N = len(active)

# calculcate the median slope of the lines
median_slope = quickselect_median_line(active)

# lines with slope > median
P = set()

# lines with slope < median
Q = set()

# split the lines based on < and > slope than the median
for line in active:
    if line.slope < median_slope:
        Q.add(line)
    elif line.slope > median_slope:
        P.add(line)

# Make pairs of lines with slope < median with lines > median
pairs = set()

for l1, l2 in zip(P, Q):
    pairs.add(Pair(l1, l2))

# Calculate the intercepts for each pair
intercepts = []

for p in pairs:
    intercepts.append(p.get_intercept().x)

# Calculate the median x value of the intercepts
median_x = quickselect_median(intercepts)

# Now to test the line x = median_x in the line query


def quickselect_kth_largest(lines, k, x_val, pivot_fn=random.choice) -> Line:
    """
    Returns the k-th largest line when evaluated at x_val
    :param lines: List of Line objects
    :param k: The k-th largest element to find (0-based, so k=0 returns the largest)
    :param x_val: The x value at which to evaluate the lines
    :param pivot_fn: Function to choose a pivot, defaults to random.choice
    :return: The k-th largest Line object when evaluated at x_val
    """

    # might need to delete this, not sure
    k = k + 1

    # Define the evaluation of a line at x_val
    def evaluate_line(line):
        return line.slope * x_val + line.intercept

    # Helper function to select the k-th largest line
    def quickselect(arr, k, pivot_fn):
        if len(arr) == 1:
            assert k == 0
            return arr[0]

        pivot = pivot_fn(arr)
        pivot_value = evaluate_line(pivot)

        # Partition the array based on the pivot_value
        lows = [line for line in arr if evaluate_line(line) < pivot_value]
        highs = [line for line in arr if evaluate_line(line) > pivot_value]
        pivots = [line for line in arr if evaluate_line(line) == pivot_value]

        if k < len(highs):
            return quickselect(highs, k, pivot_fn)
        elif k < len(highs) + len(pivots):
            # We found the k-th largest element
            return pivots[0]
        else:
            return quickselect(lows, k - len(highs) - len(pivots), pivot_fn)

    # Call quickselect to find the k-th largest line
    return quickselect(lines, k, pivot_fn)


# test line is just a number, since it's a straight vertical line (x = test_line)
def line_query(test_line: float, P: list[Line], Q, k, t):
    """
    Return the intersection point of the quantile-function
    :param test_line: int - a line x = median_x
    :param P: active lines with slope > median
    :param Q: active lines with slope < median
    :param k: The kth line in P is chosen
    :param r: The rth line in Q is chosen
    :return: The intersection point
    """

    print(k, "\t", test_line)
    for p in P:
        print(p, "computed: ", p.compute(test_line))
    print()

    # find kth largest of P
    P_k_x = quickselect_kth_largest(list(P), k, test_line)
    print(P_k_x)
    print()

    # find t largets of Q
    Q_t_x = quickselect_kth_largest(list(Q), t, test_line)

    # (x*, y*)
    intersection = P_k_x.intersection(Q_t_x)
    print(intersection)
    return intersection


intersection = line_query(
    median_x, P, Q, math.floor(len(P) / 2), math.floor(len(Q) / 2)
)


def line_query_with_slope(test_line: Line, P: list[Line], Q, k, t):
    kth_largets = quickselect_kth_largest(P, x, k)
    tth_largest = quickselect_kth_largest(Q, x, t)

    intersection = kth_largets.intersection(tth_largest)


if intersection.x > median_x:
    print("x* > x'")
elif median_x == intersection.x:
    print("equal to x*")
else:
    print("x* < x'")
    # consider pairs whose intersections are x values greater or equal to median_x

    considered = []

    for pair in pairs:
        if pair.get_intercept().x >= median_x:
            considered.append(pair)

    # print(considered)

    # the second line to query is one with a slope of median_slope that divides the intersection points in half
    # the intercept is the median of the set { y - sx}, where (x,y) runs over the intersection points still under consideration

    second_line_intercepts_list = []
    for pair in considered:
        inter = pair.get_intercept()

        second_line_intercepts_list.append(inter.y - median_slope * inter.x)

    y_inter = quickselect_median(second_line_intercepts_list)
    second_line = Line(median_slope, y_inter)
    print("second_line: ", second_line)

    # test this line to identify a quadrant Q in which x*, y* lies
