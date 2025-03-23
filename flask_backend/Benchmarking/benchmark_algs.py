
import timeit

from matplotlib import pyplot as plt
import numpy as np
from flask_backend.ham_sandwich_cuts.BruteForce.HamSandwichBruteForce import find_line_through_points_with_dual_intersection_brute, find_line_through_points_with_dual_intersection_brute_no_numpy
from flask_backend.ham_sandwich_cuts.ExistingProjects.Existing_Project_Viz.Cuts import LinearPlanarCut
from flask_backend.ham_sandwich_cuts.ExistingProjects.Existing_Project_Viz.GeomUtils import random_point_set
from flask_backend.ham_sandwich_cuts.ExistingProjects.Existing_Project_Viz.IOUtils import HamInstance


def test_algorithms(num_tests=50, num_runs=3):
    # Collect results for each algorithm as dictionaries
    brute_times = {}
    ortools_times = {}
    planar_cut_times = {}
    brute_no_numpy_times = {}

    # Loop through each size from 100 to num_tests (step 25)
    for size in range(100, num_tests + 1, 25):
        print(f"Running tests for input size: {size}")

        brute_time_list = []
        brute_no_numpy_time_list = []
        ortools_time_list = []
        planar_cut_time_list = []

        # Run each test 'num_runs' times and calculate the average
        for _ in range(num_runs):
            try:
                # Generate random points of the given size
                red_points = [[point.x, point.y] for point in random_point_set(size)]
                blue_points = [[point.x, point.y] for point in random_point_set(size)]

                # Measure time for brute force algorithm
                brute_time = timeit.timeit(
                    lambda: find_line_through_points_with_dual_intersection_brute(red_points, blue_points), number=1
                )
                brute_time_list.append(brute_time)

                # Measure time for brute force (no numpy)
                brute_no_numpy_time = timeit.timeit(
                    lambda: find_line_through_points_with_dual_intersection_brute_no_numpy(red_points, blue_points), number=1
                )
                brute_no_numpy_time_list.append(brute_no_numpy_time)

                # Measure time for planar cut
                NewCut = HamInstance(red_points=red_points, blue_points=blue_points, plot_constant=1)
                LPC = LinearPlanarCut(0.5)
                planar_cut_time = timeit.timeit(lambda: LPC.cut(NewCut), number=1)
                planar_cut_time_list.append(planar_cut_time)

                # Placeholder for ortools (not implemented in this example)
                ortools_time_list.append(100)

            except Exception as e:
                # If any function raises an error, skip this run
                continue

        # Average the times for each algorithm and store in dictionaries
        if brute_time_list:
            brute_times[size] = np.mean(brute_time_list)
        if ortools_time_list:
            ortools_times[size] = np.mean(ortools_time_list)
        if planar_cut_time_list:
            planar_cut_times[size] = np.mean(planar_cut_time_list)
        if brute_no_numpy_time_list:
            brute_no_numpy_times[size] = np.mean(brute_no_numpy_time_list)

    return brute_times, ortools_times, planar_cut_times, brute_no_numpy_times


# Run the tests and collect the results
num_tests = 1500  # max size of the point set
brute_times, ortools_times, planar_cut_times, brute_no_numpy_times = test_algorithms(num_tests)

# Plot the results
def plot_times(brute_times, ortools_times, planar_cut_times, brute_no_numpy_times):
    # Extract sizes and times from dictionaries
    brute_sizes = list(brute_times.keys())
    brute_values = list(brute_times.values())

    ortools_sizes = list(ortools_times.keys())
    ortools_values = list(ortools_times.values())

    planar_cut_sizes = list(planar_cut_times.keys())
    planar_cut_values = list(planar_cut_times.values())

    brute_no_numpy_sizes = list(brute_no_numpy_times.keys())
    brute_no_numpy_values = list(brute_no_numpy_times.values())

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(brute_sizes, brute_values, label="Brute Force", color='red', marker='o')
    plt.plot(planar_cut_sizes, planar_cut_values, label="Linear Planar Cut", color='green', marker='^')
    plt.plot(brute_no_numpy_sizes, brute_no_numpy_values, label="Brute Force (No NumPy)", color='purple', marker='x')
    # Uncomment if ORTools times are implemented
    # plt.plot(ortools_sizes, ortools_values, label="ORTools Extended", color='blue', marker='s')

    # Add labels, title, and legend
    plt.xlabel('Number of Points')
    plt.ylabel('Average Execution Time (seconds)')
    plt.title('Algorithm Runtime Comparison (Averaged Over 3 Runs)')
    plt.legend()
    plt.grid(True)
    plt.show()

# Plot the results
plot_times(brute_times, ortools_times, planar_cut_times, brute_no_numpy_times)