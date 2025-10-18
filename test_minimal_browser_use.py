#!/usr/bin/env python3
"""Minimal Browser Use Test - Direct SDK call"""
import os
import time
from dotenv import load_dotenv
load_dotenv()

from browser_use_sdk import BrowserUse

api_key = os.getenv("BROWSERUSE_API_KEY")
print(f"API Key: {api_key[:20]}..." if api_key else "No API key")

client = BrowserUse(api_key=api_key)

print("\nCreating simple search task...")
task = client.tasks.create_task(
    task="Go to google.com and search for 'FastAPI' and return the first result URL",
    start_url="https://www.google.com",
    max_steps=5
)

print(f"Task created: {task.id}")
print(f"Status: {task.status}")

print("\nWaiting for completion (30 second timeout)...")
for i in range(15):
    time.sleep(2)
    status = client.tasks.get_task(task_id=task.id)
    print(f"  {i*2}s - Status: {status.status}")

    if status.status == "completed":
        print(f"\n✅ SUCCESS! Result: {status.result[:200]}")
        break
    elif status.status == "failed":
        print(f"\n❌ FAILED! Error: {status.error}")
        break
else:
    print("\n⏱️  TIMEOUT - Task did not complete in 30 seconds")
    print(f"Final status: {status.status}")
