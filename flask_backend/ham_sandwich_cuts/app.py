from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import traceback
import gc


from ExistingProjects.Existing_Project_Viz.Cuts import LinearPlanarCut
from ExistingProjects.Existing_Project_Viz.IOUtils import HamInstance
from ExistingProjects.Existing_Project_Viz.GeomUtils import random_point_set
from config import Config
from ILP.HamSandwichILP import find_line_through_points_ILP
from MLP.HamSandwichMLP import find_line_through_points_ortools_extended
from BruteForce.HamSandwichBruteForce import (
    find_line_through_points_with_dual_intersection_brute,
    find_line_through_points_with_dual_intersection_brute_no_numpy
)

import numpy as np

app = Flask(__name__)

app.config.from_object(Config)

flask_env = os.getenv("FLASK_ENV", "development")
if flask_env != "production":
    # Allow localhost:5173 in non-production environments
    CORS(app, origins=["http://localhost:5173"])
    print("CORS enabled for development env")
else:
    # In production, you can restrict origins or leave it empty (disallow all)
    CORS(app, origins=["http://frontend:5173", "http://localhost:5173"])
    print("CORS enabled for prod env")


@app.route("/ham-sandwich-viz/", methods=["POST"])
def calculate_ham_cut_viz():
    try:
        # Parse JSON data
        data = request.get_json()
        blue_points = data.get("bluePoints", [])
        red_points = data.get("redPoints", [])

        # Validate inputs
        if not isinstance(blue_points, list) or not isinstance(red_points, list):
            return jsonify({"error": "Invalid input format. Arrays expected."}), 400

        # Create the HamInstance and calculate the sandwich cut
        NewCut = HamInstance(
            red_points=red_points, blue_points=blue_points, plot_constant=1
        )
        LPC = LinearPlanarCut(0.5)
        result = LPC.cut(NewCut)
        
        # Trigger garbage collection explicitly after the work is done
        gc.collect()

        if result is None:
            return jsonify({"error": "No feasible line found."}), 400

        # Prepare the response based on the result (vertical or non-vertical)
        if result[0] == "vertical":
            # Vertical line found
            return jsonify({"is_vertical": True, "x_intercept": result[1]}), 200
        else:
            # Non-vertical line found
            slope, intercept = result[1]
            return jsonify({"is_vertical": False, "slope": slope, "y_intercept": intercept}), 200
        

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return jsonify({"error": "Invalid input or processing error: " + str(e)}), 400
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": "unexpected error"}), 500


@app.route("/teach-ham-sandwich-viz/", methods=["POST"])
def teach_ham_cut_viz():
    try:
        # Parse JSON data
        data = request.get_json()
        blue_points = data.get("bluePoints", [])
        red_points = data.get("redPoints", [])

        # Validate inputs
        if not isinstance(blue_points, list) or not isinstance(red_points, list):
            return jsonify({"error": "Invalid input format. Arrays expected."}), 400

        steps_taken = []

        NewCut = HamInstance(
            red_points=red_points,
            blue_points=blue_points,
            plot_constant=1,
            steps_taken=steps_taken,
        )
        LPC = LinearPlanarCut(0.5)
        LPC.teach(NewCut, steps_taken=steps_taken)

        # Trigger garbage collection explicitly after the work is done
        gc.collect()

        return jsonify({"stepsTaken": steps_taken}), 200

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return jsonify({"error": "Invalid input or processing error: " + str(e)}), 400
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": "unexpected error"}), 500


