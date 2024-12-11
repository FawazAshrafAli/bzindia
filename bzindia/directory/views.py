from django.shortcuts import render
import requests
import pandas
import time
import sys
from django.views.generic import ListView
from django.templatetags.static import static
from django.db import IntegrityError
from django.db.models import Q
import logging
import pandas

from .models import PostOffice, PoliceStation, Bank, TouristAttraction, Court

logger = logging.getLogger(__name__)

def row_generator(csv_data):
    for index, row in csv_data.iterrows():
        yield index, row

def import_postoffice_data():
    GREEN = "\033[92m"
    RESET = "\033[0m"

    # Corrected path string (remove the extra quotes)
    csv_data = pandas.read_csv(r"C:\Users\HP\Downloads\pincode.csv")
    length = len(csv_data)

    post_offices = []

    for index, row in csv_data.iterrows():
        time.sleep(0.001)

        circle_name = row["CircleName"] if pandas.notna(row["CircleName"]) else None
        region_name = row["RegionName"] if pandas.notna(row["RegionName"]) else None
        division_name = row["DivisionName"] if pandas.notna(row["DivisionName"]) else None
        office_name = row["OfficeName"] if pandas.notna(row["OfficeName"]) else None
        pincode = row["Pincode"] if pandas.notna(row["Pincode"]) else None
        office_type = row["OfficeType"] if pandas.notna(row["OfficeType"]) else None
        delivery = True if row["Delivery"] == "Delivery" else False
        district = row["District"] if pandas.notna(row["District"]) else None
        state_name = row["StateName"] if pandas.notna(row["StateName"]) else None
        latitude = row["Latitude"] if pandas.notna(row["Latitude"]) else None
        longitude = row["Longitude"] if pandas.notna(row["Longitude"]) else None
        
        post_offices.append(PostOffice(
            circle_name=circle_name,
            region_name=region_name,
            division_name=division_name,
            office_name=office_name,
            pincode=pincode,
            office_type=office_type,
            delivery=delivery,
            district=district,
            state_name=state_name,
            latitude=latitude,
            longitude=longitude
        ))

        # Progress bar display
        sys.stdout.write(
            f"{GREEN}\rExecuted {index + 1}/{length} rows - Completed {int((index + 1) / length * 100)}%{RESET}"
        )
        sys.stdout.flush()

    # Bulk create all the PostOffice instances at once
    PostOffice.objects.bulk_create(post_offices)

    print()  # To move the cursor to a new line after the progress bar

    
