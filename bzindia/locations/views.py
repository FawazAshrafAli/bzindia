from django.http import JsonResponse, HttpResponse, Http404
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
import logging
import requests
import csv
import time
import os
import pandas
import sys


from .models import (
    State, District, Place,
    TestedCoordinates, RetestedCoordinates, TestPincode, 
    UniqueState, UniqueDistrict, UniquePlace
    )

logger = logging.getLogger(__name__)

def generate_location_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=location_india.csv"  # Remove quotes

    writer = csv.writer(response)

    # Write the header row to the CSV
    writer.writerow(["Place", "District", "State", "Pincode", "Latitude", "Longitude"])

    # Efficient query using select_related to avoid multiple database hits for related fields
    places = Place.objects.all().select_related('district', 'state').order_by("name")

    # Write the data rows to the CSV
    for place in places:
        writer.writerow([
            place.name,
            place.district.name,  # Assuming `district` is a ForeignKey
            place.state.name,     # Assuming `state` is a ForeignKey
            place.pincode,
            place.latitude,
            place.longitude
        ])

    return response
    

def update_location_data():
    # For India
    # top_left = (35.2, 68.1)
    # bottom_right = (6.7, 93.8)

    # Jammu And Kashmir
    # top_left = (36.5, 73.2) # fetched till 0.5 precision
    # bottom_right = (32.1, 80.3) # fetched till 0.5 precision

    # Madhya Pradesh
    # top_left = (24.5, 74.7) # fetched till 0.03 precision
    # bottom_right = (18.4, 81.8) # fetched till 0.03 precision

    # Kerala
    # top_left = (12.7, 74.8) # fetched till 0.02 precision (midway)
    # bottom_right = (8.2, 77.4) # fetched till 0.02 precision (midway)

    # Gujarat
    # top_left = (24.7, 68.1) # fetched till 0.3 precision
    # bottom_right = (20.1, 74.4) # fetched till 0.3 precision

    # Karnataka
    # top_left = (18.4, 74.0) # fetched till 0.02 precision
    # bottom_right = (11.6, 78.3) # fetched till 0.02 precision

    # Telangana
    # top_left = (19.9, 77.2) # fetched till 0.03 precision
    # bottom_right = (15.8, 81.3) # fetched till 0.03 precision

    # Chhattisgarh
    # top_left = (24.1, 80.2) # Ended midway at 0.03 precision
    # bottom_right = (17.7, 84.3) # Ended midway at 0.03 precision

    # Tamil Nadu
    # top_left = (13.5, 76.2) # fetched till 0.03 precision
    # bottom_right = (8.0, 80.3) # fetched till 0.03 precision

    # Andhra Pradesh
    # top_left = (19.1, 76.7) # fetched till 0.03 precision
    # bottom_right = (12.6, 84.7) # fetched till 0.03 precision

    # Maharashtra
    # top_left = (22.0, 72.6) # fetched till 0.03 precision
    # bottom_right = (15.6, 80.8) # fetched till 0.03 precision

    # Jharkhand
    # top_left = (25.3, 83.3) # fetched till 0.03 precision
    # bottom_right = (21.9, 87.9) # fetched till 0.03 precision

    # Haryana
    # top_left = (30.9, 74.4) # fetched till 0.03 precision
    # bottom_right = (27.6, 77.6) # fetched till 0.03 precision

    # West Bengal
    # top_left = (27.2, 85.5) # fetched till 0.03 precision
    # bottom_right = (21.5, 89.8) # fetched till 0.03 precision

    # Punjab
    # top_left = (32.5, 73.8) # fetched till 0.03 precision
    # bottom_right = (29.5, 77.9) # fetched till 0.03 precision
    
    # Uttar Pradesh
    # top_left = (30.4, 77.0) # Ended midway at 0.03 precision
    # bottom_right = (23.8, 84.6) # Ended midway at 0.03 precision

    # Meghalaya
    # top_left = (26.1, 89.8) # fetched till 0.03 precision
    # bottom_right = (25.0, 92.8) # fetched till 0.03 precision

    # Manipur
    # top_left = (25.6, 92.9) # fetched till 0.03 precision
    # bottom_right = (23.8, 94.7) # fetched till 0.03 precision

    # Mizoram
    # top_left = (24.5, 92.2) # fetched till 0.03 precision
    # bottom_right = (21.9, 93.4) # fetched till 0.03 precision

    # Tripura
    # top_left = (25.5, 91.1) # fetched till 0.05 precision
    # bottom_right = (22.9, 92.3) # fetched till 0.05 precision

    # Nagaland
    # top_left = (27.0, 93.3) # fetched till 0.05 precision
    # bottom_right = (25.1, 95.2) # fetched till 0.05 precision

    # Goa
    # top_left = (15.8, 73.6) # fetched till 0.01 precision
    # bottom_right = (14.9, 74.3) # fetched till 0.01 precision

    # Odisha
    # top_left = (22.5, 81.3) # fetched till 0.03 precision
    # bottom_right = (17.8, 87.4) # fetched till 0.03 precision

    # Rajasthan
    top_left = (30.1, 69.4) # fetched till 0.05 precision
    bottom_right = (23.0, 78.2) # fetched till 0.05 precision

    # Himachal Pradesh
    # top_left = (33.2, 75.5) # fetched till 0.02 precision, stopped midway at (32.34, 78.72)
    # bottom_right = (30.3, 79.0) # fetched till 0.02 precision, stopped midway at (32.34, 78.72)

    # Uttarakhand
    # top_left = (31.4, 77.7) # fetched till 0.03 precision
    # bottom_right = (28.7, 81.0) # fetched till 0.03 precision

    # Puducherry (Pondicherry)
    # top_left = (11.9, 79.7) # fetched till 0.01 precision
    # bottom_right = (11.8, 79.8) # fetched till 0.01 precision

    # Sikkim
    # top_left = (28.1, 88.0) # fetched till 0.01 precision
    # bottom_right = (27.0, 88.9) # fetched till 0.01 precision

    # Assam
    # top_left = (28.2, 89.4) # fetched till 0.05 precision
    # bottom_right = (24.8, 96.0) # fetched till 0.05 precision

    # Arunachal Pradesh
    # top_left = (29.4, 91.5) # fetched till 0.05 precision
    # bottom_right = (26.4, 97.4) # fetched till 0.05 precision

    # Chandigarh
    # top_left = (30.7, 76.7) # fetched till 0.01 precision
    # bottom_right = (30.6, 76.8) # fetched till 0.01 precision

    # Andaman And Nicobar Islands (1st Part)
    # top_left = (13.6, 92.2) # fetched till 0.03 precision
    # bottom_right = (10.5, 93.1) # fetched till 0.03 precision

    # Andaman And Nicobar Islands (2nd Part)
    # top_left = (13.6, 92.2) # fetched till 0.05 precision
    # bottom_right = (6.7, 93.9) # fetched till 0.05 precision

    # Delhi
    # top_left = (28.9, 76.8) # fetched till 0.01 precision
    # bottom_right = (28.4, 77.4) # fetched till 0.01 precision

    # Bihar
    # top_left = (27.6, 83.3) # fetched till 0.01 precision
    # bottom_right = (24.2, 88.3) # fetched till 0.01 precision

    api_key = os.getenv('OPENCAGE_API_KEY')
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    top_left = (23.95, 69.4)

    lat_step = 0.03
    lon_step = 0.03

    latitude = top_left[0]
    
    while latitude >= bottom_right[0]:
        longitude = top_left[1]

        while longitude <= bottom_right[1]:
            request_count = cache.get('opencage_requested', 0)
            
            if not RetestedCoordinates.objects.filter(latitude=latitude, longitude=longitude).exists():
                if request_count <= 20000:
                    try:
                        print(f"Querying Coordinates: ({latitude}, {longitude})")
                        response = requests.get(f"{base_url}?q={latitude}+{longitude}&key={api_key}")
                        response.raise_for_status()                        
                        
                        request_count += 1
                        cache.set('opencage_requested', request_count, timeout=60*60*24)
                        data = response.json()

                        print(f"Request number: {request_count}")

                        if "results" in data and data["results"]:
                            components = data["results"][0].get("components", {})
                            country = components.get("country")

                            if country == "India":
                                place = components.get("village") or components.get("town") or components.get("city") or components.get("county")
                                state_name = components.get("state")
                                district_name = components.get("state_district")
                                pincode = components.get("postcode")
                                
                                if place and state_name and district_name and pincode:
                                    state, _ = State.objects.get_or_create(name=state_name)
                                    district, _ = District.objects.get_or_create(name=district_name, state=state)

                                    if not Place.objects.filter(name = place, district = district, state = state, pincode = pincode).exists():

                                        Place.objects.create(
                                            name = place,
                                            district=district,
                                            state=state,
                                            pincode=pincode,
                                            latitude=data["results"][0]["geometry"]["lat"],
                                            longitude=data["results"][0]["geometry"]["lng"]
                                        )
                                        print(f"Place created for {place}, {district.name}, {state.name}")
                        
                        RetestedCoordinates.objects.create(latitude=latitude, longitude=longitude)
                        
                    except requests.exceptions.RequestException as e:
                        print(f"Error during API request: {e}")
                        time.sleep(2)
                        break
            
                    time.sleep(0.25)

                else:
                    print("You have used up your daily API call limit.")
                    break

            longitude += lon_step
            longitude = round(longitude, 2)

        latitude -= lat_step
        latitude = round(latitude, 2)
        

