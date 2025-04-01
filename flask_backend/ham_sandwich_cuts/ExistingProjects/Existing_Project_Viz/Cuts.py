import math
from random import choice

from .GeomUtils import *

from shapely import MultiPoint
from shapely.geometry import Point
from shapely.geometry.linestring import LineString as LineStringEmpty

class LinearPlanarCut:
    def __init__(self, min_interval=1):
        self.min_interval = min_interval

    def cut(self, ham_instance):
        self.ham_instance = ham_instance
        x_min, x_max = find_x_bounds(self.ham_instance.all_points)
        self.interval = Interval(x_min - 40, x_max + 40)

        while len(self.interval) > self.min_interval:
            lint, rint = self._split_interval(self.interval)

            if self._odd_intersection(lint):
                self.interval = lint
            else:
                self.interval = rint

        return self.median_intersection()

    def teach(self, ham_instance, steps_taken=None):
        self.ham_instance = ham_instance
        x_min, x_max = find_x_bounds(self.ham_instance.all_points)
        self.interval = Interval(x_min - 5, x_max + 5)

        self._show_interval(self.ham_instance, self.interval)

        steps_taken.append({
            "id": len(steps_taken) + 1,
            "type": "binary_search",
            "description": "Perform binary search to find the cut.",
            "data": {"interval": {"start": self.interval.l, "end": self.interval.r}},
        })
        
        while len(self.interval) > self.min_interval:
            lint, rint = self._split_interval(self.interval)
            self._show_interval(
                self.ham_instance, lint, steps_taken=steps_taken, side="left"
            )

            self._show_interval(
                self.ham_instance, rint, steps_taken=steps_taken, side="right"
            )

            if self._odd_intersection(lint):
                self.interval = lint
                chosen_side = "left"
            else:
                self.interval = rint
                chosen_side = "right"

            steps_taken.append(
                {
                    "id": len(steps_taken) + 1,
                    "type": "iteration_step",
                    "description": f"Iterate on the {chosen_side} half.",
                    "data": {
                        "interval": {"start": self.interval.l, "end": self.interval.r},
                        "chosenSide": chosen_side,
                    },
                }
            )

            self._show_interval(self.ham_instance, self.interval)

        cut = self.median_intersection()
        
        if cut[0] == "vertical":
            steps_taken.append(
                {
                    "id": len(steps_taken) + 1,
                    "type": "compute_cut",
                    "description": "Compute the cut.",
                    "data": {"cut": {"is_vertical": True, "x_intercept": cut[1]}},
                }
            )
        else:
            slope, intercept = cut[1]
            steps_taken.append(
                {
                    "id": len(steps_taken) + 1,
                    "type": "compute_cut",
                    "description": "Compute the cut.",
                    "data": {"cut": {"slope": slope, "intercept": intercept, "is_vertical": False}},
                }
            )

        return cut

    def all_ham_cuts(self, ham_instance):
        # plt.gca().clear()
        self.ham_instance = ham_instance
        x_min, x_max = find_x_bounds(self.ham_instance.all_points)
        self.interval = Interval(x_min - 40, x_max + 40)
        y_min, y_max = find_y_bounds(ham_instance.all_points)
        # prepare_axis(self.interval.l-1, self.interval.r+1, y_min-5,y_max+5)
        self.intervalymin = y_min
        self.intervalymax = y_max

        # plt.title('Points and Duals')
        # plot_points_and_duals(ham_instance,0.1)
        # plt.pause(0.5)
        self.median_intersection()

    def median_intersection(self):
        red_intersections = self._get_intersections(self.ham_instance.red_duals)
        blue_intersections = self._get_intersections(self.ham_instance.blue_duals)

        red_med_linestring = self._get_med_linestring(
            self.ham_instance.red_duals, red_intersections, color="r"
        )
        blue_med_linestring = self._get_med_linestring(
            self.ham_instance.blue_duals, blue_intersections, color="b"
        )

        ham_points = red_med_linestring.intersection(blue_med_linestring)

        if isinstance(ham_points, (Point, MultiPoint)):
            ham_points = ham_points.geoms[0] if isinstance(ham_points, MultiPoint) else ham_points  

            # print("ham_points:", ham_points)  

            line = compute_dual_line(ham_points, constant=self.ham_instance.plot_constant)
            
            return "non-vertical", (line.m, line.b)

        elif isinstance(ham_points, (LineString, LineStringEmpty) or ham_points.is_empty):
            # In the case where the cut is a vertical line
            def get_dual_point(line): 
                x1, y1 = line.coords[0]
                x2, y2  = line.coords[1]
                
                a = (y2-y1)/(x2-x1)
                b = y1 - a * x1
                
                # dual point = (a, -b)                    
                return (a, -b)
                        
            dual_point_1 = get_dual_point(red_med_linestring)
            dual_point_2 = get_dual_point(blue_med_linestring)
            # print(dual_point_1, dual_point_2)
            
            # Check if the two dual points are on a vertical line (i.e., the x-coordinates are the same)
            if dual_point_1[0] == dual_point_2[0]:  # x-coordinates are the same
                # The equation of the vertical line would be x = dual_point_1[0]
                # print(f"The equation of the vertical line is: x = {dual_point_1[0]}")
                return "vertical", dual_point_1[0]
        else:
            print("\n\n")
            print("ham points: ", ham_points, type(ham_points), ham_points.is_empty)
            print("red_med_linestring: ", red_med_linestring)
            print("blue_med_linestring: ", blue_med_linestring)
            print("\n\n")
            

    def _show_interval(self, ham_instance, interval, steps_taken=None, side=None):
        l_red_med = self._find_median_level(interval.l, ham_instance.red_duals)
        l_blue_med = self._find_median_level(interval.l, ham_instance.blue_duals)

        r_red_med = self._find_median_level(interval.r, ham_instance.red_duals)
        r_blue_med = self._find_median_level(interval.r, ham_instance.blue_duals)

        interval_medians = [
            Point(interval.l, l_red_med),
            Point(interval.l, l_blue_med),
            Point(interval.r, r_red_med),
            Point(interval.r, r_blue_med),
        ]

        y_min, y_max = find_y_bounds(ham_instance.all_points + interval_medians)
        # prepare_axis(interval.l-5, interval.r+5, y_min-5,y_max+5)
        self.intervalymin = y_min
        self.intervalymax = y_max

        # plot_interval(interval)
        # plt.pause(0.5)

        # plot_point(interval_medians[0],marker='*',color='r',size=15)
        # plot_point(interval_medians[1],marker='*',color='b',size=15)
        # plot_point(interval_medians[2],marker='*',color='r',size=15)
        # plot_point(interval_medians[3],marker='*',color='b',size=15)

        if steps_taken and side:
            has_odd_intersection = self._odd_intersection(interval)

            steps_taken.append(
                {
                    "id": len(steps_taken) + 1,
                    "type": "interval_check",
                    "description": f"Check the {side} half of the interval.",
                    "data": {
                        "intervalMedians": [
                            {
                                "x": interval_medians[0].x,
                                "y": interval_medians[0].y,
                                "color": "red",
                            },
                            {
                                "x": interval_medians[1].x,
                                "y": interval_medians[1].y,
                                "color": "blue",
                            },
                            {
                                "x": interval_medians[2].x,
                                "y": interval_medians[2].y,
                                "color": "red",
                            },
                            {
                                "x": interval_medians[3].x,
                                "y": interval_medians[3].y,
                                "color": "blue",
                            },
                        ],
                        "interval": {"start": interval.l, "end": interval.r},
                        "oddIntersectionProperty": has_odd_intersection,
                    },
                }
            )

    def _get_intersections(self, duals):

        intersections = []
        for i in range(len(duals)):
            for j in range(len(duals)):
                if (not i == j) and (i < j):
                    d1 = duals[i]
                    d2 = duals[j]
                    new_inter = Intersection(d1, d2)
                    if new_inter.x == np.inf:
                        pass
                    elif (
                        self.interval.l < new_inter.x and self.interval.r > new_inter.x
                    ):
                        intersections.append(new_inter)
                    else:
                        pass
        intersections.sort(key=lambda I: I.x)
        return intersections

    def _get_med_linestring(self, duals, intersections, color):

        med_levels = [
            Point(self.interval.l, self._find_median_level(self.interval.l, duals))
        ]
        med_levels.extend(
            [Point(i.x, self._find_median_level(i.x, duals)) for i in intersections]
        )
        med_levels.extend(
            [Point(self.interval.r, self._find_median_level(self.interval.r, duals))]
        )

        # for i in range(0,len(med_levels)-1):
        #     plot_line_segment(LineSegment(med_levels[i], med_levels[i+1]), color=color)
        # plt.pause(0.5)

        return LineString(med_levels)

    def _get_intervals(self, interval):
        # returns two new intervals
        intersections = []
        for i in self.ham_instance.intersections:
            if interval.l <= i.x and interval.r >= i.x:
                intersections.append(i)
        random_intersection = choice(intersections)
        return Interval(interval.l, random_intersection.x), Interval(
            random_intersection.x, interval.r
        )

    def _split_interval(self, interval):
        mid = float((interval.l + interval.r) / 2.0)
        return Interval(interval.l, mid), Interval(mid, interval.r)

    def _odd_intersection(self, interval):
        l = interval.l
        r = interval.r

        lmr = self._find_median_level(l, self.ham_instance.red_duals)
        lmb = self._find_median_level(l, self.ham_instance.blue_duals)

        rmr = self._find_median_level(r, self.ham_instance.red_duals)
        rmb = self._find_median_level(r, self.ham_instance.blue_duals)

        return (lmr - lmb) * (rmr - rmb) < 0

    def _find_median_level(self, x, lines):
        y_vals = [line.b + (x * line.m) for line in lines]
        y_vals.sort()
        med = math.floor((len(y_vals) + 1) / 2)
        return y_vals[med - 1]
