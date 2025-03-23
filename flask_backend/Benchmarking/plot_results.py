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
def plot_times(results):
    if not results:
        print("No data to plot.")
        return
    
    plt.figure(figsize=(10, 6))
    
    for key, times in results.items():
        sizes = list(map(int, times.keys()))
        values = list(map(float, times.values()))
        plt.plot(sizes, values, marker='o', label=key.replace("_", " ").title())
    
    plt.xlabel("Number of Points")
    plt.ylabel("Average Execution Time (seconds)")
    plt.title("Algorithm Runtime Comparison")
    plt.legend()
    plt.grid(True)
    plt.show()

# Main execution
if __name__ == "__main__":
    results = load_results()
    if results:
        plot_times(results)
