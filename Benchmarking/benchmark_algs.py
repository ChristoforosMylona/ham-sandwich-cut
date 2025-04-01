import sys
import os
import timeit
from datetime import datetime
import json
from matplotlib import pyplot as plt
import numpy as np

# Dynamically determine the project path and add it to sys.path
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_path not in sys.path:
    sys.path.append(project_path)

from flask_backend.ham_sandwich_cuts.ExistingProjects.Existing_Project_Viz.GeomUtils import random_point_set

import timeit

def test_algorithms(start=5, end=500, step=25, num_runs=3, functions_to_test=None):
    # Collect results for each algorithm as dictionaries
    brute_times = {}
    ortools_times = {}
    planar_cut_times = {}
    brute_no_numpy_times = {}

    # Loop through each size from start to end (step)
    for size in range(start, end + 1, step):
        print(f"Running tests for input size: {size}")

        brute_time_list = []
        brute_no_numpy_time_list = []
        ortools_time_list = []
        planar_cut_time_list = []

        # Generate random points of the given size (setup code)
        red_points = [[point.x, point.y] for point in random_point_set(size)]
        blue_points = [[point.x, point.y] for point in random_point_set(size)]

        # Test planar cut
        if "planar" in functions_to_test:
            timer = timeit.Timer(
                stmt="LPC.cut(NewCut)",
                setup=(
                    "from flask_backend.ham_sandwich_cuts.ExistingProjects.Existing_Project_Viz.Cuts import LinearPlanarCut; "
                    "from flask_backend.ham_sandwich_cuts.ExistingProjects.Existing_Project_Viz.IOUtils import HamInstance; "
                    f"red_points = {red_points}; blue_points = {blue_points}; "
                    "NewCut = HamInstance(red_points=red_points, blue_points=blue_points, plot_constant=1); "
                    "LPC = LinearPlanarCut(0.5)"
                ),
            )
            planar_cut_time_list.append(timer.timeit(number=num_runs) / num_runs)

        # Test brute force algorithm
        if "brute" in functions_to_test:
            timer = timeit.Timer(
                stmt="find_line_through_points_with_dual_intersection_brute(red_points, blue_points)",
                setup=(
                    "from flask_backend.ham_sandwich_cuts.BruteForce.HamSandwichBruteForce import "
                    "find_line_through_points_with_dual_intersection_brute; "
                    f"red_points = {red_points}; blue_points = {blue_points}"
                ),
            )
            brute_time_list.append(timer.timeit(number=num_runs) / num_runs)

        # Test brute force (no numpy)
        if "brute_no_numpy" in functions_to_test:
            timer = timeit.Timer(
                stmt="find_line_through_points_with_dual_intersection_brute_no_numpy(red_points, blue_points)",
                setup=(
                    "from flask_backend.ham_sandwich_cuts.BruteForce.HamSandwichBruteForce import "
                    "find_line_through_points_with_dual_intersection_brute_no_numpy; "
                    f"red_points = {red_points}; blue_points = {blue_points}"
                ),
            )
            brute_no_numpy_time_list.append(timer.timeit(number=num_runs) / num_runs)



        # Placeholder for ortools (not implemented in this example)
        if "ortools" in functions_to_test:
            timer = timeit.Timer(
                stmt="find_line_through_points_ortools_extended(red_points, blue_points)",
                setup=("from flask_backend.ham_sandwich_cuts.MLP.HamSandwichMLP import find_line_through_points_ortools_extended; "
                       f"red_points = {red_points}; blue_points = {blue_points}")
            )
            ortools_time_list.append(timer.timeit(number=num_runs) / num_runs)

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


def save_results_to_file(results):
    # Generate a filename with the current datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}.json"

    # Define the Results directory path
    results_dir = os.path.join(os.path.dirname(__file__), "Results")

    # Ensure the directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Full filepath inside the Results directory
    filepath = os.path.join(results_dir, filename)

    # Save the results as a JSON file
    with open(filepath, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Results saved to {filepath}")


# Main execution
if __name__ == "__main__":
    # Default parameters
    start = 100
    end = 1500
    step = 25
    num_runs = 3  # Default number of runs
    functions_to_test = {"brute", "ortools", "planar", "brute_no_numpy"}  # Default to all functions

    # Parse command-line arguments
    for arg in sys.argv[1:]:
        if arg.startswith("start="):
            start = int(arg.split("=")[1])
        elif arg.startswith("end="):
            end = int(arg.split("=")[1])
        elif arg.startswith("step="):
            step = int(arg.split("=")[1])
        elif arg.startswith("runs="):
            num_runs = int(arg.split("=")[1])
        elif arg.startswith("functions="):
            functions_to_test = set(arg.split("=")[1].split(","))

    # Run the tests and collect the results
    brute_times, ortools_times, planar_cut_times, brute_no_numpy_times = test_algorithms(
        start, end, step, num_runs=num_runs, functions_to_test=functions_to_test
    )

    # Save the results to a file
    results = {
        "brute_times": brute_times,
        "ortools_times": ortools_times,
        "planar_cut_times": planar_cut_times,
        "brute_no_numpy_times": brute_no_numpy_times,
    }
    save_results_to_file(results)

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
        if brute_times:
            plt.plot(brute_sizes, brute_values, label="Brute Force", color='red', marker='o')
        if planar_cut_times:
            plt.plot(planar_cut_sizes, planar_cut_values, label="Linear Planar Cut", color='green', marker='^')
        if brute_no_numpy_times:
            plt.plot(brute_no_numpy_sizes, brute_no_numpy_values, label="Brute Force (No NumPy)", color='purple', marker='x')
        if ortools_times:
            plt.plot(ortools_sizes, ortools_values, label="ORTools Extended", color='blue', marker='s')

        # Add labels, title, and legend
        plt.xlabel('Number of Points')
        plt.ylabel('Average Execution Time (seconds)')
        plt.title('Algorithm Runtime Comparison (Averaged Over 3 Runs)')
        plt.legend()
        plt.grid(True)
        plt.show()

    plot_times(brute_times, ortools_times, planar_cut_times, brute_no_numpy_times)