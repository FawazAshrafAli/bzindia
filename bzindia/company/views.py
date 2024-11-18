from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from django.http import JsonResponse, Http404
import logging

from company.models import Company

logger = logging.getLogger(__name__)

class CompanyHomePageView(DetailView):
    model = Company
    template_name = "product_company/home.html"
    context_object_name = "company"


def get_company(request, slug):
    data = {}
    
    try:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            company = get_object_or_404(Company, slug = slug)
            company = {
                "name": company.name
            }

            data = {"company": company}
    
    except Http404:
        data = {"error": "Invalid Company"}

    except Exception as e:
        msg = "Error in getting the requested company"
        logger.exception(f"{msg}: {e}")
        data = {"error": msg}
        
    print(data)
    return JsonResponse(data)


import osmnx as ox

# def populate_places_from_osmnx():
#     # Specify the country and place type for extraction
#     country = "India"
#     place_types = ["city", "town", "village"]  # Adjust as needed for desired place types

#     # Fetch the place data for India
#     for place_type in place_types:
#         # Use osmnx to get geometries for each place type within India
#         gdf = ox.features_from_place(country, tags={"place": place_type})
        
#         # Filter for places with names, district, and state information
#         for _, row in gdf.iterrows():
#             name = row.get("name")
#             district = row.get("is_in:state_district")
#             state = row.get("is_in:state") or row.get("addr:state")

#             if name and state:
#                 print(f"Added: {name}, {district}, {state}")

#     print("Database population complete.")

def populate_places_by_state():
    states = [
        "Kerala, India" 
        # Add more states as needed
    ]
    place_types = ["city", "town", "village"]

    for state in states:
        for place_type in place_types:
            try:
                # Query each state with specified place type
                gdf = ox.features_from_place(state, tags={"place": place_type})
                
                # Process each row for place information
                for _, row in gdf.iterrows():
                    name = row.get("name")
                    district = row.get("is_in:state_district")
                    state_name = row.get("is_in:state") or row.get("addr:state")

                    if name and state_name:
                        print(f"Added: {name}, {district}, {state_name}")
            except Exception as e:
                print(f"Error querying {state} for {place_type}: {e}")

    print("Database population complete.")


# def populate_places_with_admin_levels():
#     # Define the place type and country
#     country = "India"
#     place_types = ["city", "town", "village"]

#     # Fetch the administrative boundaries for states and districts
#     state_gdf = ox.features_from_place(country, tags={"boundary": "administrative", "admin_level": "4"})
#     district_gdf = ox.features_from_place(country, tags={"boundary": "administrative", "admin_level": "6"})

#     # Convert to dictionaries for faster lookup
#     states = {row["name"]: row for _, row in state_gdf.iterrows()}
#     districts = {row["name"]: row for _, row in district_gdf.iterrows()}

#     # Iterate through each place type and add entries
#     for place_type in place_types:
#         place_gdf = ox.features_from_place(country, tags={"place": place_type})
        
#         for _, row in place_gdf.iterrows():
#             name = row.get("name")

#             # Look up state and district boundaries based on proximity
#             state = next((s for s, v in states.items() if v.geometry.contains(row.geometry)), None)
#             district = next((d for d, v in districts.items() if v.geometry.contains(row.geometry)), None)

#             if name and state:
#                 print(f"Added: {name}, {district}, {state}")

#     print("Database population complete.")


# def populate_places_by_admin_levels():
#     # List of regions or states in India
#     states = [
#         "Kerala, India"
#     ]
    
#     # Query state boundaries (admin level 4) and district boundaries (admin level 6)
#     state_boundaries = []
#     district_boundaries = []

#     for state in states:
#         try:
#             # Query for state boundaries (admin_level 4)
#             state_gdf = ox.features_from_place(state, tags={"boundary": "administrative", "admin_level": "4"})
#             state_boundaries.append(state_gdf)
            
#             # Query for district boundaries (admin_level 6)
#             district_gdf = ox.features_from_place(state, tags={"boundary": "administrative", "admin_level": "6"})
#             district_boundaries.append(district_gdf)

#         except Exception as e:
#             print(f"Error querying {state}: {e}")

#     # Process each state and its districts
#     for state_gdf, district_gdf in zip(state_boundaries, district_boundaries):
#         for _, state_row in state_gdf.iterrows():
#             state_name = state_row.get("name")

#             # Loop through districts in the state
#             for _, district_row in district_gdf.iterrows():
#                 district_name = district_row.get("name")
                
#                 # Get bounding box coordinates for the district
#                 bounds = district_row.geometry.bounds  # This gives a tuple (minx, miny, maxx, maxy)
#                 bbox = (bounds[1], bounds[3], bounds[2], bounds[0])  # Convert to (south, north, east, west)
                
#                 # Query for places (city, town, village) within each district
#                 try:
#                     # Query for places within the bounding box using bbox instead of separate params
#                     place_gdf = ox.geometries_from_bbox(bbox=bbox, tags={"place": ["city", "town", "village"]})

#                     for _, place_row in place_gdf.iterrows():
#                         place_name = place_row.get("name")
                        
#                         if place_name and state_name and district_name:
#                             print(f"Added: {place_name}, {district_name}, {state_name}")
#                 except Exception as e:
#                     print(f"Error processing places for {district_name}, {state_name}: {e}")
                
#     print("Database population complete.")
