import random
import numpy as np
from shapely.geometry import Point, LineString
from numpy.linalg import det

class Line:
    def __init__(self, m=None, b=None, vertical=False, x_intercept=None):
        if vertical and x_intercept is None:
            raise ValueError("Vertical lines must have an x_intercept.")
        self.m = m
        self.b = b
        self.vertical = vertical
        self.x_intercept = x_intercept

    def to_dict(self):
        if self.vertical:
            return {'vertical': True, 'x_intercept': self.x_intercept}
        return {'m': self.m, 'b': self.b}

class LineSegment:
    def __init__(self,point1,point2):
        self.p1 = point1
        self.p2 = point2

    def __str__(self):
        return 'LineSegment ({},{})'.format(self.p1, self.p2)
    
    def to_dict(self):
        return {"p1": self.p1, "p2": self.p2}

class Interval:
    def __init__(self,l,r):
        self.l = l
        self.r = r
        assert l < r 

    def __str__(self):
        return 'Interval from {} to {}'.format(self.l, self.r)

    def __len__(self):
        return int(self.r - self.l)

    def to_dict(self):
        return {"l": self.l, "r": self.r, "length": len(self)}

class Intersection:
    def __init__(self, line1, line2):
        if line1.m == line2.m:
            self.x = np.inf
            self.y = np.inf
        else:
            self.x = (line2.b - line1.b) / (line1.m - line2.m)
            self.y = line1.m * self.x + line1.b

def find_x_bounds(point_set):
    """Find min and max x
    
    Arguments:
        point_set {array of shapely.geometry.Point} -- set of points
    """
    min_x = min(point_set, key=lambda P: P.x).x
    max_x = max(point_set, key=lambda P: P.x).x
    return min_x, max_x
    
def find_y_bounds(point_set):
    """Find min and max y
    
    Arguments:
        point_set {array of shapely.geometry.Point} -- set of points
    """
    min_y = min(point_set, key=lambda P: P.y).y
    max_y = max(point_set, key=lambda P: P.y).y
    return min_y, max_y

def compute_dual_line(P, constant=1):
    """Compute dual of a point
    
    Arguments:
        P {shapely.geometry.Point}
    """
    return Line(constant*P.x, -P.y)

def random_point(lower_bound=-10, upper_bound=10):
    assert lower_bound <= upper_bound
    x = random.uniform(lower_bound, upper_bound)
    y = random.uniform(lower_bound,upper_bound)
    return Point(x,y)

def random_point_set(n, lower_bound=-10, upper_bound=10):
    points = []
    for i in range(n):
        points.append(random_point(lower_bound, upper_bound))
    return points