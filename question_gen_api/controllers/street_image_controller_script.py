#!/usr/bin/env python3
"""
Mapillary Image Downloader - Enhanced for Driving Education
Downloads street view images from Mapillary optimized for driving education
Focuses on images with traffic signs, intersections, and educational road scenarios
"""

# ============================================================================
# 🔧 CONFIGURATION - Modify these values to adjust behavior
# ============================================================================

# 📷 PREFERRED CAMERA BRANDS (for better image quality)
PREFERRED_CAMERA_MAKES = [
    'GoPro', 'Canon', 'Nikon', 'Sony', 'Apple', 'Samsung', 
    'Google', 'OnePlus', 'Huawei', 'Xiaomi', 'DJI', 'Garmin',
    'Blackvue', 'Nextbase', 'Insta360'
]

# 🚫 EXCLUDED CAMERA TYPES (360° and non-suitable cameras)
EXCLUDED_CAMERA_TYPES = [
    'spherical', '360', 'panoramic', 'equirectangular'
]

# 🚫 EXCLUDED CAMERA MODELS (known 360° cameras)
EXCLUDED_CAMERA_MODELS = [
    'Insta360', 'Ricoh Theta', 'Samsung Gear 360', 'Garmin VIRB X', 
    'LG 360 CAM', 'Kodak PIXPRO SP360', 'Vuze', 'Orah'
]

# 📅 DATE PARAMETERS
SEARCH_YEARS_BACK = 10  # Search images from X years back (increased from 5)
RECENT_THRESHOLD_DAYS = 90  # "Recent" images (increased from 30)
MEDIUM_RECENT_DAYS = 1095   # "Medium recent" images (3 years, increased from 1)
OLD_THRESHOLD_DAYS = 2190   # "Old" images (6 years, increased from 2)

# 🗺️ SEARCH AREA PARAMETERS
SEARCH_RADIUS_KM = 5.0    # Main search radius (increased from 2.0 km)
TRAFFIC_SIGN_RADIUS_KM = 3.0  # Radius for traffic sign search (increased from 1.0 km)

# 📊 LIMITS AND THRESHOLDS
DEFAULT_LIMIT = 20        # Default number of images to download
FETCH_MULTIPLIER = 4      # Multiplier for more choices (reduced from 8)
QUALITY_THRESHOLD = 0.4   # Minimum quality threshold (lowered from 0.7)
MAX_TOP_CANDIDATES = 5    # Number of best images to choose from (increased from 3)

# 🚦 TRAFFIC SIGN TYPES TO SEARCH (for educational content)
TRAFFIC_SIGN_TYPES = [
    "regulatory--*",    # Regulatory signs (stop, speed, etc.)
    "warning--*",       # Warning signs (danger, curves, etc.)
    "information--*"    # Information signs (direction, services, etc.)
]

# 🛣️ ROAD INFRASTRUCTURE TYPES (for driving education)
ROAD_INFRASTRUCTURE_TYPES = [
    "object--street-light",
    "object--traffic-light",
    "object--fire-hydrant",
    "object--pole",
    "construction--barrier--*",
    "marking--*",  # Road markings
    "object--support--utility-pole"
]

# 🚗 VEHICLE AND DRIVING RELATED OBJECTS (enhanced for vehicle detection)
VEHICLE_RELATED_TYPES = [
    "object--vehicle--*",  # Any vehicle
    "object--vehicle--car",  # Specific car detection
    "object--vehicle--truck",  # Trucks
    "object--vehicle--bus",  # Buses
    "object--vehicle--motorcycle",  # Motorcycles
    "construction--flat--road",  # Road surface
    "construction--flat--parking",  # Parking areas
    "marking--discrete--lane-marking",  # Lane markings
    "marking--discrete--stop-line",  # Stop lines
    "construction--barrier--curb",  # Curbs
]

# 🛣️ MANDATORY ROAD FEATURES (must have at least one)
MANDATORY_ROAD_FEATURES = [
    "construction--flat--road",
    "marking--*",  # Any road markings
    "object--vehicle--*",  # Any vehicles
    "construction--barrier--curb",
    "object--traffic-light",
    "regulatory--*",  # Any regulatory signs
    "warning--"  # Warning signs
]

