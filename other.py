import json
import requests
from colorama import init, Fore, Style
from collections import defaultdict
from datetime import datetime
import sys
from io import StringIO

# Initialize colorama
init()

OPENROUTER_API_KEY = (
    "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"
)

url = "https://openrouter.ai/api/v1/models"
headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}


def get_existing_data():
    try:
        with open("tokens.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(
            f"{Fore.YELLOW}tokens.json not found. This appears to be the first run.{Style.RESET_ALL}"
        )
        return {"data": []}


def fetch_new_data():
    response = requests.get(url, headers=headers)
    return response.json()


def compare_data(old_data, new_data):
    old_models = {model["id"]: model for model in old_data.get("data", [])}
    new_models = {model["id"]: model for model in new_data.get("data", [])}

    added_models = [
        model for model_id, model in new_models.items() if model_id not in old_models
    ]
    removed_models = [
        model for model_id, model in old_models.items() if model_id not in new_models
    ]

    return added_models, removed_models


def format_provider_name(provider):
    # For hyphenated names, capitalize each part
    if "-" in provider:
        return "-".join(part.capitalize() for part in provider.split("-"))

    # Default case: just capitalize first letter
    return provider.capitalize()


def group_models_by_provider(models):
    grouped = defaultdict(list)
    for model in models:
        provider = format_provider_name(model["id"].split("/")[0])
        grouped[provider].append(model)
    return grouped


def format_context_window(tokens):
    if tokens >= 1000000:
        return f"{tokens/1000000:.1f}M"
    elif tokens >= 1000:
        return f"{tokens//1000}K"
    return str(tokens)


def format_models(models, title="OpenRouter Models by Provider", file=sys.stdout):
    print(f"{title}", file=file)
    print("=" * len(title), file=file)
    print(file=file)

    grouped = group_models_by_provider(models)

    for provider in sorted(grouped.keys()):
        print(f"{provider}", file=file)
        print("-" * len(provider), file=file)

        for model in sorted(grouped[provider], key=lambda x: x["id"]):
            model_name = model["id"].split("/")[-1]
            context_window = format_context_window(model.get("context_length", 0))
            created_at = (
                datetime.fromisoformat(
                    model.get("created_at", "").replace("Z", "+00:00")
                ).strftime("%Y-%m-%d")
                if model.get("created_at")
                else ""
            )

            # Format: + model_name (padded to 45 chars) created_at (padded to 15 chars) context_window (right-aligned to 5 chars)
            print(f"+ {model_name:<45} {created_at:<15} {context_window:>5}", file=file)

        print(file=file)


def display_changes(added_models, removed_models):
    if added_models:
        print(f"\n{Fore.GREEN}New Models Added:{Style.RESET_ALL}")
        format_models(added_models, "New Models Added")

    if removed_models:
        print(f"\n{Fore.RED}Models Removed:{Style.RESET_ALL}")
        format_models(removed_models, "Models Removed")

    if not added_models and not removed_models:
        print(f"{Fore.YELLOW}No changes detected.{Style.RESET_ALL}")


def main():
    existing_data = get_existing_data()
    new_data = fetch_new_data()

    # Create a string buffer for the formatted output
    output = StringIO()
    format_models(new_data["data"], file=output)

    # Write the formatted output to tokens.txt
    with open("tokens.txt", "w", encoding="utf-8") as file:
        file.write(output.getvalue())
    output.close()

    # Display the changes in the terminal
    if not existing_data["data"]:
        print(
            f"{Fore.GREEN}Initial data fetch. All models will be considered new.{Style.RESET_ALL}"
        )
        added_models = new_data["data"]
        removed_models = []
    else:
        added_models, removed_models = compare_data(existing_data, new_data)
        display_changes(added_models, removed_models)

    # Save the new data to tokens.json
    with open("tokens.json", "w") as file:
        json.dump(new_data, file, indent=4)

    print(
        f"\n{Fore.CYAN}Updated data saved to tokens.json and tokens.txt{Style.RESET_ALL}"
    )


if __name__ == "__main__":
    main()
