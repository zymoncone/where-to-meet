"""
All required fetch requests to any required APIs will be made in this file.
"""
import os
from dotenv import load_dotenv
import requests
import streamlit as st
from typing import Optional, Tuple
from status_codes import SUCCESS, UNAUTHORIZED

load_dotenv()

def parse_flight_offers(data: dict) -> list:
    """
    """
    flight_offers = []
    for offer in data.get('data', []):
        price = float(offer['price']['total'])
        flight_path = {'to': [], 'return': []}
        for i, itinerary in enumerate(offer['itineraries']):
            one_way_path = []
            for segment in itinerary['segments']:
                if segment['departure']['iataCode'] not in one_way_path:
                    one_way_path.append(segment['departure']['iataCode'])
                if segment['arrival']['iataCode'] not in one_way_path:
                    one_way_path.append(segment['arrival']['iataCode'])
            if i == 0:
                flight_path['to'] = one_way_path
            else:
                flight_path['return'] = one_way_path

        flight_offers.append({'price': price, 'flight_paths': flight_path})
    return flight_offers

class AmadeusAPI:
    def __init__(self):
        self.__client_id = None
        self.__client_secret = None
        self.__access_token = None

    def __str__(self):
        return f"AmadeusAPI(client_id={self.client_id}, client_secret={self.client_secret})"

    @property
    def client_id(self):
        if self.__client_id is None:
            self.__client_id = os.getenv("AMADEUS_CLIENT_ID")
        return self.__client_id

    @property
    def client_secret(self):
        if self.__client_secret is None:
            self.__client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
        return self.__client_secret

    @property
    def access_token(self):
        if self.__access_token is None:
            self.get_access_token()
        return self.__access_token

    def get_access_token(self) -> None:
        if self.__access_token is None:
            print("Getting access token...")
            url = "https://test.api.amadeus.com/v1/security/oauth2/token"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            response = requests.post(url, headers=headers, data=data)
            self.__access_token = response.json().get('access_token')

    def get_flight_offers(self,
                          originLocationCode: str,
                          destinationLocationCode: str,
                          departureDate: str,
                          returnDate: str) -> list:
        """
        Get flight offers from the Amadeus API.

        param: originLocationCode (str): The IATA code of the origin airport.
        param: destinationLocationCode (str): The IATA code of the destination airport.
        param: departureDate (str): The departure date in the format 'YYYY-MM-DD'.
        param: returnDate (str): The return date in the format 'YYYY-MM-DD'.

        return: list: A list of flight offers.

        """
        print(f"Getting flight offers departing {departureDate}")
        print(f"   ...and returning {returnDate}")

        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        params = {
            'originLocationCode': originLocationCode,
            'destinationLocationCode': destinationLocationCode,
            'departureDate': departureDate,
            'returnDate': returnDate,
            'adults': 1,
            'currencyCode': 'USD',
            'max': 1
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == SUCCESS:
            return parse_flight_offers(response.json())

        elif response.status_code == UNAUTHORIZED:
            print("Refreshing access token...")
            self.get_access_token()  # Refresh the access token
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == SUCCESS:
                return parse_flight_offers(response.json())
            else:
                print(f"Failed to get flight offers after refreshing token: {response.status_code}")
                return []
        else:
            print(f"Failed to get flight offers: {response.status_code}")
            return []

    def get_airport_coordinates(self, airport_code: str) -> Optional[Tuple[float, float]]:
        print(f"Getting coordinates for {airport_code}")
        url = f"https://test.api.amadeus.com/v1/reference-data/locations?subType=AIRPORT&keyword={airport_code}&countryCode=US"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(url, headers=headers)

        if response.status_code == SUCCESS:
            data = response.json()
            if data.get('data'):
                location = data['data'][0]['geoCode']
                return (location['latitude'], location['longitude'])
            else:
                return None
        elif response.status_code == UNAUTHORIZED:
            print("Refreshing access token...")
            self.get_access_token()  # Refresh the access token
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.get(url, headers=headers)

            if response.status_code == SUCCESS:
                data = response.json()
                if data.get('data'):
                    location = data['data'][0]['geoCode']
                    return (location['latitude'], location['longitude'])
                else:
                    return None
            else:
                print(f"Failed to get airport coordinates after refreshing token: {response.status_code}")
                return None
        else:
            print(f"Failed to get airport coordinates: {response.status_code}")
            return None

    def get_nearest_airport(self, latitude: float, longitude: float) -> Optional[str]:
        print(f"Getting closest airport to {latitude}, {longitude}")
        url = f"https://test.api.amadeus.com/v1/reference-data/locations/airports?latitude={latitude}&longitude={longitude}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(url, headers=headers)

        if response.status_code == SUCCESS:
            data = response.json()
            if data.get('data'):
                return data['data'][0]['iataCode']
            else:
                return None
        elif response.status_code == UNAUTHORIZED:
            print("Refreshing access token...")
            self.get_access_token()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.get(url, headers=headers)

            if response.status_code == SUCCESS:
                data = response.json()
                if data.get('data'):
                    return data['data'][0]['iataCode']
                else:
                    return None

def get_auth_key():
    try:
        # Get the API key from Streamlit secrets when deployed
        return st.secrets["AMADEUS_AUTH_KEY"]
    except FileNotFoundError:
        # Load the API key from .env file for local development
        load_dotenv()
        return os.getenv("AMADEUS_AUTH_KEY")

if __name__ == "__main__":
    auth = AmadeusAPI()
    print(auth)
