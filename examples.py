import requests

# Base URL - adjust if your server runs on a different port
BASE_URL = "http://localhost:8000"

def test_flight_search():
    """Example of searching for flights"""
    endpoint = f"{BASE_URL}/api/flights/search"
    
    # Search parameters
    params = {
        "departure_airport": "SYD",
        "arrival_airport": "MEL",
        "departure_date": "2024-04-01",
        "max_results": 5
    }
    
    response = requests.post(endpoint, params=params)
    print("\nFlight Search Response:")
    print(response.json())

def test_airport_code():
    """Example of getting airport code"""
    endpoint = f"{BASE_URL}/api/airport/code"
    
    # Search parameters
    params = {
        "city_name": "Sydney"
    }
    
    response = requests.post(endpoint, params=params)
    print("\nAirport Code Response:")
    print(response.json())

if __name__ == "__main__":
    test_flight_search()
    test_airport_code() 