from flask import Flask, jsonify, request
import json

app = Flask(__name__)


def get_fresh_models():
    """Load fresh models data from models.json file"""
    try:
        with open("models.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading models.json: {str(e)}")
        return None


@app.route("/api/models", methods=["GET"])
def get_model_ids():
    """Return list of all model IDs"""
    models_data = get_fresh_models()

    if not models_data:
        return jsonify({"error": "Failed to load models data"}), 500

    try:
        model_ids = [model["id"] for model in models_data["data"]]
        response = {
            "success": True,
            "count": len(model_ids),
            "model_ids": sorted(model_ids),
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Error processing models: {str(e)}"}), 500


@app.route("/test")
def test():
    return jsonify({"message": "Test endpoint working"})


@app.route("/api/models/search", methods=["GET"])
def search_models():
    """Search for models by query string"""
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    models_data = get_fresh_models()
    if not models_data:
        return jsonify({"error": "Failed to load models data"}), 500

    try:
        matching_models = [
            model["id"] for model in models_data["data"] if query in model["id"].lower()
        ]
        return jsonify(
            {
                "success": True,
                "count": len(matching_models) if matching_models else 0,
                "matches": sorted(matching_models) if matching_models else None,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Error searching models: {str(e)}"}), 500


@app.route("/api/get_providers", methods=["GET"])
def get_providers():
    """Get provider information for a model by query"""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "No model ID provided"}), 400

    models_data = get_fresh_models()
    if not models_data:
        return jsonify({"error": "Failed to load models data"}), 500

    try:
        model = next(
            (model for model in models_data["data"] if model["id"] == query), None
        )
        if not model:
            return jsonify({"success": True, "providers": None})

        providers = model.get("providers", [])
        return jsonify({"success": True, "model_id": query, "providers": providers})
    except Exception as e:
        return jsonify({"error": f"Error getting providers: {str(e)}"}), 500


if __name__ == "__main__":
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} {rule}")
    print("\nStarting server...")
    app.run(host="0.0.0.0", port=8000, debug=True)