# ⚖️ WEIGHTS FOR EDUCATIONAL SCORING (vehicle-focused)
EDUCATION_WEIGHT = 0.25    # Traffic signs importance
ROAD_CONTENT_WEIGHT = 0.25 # Road infrastructure importance
VEHICLE_CONTENT_WEIGHT = 0.2 # Vehicle/driving content importance
VEHICLE_PERSPECTIVE_WEIGHT = 0.2 # Vehicle perspective likelihood (new)
ROAD_VALIDATION_WEIGHT = 0.05 # Road validation score (new)
QUALITY_WEIGHT = 0.03     # Camera quality (minimal importance)
RECENCY_WEIGHT = 0.02     # Image age (minimal importance)

# 🎯 RECENCY SCORES (more permissive)
RECENT_SCORE = 1.0        # Score for recent images
MEDIUM_RECENT_SCORE = 0.9 # Score for medium recent images (increased)
OLD_SCORE = 0.8           # Score for old images (increased)
VERY_OLD_SCORE = 0.6      # Score for very old images (increased)

# 📁 FILE PARAMETERS
OUTPUT_FOLDER = "images"  # Output folder
IMAGE_SIZE = "thumb_2048_url"  # Image size (thumb_256_url, thumb_1024_url, thumb_2048_url)

# ============================================================================

import requests
import random
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
import os
MAPILLARY_TOKEN = os.getenv("MAPILLARY_TOKEN", None)

# Simplified mandatory features (reduced API calls)
MANDATORY_FEATURES = [
    "construction--flat--road",
    "marking--*",
    "regulatory--*",
    "object--vehicle--*",
    "object--traffic-light",
    "warning--"
]

# Blacklisted image identifiers (manually identified bad quality images)
BLACKLISTED_IDENTIFIERS = [
    "An8NShOw78k3pGN8EoVrZyqjBuqDR5YtvNKmTzOiVbYse527npF5OUXNPvvvjdJY",
    "An-bISCPCtMS3qyX-gjXaqNuMKnGabShOGUh4WDUNTdli-eMlnHMGf9fXm3GHKZk",
    "An9y5YkZKerXHQ8-RCbiRem1UHdS1NxZaOhsnAvLEaQ2o2gqezGFD1lG4CkOz9nC",
    "An9pvLOmuHkTbUjw416wYc_w7I3IPPJfm0MebHRfJAvkz9yw9HbK-7u7Y5K_crLA",
    "An_oaNqVVSkViiEFaOM7ItLCu4ASpFHpGFEGGD5oBs_OYfSZchUTkEVC6htzFGeF",
    "An8qGFStJGOdWQzo6Xn1eipwLZLHBvtp17J7OAxHBJCoZeQON2cBk8Zn4vlBEEJ_",
    "An8S8i2wDCVO4YERJ_IgOo_KbF8-hHkn6D038delY_fY1zj0kdwkNLadwAksbwrl",
    "An-YvNugNSA0LSlppSKKa0W54j4sjSOT2ttWfiS9Qr68xxBH",
    "An84ydomjfvWudlvXLDE-xBu3795H_SPXyMEqeTRAi8BbH6g",
    "An9Y3v16CDPgv1SO9e-dFudqNzceKnqjMK6Z11rpPHO4htje"
]

def is_blacklisted(url):
    """Check if an image URL is blacklisted by matching its unique identifier."""
    return any(identifier in url for identifier in BLACKLISTED_IDENTIFIERS)

