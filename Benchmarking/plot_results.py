import argparse
import json
import matplotlib.pyplot as plt

# Check if running in Google Colab
try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    from google.colab import files
else:
    import tkinter as tk
    from tkinter import filedialog

def load_results():
    if IN_COLAB:
        uploaded = files.upload()
        filename = list(uploaded.keys())[0]
    else:
        root = tk.Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    
    if filename:
        with open(filename, "r") as f:
            data = json.load(f)
        print(f"Loaded results from {filename}")
        return data
    else:
        print("No file selected.")
        return None

def plot_times(results, show_stderr=True, selected_algorithms=None):
    if not results:
        print("No data to plot.")
        return

    # Alias "ortools_times" and "ortools" to "milp_times" for consistent labeling
    aliased_results = {}
    for k, v in results.items():
        if k in ("ortools_times", "ortools"):
            aliased_results["milp_times"] = v
        else:
            aliased_results[k] = v

    algorithm_colors = {
        "brute_times": "red",
        "milp_times": "blue",
        "planar_cut_times": "green",
        "brute_no_numpy_times": "purple",
    }

    plt.figure(figsize=(10, 6))

    for algorithm, times in aliased_results.items():
        if not times:
            continue
        if selected_algorithms and algorithm not in selected_algorithms:
            continue

        sizes = list(map(int, times.keys()))
        means = [times[str(size)]["mean"] for size in sizes]
        stdevs = [times[str(size)]["stdev"] for size in sizes]

        color = algorithm_colors.get(algorithm, "black")

        # Always label milp_times as "MILP"
        label = "MILP" if algorithm == "milp_times" else algorithm.replace("_times", "").replace("_", " ").title()

        plt.errorbar(
            sizes, means, yerr=stdevs if show_stderr else None,
            label=label,
            color=color, marker='o', capsize=5, linestyle="-"
        )

    plt.xlabel("Number of Points")
    plt.ylabel("Average Execution Time (seconds)")
    plt.title("Algorithm Runtime Comparison" + (" with Standard Deviation" if show_stderr else ""))
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Add argument parsing
    parser = argparse.ArgumentParser(description="Plot algorithm runtimes from results.")
    parser.add_argument("--show-stderr", type=str, choices=["yes", "no"], help="Show standard error lines in the plot.")
    parser.add_argument("--select-algorithms", type=str, help="Comma-separated list of algorithms to plot.")
    args = parser.parse_args()

    # Load results
    results = load_results()
    if results:
        # Determine whether to show stderr
        if args.show_stderr is None:
            # Ask the user if they want to show stderr lines
            if not IN_COLAB:
                root = tk.Tk()
                root.withdraw()
                show_stderr = tk.messagebox.askyesno("Show Standard Error", "Do you want to show standard error lines?")
            else:
                show_stderr = input("Do you want to show standard error lines? (yes/no): ").strip().lower() == "yes"
        else:
            show_stderr = args.show_stderr == "yes"

        # Determine which algorithms to plot
        if args.select_algorithms:
            selected_algorithms = set(args.select_algorithms.split(","))
        else:
            # Interactive selection if no algorithms are specified
            print("Available algorithms:")
            for algorithm in results.keys():
                print(f"- {algorithm}")
            selected_algorithms = input("Enter a comma-separated list of algorithms to plot (or press Enter to plot all): ").strip()
            selected_algorithms = set(selected_algorithms.split(",")) if selected_algorithms else None

        # Plot the results
        plot_times(results, show_stderr=show_stderr, selected_algorithms=selected_algorithms)