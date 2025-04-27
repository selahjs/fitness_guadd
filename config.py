import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Categories
CATEGORIES = ["tech", "fitness", "education", "business", "arts", "entertainment"]

# Ethiopian locations
LOCATIONS = [
    "Addis Ababa", 
    "Bahir Dar", 
    "Hawassa", 
    "Dire Dawa", 
    "Mekelle", 
    "Gondar", 
    "Adama"
]

# Default language options
LANGUAGES = ["english", "amharic", "both"]