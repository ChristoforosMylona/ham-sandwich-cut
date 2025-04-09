import argparse
import json
import numpy as np
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

# Function to load JSON results
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

# Function to plot results
def plot_times(results, show_stderr=True):
    if not results:
        print("No data to plot.")
        return
    
    plt.figure(figsize=(10, 6))
    
    for algorithm, times in results.items():
        if not times:  # Skip algorithms with no data
            continue
        
        sizes = list(map(int, times.keys()))
        means = [times[str(size)]["mean"] for size in sizes]
        stdevs = [times[str(size)]["stdev"] for size in sizes]
        
        # Plot with or without error bars
        plt.errorbar(
            sizes, means, yerr=stdevs if show_stderr else None, label=algorithm.replace("_", " ").title(),
            marker='o', capsize=5, linestyle="--"
        )
    
    plt.xlabel("Number of Points")
    plt.ylabel("Average Execution Time (seconds)")
    plt.title("Algorithm Runtime Comparison" + (" with Standard Deviation" if show_stderr else ""))
    plt.legend()  # Only include algorithms that were plotted
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Add argument parsing
    parser = argparse.ArgumentParser(description="Plot algorithm runtimes from results.")
    parser.add_argument("--show-stderr", type=str, choices=["yes", "no"], help="Show standard error lines in the plot.")
    args = parser.parse_args()

    # Load results
    results = load_results()
    if results:
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

        # Plot the results
        plot_times(results, show_stderr=show_stderr)