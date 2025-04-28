import os
import logging
from dotenv import load_dotenv
from bot import main  # Import the main function from your bot.py file

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Start the bot
    main()