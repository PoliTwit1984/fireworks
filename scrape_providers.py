from playwright.sync_api import sync_playwright
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

def clean_and_convert_values(value, data_type):
    if value is None:
      return None

    value = value.strip()

    if data_type == "str":
      return str(value)

    if data_type == 'int' or data_type == 'float':
        value = value.replace(',', '')
        try:
            if data_type == 'float':
                return float(value.replace('$', '').replace('K', '000'))
            else:
                return int(value.replace('K', '000'))
        except ValueError:
            return None
    elif data_type == 'latency':
        value = value.replace('s','')
        try:
            return float(value)
        except ValueError:
            return None
    elif data_type == 'throughput':
        value = value.replace('t/s', '')
        try:
            return float(value)
        except ValueError:
            return None
    return value

def scrape_providers(model_url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        print("Loading main page...")
        page.goto(model_url, wait_until='networkidle')
        page.wait_for_timeout(2000)
        
        print("Looking for Providers tab...")
        try:
            providers_tab = page.get_by_role("tab", name="Providers")
            providers_tab.click(timeout=5000)
            page.wait_for_timeout(2000)
        except Exception as e:
            print("No Providers tab found. This model may not support provider selection.")
            browser.close()
            return [{
                "name": None,
                "metrics": {
                    "context_length": None,
                    "max_output_tokens": None,
                    "input_price_per_million": None,
                    "output_price_per_million": None,
                    "latency_seconds": None,
                    "throughput_tokens_per_second": None
                }
            }]
            
        print("Waiting for provider section...")
        try:
            page.wait_for_selector('div.flex.flex-col.gap-3', state='visible', timeout=5000)
        except Exception as e:
            print("Provider section not found after clicking tab.")
            browser.close()
            return [{
                "name": None,
                "metrics": {
                    "context_length": None,
                    "max_output_tokens": None,
                    "input_price_per_million": None,
                    "output_price_per_million": None,
                    "latency_seconds": None,
                    "throughput_tokens_per_second": None
                }
            }]
            
        providers = []
        
        # Get all provider rows
        rows = page.locator('tr.flex.flex-col.py-4.border-t.border-border\\/50').all()
        print(f"Found {len(rows)} provider rows")
        
        if len(rows) == 0:
            print("No provider rows found on the page")
            return [{
                "name": None,
                "metrics": {
                    "context_length": None,
                    "max_output_tokens": None,
                    "input_price_per_million": None,
                    "output_price_per_million": None,
                    "latency_seconds": None,
                    "throughput_tokens_per_second": None
                }
            }]
            
        for row in rows:
            try:
                # Get provider name from the link
                name_el = row.locator('a.text-muted-foreground\\/80').first
                if not name_el:
                    print("No name element found")
                    continue
                    
                name = name_el.inner_text().lower()
                
                # Get metrics from the flex container
                metrics_container = row.locator('div.flex.flex-wrap.items-center.justify-between.gap-8').first
                metrics = metrics_container.locator('div.text-lg').all()
                if len(metrics) < 6:
                    continue
                
                metrics_text = [m.inner_text() for m in metrics]
                
                provider_data = {
                    "name": name.replace(" ", "_"),
                    "metrics": {
                        "context_length": clean_and_convert_values(metrics_text[0], 'int'),
                        "max_output_tokens": clean_and_convert_values(metrics_text[1], 'int'),
                        "input_price_per_million": clean_and_convert_values(metrics_text[2], 'float'),
                        "output_price_per_million": clean_and_convert_values(metrics_text[3], 'float'),
                        "latency_seconds": clean_and_convert_values(metrics_text[4], 'latency'),
                        "throughput_tokens_per_second": clean_and_convert_values(metrics_text[5], 'throughput')
                    }
                }
                providers.append(provider_data)
                
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                continue
        
        browser.close()
        
        return providers

def save_providers_to_json(providers, filename='providers.json'):
    """Save the providers data to a JSON file"""
    with open(filename, 'w') as f:
        json.dump({"providers": providers}, f, indent=2)

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            model_url = sys.argv[1]
        else:
            print("Usage: python scrape_providers.py <model_url>")
            print("Example: python scrape_providers.py https://openrouter.ai/google/gemini-2.0-flash-thinking-exp:free")
            sys.exit(1)
            
        providers = scrape_providers(model_url)
        save_providers_to_json(providers)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
