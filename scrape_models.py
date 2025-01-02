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

    # Get raw response data and process descriptions
    models_data = response.json()

    # Remove line breaks from descriptions
    for model in models_data.get("data", []):
        if "description" in model:
            # Replace newlines and multiple spaces with single space
            model["description"] = " ".join(model["description"].split())

    # Save processed response to JSON
    with open("models.json", "w") as f:
        json.dump(models_data, f, indent=2)


if __name__ == "__main__":
    try:
        scrape_models()
        print("✓ Successfully saved to models.json")
    except Exception as e:
        print(f"Error: {str(e)}")
