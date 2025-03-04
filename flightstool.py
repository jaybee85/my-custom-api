from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from serpapi import GoogleSearch
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Flights Search API",
    description="API to search flights and get airport codes using SerpApi",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment variable
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

@dataclass
class FlightPrice:
    amount: float
    currency: str = "AUD"

@dataclass
class Flight:
    airline: str
    departure_time: datetime
    arrival_time: datetime
    departure_airport: str
    arrival_airport: str
    price: FlightPrice
    duration: str
    stops: int

@dataclass
class FlightResults:
    flights: List[Flight]
    search_metadata: Dict

@app.post("/api/flights/search")
async def search_flights(
    departure_airport: str,
    arrival_airport: str,
    departure_date: str,
    max_results: int = 5
) -> FlightResults:
    """
    Search for flights using provided parameters
    """
    if not SERPAPI_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        return get_best_flights(
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            departure_date=departure_date,
            api_key=SERPAPI_KEY,
            max_results=max_results
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/airport/code")
async def get_airport_code_endpoint(city_name: str) -> Dict[str, Optional[str]]:
    """
    Get airport code for a given city
    """
    if not SERPAPI_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        code = get_airport_code(city_name, SERPAPI_KEY)
        return {"city": city_name, "airport_code": code}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_best_flights(
    departure_airport: str,
    arrival_airport: str,
    departure_date: str,
    api_key: str,
    max_results: int = 5
) -> FlightResults:
    """
    Search for the best available flights using Google Flights via SerpApi.
    
    Args:
        departure_airport: Origin airport code (e.g., 'JFK')
        arrival_airport: Destination airport code (e.g., 'LAX')
        departure_date: Date in YYYY-MM-DD format
        api_key: Your SerpApi API key
        max_results: Maximum number of flights to return
    
    Returns:
        FlightResults object containing list of flights and search metadata
    """
    params = {
        "engine": "google_flights",
        "departure_id": departure_airport,
        "arrival_id": arrival_airport,
        "outbound_date": departure_date,
        "api_key": api_key,
        "hl": "en"
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    flights_data = []
    
    if "flights" in results:
        for flight in results["flights"][:max_results]:
            price_info = flight.get("price", {})
            flights_data.append(
                Flight(
                    airline=flight.get("airline", ""),
                    departure_time=datetime.fromisoformat(flight.get("departure_time", "")),
                    arrival_time=datetime.fromisoformat(flight.get("arrival_time", "")),
                    departure_airport=departure_airport,
                    arrival_airport=arrival_airport,
                    price=FlightPrice(
                        amount=float(price_info.get("value", 0)),
                        currency=price_info.get("currency", "USD")
                    ),
                    duration=flight.get("duration", ""),
                    stops=flight.get("stops", 0)
                )
            )
    
    return FlightResults(
        flights=flights_data,
        search_metadata=results.get("search_metadata", {})
    )

def get_airport_code(city_name: str, api_key: str) -> Optional[str]:
    """
    Get the three letter airport code for a given city using Google Places via SerpApi.
    
    Args:
        city_name: Name of the city (e.g., 'New York', 'Los Angeles')
        api_key: Your SerpApi API key
    
    Returns:
        str: Three letter airport code if found, None otherwise
    """
    params = {
        "engine": "google",
        "q": f"{city_name} airport code",
        "api_key": api_key,
        "num": 1
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    # Try to find airport code in the featured snippet or knowledge graph
    if "answer_box" in results:
        answer = results["answer_box"].get("snippet", "")
    elif "knowledge_graph" in results:
        answer = results["knowledge_graph"].get("description", "")
    else:
        return None
    
    # Look for a three-letter code in uppercase
    import re
    match = re.search(r'\b[A-Z]{3}\b', answer)
    if match:
        return match.group(0)
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 