import os
import requests
from dotenv import load_dotenv

load_dotenv()

response = requests.post(
    "https://api.twitterapis.com/twitter/customer/session",
    headers={
        "Authorization": f"Bearer {os.environ['TWITTERAPIS_KEY']}"
    },
    json={
        "auth_token": os.environ["X_AUTH_TOKEN"],
        "ct0": os.environ["X_CT0"],
    },
    timeout=30,
)

print("Status:", response.status_code)
print("Response:", response.text)
response.raise_for_status()

print("X session registered!")
