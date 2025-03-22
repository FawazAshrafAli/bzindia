from django.http import JsonResponse, HttpResponse, Http404
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404

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
    UniqueState, UniqueDistrict, UniquePlace,

    AndmanAndNicobarTestedCoordinates, UaeCoordinates, KsaCoordinates,    
    UaeLocationData, KsaLocationData
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

def places_count():
    places = Place.objects.all()
    return places.count()

def get_locations(top_left, bottom_right, api_key, opencage_cache):
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    lat_step = 0.02
    lon_step = 0.02

    latitude = top_left[0]
    
    while latitude >= bottom_right[0]:
        longitude = top_left[1]

        while longitude <= bottom_right[1]:
            request_count = cache.get(opencage_cache, 0)

            with transaction.atomic():            
                if not RetestedCoordinates.objects.filter(latitude=latitude, longitude=longitude).exists():
                    if request_count <= 10000:
                        try:
                            logger.info(f"Querying Coordinates: ({latitude}, {longitude})")
                            response = requests.get(f"{base_url}?q={latitude}+{longitude}&key={api_key}")
                            response.raise_for_status()

                            request_count += 1
                            cache.set(opencage_cache, request_count, timeout=60*60*24)
                            data = response.json()

                            logger.info(f"Request number: {request_count}")

                            if "results" in data and data["results"]:
                                components = data["results"][0].get("components", {})
                                country = components.get("country")

                                if country == "India":
                                    place = components.get("village") or components.get("town") or components.get("city") or components.get("county")
                                    state_name = components.get("state")
                                    district_name = components.get("state_district")
                                    pincode = components.get("postcode")
                                    
                                    if place and state_name and district_name:
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
                                            logger.info(f"Place created for {place}, {district.name}, {state.name}")
                            
                            RetestedCoordinates.objects.create(latitude=latitude, longitude=longitude)
                            
                        except requests.exceptions.RequestException as e:
                            logger.info(f"Error during API request: {e}")
                            time.sleep(2)
                            break

                        except Exception as e:
                            logger.info(f"An Unexpected Error occured: {e}")
                            time.sleep(2)
                            break
                
                        time.sleep(0.25)

                    else:
                        logger.info("You have used up your daily API call limit.")
                        break

                longitude += lon_step
                longitude = round(longitude, 2)

        latitude -= lat_step
        latitude = round(latitude, 2)

def get_uae_locations(top_left, bottom_right, api_key, opencage_cache):
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    lat_step = 0.01
    lon_step = 0.01

    latitude = top_left[0]
    
    while latitude >= bottom_right[0]:
        longitude = top_left[1]

        while longitude <= bottom_right[1]:
            request_count = cache.get(opencage_cache, 0)

            if not UaeCoordinates.objects.filter(latitude=latitude, longitude=longitude).exists():
                with transaction.atomic():            
                    if request_count <= 10000:
                        try:
                            logger.info(f"Querying Coordinates: ({latitude}, {longitude})")

                            response = requests.get(base_url, params={
                                "q": f"{latitude},{longitude}",
                                "key": api_key
                            })

                            response.raise_for_status()

                            request_count += 1
                            cache.set(opencage_cache, request_count, timeout=60*60*24)
                            data = response.json()

                            logger.info(f"Request number: {request_count}")

                            if "results" in data and data["results"]:
                                first_result = data["results"][0]
                                components = first_result.get("components", {})
                                formatted = first_result.get("formatted")

                                country = components.get("country")

                                if str(country).lower() in {"united arab emirates", "uae"}:
                                    road = components.get("road")
                                    address = formatted.replace(f"{road},", "").strip() if road else formatted

                                    location, created = UaeLocationData.objects.get_or_create(                                        
                                        address= address,                                        
                                        defaults={
                                            "json_data": data,
                                            "requested_latitude": latitude,
                                            "requested_longitude": longitude
                                            }
                                    )

                                    if created:
                                        logger.info(f"Place created: '{address}'\n")
                            
                            UaeCoordinates.objects.get_or_create(latitude=latitude, longitude=longitude)

                        except requests.exceptions.RequestException as e:
                            logger.info(f"Error during API request: {e}")
                            time.sleep(2)
                            continue

                        except Exception as e:
                            logger.info(f"An Unexpected Error occured: {e}")
                            time.sleep(2)
                            continue
                
                        time.sleep(0.2)

                    else:
                        logger.info("You have used up your daily API call limit.")
                        return

            longitude += lon_step
            longitude = round(longitude, 2)

        latitude -= lat_step
        latitude = round(latitude, 2)

