#!/usr/bin/env python3.11
"""
Check Galileo API directly to see if workflows are stored
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GALILEO_API_KEY")
project = os.getenv("GALILEO_PROJECT", "codeswarm-hackathon")
console_url = os.getenv("GALILEO_CONSOLE_URL", "https://app.galileo.ai")

print("=" * 80)
print("GALILEO API CHECK")
print("=" * 80)
print(f"Project: {project}")
print(f"API Key (last 10): ...{api_key[-10:]}")
print()

# Try to list projects
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Common Galileo API endpoints
endpoints_to_try = [
    f"{console_url}/api/v1/projects",
    f"{console_url}/api/projects",
    "https://api.galileo.ai/v1/projects",
    "https://api.galileo.ai/projects",
]

print("Trying to find Galileo API endpoint...")
print()

for endpoint in endpoints_to_try:
    print(f"Trying: {endpoint}")
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ SUCCESS!")
            print(f"  Response: {response.json()}")
            break
        elif response.status_code == 401:
            print(f"  ❌ Unauthorized - API key may be invalid")
        elif response.status_code == 404:
            print(f"  ❌ Not found - wrong endpoint")
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()

print("=" * 80)
print("NOTE: Galileo Observe may not have a public REST API for querying workflows.")
print("The SDK uploads data but retrieval may only be through the UI.")
print("This is common for observability platforms (e.g., Datadog, New Relic).")
print("=" * 80)
