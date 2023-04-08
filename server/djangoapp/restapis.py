import requests
import json
import os
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from decouple import config
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Function for making HTTP GET requests
def get_request(url, api_key=False, **kwargs):
    print(f"GET from {url}")
    if api_key:
        # Basic authentication GET
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        except:
            print("An error occurred while making GET request. ")
    else:
        # No authentication GET
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        except:
            print("An error occurred while making GET request. ")

    # Retrieving the response status code and content
    status_code = response.status_code
    print(f"With status {status_code}")
    json_data = json.loads(response.text)

    return json_data


# Function for making HTTP POST requests
def post_request(url, json_payload, **kwargs):
    print(f"POST to {url}")
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("An error occurred while making POST request. ")
    status_code = response.status_code
    print(f"With status {status_code}")

    return response


# Gets all dealers from the Cloudant DB with the Cloud Function get-dealerships
def get_dealers_from_cf(url):
    results = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
        dealers = json_data['result']
        for dealer in dealers:
            doc = dealer['doc']
            dealer_info = {
                'id': doc['id'],
                'full_name': doc['full_name'],
                'address': doc['address'],
                'city': doc['city'],
                'state': doc['state'],
                'zip': doc['zip'],
                'lat': doc['lat'],
                'long': doc['long']
            }
            results.append(dealer_info)
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f'Error while retrieving dealers: {e}')
    return results


# Gets a single dealer from the Cloudant DB with the Cloud Function get-dealerships
# Requires the dealer_id parameter with only a single value
def get_dealer_by_id(url, dealer_id):
    # Call get_request with the dealer_id param
    json_result = get_request(url, dealerId=dealer_id)

    dealers = json_result["result"]
   
    for dealer in dealers:
            doc = dealer['doc']
            if doc['id'] == dealer_id :
             dealer_info = {
                'id': doc['id'],
                'full_name': doc['full_name'],
                'address': doc['address'],
                'city': doc['city'],
                'state': doc['state'],
                'zip': doc['zip'],
                'lat': doc['lat'],
                'long': doc['long'],
                'short_name' : doc['short_name'],
                'st' : doc['st']
            }
   

    # Create a CarDealer object from response
    dealer = dealer_info
 
    dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                           id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                           short_name=dealer["short_name"],
                           st=dealer["st"], state=dealer["state"], zip=dealer["zip"])

    return dealer_obj


# Gets all dealers in the specified state from the Cloudant DB with the Cloud Function get-dealerships
def get_dealers_by_state(url, state):
    results = []
    # Call get_request with the state param
    json_result = get_request(url, state=state)
    dealers = json_result["body"]["docs"]
    # For each dealer in the response
    for dealer in dealers:
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                               id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                               short_name=dealer["short_name"],
                               st=dealer["st"], state=dealer["state"], zip=dealer["zip"])
        results.append(dealer_obj)

    return results


# Gets all dealer reviews for a specified dealer from the Cloudant DB
# Uses the Cloud Function get_reviews
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
      
        reviews = json_data['result']
    except(requests.exceptions.RequestException, ValueError) as e :
        print(f'Error while retrieving reviews: {e}')
        
    for review in reviews:
        try :
            doc = review['doc']
           
          
            review_info = {
                'id' : doc['_id'],
                'name' : doc.get('name'),
                'purchase' :  doc.get('purchase'),
                'dealership' :  doc.get('dealership'),
                'review' : doc.get('review'),
                'car_make' : doc.get('car_make'),
                'car_model' :  doc.get('car_model'),
                'car_year' :  doc.get('car_year'),
                'purchase_date' :  doc.get('purchase_date'),
                
                
            }
            
            results.append(review_info)
 
    
                # Creating a review object
            
            review_obj = DealerReview(dealership= doc.get('dealership'), id=id, name =doc.get('name'),
                                          purchase=doc.get('purchase'), review=doc.get('review'), car_make=doc.get('car_make'),
                                          car_model=doc.get('car_model'), car_year=doc.get('car_year'), purchase_date=doc.get('purchase_date')
                                             )
         
        

        except KeyError:
            print("Something is missing from this review. Using default values.")
            # Creating a review object with some default values
            review_obj = DealerReview(
                dealership=dealership, id=id, name=name, purchase=purchase, review=review_content)

            # Analysing the sentiment of the review object's review text and saving it to the object attribute "sentiment"
        review_obj.sentiment = analyze_review_sentiments(review_obj.review)
        print(review_obj.review)
        print(f"sentiment: {review_obj.sentiment}")

            # Saving the review object to the list of results
        results.append(review_obj)

 
    return results


# Calls the Watson NLU API and analyses the sentiment of a review
def analyze_review_sentiments(review_text):
    # Watson NLU configuration
    try:
        
            url = 'https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/41880061-1232-43d5-aa05-63718ee659b2'
            api_key = "nCH1Flo_SQOLZqF9VwMvhR7o6V-xJr0SkXItHNhWMqFM"
            print("1///////////////////////")
    except KeyError:
        print(err)

    version = '2021-08-01'
    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version=version, authenticator=authenticator)
    nlu.set_service_url(url)

    # get sentiment of the review
    try:
        response = nlu.analyze(text=review_text, features=Features(
            sentiment=SentimentOptions())).get_result()
        print(json.dumps(response))
        # sentiment_score = str(response["sentiment"]["document"]["score"])
        sentiment_label = response["sentiment"]["document"]["label"]
    except:
        print("Review is too short for sentiment analysis. Assigning default sentiment value 'neutral' instead")
        sentiment_label = "neutral"

    # print(sentiment_score)
    print(sentiment_label)

    return sentiment_label
