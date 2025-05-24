
import requests
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from shared.constants import (
    DEFAULT_STREET_IMAGE_LIMIT,
    STREET_IMAGE_QUALITY_THRESHOLD,
    PREFERRED_CAMERA_MAKES,
    SEARCH_RADIUS_KM,
    SEARCH_YEARS_BACK,
    FETCH_MULTIPLIER,
    TRAFFIC_SIGN_RADIUS_KM,
    TRAFFIC_SIGN_TYPES,
    MAX_TOP_CANDIDATES,
    EDUCATION_WEIGHT,
    QUALITY_WEIGHT,
    RECENCY_WEIGHT,
    RECENT_THRESHOLD_DAYS,
    MEDIUM_RECENT_DAYS,
    OLD_THRESHOLD_DAYS,
    RECENT_SCORE,
    MEDIUM_RECENT_SCORE,
    OLD_SCORE,
    VERY_OLD_SCORE,
    IMAGE_SIZE
)


class StreetImageController:

    def __init__(self, api_token: str):
        self._api_token = api_token

    def get_street_image_url(self, city="Paris", limit: int=DEFAULT_STREET_IMAGE_LIMIT, quality_threshold: str=STREET_IMAGE_QUALITY_THRESHOLD) -> Optional[str]:

        # 1. Get city coordinates
        coords = self._get_city_coordinates(city)
        if not coords:
            return None

        # 2. Fetch available images with enhanced filtering
        images = self._get_educational_images(coords, limit, quality_threshold)
        if not images:
            return None

        # 3. Select the best image and return URL
        selected = self._select_best_educational_image(images)
        image_url = self._get_image_url(selected)
        
        return image_url


    def _get_city_coordinates(self, city: str) -> Optional[Dict[str, float]]:
        """Gets city coordinates via Nominatim geocoding service."""
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": city, "format": "json", "limit": 1},
                headers={"User-Agent": "roadbuddy/1.0"},
                timeout=5
            )
            
            data = response.json()
            if not data:
                return None
            
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            
            return {"lat": lat, "lon": lon}
            
        except:
            return None


    def _get_educational_images(self, coords: Dict[str, float], limit: int, quality_threshold: float) -> Optional[List]:
        try:
            # Create search area around the point (configurable radius)
            margin = SEARCH_RADIUS_KM / 111.0  # Convert km to degrees (approximate)
            bbox = f"{coords['lon']-margin},{coords['lat']-margin},{coords['lon']+margin},{coords['lat']+margin}"
            
            # Calculate date filter for recent images (configurable years back)
            years_ago = datetime.now() - timedelta(days=SEARCH_YEARS_BACK * 365)
            start_date = years_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Request more images for better selection (configurable multiplier)
            fetch_limit = limit * FETCH_MULTIPLIER
            
            response = requests.get(
                "https://graph.mapillary.com/images",
                params={
                    "access_token": self._api_token,
                    "bbox": bbox,
                    "limit": fetch_limit,
                    "start_captured_at": start_date,
                    "fields": "id,thumb_2048_url,compass_angle,make,model,captured_at"
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            all_images = response.json().get("data", [])
            
            # Filter for quality cameras (configurable camera list)
            quality_images = self._filter_quality_cameras(all_images)
            
            # Look for images with traffic signs and infrastructure
            educational_images = self._get_images_with_detections(quality_images, coords)
            
            if not educational_images:
                return quality_images[:limit] if quality_images else all_images[:limit]
            
            return educational_images[:limit]
        
        except:
            return None


    def _filter_quality_cameras(self, images):
        """Filter images from higher quality cameras for better educational content."""
        quality_images = []
        other_images = []
        
        for img in images:
            make = img.get('make', '').strip()
            if any(preferred in make for preferred in PREFERRED_CAMERA_MAKES):
                img['quality_score'] = 1.0
                quality_images.append(img)
            else:
                img['quality_score'] = 0.5
                other_images.append(img)
        
        # Return quality images first, then others
        return quality_images + other_images


    def _get_images_with_detections(self, images, coords):
        """Query for images that likely contain traffic signs and educational content."""
        try:
            # Create a smaller search area for traffic sign detection (configurable)
            margin = TRAFFIC_SIGN_RADIUS_KM / 111.0  # Convert km to degrees
            bbox = f"{coords['lon']-margin},{coords['lat']-margin},{coords['lon']+margin},{coords['lat']+margin}"
            
            # Query for map features (configurable traffic sign types)
            traffic_signs_query = ",".join(TRAFFIC_SIGN_TYPES)
            
            response = requests.get(
                "https://graph.mapillary.com/map_features",
                params={
                    "access_token": self._api_token,
                    "bbox": bbox,
                    "limit": 500,  # Reduced for speed
                    "object_values": traffic_signs_query,
                    "fields": "id,object_value,images"
                },
                timeout=8
            )
            
            if response.status_code == 200:
                features = response.json().get("data", [])
                
                # Collect image IDs that have traffic signs
                educational_image_ids = set()
                for feature in features:
                    image_ids = feature.get('images', [])
                    educational_image_ids.update(image_ids)
                
                # Filter our images to those with traffic signs
                educational_images = []
                for img in images:
                    if img['id'] in educational_image_ids:
                        img['educational_score'] = 1.0
                        educational_images.append(img)
                    else:
                        img['educational_score'] = 0.3
                
                return educational_images
        
        except:
            pass
        
        # If traffic sign detection fails, return all images with basic scoring
        for img in images:
            img['educational_score'] = 0.5
        return images


    def _select_best_educational_image(self, images):
        """Select the best image based on educational value and quality (configurable weights)."""
        if not images:
            return None
        
        # Sort by educational score, then quality score (configurable weights)
        
        sorted_images = sorted(images, key=self._score_image, reverse=True)
        
        # Add some randomness among top candidates (configurable number)
        top_candidates = sorted_images[:min(MAX_TOP_CANDIDATES, len(sorted_images))]
        selected = random.choice(top_candidates)
        
        return selected
    
    def _score_image(self, img):
        educational_score = img.get('educational_score', 0)
        quality_score = img.get('quality_score', 0.5)
        recency_score = self._calculate_recency_score(img.get('captured_at', 0))
        
        # Weighted combined score (configurable weights)
        return (educational_score * EDUCATION_WEIGHT) + \
            (quality_score * QUALITY_WEIGHT) + \
            (recency_score * RECENCY_WEIGHT)


    def _calculate_recency_score(self, captured_at):
        """Calculate a score based on how recent the image is (configurable thresholds)."""
        if not captured_at:
            return 0
        
        try:
            # captured_at is in milliseconds since epoch
            capture_date = datetime.fromtimestamp(captured_at / 1000)
            now = datetime.now()
            days_ago = (now - capture_date).days
            
            # More recent images get higher scores (configurable thresholds)
            if days_ago < RECENT_THRESHOLD_DAYS:
                return RECENT_SCORE
            elif days_ago < MEDIUM_RECENT_DAYS:
                return MEDIUM_RECENT_SCORE
            elif days_ago < OLD_THRESHOLD_DAYS:
                return OLD_SCORE
            else:
                return VERY_OLD_SCORE
        except:
            return 0.5


    def _get_image_url(self, image_data):
        """Returns the direct image URL (no download needed)."""
        try:
            # Return the direct URL based on configured size
            image_url = image_data[IMAGE_SIZE]
            return image_url
            
        except:
            return None


if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(), override=True)
    import os

    api_token = os.getenv("MAPILLARY_TOKEN")


    controller = StreetImageController(api_token=api_token)
    result = controller.get_street_image_url("Paris", limit=10)
    
    if result:
        print(result)
    else:
        exit(1) 
    

    