def import_police_stations():
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:100];
    area["name"="India"]->.searchArea;
    (
    node["amenity"="police"](area.searchArea);
    way["amenity"="police"](area.searchArea);
    relation["amenity"="police"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        response.raise_for_status()

        data = response.json()
        police_stations = []

        for element in data.get('elements', []):
            if element.get("tags"):
                # Ensure essential fields are available
                name = element['tags'].get('name') or element['tags'].get('name:en')
                latitude = element.get('lat')
                longitude = element.get('lon')

                if not (name and latitude and longitude):
                    continue
                
                # Avoid duplicates
                if PoliceStation.objects.filter(
                    Q(latitude=latitude) & Q(longitude=longitude)
                ).exists():
                    continue

                # Create a new object
                police_stations.append(PoliceStation(
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    
                    name_gujarati = element['tags'].get('name:gu', None),
                    name_goan_konkani = element['tags'].get('name_goan_konkani', None),
                    name_santali = element['tags'].get('name:sat', None),
                    name_hindi = element['tags'].get('name:hi', None),
                    name_malayalam = element['tags'].get('name:ml', None),
                    name_punjabi = element['tags'].get('name:pa', None),
                    name_telugu = element['tags'].get('name:te', None),
                    name_kannada = element['tags'].get('name:kn', None),
                    name_bengali = element['tags'].get('name:bn', None),
                    name_marathi = element['tags'].get('name:mr', None),
                    name_tamil = element['tags'].get('name:ta', None),
                    name_odiya = element['tags'].get('name:or', None),
                    name_assamese = element['tags'].get('name:as', None),
                    name_kashmiri = element['tags'].get('name:ks', None),
                    name_urdu = element['tags'].get('name:ur', None),
                    name_maithili = element['tags'].get('name:mai', None),
                    name_sanskrit = element['tags'].get('name:sa', None),

                    pincode = element['tags'].get('postcode', None) or element['tags'].get('addr:postcode', None),
                    
                    street = element['tags'].get('addr:street', None),
                    city = element['tags'].get('addr:city', None),
                    district = element['tags'].get('addr:district', None),
                    state = element['tags'].get('addr:state', None),              

                    phone = element['tags'].get('phone', None),
                    website = element['tags'].get('website', None),
                ))

        # Bulk create objects
        PoliceStation.objects.bulk_create(police_stations)

        logger.info(f"Successfully imported {len(police_stations)} police stations into the database.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Overpass API: {e}")
    except ValueError:
        logger.error("Invalid JSON response received from Overpass API.")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")



def row_generator(csv_data):
    for index, row in csv_data.iterrows():
        yield index, row

def import_banks():
    GREEN = "\033[92m"
    RESET = "\033[0m"

    file = r"D:\Projects\BZ India\bzindia\static\w3\document\bank\bank.csv"
    csv_data = pandas.read_csv(file)

    banks = []  # List to hold Bank objects
    length = len(csv_data)

    for index, row in row_generator(csv_data):
        bank = Bank(
            name = row["BANK"],
            ifsc = row["IFSC"],
            branch = row["BRANCH"],
            center = row["CENTRE"],
            city = row["CITY"],
            district = row["DISTRICT"],
            state = row["STATE"],
            address = row["ADDRESS"],
            contact = row["CONTACT"],
            iso3166 = row["ISO3166"],
            micr = row["MICR"],
            swift = row["SWIFT"] if row["SWIFT"] and row["SWIFT"] != "nan" else None,
            imps = True if row["IMPS"] == "True" else False,
            rtgs = True if row["RTGS"] == "True" else False,
            neft = True if row["NEFT"] == "True" else False,
            upi = True if row["UPI"] == "True" else False
        )
        banks.append(bank)

        # Progress bar
        sys.stdout.write(
            f"{GREEN}\rProcessed {index + 1}/{length} rows - Completed {int((index + 1) / length * 100)}%{RESET}"
        )
        sys.stdout.flush()

    # Bulk creation
    Bank.objects.bulk_create(banks, ignore_conflicts=True)
    print("\nImport complete!")


def import_courts():
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
        [out:json][timeout:100];
        area["name"="India"]->.searchArea;
        (
        node["amenity"="courthouse"](area.searchArea);
        way["amenity"="courthouse"](area.searchArea);
        relation["amenity"="courthouse"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
    """
    try:
        # Send the request to Overpass API
        response = requests.post(overpass_url, data={'data': overpass_query})
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        print(data)

        tags = []
        lis = set()
                                                            
        # # Iterate over the elements in the response
        for element in data.get('elements', []):
            if element.get("tags"):
                print("/n",element.get("tags"))
        #         # alt_name = f"Name: {element['tags'].get('name_ja', '')}"
        #         field = element['tags'].get('postcode', None)
        #         if field:
        #             name = element['tags'].get('name', None)
        # #             print(name)
        #             lis.add(field)

        # print(lis)
                # for tag in element['tags']:
                #     if f"{tag}" not in tags:
                #         tags.append(tag)

        # print([tag for tag in tags if str(tag).startswith("name")])

        # for tag in tags:
            # print(tag)

                # print(f"Coordinates: {element['lat']}, {element['lon']}")
                # print(f"Historic: {element['tags'].get('historic', 'No historic info')}")
                # print(f"Natural: {element['tags'].get('natural', 'No natural info')}")
                # print(f"Operator: {element['tags'].get('operator', 'No operator info')}")
                # print(f"Access: {element['tags'].get('access', 'No access info')}")
                # print(f"Protected: {element['tags'].get('protected', 'No protected info')}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Overpass API: {e}")
    except ValueError:
        print("Invalid JSON response received from Overpass API.")
            

def import_attractions():
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:100];
    area["name"="India"]->.searchArea;
    (
      node["tourism"="attraction"](area.searchArea);
      way["tourism"="attraction"](area.searchArea);
      relation["tourism"="attraction"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        response.raise_for_status()

        data = response.json()
        attractions = []

        for element in data.get('elements', []):
            if element.get("tags"):
                # Ensure essential fields are available
                name = element['tags'].get('name') or element['tags'].get('name:en')
                alternative_name = element['tags'].get('alt_name')
                latitude = element.get('lat')
                longitude = element.get('lon')

                if not (name or alternative_name) and not (latitude and longitude):
                    continue
                
                # Avoid duplicates
                if TouristAttraction.objects.filter(
                    Q(latitude=latitude) & Q(longitude=longitude)
                ).exists():
                    continue

                # Create a new object
                attractions.append(TouristAttraction(
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    
                    old_name = element['tags'].get('old_name', None),

                    alternative_name = element['tags'].get('alt_name', None),

                    alternative_name_hindi = element['tags'].get('alt_name:hi', None),
                    alternative_name_bengali = element['tags'].get('alt_name:bn', None),
                    alternative_name_marathi = element['tags'].get('alt_name:mr', None),
                    alternative_name_kannada = element['tags'].get('alt_name:kn', None),
                    alternative_name_maithili = element['tags'].get('alt_name:mai', None),
                    alternative_name_malayalam = element['tags'].get('alt_name:ml', None),
                    alternative_name_tamil = element['tags'].get('alt_name:ta', None),
                    
                    name_gujarati = element['tags'].get('name:gu', None),
                    name_goan_konkani = element['tags'].get('name_goan_konkani', None),
                    name_santali = element['tags'].get('name:sat', None),
                    name_hindi = element['tags'].get('name:hi', None),
                    name_malayalam = element['tags'].get('name:ml', None),
                    name_punjabi = element['tags'].get('name:pa', None),
                    name_telugu = element['tags'].get('name:te', None),
                    name_kannada = element['tags'].get('name:kn', None),
                    name_bengali = element['tags'].get('name:bn', None),
                    name_marathi = element['tags'].get('name:mr', None),
                    name_tamil = element['tags'].get('name:ta', None),
                    name_odiya = element['tags'].get('name:or', None),
                    name_assamese = element['tags'].get('name:as', None),
                    name_kashmiri = element['tags'].get('name:ks', None),
                    name_urdu = element['tags'].get('name:ur', None),
                    name_maithili = element['tags'].get('name:mai', None),
                    name_sanskrit = element['tags'].get('name:sa', None),

                    historic_type = element['tags'].get('historic', None),

                    wheelchair_accessible = element['tags'].get('wheelchair', None),

                    sport_type = element['tags'].get('sport', None),

                    leisure_activity = element['tags'].get('leisure', None),

                    denomination = element['tags'].get('denomination', None),
                    religion = element['tags'].get('religion', None),

                    house_number = element['tags'].get('house_number', None),
                    pincode = element['tags'].get('postcode', None) or element['tags'].get('addr:postcode', None),
                    
                    street = element['tags'].get('addr:street', None),
                    place = element['tags'].get('addr:place', None),
                    city = element['tags'].get('addr:city', None),
                    district = element['tags'].get('addr:district', None),
                    state = element['tags'].get('addr:state', None),
                    place_type = element['tags'].get('place', None),
                    building_type = element['tags'].get('amenity', None),
                    building_category = element['tags'].get('building', None),
                    elevation = element['tags'].get('ele', None),
                    geography_type = element['tags'].get('natural', None),
                    man_made_contribution = element['tags'].get('man_made', None),
                    memmorial_type = element['tags'].get('memorial', None),

                    building_height = element['tags'].get('height', None),

                    waterway_type = element['tags'].get('waterway', None),
                    waterbody_type = element['tags'].get('water', None),
                    castle_type = element['tags'].get('castle', None),
                    attraction = element['tags'].get('attraction', None),

                    operated_by = element['tags'].get('operated_by', None),
                    opening_hours = element['tags'].get('opening_hours', None),
                    access_type = element['tags'].get('access', None),

                    started_date = element['tags'].get('start_date', None),

                    shops_available = element['tags'].get('shop', None),

                    description = element['tags'].get('description', None),
                    note = element['tags'].get('note', None),

                    phone = element['tags'].get('phone', None),
                    email = element['tags'].get('email', None),

                    website = element['tags'].get('website', None),
                ))

        # Bulk create objects
        TouristAttraction.objects.bulk_create(attractions)

        logger.info(f"Successfully imported {len(attractions)} attractions into the database.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Overpass API: {e}")
    except ValueError:
        logger.error("Invalid JSON response received from Overpass API.")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")


def import_courts_data():
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json][timeout:100];
    area["name"="India"]->.searchArea;
    (
    node["amenity"="courthouse"](area.searchArea);
    way["amenity"="courthouse"](area.searchArea);
    relation["amenity"="courthouse"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        response.raise_for_status()

        data = response.json()
        courts = []

        for element in data.get('elements', []):
            if element.get("tags"):
                # Ensure essential fields are available
                name = element['tags'].get('name') or element['tags'].get('name:en')
                latitude = element.get('lat')
                longitude = element.get('lon')

                if not (name and latitude and longitude):
                    continue
                
                # Avoid duplicates
                if Court.objects.filter(
                    Q(latitude=latitude) & Q(longitude=longitude)
                ).exists():
                    continue

                # Create a new object
                courts.append(Court(
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    
                    old_name = element['tags'].get('old_name', None),
                    designation = element['tags'].get('designation', None),                    
                    
                    name_gujarati = element['tags'].get('name:gu', None),
                    name_goan_konkani = element['tags'].get('name_goan_konkani', None),
                    name_santali = element['tags'].get('name:sat', None),
                    name_hindi = element['tags'].get('name:hi', None),
                    name_malayalam = element['tags'].get('name:ml', None),
                    name_punjabi = element['tags'].get('name:pa', None),
                    name_telugu = element['tags'].get('name:te', None),
                    name_kannada = element['tags'].get('name:kn', None),
                    name_bengali = element['tags'].get('name:bn', None),
                    name_marathi = element['tags'].get('name:mr', None),
                    name_tamil = element['tags'].get('name:ta', None),
                    name_odiya = element['tags'].get('name:or', None),
                    name_assamese = element['tags'].get('name:as', None),
                    name_kashmiri = element['tags'].get('name:ks', None),
                    name_urdu = element['tags'].get('name:ur', None),
                    name_maithili = element['tags'].get('name:mai', None),
                    name_sanskrit = element['tags'].get('name:sa', None),

                    pincode = element['tags'].get('postcode', None) or element['tags'].get('addr:postcode', None),
                    
                    street = element['tags'].get('addr:street', None),
                    city = element['tags'].get('addr:city', None),
                    district = element['tags'].get('addr:district', None),
                    state = element['tags'].get('addr:state', None),              

                    opening_hours = element['tags'].get('opening_hours', None),

                    phone = element['tags'].get('phone', None),
                    website = element['tags'].get('website', None),
                ))

        # Bulk create objects
        Court.objects.bulk_create(courts)

        logger.info(f"Successfully imported {len(courts)} courts into the database.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Overpass API: {e}")
    except ValueError:
        logger.error("Invalid JSON response received from Overpass API.")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")