def get_districts(request):
    try:
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({"status": "failed", "error_msg": "Method not allowed"}, status=403)

        state_slug = request.GET.get("state")

        if not state_slug:
            return JsonResponse({"status": "failed", "error_msg": "Bad Request"}, status=400)

        # district_names = District.objects.filter(state__slug = state_slug).values_list("name")
        # unique_district_names = list(set(district_names))
        # unique_district_slugs = [slugify(f"{district_name}-{state_slug}") for district_name in unique_district_names]

        districts = list(UniqueDistrict.objects.filter(state__slug = state_slug).values("name", "slug"))

        return JsonResponse({"status": "success", "districts": districts}, status=200)

    except Exception as e:
        logger.exception(f"Error in getting districts: {e}")
        return JsonResponse({"status": "failed", "error_msg": "An unexpected error occured"}, status=500)
    
def get_places(request):
    try:
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({"status": "failed", "error_msg": "Method not allowed"}, status=403)

        district_slug = request.GET.get("district")
        state_slug = request.GET.get("state")

        if not district_slug or  not state_slug:
            return JsonResponse({"status": "failed", "error_msg": "Bad Request"}, status=400)

        # place_names = Place.objects.filter(district__slug = district_slug).values_list("name")
        # unique_place_names = list(set(place_names))
        # unique_place_slugs = [slugify(f"{place_name}-{district_slug}") for place_name in unique_place_names]

        places = list(UniquePlace.objects.filter(state__slug = state_slug, district__slug = district_slug,).values("name", "slug"))

        return JsonResponse({"status": "success", "places": places}, status=200)

    except Exception as e:
        logger.exception(f"Error in getting places: {e}")
        return JsonResponse({"status": "failed", "error_msg": "An unexpected error occured"}, status=500)
    


