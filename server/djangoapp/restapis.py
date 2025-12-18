import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("backend_url", "http://localhost:3030")
SENTIMENT_URL = os.getenv(
    "sentiment_analyzer_url",
    "http://localhost:5050/",
)


def get_request(endpoint, **kwargs):
    try:
        response = requests.get(
            f"{BACKEND_URL}{endpoint}",
            params=kwargs,
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []


def analyze_review_sentiments(text):
    try:
        response = requests.get(
            f"{SENTIMENT_URL}analyze/{text}",
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {"sentiment": "neutral"}


def post_review(data):
    try:
        response = requests.post(
            f"{BACKEND_URL}/insert_review",
            json=data,
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None
