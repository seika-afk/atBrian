import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["TWITTERAPIS_KEY"]

def reply_to_tweet(tweet_id, message):
    response = requests.post(
        "https://api.twitterapis.com/twitter/tweet/create",
        headers={
            "Authorization": f"Bearer {API_KEY}"
        },
        json={
            "text": message,
            "reply_to": str(tweet_id)
        },
        timeout=30
    )

    print("Status:", response.status_code)
    print("Response:", response.text)
    response.raise_for_status()
    result = response.json()

    if result.get("ok"):
        print("Reply posted:", result.get("url"))
    else:
        print("Failed:", result)

# reply_to_tweet(
#     "2114604615199277168",
#     "Hello! This is an automated reply."
# )