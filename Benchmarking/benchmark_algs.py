import argparse
import statistics
import sys
import os
import time
import timeit
from datetime import datetime
import json
from matplotlib import pyplot as plt
import numpy as np


# Dynamically add the `src` folder to the Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.append(src_path)

from flask_backend.ham_sandwich_cuts.ExistingProjects.Existing_Project_Viz.Cuts import LinearPlanarCut
from flask_backend.ham_sandwich_cuts.ExistingProjects.Existing_Project_Viz.IOUtils import HamInstance
from flask_backend.ham_sandwich_cuts.MLP.HamSandwichMLP import find_line_through_points_ortools_extended
from flask_backend.ham_sandwich_cuts.BruteForce.HamSandwichBruteForce import find_line_through_points_with_dual_intersection_brute, find_line_through_points_with_dual_intersection_brute_no_numpy
from flask_backend.ham_sandwich_cuts.ExistingProjects.Existing_Project_Viz.GeomUtils import (
    random_point_set,
)


def load_or_generate_points(file_path, size, num_runs):
    """
    Load points from a file or generate new ones if not enough exist for the given size and num_runs.

    Parameters:
        file_path (str): Path to the file storing the points.
        size (int): Number of points per set.
        num_runs (int): Number of sets required.

    Returns:
        list: A list of dictionaries containing red and blue points.
    """
    # Ensure the file exists and load existing data
    if not os.path.exists(file_path):
        points_data = {}
    else:
        with open(file_path, "r") as f:
            points_data = json.load(f)

    # Check if there are enough points for the given size
    if str(size) not in points_data or len(points_data[str(size)]) < num_runs:
        # Generate additional points if needed
        existing_points = points_data.get(str(size), [])
        additional_runs = num_runs - len(existing_points)
        for _ in range(additional_runs):
            red_points = [[point.x, point.y] for point in random_point_set(size)]
            blue_points = [[point.x, point.y] for point in random_point_set(size)]
            existing_points.append({"red_points": red_points, "blue_points": blue_points})

        # Update the file with the new points
        points_data[str(size)] = existing_points
        with open(file_path, "w") as f:
            json.dump(points_data, f, indent=4)

    return points_data[str(size)][:num_runs]

def test_algorithms(start=5, end=500, step=25, num_runs=3, functions_to_test=None):
    """
    Benchmark algorithms with scientific testing improvements.
    """
    # Collect results for each algorithm as dictionaries
    brute_times = {}
    ortools_times = {}
    planar_cut_times = {}
    brute_no_numpy_times = {}

    # Path to the file storing the points
    points_file_path = os.path.join(
        os.path.dirname(__file__), "Points", "points_data.json"
    )

    # Ensure the Points directory exists
    os.makedirs(os.path.dirname(points_file_path), exist_ok=True)

    # Loop through each size from start to end (step)
    for size in range(start, end + 1, step):
        print(f"Running tests for input size: {size}")

        # Load or generate points for the current size
        points_data = load_or_generate_points(
            points_file_path, size, num_runs + 1
        )  # +1 for warm-up

        brute_time_list = []
        brute_no_numpy_time_list = []
        ortools_time_list = []
        planar_cut_time_list = []

        for i, point_set in enumerate(points_data):
            red_points = point_set["red_points"]
            blue_points = point_set["blue_points"]

            # Skip the first run (warm-up)
            if i == 0:
                continue

            # Test planar cut
            if "planar" in functions_to_test:
                start_time = time.perf_counter()
                LPC = LinearPlanarCut(0.5)
                NewCut = HamInstance(
                    red_points=red_points, blue_points=blue_points, plot_constant=1
                )
                LPC.cut(NewCut)
                elapsed_time = time.perf_counter() - start_time
                planar_cut_time_list.append(elapsed_time)

            # Test brute force algorithm
            if "brute" in functions_to_test:
                start_time = time.perf_counter()
                find_line_through_points_with_dual_intersection_brute(
                    red_points, blue_points
                )
                elapsed_time = time.perf_counter() - start_time
                brute_time_list.append(elapsed_time)

            # Test brute force (no numpy)
            if "brute_no_numpy" in functions_to_test:
                start_time = time.perf_counter()
                find_line_through_points_with_dual_intersection_brute_no_numpy(
                    red_points, blue_points
                )
                elapsed_time = time.perf_counter() - start_time
                brute_no_numpy_time_list.append(elapsed_time)

            # Placeholder for ortools (not implemented in this example)
            if "ortools" in functions_to_test and size <= 50:
                start_time = time.perf_counter()
                find_line_through_points_ortools_extended(red_points, blue_points)
                elapsed_time = time.perf_counter() - start_time
                ortools_time_list.append(elapsed_time)

        # Calculate average and standard deviation for each algorithm
        if brute_time_list:
            brute_times[size] = {
                "mean": statistics.mean(brute_time_list),
                "stdev": statistics.stdev(brute_time_list),
                "raw_times": brute_time_list,
            }
        if ortools_time_list:
            ortools_times[size] = {
                "mean": statistics.mean(ortools_time_list),
                "stdev": statistics.stdev(ortools_time_list),
                "raw_times": ortools_time_list,
            }
        if planar_cut_time_list:
            planar_cut_times[size] = {
                "mean": statistics.mean(planar_cut_time_list),
                "stdev": statistics.stdev(planar_cut_time_list),
                "raw_times": planar_cut_time_list,
            }
        if brute_no_numpy_time_list:
            brute_no_numpy_times[size] = {
                "mean": statistics.mean(brute_no_numpy_time_list),
                "stdev": statistics.stdev(brute_no_numpy_time_list),
                "raw_times": brute_no_numpy_time_list,
            }

    return (
        brute_times,
        ortools_times,
        planar_cut_times,
        brute_no_numpy_times,
    )