def get_ksa_locations(top_left, bottom_right, api_key, opencage_cache):
    base_url = 'https://api.opencagedata.com/geocode/v1/json'

    lat_step = 0.7
    lon_step = 0.7

    latitude = top_left[0]
    
    while latitude >= bottom_right[0]:
        longitude = top_left[1]

        while longitude <= bottom_right[1]:
            request_count = cache.get(opencage_cache, 0)

            if not KsaCoordinates.objects.filter(latitude=latitude, longitude=longitude).exists():
                with transaction.atomic():            
                    if request_count <= 10000:
                        try:
                            logger.info(f"Querying Coordinates: ({latitude}, {longitude})")

                            response = requests.get(base_url, params={
                                "q": f"{latitude},{longitude}",
                                "key": api_key
                            })

                            response.raise_for_status()

                            request_count += 1
                            cache.set(opencage_cache, request_count, timeout=60*60*24)
                            data = response.json()

                            logger.info(f"Request number: {request_count}")

                            if "results" in data and data["results"]:
                                first_result = data["results"][0]
                                components = first_result.get("components", {})
                                formatted = first_result.get("formatted")

                                country = components.get("country")

                                if str(country).lower() in {"kingdom of saudi arabia", "saudi arabia", "ksa"}:
                                    road = components.get("road")
                                    address = formatted.replace(f"{road},", "").strip() if road else formatted

                                    location, created = KsaLocationData.objects.get_or_create(                                        
                                        address= address,                                        
                                        defaults={
                                            "json_data": data,
                                            "requested_latitude": latitude,
                                            "requested_longitude": longitude
                                            }
                                    )

                                    if created:
                                        logger.info(f"Place created: '{address}'\n")
                            
                            KsaCoordinates.objects.get_or_create(latitude=latitude, longitude=longitude)

                        except requests.exceptions.RequestException as e:
                            logger.info(f"Error during API request: {e}")
                            time.sleep(2)
                            continue

                        except Exception as e:
                            logger.info(f"An Unexpected Error occured: {e}")
                            time.sleep(2)
                            continue
                
                        time.sleep(0.2)

                    else:
                        logger.info("You have used up your daily API call limit.")
                        return

            longitude += lon_step
            longitude = round(longitude, 2)

        latitude -= lat_step
        latitude = round(latitude, 2)


def reset_count():
    for opencage_count in ("opencage_requested_1", "opencage_requested_2", "opencage_requested_3"):
        cache.set(opencage_count, 0, 24 * 3600)
    
    print("Resetted Counts\n")

# def update_location_data():
#     # Maharashtra
#     top_left = (22.0, 72.6) # fetched till 0.03 precision
#     bottom_right = (15.6, 80.8) # fetched till 0.03 precision

#     api_key = os.getenv('OPENCAGE_API_KEY')
#     base_url = 'https://api.opencagedata.com/geocode/v1/json'

#     top_left = (18.58, 72.6)

#     lat_step = 0.02
#     lon_step = 0.02

#     latitude = top_left[0]
    
#     while latitude >= bottom_right[0]:
#         longitude = top_left[1]

#         while longitude <= bottom_right[1]:
#             request_count = cache.get('opencage_requested', 0)            
            
#             if not RetestedCoordinates.objects.filter(latitude=latitude, longitude=longitude).exists():
#                 if request_count <= 20015:
#                     try:
#                         print(f"Querying Coordinates: ({latitude}, {longitude})")
#                         response = requests.get(f"{base_url}?q={latitude}+{longitude}&key={api_key}")
#                         response.raise_for_status()

#                         request_count += 1
#                         cache.set('opencage_requested', request_count, timeout=60*60*24)
#                         data = response.json()

#                         print(f"Request number: {request_count}")

#                         if "results" in data and data["results"]:
#                             components = data["results"][0].get("components", {})
#                             country = components.get("country")

#                             if country == "India":
#                                 place = components.get("village") or components.get("town") or components.get("city") or components.get("county")
#                                 state_name = components.get("state")
#                                 district_name = components.get("state_district")
#                                 pincode = components.get("postcode")
                                
#                                 if place and state_name and district_name:
#                                     state, _ = State.objects.get_or_create(name=state_name)
#                                     district, _ = District.objects.get_or_create(name=district_name, state=state)

#                                     if not Place.objects.filter(name = place, district = district, state = state, pincode = pincode).exists():

#                                         Place.objects.create(
#                                             name = place,
#                                             district=district,
#                                             state=state,
#                                             pincode=pincode,
#                                             latitude=data["results"][0]["geometry"]["lat"],
#                                             longitude=data["results"][0]["geometry"]["lng"]
#                                         )
#                                         print(f"Place created for {place}, {district.name}, {state.name}")
                        
#                         RetestedCoordinates.objects.create(latitude=latitude, longitude=longitude)
                        
#                     except requests.exceptions.RequestException as e:
#                         print(f"Error during API request: {e}")
#                         time.sleep(2)
#                         break

