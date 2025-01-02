from flask import Flask, jsonify, request
import json

app = Flask(__name__)


def load_models():
    """Load models from models.json file"""
    try:
        with open("models.json", "r") as f:
            models_data = json.load(f)
        return models_data
    except Exception as e:
        print(f"Error loading models.json: {str(e)}")
        return None


@app.route("/api/models", methods=["GET"])
def get_model_ids():
    """Return list of all model IDs"""
    models_data = load_models()

    if not models_data:
        return jsonify({"error": "Failed to load models data"}), 500

    try:
        model_ids = [model["id"] for model in models_data["data"]]
        response = {
            "success": True,
            "count": len(model_ids),
            "model_ids": sorted(
                model_ids
            ),  # Sort alphabetically for better readability
        }
        return (
            jsonify(response),
            200,
            {"Content-Type": "application/json; charset=utf-8"},
        )
    except Exception as e:
        return jsonify({"error": f"Error processing models: {str(e)}"}), 500


@app.route("/test")
def test():
    return jsonify({"message": "Test endpoint working"})


@app.route("/api/models/search", methods=["GET"])
def search_models():
    """Search for models by query string"""
    print("Search endpoint hit")  # Debug output
    query = request.args.get("q", "").lower()
    print(f"Search query: {query}")  # Debug output
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    models_data = load_models()
    if not models_data:
        return jsonify({"error": "Failed to load models data"}), 500

    try:
        # Search through model IDs
        matching_models = [
            model["id"] for model in models_data["data"] if query in model["id"].lower()
        ]

        # Return null if no matches found
        if not matching_models:
            return jsonify({"success": True, "matches": None})

        return jsonify(
            {
                "success": True,
                "count": len(matching_models),
                "matches": sorted(matching_models),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Error searching models: {str(e)}"}), 500


if __name__ == "__main__":
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} {rule}")
    print("\nStarting server...")
    app.run(host="0.0.0.0", port=8000, debug=True)