def save_results_to_file(results):
    # Generate a filename with the current datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_filename = f"{timestamp}.json"

    # Define the Results and Points directory paths
    results_dir = os.path.join(os.path.dirname(__file__), "Results")

    # Ensure the directories exist
    os.makedirs(results_dir, exist_ok=True)

    # Save the results as a JSON file
    results_filepath = os.path.join(results_dir, results_filename)
    with open(results_filepath, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Results saved to {results_filepath}")


def plot_times(brute_times, ortools_times, planar_cut_times, brute_no_numpy_times, show_stderr=True):
    # Extract sizes, mean times, and standard deviations from dictionaries
    brute_sizes = list(brute_times.keys())
    brute_means = [brute_times[size]["mean"] for size in brute_sizes]
    brute_stdevs = [brute_times[size]["stdev"] for size in brute_sizes]

    ortools_sizes = list(ortools_times.keys())
    ortools_means = [ortools_times[size]["mean"] for size in ortools_sizes]
    ortools_stdevs = [ortools_times[size]["stdev"] for size in ortools_sizes]

    planar_cut_sizes = list(planar_cut_times.keys())
    planar_cut_means = [planar_cut_times[size]["mean"] for size in planar_cut_sizes]
    planar_cut_stdevs = [planar_cut_times[size]["stdev"] for size in planar_cut_sizes]

    brute_no_numpy_sizes = list(brute_no_numpy_times.keys())
    brute_no_numpy_means = [brute_no_numpy_times[size]["mean"] for size in brute_no_numpy_sizes]
    brute_no_numpy_stdevs = [brute_no_numpy_times[size]["stdev"] for size in brute_no_numpy_sizes]

    # Plot the results with or without error bars
    plt.figure(figsize=(10, 6))
    if brute_times:
        plt.errorbar(
            brute_sizes, brute_means, yerr=brute_stdevs if show_stderr else None, label="Brute Force",
            color="red", marker="o", capsize=5, linestyle="--"
        )
    if planar_cut_times:
        plt.errorbar(
            planar_cut_sizes, planar_cut_means, yerr=planar_cut_stdevs if show_stderr else None, label="Linear Planar Cut",
            color="green", marker="^", capsize=5, linestyle="--"
        )
    if brute_no_numpy_times:
        plt.errorbar(
            brute_no_numpy_sizes, brute_no_numpy_means, yerr=brute_no_numpy_stdevs if show_stderr else None, label="Brute Force (No NumPy)",
            color="purple", marker="x", capsize=5, linestyle="--"
        )
    if ortools_times:
        plt.errorbar(
            ortools_sizes, ortools_means, yerr=ortools_stdevs if show_stderr else None, label="ORTools Extended",
            color="blue", marker="s", capsize=5, linestyle="--"
        )

    # Add labels, title, and legend
    plt.xlabel("Number of Points")
    plt.ylabel("Average Execution Time (seconds)")
    plt.title("Algorithm Runtime Comparison" + (" with Standard Deviation" if show_stderr else ""))
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Add argument parsing
    parser = argparse.ArgumentParser(description="Benchmark and plot algorithm runtimes.")
    parser.add_argument("--start", type=int, required=True, help="Starting number of points.")
    parser.add_argument("--end", type=int, required=True, help="Ending number of points.")
    parser.add_argument("--step", type=int, required=True, help="Step size for the number of points.")
    parser.add_argument("--num-runs", type=int, required=True, help="Number of runs for each input size.")
    parser.add_argument(
        "--functions-to-test",
        type=str,
        required=True,
        help="Comma-separated list of functions to test (e.g., brute,ortools,planar,brute_no_numpy)."
    )
    parser.add_argument("--show-stderr", action="store_true", help="Show standard error lines in the plot.")
    args = parser.parse_args()

    # Validate arguments
    if args.start <= 0:
        raise ValueError("The 'start' value must be greater than 0.")
    if args.end <= args.start:
        raise ValueError("The 'end' value must be greater than the 'start' value.")
    if args.step <= 0:
        raise ValueError("The 'step' value must be greater than 0.")
    if args.num_runs <= 0:
        raise ValueError("The 'num-runs' value must be greater than 0.")
    
    # Parse functions_to_test
    valid_functions = {"brute", "ortools", "planar", "brute_no_numpy"}
    functions_to_test = set(args.functions_to_test.split(","))
    if not functions_to_test.issubset(valid_functions):
        raise ValueError(
            f"Invalid functions in 'functions-to-test'. Valid options are: {', '.join(valid_functions)}"
        )

    # Run the tests and collect the results
    brute_times, ortools_times, planar_cut_times, brute_no_numpy_times = test_algorithms(
        start=args.start,
        end=args.end,
        step=args.step,
        num_runs=args.num_runs,
        functions_to_test=functions_to_test,
    )

    # Save the results and points to files
    results = {
        "brute_times": brute_times,
        "ortools_times": ortools_times,
        "planar_cut_times": planar_cut_times,
        "brute_no_numpy_times": brute_no_numpy_times,
    }
    save_results_to_file(results)

    # Plot the results
    plot_times(brute_times, ortools_times, planar_cut_times, brute_no_numpy_times, show_stderr=args.show_stderr)