def populate_unique_states():    
    state_names = set(State.objects.values_list('name', flat=True))
    existing_names = set(UniqueState.objects.values_list('name', flat=True))
    
    new_names = state_names - existing_names
    
    unique_states = [UniqueState(name=name) for name in new_names]
    
    if unique_states:
        UniqueState.objects.bulk_create(unique_states)

    print(f"Inserted {len(unique_states)} new records into unique state.")

def populate_unique_districts():
    districts = District.objects.all()

    existing_states = {state.name: state for state in UniqueState.objects.all()}

    unique_districts = []
    unique_combinations = set()  

    for district in districts:
        name = district.name
        state_name = district.state.name

        if state_name in existing_states:
            state = existing_states[state_name]
        else:
            continue
        
        unique_key = (name, state.id)

        if unique_key not in unique_combinations:
            
            if not UniqueDistrict.objects.filter(name=name, state=state).exists():
                unique_districts.append(UniqueDistrict(name=name, state=state))
            
            unique_combinations.add(unique_key)

    print(f"Checked {len(districts)} districts.")

    if unique_districts:
        UniqueDistrict.objects.bulk_create(unique_districts)

    print(f"Inserted {len(unique_districts)} new unique district records.")

def populate_unique_places():
    places = Place.objects.all()
    length = places.count()

    existing_states = {state.name: state for state in UniqueState.objects.all()}
    existing_districts = {district.name: district for district in UniqueDistrict.objects.all()}

    unique_places = []
    unique_combinations = set()  

    for index, place in enumerate(places):
        name = place.name
        district_name = place.district.name
        state_name = place.state.name

        if state_name in existing_states:
            state = existing_states[state_name]
        else:
            continue

        if district_name in existing_districts:
            district = existing_districts[district_name]
        else:
            continue
        
        unique_key = (name, district.id, state.id)
        
        if unique_key not in unique_combinations:
            
            if not UniquePlace.objects.filter(name=name, district=district, state=state).exists():
                unique_places.append(UniquePlace(name=name, district=district, state=state))
            
            unique_combinations.add(unique_key)

        print(f"\rChecked {int((index + 1) / length * 100)}%", end="")

    if unique_places:
        UniquePlace.objects.bulk_create(unique_places)

    print(f"Inserted {len(unique_places)} new unique place records.")