#                     except Exception as e:
#                         print(f"An Unexpected Error occured: {e}")
#                         time.sleep(2)
#                         break
            
#                     time.sleep(0.25)

#                 else:
#                     print("You have used up your daily API call limit.")
#                     break

#             longitude += lon_step
#             longitude = round(longitude, 2)

#         latitude -= lat_step
#         latitude = round(latitude, 2)
        

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
    
    new_state_names = state_names - existing_names
    
    unique_states = [UniqueState(name=name) for name in new_state_names]
    
    if unique_states:
        UniqueState.objects.bulk_create(unique_states)

    unsaved_states = UniqueState.objects.all()

    for state in unsaved_states:
        state.save()

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

    unsaved_districts = UniqueDistrict.objects.all()

    for district in unsaved_districts:
        district.save()

    print(f"Inserted {len(unique_districts)} new unique district records.")

# def populate_unique_places():
#     places = Place.objects.all()
#     length = places.count()

#     existing_states = {state.name: state for state in UniqueState.objects.all()}
#     existing_districts = {district.name: district for district in UniqueDistrict.objects.all()}

#     unique_places = []
#     unique_combinations = set()  

#     for index, place in enumerate(places):
#         name = place.name
#         district_name = place.district.name
#         state_name = place.state.name

#         if state_name in existing_states:
#             state = existing_states[state_name]
#         else:
#             continue

#         if district_name in existing_districts:
#             district = existing_districts[district_name]
#         else:
#             continue
        
#         unique_key = (name, district.id, state.id)
        
#         if unique_key not in unique_combinations:
            
#             if not UniquePlace.objects.filter(name=name, district=district, state=state).exists():
#                 unique_places.append(UniquePlace(name=name, district=district, state=state))
            
#             unique_combinations.add(unique_key)

#         print(f"\rChecked {int((index + 1) / length * 100)}%", end="")

#     if unique_places:
#         UniquePlace.objects.bulk_create(unique_places)

#     print(f"Inserted {len(unique_places)} new unique place records.")

# def populate_unique_places():
#     places = Place.objects.all()
#     length = places.count()

#     existing_states = {state.name: state for state in UniqueState.objects.all()}
#     existing_districts = {(district.name, district.state.name): district for district in UniqueDistrict.objects.select_related('state')}
#     existing_places = set(UniquePlace.objects.values_list("name", "district_id", "state_id"))

#     unique_places = []
#     unique_combinations = set()
    
#     progress = 0
#     for index, place in enumerate(places):
#         name = place.name
#         state = existing_states.get(place.state.name)
#         district = existing_districts.get((place.district.name, place.state.name))
        
#         if not state or not district:
#             continue
        
#         unique_key = (name, district.id, state.id)
        
#         if unique_key not in existing_places:
#             unique_places.append(UniquePlace(name=name, district=district, state=state))
#             existing_places.add(unique_key)

#         new_progress = (index + 1) * 100 // length
#         if new_progress > progress:
#             print(f"\rProgress: {new_progress}%", end="")
#             progress = new_progress

#     if unique_places:
#         UniquePlace.objects.bulk_create(unique_places, ignore_conflicts=True)

#     print(f"\nInserted {len(unique_places)} new unique place records.")


def populate_unique_places():
    places = Place.objects.all()
    length = places.count()
    
    existing_states = {state.name: state for state in UniqueState.objects.all()}
    existing_districts = {
        (district.name, district.state.name): district
        for district in UniqueDistrict.objects.select_related("state")
    }
    existing_places = set(UniquePlace.objects.values_list("name", "district_id", "state_id"))

    unique_places = []
    unique_combinations = set()
    
    progress = 0
    batch_size = 1000

    for index, place in enumerate(places.iterator()):
        name = place.name
        state = existing_states.get(place.state.name)
        district = existing_districts.get((place.district.name, place.state.name))
        
        if not state or not district:
            continue
        
        unique_key = (name, district.id, state.id)
        
        if unique_key not in existing_places:
            unique_places.append(UniquePlace(name=name, district=district, state=state))
            existing_places.add(unique_key)

        if (index + 1) % batch_size == 0 or index + 1 == length:
            UniquePlace.objects.bulk_create(unique_places, ignore_conflicts=True)
            unique_places.clear()

        new_progress = (index + 1) * 100 // length
        if new_progress > progress:
            print(f"\rProgress: {new_progress}%", end="")
            progress = new_progress

    print(f"\nInserted {len(existing_places)} new unique place records.")

    print(f"\nWait for the function to finish. . .")

    unsaved_places = UniquePlace.objects.all()

    for place in unsaved_places:
        place.save()

    print(f"\nCompleted!")



