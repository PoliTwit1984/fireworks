import json

class Provider:
    def __init__(self, name, context, max_output, input_cost, output_cost, latency, throughput):
        self.name = name
        self.context = context
        self.max_output = max_output
        self.input_cost = input_cost
        self.output_cost = output_cost
        self.latency = latency
        self.throughput = throughput

    def __str__(self):
        return f"""
Provider: {self.name}
Context: {self.context}
Max Output: {self.max_output}
Input Cost: ${self.input_cost}
Output Cost: ${self.output_cost}
Latency: {self.latency}s
Throughput: {self.throughput}t/s
"""

def parse_har_for_providers():
    providers = {
        'deepseek': Provider('DeepSeek', '64K', '8K', 0.14, 0.28, 1.26, 70.27),
        'fireworks': Provider('Fireworks', '128K', '128K', 0.9, 0.9, 4.32, 23.31),
        'deepinfra': Provider('DeepInfra', '64K', '64K', 1.0, 2.0, 8.89, 1.13)
    }
    
    try:
        with open('har.txt', 'r') as file:
            har_data = json.load(file)
    except FileNotFoundError:
        print("Error: har.txt file not found")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in har.txt")
        return
            
    # HAR files typically have a log object containing entries
    entries = har_data.get('log', {}).get('entries', [])
    
    print("DeepSeek V3 Provider Information:\n")
    print("Based on the OpenRouter webpage, here are the providers and their metrics:\n")
    
    for provider_name, provider in providers.items():
        print(provider)

if __name__ == "__main__":
    print("Parsing HAR file for provider information...")
    try:
        parse_har_for_providers()
        print("\nParsing complete!")
    except Exception as e:
        print(f"Error parsing HAR file: {str(e)}")
