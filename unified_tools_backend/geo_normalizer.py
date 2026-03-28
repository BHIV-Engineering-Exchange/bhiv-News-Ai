"""
Geographic Normalization Layer
Normalizes location text to standardized geographic data.
Returns null if unresolvable. No hallucinations. Deterministic.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


# Known geographic mappings - extensible database
COUNTRY_CODES = {
    "india": "IN",
    "united states": "US",
    "usa": "US",
    "us": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "china": "CN",
    "japan": "JP",
    "germany": "DE",
    "france": "FR",
    "australia": "AU",
    "canada": "CA",
    "brazil": "BR",
    "indonesia": "ID",
    "mexico": "MX",
    "russia": "RU",
    "south korea": "KR",
    "korea": "KR",
    "south africa": "ZA",
    "argentina": "AR",
    "spain": "ES",
    "italy": "IT",
}

INDIA_REGIONS = {
    "andhra pradesh": "AP",
    "arunachal pradesh": "AR",
    "assam": "AS",
    "bihar": "BR",
    "chhattisgarh": "CG",
    "delhi": "DL",
    "goa": "GA",
    "gujarat": "GJ",
    "haryana": "HR",
    "himachal pradesh": "HP",
    "jharkhand": "JH",
    "karnataka": "KA",
    "kerala": "KL",
    "madhya pradesh": "MP",
    "maharashtra": "MH",
    "manipur": "MN",
    "meghalaya": "ML",
    "mizoram": "MZ",
    "nagaland": "NL",
    "odisha": "OR",
    "punjab": "PB",
    "rajasthan": "RJ",
    "sikkim": "SK",
    "tamil nadu": "TN",
    "telangana": "TG",
    "tripura": "TR",
    "uttar pradesh": "UP",
    "uttarakhand": "UK",
    "west bengal": "WB",
}

COUNTRY_COORDINATES = {
    "IN": {"lat": 20.5937, "lon": 78.9629},
    "US": {"lat": 37.0902, "lon": -95.7129},
    "CN": {"lat": 35.8617, "lon": 104.1954},
    "JP": {"lat": 36.2048, "lon": 138.2529},
    "GB": {"lat": 55.3781, "lon": -3.4360},
    "FR": {"lat": 46.2276, "lon": 2.2137},
    "DE": {"lat": 51.1657, "lon": 10.4515},
    "AU": {"lat": -25.2744, "lon": 133.7751},
    "CA": {"lat": 56.1304, "lon": -106.3468},
}


@dataclass
class GeoNormalized:
    """Normalized geographic data."""
    country_code: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: Optional[float] = None


class GeoNormalizer:
    """
    Normalizes location text to standardized geographic data.
    
    Properties:
    - Deterministic mapping
    - Returns null if unresolvable
    - No hallucinations or guesses
    - Confidence scoring
    """
    
    @staticmethod
    def normalize_location(location_text: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Normalize location text to structured geo data.
        
        Args:
            location_text: Text description of location
            
        Returns:
            Dictionary with geo_normalized data or None if unresolvable
        """
        if not location_text or not isinstance(location_text, str):
            return None
        
        location_lower = location_text.strip().lower()
        
        # Empty or too short
        if len(location_lower) < 2:
            return None
        
        # Try to resolve country
        country_code = None
        confidence = 0.0
        
        for country_key, code in COUNTRY_CODES.items():
            if country_key in location_lower:
                country_code = code
                confidence = 0.8  # Found country name
                break
        
        # Try to resolve region (for India)
        region = None
        if country_code == "IN":
            for region_key, code in INDIA_REGIONS.items():
                if region_key in location_lower:
                    region = region_key
                    confidence = 0.9  # Found specific region
                    break
        
        # If we couldn't resolve anything, return null
        if not country_code:
            return None
        
        # Get country center coordinates
        coords = COUNTRY_COORDINATES.get(country_code, {})
        
        geo_data = {
            "country_code": country_code,
            "region": region,
            "latitude": coords.get("lat"),
            "longitude": coords.get("lon"),
            "confidence": confidence
        }
        
        return geo_data
    
    @staticmethod
    def validate_geo_normalized(geo_obj: Optional[Dict[str, Any]]) -> bool:
        """
        Validate geo_normalized object structure.
        
        Args:
            geo_obj: Geo normalized object
            
        Returns:
            True if valid or null
        """
        if geo_obj is None:
            return True
        
        if not isinstance(geo_obj, dict):
            return False
        
        # Check required fields if not null
        if geo_obj.get("country_code"):
            if not isinstance(geo_obj["country_code"], str) or len(geo_obj["country_code"]) != 2:
                return False
        
        # Check optional fields if present
        if geo_obj.get("latitude") is not None:
            if not isinstance(geo_obj["latitude"], (int, float)):
                return False
            if not (-90 <= geo_obj["latitude"] <= 90):
                return False
        
        if geo_obj.get("longitude") is not None:
            if not isinstance(geo_obj["longitude"], (int, float)):
                return False
            if not (-180 <= geo_obj["longitude"] <= 180):
                return False
        
        if geo_obj.get("confidence") is not None:
            if not isinstance(geo_obj["confidence"], (int, float)):
                return False
            if not (0 <= geo_obj["confidence"] <= 1):
                return False
        
        return True


# Singleton instance
_normalizer = GeoNormalizer()


def normalize_location(location_text: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Normalize location text.
    Convenience function.
    
    Args:
        location_text: Location text
        
    Returns:
        Normalized geo data or None
    """
    return _normalizer.normalize_location(location_text)


def validate_geo_normalized(geo_obj: Optional[Dict[str, Any]]) -> bool:
    """
    Validate geo normalized object.
    Convenience function.
    
    Args:
        geo_obj: Geo object to validate
        
    Returns:
        True if valid
    """
    return _normalizer.validate_geo_normalized(geo_obj)


def test_geo_normalization():
    """Test geographic normalization."""
    print("Testing geographic normalization...")
    
    test_cases = [
        ("India", "IN", "Should resolve to India"),
        ("New Delhi, India", "IN", "Should resolve to India"),
        ("Maharashtra, India", "IN", "Should resolve to India with region"),
        ("United States", "US", "Should resolve to USA"),
        ("UK", "GB", "Should resolve to GB"),
        ("unknown location xyz", None, "Should return None for unknown"),
        ("", None, "Should return None for empty"),
        (None, None, "Should return None for None"),
    ]
    
    for location, expected_country, description in test_cases:
        result = normalize_location(location)
        country = result.get("country_code") if result else None
        passed = country == expected_country
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {description}")
        if result:
            print(f"       Country: {country}, Region: {result.get('region')}, Confidence: {result.get('confidence')}")
    
    # Test validation
    print("\nValidation tests:")
    valid_geo = {"country_code": "IN", "region": "MH", "latitude": 19.7515, "longitude": 75.7139, "confidence": 0.9}
    is_valid = validate_geo_normalized(valid_geo)
    print(f"Valid geo object: {'✓ PASS' if is_valid else '✗ FAIL'}")
    
    is_null_valid = validate_geo_normalized(None)
    print(f"None geo object: {'✓ PASS' if is_null_valid else '✗ FAIL'}")
    
    invalid_geo = {"country_code": "INVALID"}
    is_invalid = not validate_geo_normalized(invalid_geo)
    print(f"Invalid geo object: {'✓ PASS' if is_invalid else '✗ FAIL'}")


if __name__ == "__main__":
    test_geo_normalization()
