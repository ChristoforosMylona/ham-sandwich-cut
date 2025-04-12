# Benchmarking and Plotting Guide

This guide explains how to use the benchmarking script (`benchmark_algs.py`) to test the performance of various algorithms and how to visualize the results using the plotting script (`plot_results.py`).

---

## 1. Benchmarking Algorithms

The `benchmark_algs.py` script benchmarks the performance of different algorithms for solving the ham-sandwich problem. It generates or loads point sets, runs the algorithms, and saves the results to a JSON file.

### Usage

Run the script from the command line using the following syntax:

```bash
python -m Benchmarking.benchmark_algs --start <start> --end <end> --step <step> --num-runs <num_runs> --functions-to-test <functions> [--show-stderr]
```

### Arguments

- `--start` (required):  
  The starting number of points for the benchmark.  
  Example: `--start 5`

- `--end` (required):  
  The ending number of points for the benchmark.  
  Example: `--end 500`

- `--step` (required):  
  The step size for the number of points.  
  Example: `--step 25`

- `--num-runs` (required):  
  The number of runs for each input size.  
  Example: `--num-runs 3`

- `--functions-to-test` (required):  
  A comma-separated list of algorithms to test. Valid options are:
  - `brute`
  - `ortools`
  - `planar`
  - `brute_no_numpy`  
  Example: `--functions-to-test brute,planar`

- `--show-stderr` (optional):  
  If included, standard error lines will be shown in the plot.

### Example Command

```bash
python -m Benchmarking.benchmark_algs --start 10 --end 100 --step 10 --num-runs 5 --functions-to-test brute,planar --show-stderr
```

### Output

The script generates a JSON file in the `Results` directory with a timestamped filename (e.g., `2025-04-09_12-30-00.json`). This file contains the benchmarking results, including the mean execution time, standard deviation, and raw times for each algorithm.

---

## 2. Plotting Results

The `plot_results.py` script visualizes the benchmarking results saved in the JSON file.

### Usage

Run the script from the command line or interactively in an environment like Google Colab.

```bash
python -m Benchmarking.plot_results [--show-stderr <yes|no>]
```

### Arguments

- `--show-stderr` (optional):  
  Controls whether standard error lines are shown in the plot.
  - `yes`: Show standard error lines.
  - `no`: Do not show standard error lines.  
  If not provided, the script will prompt the user to choose.

### Example Command

```bash
python -m Benchmarking.plot_results --show-stderr yes
```

### Interactive Mode

If `--show-stderr` is not provided, the script will:

- Open a file dialog (on local machines) or prompt for file upload (in Google Colab) to select the JSON results file.
- Ask the user whether to show standard error lines.

### Output

The script generates a plot comparing the runtime of the algorithms. The plot includes:

- **X-axis**: Number of points
- **Y-axis**: Average execution time (seconds)
- **Error Bars**: Represent the standard deviation (if enabled)
- **Legend**: Displays the names of the algorithms tested

---

## 3. Workflow Example

### Step 1: Run Benchmarking

Run the `benchmark_algs.py` script to benchmark the algorithms:

```bash
python -m Benchmarking.benchmark_algs --start 10 --end 100 --step 10 --num-runs 5 --functions-to-test brute,planar,brute_no_numpy --show-stderr
```

This will generate a results file in the `Results` directory.

### Step 2: Plot Results

The benchmark also plots the data. However, if you wish to plot the data again afterwards, run the `plot_results.py` script to visualize the results:

```bash
python -m Benchmarking.plot_results --show-stderr yes
```

Alternatively, run the script without arguments to interactively select the results file and choose whether to show standard error lines.

---

## 4. Notes

- Ensure that the `src` folder is in your Python path. If running in an IDE like VS Code, set the `PYTHONPATH` to include the `src` directory.
- Use `python -m` to run the scripts as modules from the `src` directory.
- The `Results` directory will store all benchmarking results, and the `Points` directory will store generated point sets.
