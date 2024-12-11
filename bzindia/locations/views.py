from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.shortcuts import render
import requests
import csv
import time
import os
import pandas
import sys

from .models import State, District, Place, TestedCoordinates, RetestedCoordinates, TestPincode

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

def populate_location_data():
    # For India
    # top_left = (35.2, 68.1)
    # bottom_right = (6.7, 93.8)

    # For JK
    # top_left = (36.0, 72.5)
    # bottom_right = (32.4, 78.2)

    
    # top_left = (35.2, 68.1)
    # bottom_right = (6.7, 93.8)

    # For madhya pradesh
    # top_left = (24.5, 74.7)
    # bottom_right = (18.4, 81.8)

    # Center Land
    # top_left = (26.9, 72.7)
    # bottom_right = (20.5, 86.8)

    # Lower land
    # top_left = (29.5, 75.5)
    # bottom_right = (10.1, 79.2)

    # Center Rectangle
    # top_left = (26.3, 71.0)
    # bottom_right = (21.8, 87.7)

    # For kerala
    # top_left = (13.1, 74.8)
    # bottom_right = (8.2, 77.4)

    # kerala Inside rectangle
    top_left = (10.95, 74.05)
    bottom_right = (8.3, 77.35)

    api_key = os.getenv('OPENCAGE_API_KEY')
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    lat_step = 0.03
    lon_step = 0.03

    latitude = top_left[0]
    
    while latitude >= bottom_right[0]:
        longitude = top_left[1]
        
        while longitude <= bottom_right[1]:
            request_count = cache.get('opencage_requested', 0)
            
            if not TestedCoordinates.objects.filter(latitude=latitude, longitude=longitude).exists():
                if request_count <= 2500:
                    if not Place.objects.filter(latitude=latitude, longitude=longitude).exists():
                        try:
                            print(f"Querying ({latitude}), ({longitude})")
                            response = requests.get(f"{base_url}?q={latitude}+{longitude}&key={api_key}")
                            response.raise_for_status()
                            
                            # Increment request count
                            request_count += 1
                            cache.set('opencage_requested', request_count, timeout=60*60*24)
                            data = response.json()

                            print(f"Request number: {request_count}")

                            if "results" in data and data["results"]:
                                components = data["results"][0].get("components", {})
                                country = components.get("country")

                                if country == "India":
                                    place = components.get("town") or components.get("village")
                                    state_name = components.get("state")
                                    district_name = components.get("state_district")
                                    pincode = components.get("postcode")
                                    
                                    if place and state_name and district_name and pincode:
                                        state, _ = State.objects.get_or_create(name=state_name)
                                        district, _ = District.objects.get_or_create(name=district_name, state=state)

                                        if not Place.objects.filter(name=place, district=district, state=state, pincode=pincode).exists():
                                            Place.objects.get_or_create(
                                                name=place,
                                                district=district,
                                                state=state,
                                                pincode=pincode,
                                                latitude=data["results"][0]["geometry"]["lat"],
                                                longitude=data["results"][0]["geometry"]["lng"]
                                            )
                                            print(f"Place created for {place}, {district.name}, {state.name}")
                            
                            TestedCoordinates.objects.create(latitude=latitude, longitude=longitude)
                            
                        except requests.exceptions.RequestException as e:
                            print(f"Error during API request: {e}")
                            time.sleep(2)
                            break
                
                        time.sleep(1)
                    else:
                        print(f"Place already exists for ({latitude}, {longitude})")

                else:
                    print("You have used up your daily API call limit.")
                    break

            # Increment longitude and round for precision
            longitude += lon_step
            longitude = round(longitude, 2)

        # Decrement latitude and round for precision
        latitude -= lat_step
        latitude = round(latitude, 2)


def get_pincode():
    # Use environment variable for security
    api_key = os.getenv('OPENCAGE_API_KEY')

    url = "https://api.opencagedata.com/geocode/v1/json"

    # Iterate over all places, you could use pagination if there are a lot of records
    for place in Place.objects.all():
        # Prepare the query parameters for the API request
        params = {
            'q': f"{place.latitude}+{place.longitude}",
            'key': api_key,
            'language': 'en',
            'pretty': 1
        }

        try:
            # Make the API request
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()

                # Check if results are found in the response
                if data['results']:
                    components = data["results"][0].get("components", {})
                    pincode = components.get("postcode")

                    if pincode:  # Ensure a pincode is found
                        place.pincode = pincode
                        place.save()  # Save the pincode to the Place model
                        print(f"Pincode added for {place.name}: {pincode}")
                    else:
                        print(f"No pincode found for {place.name}")
                else:
                    print(f"No results for {place.name}")
            else:
                print(f"Error fetching data for {place.name}: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request error for {place.name}: {e}")
    

