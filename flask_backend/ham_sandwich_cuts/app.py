from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import traceback
import gc

from ExistingProjects.Existing_Project_Viz.Cuts import LinearPlanarCut
from ExistingProjects.Existing_Project_Viz.IOUtils import HamInstance
from config import Config


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

        NewCut = HamInstance(
            red_points=red_points, blue_points=blue_points, plot_constant=1
        )
        LPC = LinearPlanarCut(0.5)
        sandwich_cut = LPC.cut(NewCut)
        intercept, slope = sandwich_cut[0].b, sandwich_cut[0].m

        # Trigger garbage collection explicitly after the work is done
        gc.collect()

        # Return the results as JSON
        return jsonify({"slope": slope, "y_intercept": intercept}), 200

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


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
