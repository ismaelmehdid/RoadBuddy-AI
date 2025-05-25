from enum import Enum
MISTRAL_BASE_URL = "https://api.mistral.ai/v1"
MISTRAL_IMAGE_TEXT_MODEL = "pixtral-12b-2409"

S3_BUCKET_NAME = "hackathon-ai-tech"

class APIEndpoints(Enum):
    DOCS = "/api/v1/docs"
    REDOC = "/api/v1/redoc"
    OPENAPI_URL = "/api/v1/openapi.json"
    LIVENESS = "/api/v1/healthy"
    EXAM_CHAT = "/api/v1/exam-chat"
    EXAM_CHAT_QUESTION = "/api/v1/exam-chat-question"
    STREET_IMAGE = "/api/v1/street-image"
    SIMILARITY_SEARCH = "/api/v1/similarity-search"

ExamAnswerMapping = {
    1: "A",
    2: "B",
    3: "C",
    4: "D"
}

#OpenStreetMap constants
PREFERRED_CAMERA_MAKES = [
    'GoPro', 'Canon', 'Nikon', 'Sony', 'Apple', 'Samsung', 
    'Google', 'OnePlus', 'Huawei', 'Xiaomi', 'DJI', 'Garmin',
    'Blackvue', 'Nextbase', 'Insta360'
]

# DATE PARAMETERS
SEARCH_YEARS_BACK = 5  # Search images from X years back
RECENT_THRESHOLD_DAYS = 30  # "Recent" images (max score)
MEDIUM_RECENT_DAYS = 365   # "Medium recent" images
OLD_THRESHOLD_DAYS = 730   # "Old" images

# SEARCH AREA PARAMETERS
SEARCH_RADIUS_KM = 2.0    # Main search radius (in km)
TRAFFIC_SIGN_RADIUS_KM = 1.0  # Radius for traffic sign search (more precise)

# LIMITS AND THRESHOLDS
DEFAULT_STREET_IMAGE_LIMIT = 20        # Default number of images to download
FETCH_MULTIPLIER = 3      # Multiplier for more choices (reduced for speed)
STREET_IMAGE_QUALITY_THRESHOLD = 0.7   # Minimum quality threshold
MAX_TOP_CANDIDATES = 3    # Number of best images to choose from (reduced for speed)

# TRAFFIC SIGN TYPES TO SEARCH (for educational content)
TRAFFIC_SIGN_TYPES = [
    "regulatory--*",    # Regulatory signs (stop, speed, etc.)
    "warning--*",       # Warning signs (danger, curves, etc.)
    "information--*"    # Information signs (direction, services, etc.)
]

# WEIGHTS FOR EDUCATIONAL SCORING
EDUCATION_WEIGHT = 0.6    # Importance of educational content (signs, etc.)
QUALITY_WEIGHT = 0.3      # Importance of camera quality
RECENCY_WEIGHT = 0.1      # Importance of image recency

# RECENCY SCORES
RECENT_SCORE = 1.0        # Score for recent images
MEDIUM_RECENT_SCORE = 0.8 # Score for medium recent images
OLD_SCORE = 0.6           # Score for old images
VERY_OLD_SCORE = 0.3      # Score for very old images

# FILE PARAMETERS
OUTPUT_FOLDER = "images"  # Output folder
IMAGE_SIZE = "thumb_2048_url"  # Image size (thumb_256_url, thumb_1024_url, thumb_2048_url)