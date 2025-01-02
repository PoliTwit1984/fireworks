import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

def scrape_models():
    print("Fetching models from API...")
    
    # Headers required for OpenRouter API
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get models from API
    response = requests.get('https://openrouter.ai/api/v1/models', headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    models_data = response.json()
    
    # Debug API response
    print("\nAPI Response:")
    print(json.dumps(models_data, indent=2))
    
    models = []
    
    print(f"\nProcessing models...")
    if isinstance(models_data, str):
        print("Error: API returned string instead of JSON")
        return []
        
    for model in models_data.get('data', []):
        try:
            # Build model data in our format
            model_data = {
                'descriptive_name': model['name'],
                'url': f"https://openrouter.ai/{model['slug']}",
                'openrouter_model_name': model['slug'],
                'description': model.get('description', ''),
                'pricing': {
                    'input': model.get('pricing', {}).get('prompt', 0),
                    'output': model.get('pricing', {}).get('completion', 0)
                }
            }
            
            models.append(model_data)
            print(f"Processed model: {model_data['descriptive_name']}")
            
        except Exception as e:
            print(f"Error processing model: {str(e)}")
            continue
    
    return models

def save_models_to_json(models, filename='models.json'):
    """Save the models data to a JSON file"""
    with open(filename, 'w') as f:
        json.dump({"models": models}, f, indent=2)

if __name__ == "__main__":
    try:
        models = scrape_models()
        print(f"\nFound {len(models)} models")
        print("Saving model information to models.json...")
        save_models_to_json(models)
        print("✓ Successfully saved to models.json")
    except Exception as e:
        print(f"Error: {str(e)}")
