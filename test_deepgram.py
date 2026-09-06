import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPGRAM_API_KEY")
print(f"API Key: {api_key}")

# Test with a simple audio file (just check if key works)
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "audio/wav",
}
url = "https://api.deepgram.com/v1/listen?model=nova-2"

# Try with empty audio to test key validity
try:
    resp = requests.post(url, headers=headers, data=b"", timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")