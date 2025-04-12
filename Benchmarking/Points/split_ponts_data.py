import os
import json

def split_points_data(file_path, chunk_size_mb=100):
    """
    Split an existing points_data.json file into smaller chunks.

    Parameters:
        file_path (str): Path to the existing points_data.json file.
        chunk_size_mb (int): Maximum size of each chunk in megabytes.
    """
    # Helper function to calculate file size in MB
    def get_file_size_in_mb(path):
        return os.path.getsize(path) / (1024 * 1024)

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return

    # Load the existing points data
    with open(file_path, "r") as f:
        points_data = json.load(f)

    # Split the data into chunks
    chunk_index = 1
    chunk_data = {}
    for key, value in points_data.items():
        chunk_data[key] = value
        temp_file_path = f"{file_path}_chunk_{chunk_index}.json"
        with open(temp_file_path, "w") as temp_file:
            json.dump(chunk_data, temp_file, indent=4)
        if get_file_size_in_mb(temp_file_path) > chunk_size_mb:
            # Finalize the current chunk and start a new one
            chunk_index += 1
            chunk_data = {}

    # Write the remaining data to the last chunk
    if chunk_data:
        with open(f"{file_path}_chunk_{chunk_index}.json", "w") as f:
            json.dump(chunk_data, f, indent=4)

    print(f"File {file_path} has been split into {chunk_index} chunks.")
    
split_points_data("c:/Users/chris/Workspace/Year_5/Project/src/Benchmarking/Points/points_data.json", chunk_size_mb=100)