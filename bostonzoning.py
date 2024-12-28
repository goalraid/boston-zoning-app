import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

@dataclass
class ZoningInfo:
    """Data class to store zoning information for a specific location"""
    district: str
    allowed_uses: List[str]
    height_limit: float
    density_requirements: Dict[str, str]
    special_overlays: List[str]
    recent_changes: List[str]

class BostonZoningApp:
    def __init__(self):
        load_dotenv()
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.geocoder = Nominatim(user_agent="boston_zoning_app")
        
    def get_coordinates(self, address: str) -> Optional[tuple]:
        """Convert address to coordinates"""
        try:
            location = self.geocoder.geocode(f"{address}, Boston, MA")
            if location:
                return (location.latitude, location.longitude)
            return None
        except GeocoderTimedOut:
            print("Error: Geocoding service timed out")
            return None

    def get_zoning_info(self, address: str) -> Optional[ZoningInfo]:
        """Retrieve zoning information for a given address using Perplexity AI API"""
        coordinates = self.get_coordinates(address)
        if not coordinates:
            print(f"Could not find coordinates for address: {address}")
            return None

        # Check if API key exists
        if not self.perplexity_api_key:
            print("Error: Perplexity API key not found. Please check your .env file.")
            return None

        print(f"Found coordinates: {coordinates}")  # Debug line
        
        # Construct API query
        query = f"What are the zoning regulations for {address}, Boston, MA?"
        
        try:
            # Make API request to Perplexity
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json={
                    "model": "llama-3.1-sonar-huge-128k-online",
                    "messages": [{"role": "user", "content": query}]
                }
            )

            if response.status_code != 200:
                print(f"API Error: Status code {response.status_code}")
                print(f"Response: {response.text}")
                return None

            # Debug response
            print(f"API Response: {response.json()}")
            
            # Process response here...
            
        except Exception as e:
            print(f"Error making API request: {str(e)}")
            return None

    def display_zoning_info(self, zoning_info: ZoningInfo):
        """Display zoning information in a user-friendly format"""
        print("\n=== Zoning Information ===")
        print(f"District: {zoning_info.district}")
        print("\nAllowed Uses:")
        for use in zoning_info.allowed_uses:
            print(f"- {use}")
        print(f"\nHeight Limit: {zoning_info.height_limit} feet")
        print("\nDensity Requirements:")
        for key, value in zoning_info.density_requirements.items():
            print(f"- {key}: {value}")
        print("\nSpecial Overlays:")
        for overlay in zoning_info.special_overlays:
            print(f"- {overlay}")
        print("\nRecent Changes:")
        for change in zoning_info.recent_changes:
            print(f"- {change}")

    def get_zoning_info_raw(self, address: str) -> Optional[str]:
        """Get raw zoning information from Perplexity API"""
        if not self.perplexity_api_key:
            return "Error: Perplexity API key not found. Please check your .env file."

        query = f"""Provide detailed zoning information for {address}, Boston, MA. Include:
        1. Zoning district
        2. Allowed uses
        3. Height limits
        4. Density requirements
        5. Special overlays
        6. Recent zoning changes or reforms
        Format the response in clear sections."""

        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json={
                    "model": "llama-3.1-sonar-huge-128k-online",
                    "messages": [{"role": "user", "content": query}]
                }
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"API Error: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Error making API request: {str(e)}"

def main():
    app = BostonZoningApp()
    
    while True:
        address = input("\nEnter a Boston address (or 'quit' to exit): ")
        if address.lower() == 'quit':
            break
            
        zoning_info = app.get_zoning_info(address)
        if zoning_info:
            app.display_zoning_info(zoning_info)
        else:
            print("Unable to retrieve zoning information for the provided address.")

if __name__ == "__main__":
    main()
