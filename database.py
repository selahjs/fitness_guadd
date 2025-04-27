from pymongo import MongoClient
import config

# Connect to MongoDB
client = MongoClient(config.MONGO_URI)
db = client["eth_telegram_communities"]

# Collections
communities = db["communities"]
users = db["users"]
analytics = db["analytics"]

# Create text index for search
def setup_indexes():
    # Remove existing text indexes first
    try:
        communities.drop_index("name_text_description_text_keywords_text")
        print("Successfully dropped existing text index")
    except Exception as e:
        print(f"Note: {e}")
    
    # Create new index with multilingual support
    communities.create_index([
        ("name", "text"), 
        ("description", "text"),
        ("keywords", "text")
    ], default_language="none")
    print("Successfully created text index with language: none")

# Initialize database
def init_db():
    # Setup indexes
    setup_indexes()
    
    # Check if we need to add sample data
    if communities.count_documents({}) == 0:
        add_sample_data()

def add_sample_data():
    sample_communities = [
        {
            "name": "Ethiopian Tech Hub",
            "description": "Community for tech enthusiasts in Ethiopia",
            "category": "tech",
            "members": 1200,
            "language": "english",
            "location": {
                "city": "Addis Ababa",
                "region": "Addis Ababa"
            },
            "link": "https://t.me/ethiotechhub",
            "keywords": ["programming", "startup", "innovation", "code"]
        },
        {
            "name": "ፊትነስ አዲስ",
            "description": "የአካል ብቃት እና ጤናማ አኗኗር ማህበረሰብ",
            "category": "fitness",
            "members": 850,
            "language": "amharic",  # Keep language as amharic for filtering purposes
            # Remove the language_override to avoid the error
            # Change the field name to avoid triggering MongoDB's language detection
            "display_language": "amharic",  # Use this for UI display
            "location": {
                "city": "Addis Ababa",
                "region": "Addis Ababa"
            },
            "link": "https://t.me/fitnessaddis",
            "keywords": ["ስፖርት", "ጤና", "fitness", "workout"]
        }
    ]
    
    # Insert one by one to avoid batch errors
    for community in sample_communities:
        try:
            # For Amharic entries, handle differently
            if "display_language" in community:
                # Copy the value to language for consistency in your code
                community["language"] = community["display_language"]
                
            communities.insert_one(community)
            print(f"Added community: {community['name']}")
        except Exception as e:
            print(f"Error inserting {community['name']}: {e}")