def update_location_data():
    # For India
    # top_left = (35.2, 68.1)
    # bottom_right = (6.7, 93.8)

    # For JK
    # top_left = (36.5, 73.2) # fetched till 0.5 precision
    # bottom_right = (32.1, 80.3) # fetched till 0.5 precision

    
    # top_left = (35.2, 68.1)
    # bottom_right = (6.7, 93.8)

    # For madhya pradesh
    # top_left = (24.5, 74.7) # fetched till 0.1 precision
    # bottom_right = (18.4, 81.8) # fetched till 0.1 precision

    # Center Land
    # top_left = (26.9, 72.7) # fetched till 0.1 precision
    # bottom_right = (20.5, 86.8) # fetched till 0.1 precision

    # Lower land
    # top_left = (29.5, 75.5)
    # bottom_right = (10.1, 79.2)

    # Center Rectangle
    # top_left = (26.3, 71.0) # fetched till 0.1 precision
    # bottom_right = (21.8, 87.7) # fetched till 0.1 precision

    # North to South Rectangle
    # top_left = (30.1, 74.0) # fetched till 0.03 precision till (16.95), (75.05)
    # bottom_right = (12.6, 79.7) # fetched till 0.03 precision till (16.95), (75.05)

    # For kerala
    # top_left = (13.1, 74.8)
    # bottom_right = (8.2, 77.4)

    # kerala Inside rectangle
    # top_left = (10.9, 74.0) # fetched till 0.03 precision
    # bottom_right = (8.3, 77.3) # fetched till 0.03 precision

    # Gujarat (Inner)
    # top_left = (23.9, 68.9) # fetched till 0.03 precision
    # bottom_right = (20.6, 72.3) # fetched till 0.03 precision

    # Karnataka
    # top_left = (18.4, 74.0) # fetched till 0.03 precision
    # bottom_right = (11.6, 78.3) # fetched till 0.03 precision

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
    top_left = (19.1, 76.7)
    bottom_right = (12.6, 84.7)

    # Maharashtra
    # top_left = (22.0, 72.6) # fetched till 0.03 precision
    # bottom_right = (15.6, 80.8) # fetched till 0.03 precision


    api_key = os.getenv('OPENCAGE_API_KEY')
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    lat_step = 0.07
    lon_step = 0.07

    top_left = (15.18, 76.98)

    latitude = top_left[0]
    
    while latitude >= bottom_right[0]:
        longitude = top_left[1]

        while longitude <= bottom_right[1]:
            request_count = cache.get('opencage_requested', 0)
            
            if not RetestedCoordinates.objects.filter(latitude=latitude, longitude=longitude).exists():
                if request_count <= 20000:
                    try:
                        print(f"Querying ({latitude}), ({longitude})")
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

                                    Place.objects.update_or_create(
                                        district=district,
                                        state=state,
                                        pincode=pincode,
                                        latitude=data["results"][0]["geometry"]["lat"],
                                        longitude=data["results"][0]["geometry"]["lng"],
                                        defaults={"name": place}
                                    )
                                    print(f"Place updated for {place}, {district.name}, {state.name}")
                        
                        RetestedCoordinates.objects.create(latitude=latitude, longitude=longitude)
                        
                    except requests.exceptions.RequestException as e:
                        print(f"Error during API request: {e}")
                        time.sleep(2)
                        break
            
                    time.sleep(0.25)

                else:
                    print("You have used up your daily API call limit.")
                    break

            # Increment longitude and round for precision
            longitude += lon_step
            longitude = round(longitude, 2)

        # Decrement latitude and round for precision
        latitude -= lat_step
        latitude = round(latitude, 2)


def row_generator(csv_data):
    for index, row in csv_data.iterrows():
        yield index, row


def import_pincode():
    GREEN = "\033[92m"
    RESET = "\033[0m"

    # Corrected path string (remove the extra quotes)
    csv_data = pandas.read_csv(r"C:\Users\HP\Downloads\pincode.csv")
    length = len(csv_data) 

    for index, row in row_generator(csv_data):
        time.sleep(0.001)  # Artificial delay for demonstration purposes
        pincode = row["Pincode"]
        if not TestPincode.objects.filter(pincode=pincode).exists():
            TestPincode.objects.create(pincode=pincode)

        # Progress bar display
        sys.stdout.write(
            f"{GREEN}\rExecuted {index + 1}/{length} rows - Completed {int((index + 1) / length * 100)}%{RESET}"
        )
        sys.stdout.flush()
    print()
        
def update_location_using_pincode():
    # pincodes = TestPincode.objects.all()
    pincodes = TestPincode.objects.filter(pk__gt = 16474)

    api_key = os.getenv('OPENCAGE_API_KEY')
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    for pincode_obj in pincodes:
        pincode = pincode_obj.pincode

        request_count = cache.get('opencage_requested', 0)
        
        if not Place.objects.filter(pincode = pincode).exists():
            if request_count <= 50000:
                try:
                    print(f"Querying pincode: {pincode}")
                    response = requests.get(f"{base_url}?q={pincode}&key={api_key}")
                    response.raise_for_status()
                    
                    request_count += 1
                    cache.set('opencage_requested', request_count, timeout=60*60*24)
                    data = response.json()

                    print(f"Request number: {request_count}")

                    if "results" in data and data["results"]:
                        components = data["results"][0].get("components", {})
                        country = components.get("country")

                        if country == "India":
                            place = components.get("village") or components.get("town") or components.get("city") or components.get("county") or components.get("city") or components.get("county")
                            state_name = components.get("state")
                            district_name = components.get("state_district")
                            pincode = components.get("postcode")
                            
                            if place and state_name and district_name and pincode:
                                state, _ = State.objects.get_or_create(name=state_name)
                                district, _ = District.objects.get_or_create(name=district_name, state=state)

                                Place.objects.create(
                                    name = place,
                                    district=district,
                                    state=state,
                                    pincode=pincode,
                                    latitude=data["results"][0]["geometry"]["lat"],
                                    longitude=data["results"][0]["geometry"]["lng"],
                                )
                                print(f"Place created for {place}, {district.name}, {state.name}")
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error during API request: {e}")
                    time.sleep(2)
                    break
        
                time.sleep(0.25)

            else:
                print("You have used up your daily API call limit.")
                break
