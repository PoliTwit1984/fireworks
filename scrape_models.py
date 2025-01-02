import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")


def load_existing_models():
    """Load existing models.json if it exists"""
    try:
        with open("models.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"data": []}


def scrape_models():
    # Headers required for OpenRouter API
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    # Get models from API
    response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

    # Get raw response data
    new_models_data = response.json()

    # Load existing models
    existing_models_data = load_existing_models()
    existing_models = {
        model["id"]: model for model in existing_models_data.get("data", [])
    }

    # Process and update models
    updated_models = []
    changes_made = False

    for new_model in new_models_data.get("data", []):
        # Clean up description
        if "description" in new_model:
            new_model["description"] = " ".join(new_model["description"].split())

        model_id = new_model["id"]
        if model_id in existing_models:
            # Preserve provider information
            if "providers" in existing_models[model_id]:
                new_model["providers"] = existing_models[model_id]["providers"]

            # Check if anything else changed
            existing_model = existing_models[model_id]
            if any(
                new_model.get(k) != existing_model.get(k)
                for k in new_model
                if k != "providers"
            ):
                changes_made = True
                print(f"Updated model: {model_id}")
        else:
            changes_made = True
            print(f"New model: {model_id}")

        updated_models.append(new_model)

    # Only save if there were changes
    if changes_made:
        models_data = {"data": updated_models}
        with open("models.json", "w") as f:
            json.dump(models_data, f, indent=2)
        print("✓ Changes detected and saved to models.json")
    else:
        print("✓ No changes detected in models")


if __name__ == "__main__":
    try:
        scrape_models()
        print("✓ Successfully saved to models.json")
    except Exception as e:
        print(f"Error: {str(e)}")