@app.route("/ham-sandwich-ilp/", methods=["POST"])
def calculate_ham_cut_ilp():
    try:
        # Parse JSON data
        data = request.get_json()
        blue_points = data.get("bluePoints", [])
        red_points = data.get("redPoints", [])

        # Validate inputs
        if not isinstance(blue_points, list) or not isinstance(red_points, list):
            return jsonify({"error": "Invalid input format. Arrays expected."}), 400

        # Call the updated line finding function
        result = find_line_through_points_ILP(red_points, blue_points)

        if result is None:
            return jsonify({"error": "No feasible line found."}), 400

        # Prepare the response based on the result (vertical or non-vertical)
        if result[0] == "vertical":
            # Vertical line found
            return jsonify({"is_vertical": True, "x_intercept": result[1]}), 200
        else:
            # Non-vertical line found
            slope, intercept = result[1]
            return jsonify({"is_vertical": False, "slope": slope, "y_intercept": intercept}), 200

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return jsonify({"error": "Invalid input or processing error: " + str(e)}), 400
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": "unexpected error"}), 500

    
@app.route("/ham-sandwich-mlp/", methods=["POST"])
def calculate_ham_cut_mlp():
    try:
        # Parse JSON data
        data = request.get_json()
        blue_points = data.get("bluePoints", [])
        red_points = data.get("redPoints", [])

        # Validate inputs
        if not isinstance(blue_points, list) or not isinstance(red_points, list):
            return jsonify({"error": "Invalid input format. Arrays expected."}), 400

        # Call the find_line_through_points_ortools_extended function
        result = find_line_through_points_ortools_extended(red_points, blue_points)

        # If no feasible line is found
        if result is None:
            return jsonify({"error": "No feasible line found."}), 400

        
        # If result is vertical
        if result[0] == "vertical":
            return jsonify({"is_vertical": True, "x_intercept": result[1]}), 200

        # If result is non-vertical
        elif result[0] == "non-vertical":
            slope, intercept = result[1]
            return jsonify({"is_vertical": False, "slope": slope, "y_intercept": intercept}), 200

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return jsonify({"error": "Invalid input or processing error: " + str(e)}), 400
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": "unexpected error"}), 500


@app.route("/brute-force/", methods=["POST"])
def brute_force():
    try:
        # Parse JSON data
        data = request.get_json()
        blue_points = data.get("bluePoints", [])
        red_points = data.get("redPoints", [])

        # Validate inputs
        if not isinstance(blue_points, list) or not isinstance(red_points, list):
            return jsonify({"error": "Invalid input format. Arrays expected."}), 400

        result = find_line_through_points_with_dual_intersection_brute(
            red_points, blue_points
        )
        
        
        
        if result is None:
            return jsonify({"error": "No feasible line found."}), 400

        # Prepare the response based on the result (vertical or non-vertical)
        if result[0] == "vertical":
            # Vertical line found
            return jsonify({"is_vertical": True, "x_intercept": result[1]}), 200
        else:
            # Non-vertical line found
            slope, intercept = result[1]
            return jsonify({"is_vertical": False, "slope": slope, "y_intercept": intercept}), 200

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return jsonify({"error": "Invalid input or processing error: " + str(e)}), 400
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": "unexpected error"}), 500


@app.route("/get-sample-file/<file_type>", methods=["GET"])
def get_sample_file(file_type):
    try:
        # Get the requested file type from the URL parameter
        file_type = file_type.lower()

        # Define the directory containing sample files
        sample_dir = os.path.join(os.getcwd(), "sample_files")

        # Map file types to filenames
        file_map = {
            "csv": "sample_data.csv",
            "json": "sample_data.json",
            "excel": "sample_data.xlsx",
            "xlsx": "sample_data.xlsx",  # Alias for Excel
        }

        # Get the filename based on requested type
        filename = file_map.get(file_type)
        if not filename:
            return jsonify({"error": "Invalid file type"}), 400

        # Construct the full file path
        file_path = os.path.join(sample_dir, filename)

        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Serve the file as a response
        return send_file(file_path, as_attachment=True, download_name=filename)

    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": "Unexpected error occurred"}), 500


@app.route("/random_points/", methods=["POST"])
def generate_random_points():
    try:
        red_points = request.form.get("redPoints", "5")
        blue_points = request.form.get("bluePoints", "7")

        # Ensure inputs are valid integers
        if not red_points.isdigit() or not blue_points.isdigit():
            return jsonify({"error": "Invalid input format. Integers expected."}), 400

        red_points = int(red_points)
        blue_points = int(blue_points)

        # Ensure non-negative values
        if red_points < 0 or blue_points < 0:
            return jsonify({"error": "Point counts must be non-negative integers."}), 400

        blue_data = [{"x": point.x, "y": point.y} for point in random_point_set(blue_points)]
        red_data = [{"x": point.x, "y": point.y} for point in random_point_set(red_points)]

        return jsonify({
            "redData": red_data,
            "blueData": blue_data
        }), 200

    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": "Unexpected error occurred."}), 500
    

def handler(request):
    with app.app_context():
        response = app.full_dispatch_request()
        return response

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])