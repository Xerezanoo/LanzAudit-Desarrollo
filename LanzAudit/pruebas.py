import json

with open('wpscan_stdout.log', 'r') as f:
    data = json.load(f)

print(json.dumps(data, indent=2))
