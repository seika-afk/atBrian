import os
import time
import requests
from dotenv import load_dotenv

from jev_call import call
from Responder import reply_to_tweet


load_dotenv()
TEXT=""
API_KEY = os.environ["TWITTERAPIS_KEY"]
USERNAME = "brianTheClanker"                       # no leading @

# Each poll runs every query below and merges the results.
# Remove one to halve the cost.
QUERIES = [
    f"@{USERNAME} -from:{USERNAME}",                      # any tweet tagging you
    f"@{USERNAME} filter:replies -from:{USERNAME}",       # replies tagging you
]

POLL_INTERVAL = 30        # seconds. Cost per poll = len(QUERIES) * $0.0008
MAX_THREAD_DEPTH = 5
STATE_FILE = "last_id.txt"
DEBUG = True

BASE = "https://api.twitterapis.com/twitter"

session = requests.Session()
session.headers["Authorization"] = f"Bearer {API_KEY}"

tweet_cache = {}
use_query_type = True     # auto-disabled if the API rejects queryType


# ---------- state ----------
def load_last_id():
    try:
        with open(STATE_FILE) as f:
            return f.read().strip() or None
    except FileNotFoundError:
        return None


def save_last_id(value):
    with open(STATE_FILE, "w") as f:
        f.write(str(value))


# ---------- http ----------
def api_get(path, params, retries=3, quiet_400=False):
    for attempt in range(retries):
        try:
            r = session.get(f"{BASE}{path}", params=params, timeout=20)
        except requests.RequestException as e:
            print(f"Network error on {path}: {e}")
            time.sleep(2 ** attempt)
            continue

        if r.status_code == 200:
            return r.json()
        if r.status_code == 400 and quiet_400:
            return "BAD_REQUEST"
        if r.status_code == 429 or r.status_code >= 500:
            wait = 2 ** attempt * 2
            print(f"{r.status_code} from {path}, retrying in {wait}s")
            time.sleep(wait)
            continue
        if r.status_code == 401:
            raise SystemExit("401: API key missing/invalid. Check TWITTERAPIS_KEY in .env")
        if r.status_code == 402:
            raise SystemExit("402: out of credits. Top up at twitterapis.com")

        print(f"{r.status_code} from {path}: {r.text[:300]}")
        return None
    return None


def search(query):
    """Run one search query. Returns a list of tweets."""
    global use_query_type
    params = {"query": query}
    if use_query_type:
        params["queryType"] = "Latest"
        data = api_get("/tweet/advanced_search", params, quiet_400=True)
        if data == "BAD_REQUEST":
            print("API rejected queryType, retrying without it")
            use_query_type = False
            data = api_get("/tweet/advanced_search", {"query": query})
    else:
        data = api_get("/tweet/advanced_search", params)

    if not isinstance(data, dict):
        return []
    tweets = data.get("tweets")
    if tweets is None:
        print("Unexpected response:", str(data)[:300])
        return []
    return tweets


# ---------- helpers ----------
def author_name(tweet):
    a = tweet.get("author") or {}
    return a.get("username") or a.get("userName") or a.get("screen_name") or "unknown"


def parent_id_of(tweet):
    for key in ("in_reply_to_status_id", "in_reply_to_tweet_id",
                "in_reply_to_status_id_str", "in_reply_to_id",
                "inReplyToId", "reply_to_tweet_id"):
        v = tweet.get(key)
        if v:
            return str(v)
    return None


def get_tweet(tweet_id):
    if tweet_id in tweet_cache:
        return tweet_cache[tweet_id]
    data = api_get("/tweet/detail", {"id": tweet_id})
    tweet = (data or {}).get("tweet") if isinstance(data, dict) else None
    tweet_cache[tweet_id] = tweet
    return tweet


def get_parents(tweet):
    """Walk UP the reply chain. Returns parents oldest-first."""
    chain = []
    pid = parent_id_of(tweet)
    while pid and len(chain) < MAX_THREAD_DEPTH:
        parent = get_tweet(pid)
        if not parent:
            break
        chain.append(parent)
        pid = parent_id_of(parent)
    return chain[::-1]




def on_mention(tweet):
    print("\n" + "=" * 55)
    print("New mention!  ID:", tweet["id"])

    if author_name(tweet).lower() == USERNAME.lower():
        return

    parents = get_parents(tweet)
    if parents:
        above = parents[-1]
        text = above.get("text", "")
        print(f"--- Tweet above ---\n@{author_name(above)}: {text}")
        print("--- Mention ---")
        print(f"@{author_name(tweet)}: {tweet.get('text', '')}")

        try:
            print("Getting reply...")
            reply = call(text)
            print("Got reply:", reply)
            reply_to_tweet(tweet["id"], reply)   # reply to the mention
            print("REPLIED------")
        except Exception as e:
            print("Reply failed:", repr(e))
        return
    elif DEBUG and tweet.get("is_reply"):
        print("(is_reply=True but no parent id found. Tweet keys:", list(tweet.keys()), ")")

    print(f"@{author_name(tweet)}: {tweet.get('text', '')}")
    print("=" * 55)

def check_mentions(state):
    merged = {}
    per_query = []
    for q in QUERIES:
        tweets = search(q)
        per_query.append(len(tweets))
        for t in tweets:
            merged[str(t["id"])] = t

    if DEBUG:
        ids = sorted((int(i) for i in merged), reverse=True)[:3]
        print(f"[poll] per-query counts={per_query} merged={len(merged)} "
              f"top_ids={ids} last_id={state['last_id']}")

    if not merged:
        return

    tweets = sorted(merged.values(), key=lambda t: int(t["id"]))  # oldest first
    newest = int(tweets[-1]["id"])

    if state["last_id"] is None:
        state["last_id"] = str(newest)
        save_last_id(state["last_id"])
        print(f"Initialised at {newest}. Waiting for new mentions...")
        return

    for t in tweets:
        if int(t["id"]) > int(state["last_id"]):
            on_mention(t)
            state["last_id"] = str(t["id"])
            save_last_id(state["last_id"])


if __name__ == "__main__":
    state = {"last_id": load_last_id()}
    print(f"Listening for mentions of @{USERNAME} every {POLL_INTERVAL}s...")
    for q in QUERIES:
        print("Query:", q)

    while True:
        try:
            check_mentions(state)
        except Exception as e:
            print("Unexpected error:", repr(e))
        time.sleep(POLL_INTERVAL)
