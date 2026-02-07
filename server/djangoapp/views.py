from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime
from .models import CarMake, CarModel

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_request

logger = logging.getLogger(__name__)

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

#logout
def logout_user(request):
    logout(request) # Terminate user session
    data = {"userName":""} # Return empty username
    return JsonResponse(data)

@csrf_exempt
def registration(request):
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)

def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    
    if dealerships is None:
        return JsonResponse({"status": 500, "message": "Failed to fetch dealerships"}, status=500)
    
    return JsonResponse({"status": 200, "dealers": dealerships})

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    endpoint = f"/fetchDealer/{dealer_id}"
    dealer = get_request(endpoint)
    
    if dealer is None:
        return JsonResponse({"status": 500, "message": f"Failed to fetch dealer with id {dealer_id}"}, status=500)
    
    return JsonResponse({"status": 200, "dealer": dealer})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint)
    
    if reviews is None:
        return JsonResponse({"status": 500, "message": f"Failed to fetch reviews for dealer id {dealer_id}"}, status=500)
    
    # Analyze sentiment for each review
    analyzed_reviews = []
    for review in reviews:
        review_detail = dict(review)
        
        # Analyze sentiment
        if 'review' in review_detail:
            sentiment_result = analyze_review_sentiments(review_detail['review'])
            review_detail['sentiment'] = sentiment_result.get('sentiment', 'neutral')
        else:
            review_detail['sentiment'] = 'neutral'
        
        analyzed_reviews.append(review_detail)
    
    return JsonResponse({"status": 200, "reviews": analyzed_reviews})

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request, dealer_id):
    if request.method == "POST":
        try:
            if not request.user.is_authenticated:
                return JsonResponse({"status": 401, "message": "User not authenticated"}, status=401)
            
            data = json.loads(request.body)
            
            # Create review payload
            review_payload = {
                "dealership": dealer_id,
                "name": request.user.get_full_name() or request.user.username,
                "purchase": data.get("purchase", False),
                "review": data.get("review", "")
            }
            
            # Add purchase details if purchase is true
            if data.get("purchase", False):
                review_payload["purchase_date"] = data.get("purchase_date", "")
                review_payload["car_make"] = data.get("car_make", "")
                review_payload["car_model"] = data.get("car_model", "")
                review_payload["car_year"] = data.get("car_year", "")
            
            # Analyze sentiment
            sentiment_result = analyze_review_sentiments(review_payload["review"])
            review_payload["sentiment"] = sentiment_result.get('sentiment', 'neutral')
            
            # Post the review
            endpoint = "/postReview"
            response = post_request(endpoint, review_payload)
            
            if "error" in response:
                return JsonResponse({"status": 500, "message": response["error"]}, status=500)
            
            return JsonResponse({"status": 201, "message": "Review added successfully", "review": response})
            
        except json.JSONDecodeError:
            return JsonResponse({"status": 400, "message": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"status": 500, "message": str(e)}, status=500)
    
    return JsonResponse({"status": 405, "message": "Method not allowed"}, status=405)


    # Add this import at the top
from .restapis import get_request, analyze_review_sentiments, post_review

# Replace your existing add_review function with this EXACT Coursera code:
@csrf_exempt
def add_review(request):
    if request.user.is_anonymous == False:
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status": 200})
        except:
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})