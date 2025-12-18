import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import (
    analyze_review_sentiments,
    get_request,
    post_review,
)

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    user = authenticate(
        username=data.get("userName"),
        password=data.get("password"),
    )

    if user:
        login(request, user)
        return JsonResponse(
            {"userName": user.username, "status": "Authenticated"}
        )

    return JsonResponse({"error": "Invalid credentials"}, status=401)


def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
def registration(request):
    data = json.loads(request.body)

    if User.objects.filter(username=data["userName"]).exists():
        return JsonResponse(
            {"error": "Already Registered"},
            status=400,
        )

    user = User.objects.create_user(
        username=data["userName"],
        password=data["password"],
        first_name=data["firstName"],
        last_name=data["lastName"],
        email=data["email"],
    )

    login(request, user)
    return JsonResponse(
        {"userName": user.username, "status": "Authenticated"}
    )


def get_cars(request):
    if CarMake.objects.count() == 0:
        initiate()

    cars = [
        {
            "CarModel": model.name,
            "CarMake": model.car_make.name,
        }
        for model in CarModel.objects.select_related("car_make")
    ]

    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealers = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealers})


def get_dealer_details(request, dealer_id):
    dealer = get_request(f"/fetchDealer/{dealer_id}")
    return JsonResponse({"status": 200, "dealer": dealer})


def get_dealer_reviews(request, dealer_id):
    reviews = get_request(f"/fetchReviews/dealer/{dealer_id}")

    for review in reviews:
        sentiment = analyze_review_sentiments(review["review"])
        review["sentiment"] = sentiment.get("sentiment")

    return JsonResponse({"status": 200, "reviews": reviews})


@csrf_exempt
def add_review(request):
    if request.user.is_anonymous:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    data = json.loads(request.body)
    post_review(data)
    return JsonResponse({"status": 200})