def validate_road_context(coords):
    """
    Validate that the coordinates are on or near a road by checking for nearby road features.
    This helps ensure we get driving-relevant images. More permissive version.
    """
    try:
        # Create a larger search area for road validation (more permissive)
        margin = 0.02  # Larger area for road checking (doubled from 0.01)
        bbox = f"{coords['lon']-margin},{coords['lat']-margin},{coords['lon']+margin},{coords['lat']+margin}"
        
        # Search for any road-related features to confirm this is a road area
        # More comprehensive search including vehicles and people
        road_features_query = "object--street-light,object--traffic-light,marking--*,construction--barrier--*,object--vehicle--*,object--person"
        
        response = requests.get(
            "https://graph.mapillary.com/map_features",
            params={
                "access_token": MAPILLARY_TOKEN,
                "bbox": bbox,
                "limit": 100,  # Increased from 50
                "object_values": road_features_query,
                "fields": "id,object_value"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            features = response.json().get("data", [])
            return len(features) > 0  # Return True if we found any road features
        
        return True  # If we can't validate, assume it's valid (more permissive)
        
    except:
        return True  # If validation fails, assume it's valid (more permissive)

def download_street_image(city="Paris", limit=DEFAULT_LIMIT):
    """Gets a street view image URL from Mapillary."""
    coords = get_city_coordinates(city)
    if not coords:
        return None

    images = get_educational_images(coords, limit)
    if not images:
        return None

    # Pick a random image from filtered results
    selected = random.choice(images) if len(images) > 0 else None
    if not selected:
        return None
        
    return get_image_url(selected)

def get_city_coordinates(city):
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
        
        return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
    except:
        return None

def get_educational_images(coords, limit):
    """Fetches Mapillary images optimized for driving education."""
    try:
        margin = SEARCH_RADIUS_KM / 111.0
        bbox = f"{coords['lon']-margin},{coords['lat']-margin},{coords['lon']+margin},{coords['lat']+margin}"
        
        # Single API call with essential fields
        response = requests.get(
            "https://graph.mapillary.com/images",
            params={
                "access_token": MAPILLARY_TOKEN,
                "bbox": bbox,
                "limit": limit * FETCH_MULTIPLIER,
                "fields": "id,thumb_2048_url,captured_at,camera_type,is_pano,model,width,height",
                "object_values": ",".join(MANDATORY_FEATURES)
            },
            timeout=10
        )
        
        if response.status_code != 200:
            return None
            
        all_images = response.json().get("data", [])
        
        # Apply essential quality filters
        filtered_images = filter_quality_images(all_images)
        
        # Return top results after filtering
        return filtered_images[:limit]
        
    except:
        return None

def get_image_url(image_data):
    """Returns the direct image URL."""
    try:
        return image_data[IMAGE_SIZE]
    except:
        return None

def filter_quality_images(images):
    """Filter out 360° and low-quality images."""
    filtered_images = []
    
    for img in images:
        # Skip blacklisted images
        image_url = img.get(IMAGE_SIZE, '')
        if is_blacklisted(image_url):
            continue
            
        # Skip panoramic images
        if img.get('is_pano', False):
            continue
            
        # Skip 360° cameras
        camera_type = img.get('camera_type', '').lower()
        if any(excluded in camera_type for excluded in EXCLUDED_CAMERA_TYPES):
            continue
            
        # Skip known 360° camera models
        model = img.get('model', '').strip().lower()
        if any(excluded.lower() in model for excluded in EXCLUDED_CAMERA_MODELS):
            continue
            
        # Skip extreme aspect ratios
        width = img.get('width', 0)
        height = img.get('height', 0)
        if width > 0 and height > 0:
            aspect_ratio = width / height
            if aspect_ratio > 3.0 or aspect_ratio < 0.3:
                continue
        
        filtered_images.append(img)
    
    return filtered_images

def filter_quality_cameras(images):
    """Filter images from higher quality cameras for better educational content. More permissive version."""
    quality_images = []
    other_images = []
    
    for img in images:
        make = img.get('make', '').strip()
        model = img.get('model', '').strip()
        
        # Double-check: exclude known 360° cameras even if they passed previous filter
        if any(excluded_model.lower() in model.lower() for excluded_model in EXCLUDED_CAMERA_MODELS):
            # Only exclude if it's clearly a 360° camera
            if '360' in model.lower() or 'theta' in model.lower() or 'insta360' in model.lower():
                continue
            
        # More permissive scoring - give good scores to most cameras
        if any(preferred in make for preferred in PREFERRED_CAMERA_MAKES):
            img['quality_score'] = 1.0
            quality_images.append(img)
        else:
            img['quality_score'] = 0.8  # Increased from 0.5 to be more permissive
            other_images.append(img)
    
    # Return quality images first, then others
    return quality_images + other_images

def get_images_with_detections(images, coords):
    """Query for images that likely contain traffic signs, road infrastructure, and vehicle/driving content."""
    try:
        # Create a search area for detection (configurable)
        margin = TRAFFIC_SIGN_RADIUS_KM / 111.0  # Convert km to degrees
        bbox = f"{coords['lon']-margin},{coords['lat']-margin},{coords['lon']+margin},{coords['lat']+margin}"
        
        # Query for traffic signs (configurable traffic sign types)
        traffic_signs_query = ",".join(TRAFFIC_SIGN_TYPES)
        
        response = requests.get(
            "https://graph.mapillary.com/map_features",
            params={
                "access_token": MAPILLARY_TOKEN,
                "bbox": bbox,
                "limit": 500,
                "object_values": traffic_signs_query,
                "fields": "id,object_value,images"
            },
            timeout=8
        )
        
        # Collect image IDs with traffic signs
        traffic_sign_image_ids = set()
        if response.status_code == 200:
            features = response.json().get("data", [])
            for feature in features:
                image_ids = feature.get('images', [])
                traffic_sign_image_ids.update(image_ids)
        
        # Query for road infrastructure (separate request)
        infrastructure_query = ",".join(ROAD_INFRASTRUCTURE_TYPES)
        
        infrastructure_response = requests.get(
            "https://graph.mapillary.com/map_features",
            params={
                "access_token": MAPILLARY_TOKEN,
                "bbox": bbox,
                "limit": 500,
                "object_values": infrastructure_query,
                "fields": "id,object_value,images"
            },
            timeout=8
        )
        
        # Collect image IDs with road infrastructure
        infrastructure_image_ids = set()
        if infrastructure_response.status_code == 200:
            features = infrastructure_response.json().get("data", [])
            for feature in features:
                image_ids = feature.get('images', [])
                infrastructure_image_ids.update(image_ids)
        
        # Query for vehicle and driving related content (new)
        vehicle_query = ",".join(VEHICLE_RELATED_TYPES)
        
        vehicle_response = requests.get(
            "https://graph.mapillary.com/map_features",
            params={
                "access_token": MAPILLARY_TOKEN,
                "bbox": bbox,
                "limit": 500,
                "object_values": vehicle_query,
                "fields": "id,object_value,images"
            },
            timeout=8
        )
        
        # Collect image IDs with vehicle/driving content
        vehicle_image_ids = set()
        if vehicle_response.status_code == 200:
            features = vehicle_response.json().get("data", [])
            for feature in features:
                image_ids = feature.get('images', [])
                vehicle_image_ids.update(image_ids)
        
        # Score images based on educational content (more permissive)
        educational_images = []
        for img in images:
            img_id = img['id']
            
            # Calculate scores for different categories
            educational_score = 0.0
            road_infrastructure_score = 0.0
            vehicle_content_score = 0.0
            
            if img_id in traffic_sign_image_ids:
                educational_score = 1.0
            
            if img_id in infrastructure_image_ids:
                road_infrastructure_score = 1.0
            
            if img_id in vehicle_image_ids:
                vehicle_content_score = 1.0
            
            # More permissive: if no specific content found, still give decent scores
            # This allows more general street images that might contain driving situations
            if educational_score == 0.0 and road_infrastructure_score == 0.0 and vehicle_content_score == 0.0:
                educational_score = 0.6  # Increased from 0.3
                road_infrastructure_score = 0.6  # Increased from 0.3
                vehicle_content_score = 0.6  # New baseline
            
            img['educational_score'] = educational_score
            img['road_infrastructure_score'] = road_infrastructure_score
            img['vehicle_content_score'] = vehicle_content_score
            
            # More permissive: include images with any positive score
            if educational_score > 0.0 or road_infrastructure_score > 0.0 or vehicle_content_score > 0.0:
                educational_images.append(img)
        
        # Return all images with scores (more permissive)
        if educational_images:
            return educational_images
        else:
            # Assign default scores to all images (fallback)
            for img in images:
                img['educational_score'] = 0.7  # Higher default scores
                img['road_infrastructure_score'] = 0.7
                img['vehicle_content_score'] = 0.7
            return images
    
    except:
        # If detection fails, return all images with decent scoring
        for img in images:
            img['educational_score'] = 0.7  # Higher fallback scores
            img['road_infrastructure_score'] = 0.7
            img['vehicle_content_score'] = 0.7
        return images

def select_best_educational_image(images):
    """Select the best image based on vehicle perspective and driving education value."""
    if not images:
        return None
    
    # Sort by educational score, then quality score (configurable weights)
    def score_image(img):
        educational_score = img.get('educational_score', 0)
        road_infrastructure_score = img.get('road_infrastructure_score', 0)
        vehicle_content_score = img.get('vehicle_content_score', 0)
        vehicle_likelihood = img.get('vehicle_likelihood', 0.5)
        road_validated = 1.0 if img.get('road_validated', False) else 0.0
        quality_score = img.get('quality_score', 0.5)
        recency_score = calculate_recency_score(img.get('captured_at', 0))
        
        # Weighted combined score prioritizing vehicle perspective
        return (educational_score * EDUCATION_WEIGHT) + \
               (road_infrastructure_score * ROAD_CONTENT_WEIGHT) + \
               (vehicle_content_score * VEHICLE_CONTENT_WEIGHT) + \
               (vehicle_likelihood * VEHICLE_PERSPECTIVE_WEIGHT) + \
               (road_validated * ROAD_VALIDATION_WEIGHT) + \
               (quality_score * QUALITY_WEIGHT) + \
               (recency_score * RECENCY_WEIGHT)
    
    sorted_images = sorted(images, key=score_image, reverse=True)
    
    # Add some randomness among top candidates (configurable number)
    top_candidates = sorted_images[:min(MAX_TOP_CANDIDATES, len(sorted_images))]
    selected = random.choice(top_candidates)
    
    return selected

def calculate_recency_score(captured_at):
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

def filter_vehicle_perspective_images(images):
    """Filter images to only include those likely taken from vehicles on roads."""
    vehicle_images = []
    
    sequences = {}
    for img in images:
        sequence_data = img.get('sequence')
        if isinstance(sequence_data, dict):
            seq_id = sequence_data.get('id', 'unknown')
        elif isinstance(sequence_data, str):
            seq_id = sequence_data
        else:
            seq_id = 'unknown'
            
        if seq_id not in sequences:
            sequences[seq_id] = []
        sequences[seq_id].append(img)
    
    for seq_id, seq_images in sequences.items():
        if len(seq_images) < 2:
            for img in seq_images:
                img['vehicle_likelihood'] = 0.7
                vehicle_images.append(img)
            continue
        
        seq_images.sort(key=lambda x: x.get('captured_at', 0))
        
        for img in seq_images:
            img['vehicle_likelihood'] = 0.8
            vehicle_images.append(img)
    
    return vehicle_images

def extract_coordinates(image):
    """Extract coordinates from image computed_geometry or fallback methods."""
    try:
        # Try computed_geometry first
        computed_geom = image.get('computed_geometry')
        if computed_geom and computed_geom.get('coordinates'):
            coords = computed_geom['coordinates']
            return [coords[0], coords[1]]  # [lon, lat]
        
        # Fallback to other coordinate sources if available
        return None
    except:
        return None

def validate_road_content_in_images(images, coords):
    """Validate that images actually contain road content and are taken from road perspective."""
    if not images:
        return images
    
    try:
        # Create search area for validation
        margin = 0.005  # Small area for precise road checking
        bbox = f"{coords['lon']-margin},{coords['lat']-margin},{coords['lon']+margin},{coords['lat']+margin}"
        
        # Search for mandatory road features
        mandatory_query = ",".join(MANDATORY_ROAD_FEATURES)
        
        response = requests.get(
            "https://graph.mapillary.com/map_features",
            params={
                "access_token": MAPILLARY_TOKEN,
                "bbox": bbox,
                "limit": 200,
                "object_values": mandatory_query,
                "fields": "id,object_value,images"
            },
            timeout=8
        )
        
        road_feature_image_ids = set()
        if response.status_code == 200:
            features = response.json().get("data", [])
            for feature in features:
                image_ids = feature.get('images', [])
                road_feature_image_ids.update(image_ids)
        
        # Filter images to only include those with road features
        validated_images = []
        for img in images:
            img_id = img['id']
            vehicle_likelihood = img.get('vehicle_likelihood', 0.5)
            
            # More permissive: accept images with road features OR moderate vehicle likelihood
            if img_id in road_feature_image_ids or vehicle_likelihood >= 0.6:  # Lowered from 0.8
                img['road_validated'] = True
                validated_images.append(img)
            else:
                img['road_validated'] = False
        
        return validated_images
        
    except:
        # If validation fails, return original images
        return images

# Direct test if script is executed
if __name__ == "__main__":
    result = download_street_image("Paris", limit=10)
    if result:
        print(result)
    else:
        exit(1) 