"""
Ethiopian Telegram Communities Bot
- Helps users discover Telegram communities in Ethiopia
- Filters by category, location, language, and size
- Supports both English and Amharic search
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, CallbackContext
from dotenv import load_dotenv
import config
from database import communities, users, analytics, init_db, setup_indexes

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when the command /start is issued."""
    user_data = {
        "telegramId": update.effective_user.id,
        "username": update.effective_user.username,
        "firstName": update.effective_user.first_name,
        "lastName": update.effective_user.last_name,
        "joinedAt": update.message.date,
        "lastActive": update.message.date
    }
    
    # Update or insert user data
    users.update_one(
        {"telegramId": user_data["telegramId"]},
        {"$set": user_data},
        upsert=True
    )
    
    await update.message.reply_text(
        "👋 Welcome to Ethiopian Telegram Communities Bot!\n\n"
        "I can help you find Telegram groups and channels in Ethiopia based on your interests.\n\n"
        "Commands:\n"
        "/search - Search for communities\n"
        "/categories - Browse by category\n"
        "/location - Filter by location\n"
        "/submit - Submit a new community\n"
        "/help - Show help information"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help information when the command /help is issued."""
    # Update last active timestamp
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$set": {"lastActive": update.message.date}}
    )
    
    await update.message.reply_text(
        "Ethiopian Telegram Communities Bot Help:\n\n"
        "• Use /search to find communities by keywords\n"
        "• Use /categories to browse by category\n"
        "• Use /location to filter by city/region\n"
        "• Use /submit to add a new community\n\n"
        "Examples:\n"
        "- /search programming (find tech communities)\n"
        "- /search ስፖርት (find fitness communities in Amharic)\n"
        "- Search supports both English and Amharic"
    )

async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display categories to browse"""
    # Update last active timestamp
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$set": {"lastActive": update.message.date}}
    )
    
    # Use categories from config
    keyboard = []
    row = []
    
    for i, category in enumerate(config.CATEGORIES):
        # Create button with emoji based on category
        emoji = get_category_emoji(category)
        button = InlineKeyboardButton(f"{emoji} {category.capitalize()}", callback_data=f"category_{category}")
        
        row.append(button)
        
        # Create rows with 2 buttons each
        if len(row) == 2 or i == len(config.CATEGORIES) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a category to browse:", reply_markup=reply_markup)

def get_category_emoji(category):
    """Return emoji for a given category"""
    emoji_map = {
        "tech": "💻",
        "fitness": "💪",
        "education": "📚",
        "business": "💼",
        "arts": "🎨",
        "entertainment": "🎮"
    }
    return emoji_map.get(category, "📌")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /search command"""
    # Update last active timestamp
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$set": {"lastActive": update.message.date}}
    )
    
    if not context.args:
        await update.message.reply_text(
            "Please provide search terms after /search. For example:\n"
            "/search programming\n"
            "/search ስፖርት\n"
            "You can search in both English and Amharic."
        )
        return
    
    search_query = ' '.join(context.args)
    
    # Record search query in user's history
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$push": {"searchHistory": {"query": search_query, "timestamp": update.message.date}}}
    )
    
    await perform_search(update, search_query)

async def perform_search(update: Update, search_query: str):
    """Search for communities based on the query"""
    try:
        # Perform text search
        results = communities.find({
            "$text": {"$search": search_query}
        }).limit(5)
        
        result_list = list(results)
        
        if not result_list:
            await update.message.reply_text(f"No communities found for '{search_query}'. Try different keywords or use /categories to browse.")
            return
        
        await update.message.reply_text(f"Found {len(result_list)} communities matching '{search_query}':")
        
        for community in result_list:
            # Track search hit for this community
            communities.update_one(
                {"_id": community["_id"]},
                {"$inc": {"metrics.searchHits": 1}}
            )
            
            # Create join button for each community
            keyboard = [[InlineKeyboardButton("Join Group", url=community["link"])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Format member count
            member_count = f"{community['members']:,}"
            
            # Get location string (handle both formats)
            if isinstance(community.get('location'), dict):
                location_str = community['location'].get('city', 'Unknown')
            else:
                location_str = community.get('location', 'Unknown')
            
            # Send community information
            await update.message.reply_text(
                f"📱 *{community['name']}*\n"
                f"📝 {community['description']}\n"
                f"👥 Members: {member_count}\n"
                f"🗣️ Language: {community['language'].capitalize()}\n"
                f"📍 Location: {location_str}\n"
                f"🏷️ Category: {community['category'].capitalize()}",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text("Sorry, an error occurred while searching. Please try again later.")

async def submit_community(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /submit command to add new communities"""
    # Update last active timestamp
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$set": {"lastActive": update.message.date}}
    )
    
    await update.message.reply_text(
        "To submit a new Telegram community, please provide the following information:\n\n"
        "1. Group/Channel name\n"
        "2. Description\n"
        "3. Category (tech, fitness, etc.)\n"
        "4. Language (English, Amharic, or both)\n"
        "5. Location in Ethiopia\n"
        "6. Invite link\n\n"
        "Please format your submission as:\n"
        "/add [name] | [description] | [category] | [language] | [location] | [link]"
    )

async def add_community(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process new community submission"""
    # Update last active timestamp
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$set": {"lastActive": update.message.date}}
    )
    
    text = update.message.text
    
    # Remove the command part
    if text.startswith('/add '):
        text = text[5:]
    
    # Split by delimiter
    parts = [part.strip() for part in text.split('|')]
    
    if len(parts) != 6:
        await update.message.reply_text(
            "❌ Invalid format. Please use:\n"
            "/add [name] | [description] | [category] | [language] | [location] | [link]"
        )
        return
    
    name, description, category, language, location, link = parts
    
    # Validate the link
    if not link.startswith('https://t.me/'):
        await update.message.reply_text("❌ Invalid Telegram link. It should start with https://t.me/")
        return
    
    # Check if category is valid
    if category.lower() not in [c.lower() for c in config.CATEGORIES]:
        category_list = ", ".join(config.CATEGORIES)
        await update.message.reply_text(f"❌ Invalid category. Please use one of: {category_list}")
        return
    
    # Check if language is valid
    if language.lower() not in [l.lower() for l in config.LANGUAGES]:
        language_list = ", ".join(config.LANGUAGES)
        await update.message.reply_text(f"❌ Invalid language. Please use one of: {language_list}")
        return
    
    # Create new community entry
    new_community = {
        "name": name,
        "description": description,
        "category": category.lower(),
        "members": 0,  # Will be updated later
        "language": language.lower(),
        "location": {
            "city": location,
            "region": ""  # Can be filled later or through admin panel
        },
        "link": link,
        "keywords": [category.lower()],
        "createdAt": update.message.date,
        "updatedAt": update.message.date,
        "verifiedStatus": False,
        "activityLevel": "medium",
        "submittedBy": {
            "userId": update.effective_user.id,
            "username": update.effective_user.username
        },
        "approved": False,  # Requires admin approval
        "metrics": {
            "searchHits": 0,
            "clicks": 0,
            "userRating": 0
        }
    }
    
    try:
        # Add to database (pending approval)
        result = communities.insert_one(new_community)
        
        # Update user's submitted communities
        users.update_one(
            {"telegramId": update.effective_user.id},
            {"$push": {"submittedCommunities": result.inserted_id}}
        )
        
        await update.message.reply_text(
            "✅ Thank you! Your community submission has been received and is pending approval."
        )
        
    except Exception as e:
        logger.error(f"Error adding community: {e}")
        await update.message.reply_text("Sorry, an error occurred while submitting the community. Please try again later.")

async def location_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Filter communities by location"""
    # Update last active timestamp
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$set": {"lastActive": update.message.date}}
    )
    
    # Use locations from config
    keyboard = []
    row = []
    
    for i, location in enumerate(config.LOCATIONS):
        button = InlineKeyboardButton(location, callback_data=f"location_{location.lower().replace(' ', '')}")
        
        row.append(button)
        
        # Create rows with 2 buttons each
        if len(row) == 2 or i == len(config.LOCATIONS) - 1:
            keyboard.append(row)
            row = []
    
    # Add "All Locations" button
    keyboard.append([InlineKeyboardButton("All Locations", callback_data="location_all")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a location to filter communities:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: CallbackContext):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    # Update last active timestamp
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$set": {"lastActive": query.message.date}}
    )
    
    callback_data = query.data
    
    if callback_data.startswith("category_"):
        category = callback_data.split("_")[1]
        
        try:
            results = communities.find({"category": category, "approved": True})
            
            result_list = list(results)
            if not result_list:
                await query.message.reply_text(f"No communities found in the {category} category.")
                return
            
            await query.message.reply_text(f"Found {len(result_list)} communities in {category}:")
            
            for community in result_list:
                keyboard = [[InlineKeyboardButton("Join Group", url=community["link"])]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Track click
                communities.update_one(
                    {"_id": community["_id"]},
                    {"$inc": {"metrics.clicks": 1}}
                )
                
                # Get location string (handle both formats)
                if isinstance(community.get('location'), dict):
                    location_str = community['location'].get('city', 'Unknown')
                else:
                    location_str = community.get('location', 'Unknown')
                
                await query.message.reply_text(
                    f"📱 *{community['name']}*\n"
                    f"📝 {community['description']}\n"
                    f"👥 Members: {community['members']:,}\n"
                    f"🗣️ Language: {community['language'].capitalize()}\n"
                    f"📍 Location: {location_str}",
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"Category filter error: {e}")
            await query.message.reply_text("Sorry, an error occurred. Please try again later.")
    
    elif callback_data.startswith("location_"):
        location_code = callback_data.split("_")[1]
        
        if location_code == "all":
            await query.message.reply_text("Showing communities from all locations. Use /categories to browse by interest.")
            return
        
        # Find the actual location name from the location code
        location_name = None
        for loc in config.LOCATIONS:
            if loc.lower().replace(' ', '') == location_code:
                location_name = loc
                break
        
        if not location_name:
            await query.message.reply_text("Invalid location selected.")
            return
        
        try:
            # Search for communities in this location (supporting both location formats)
            results = communities.find({
                "$or": [
                    {"location": location_name},
                    {"location.city": location_name}
                ],
                "approved": True
            })
            
            result_list = list(results)
            if not result_list:
                await query.message.reply_text(f"No communities found in {location_name}.")
                return
            
            await query.message.reply_text(f"Found {len(result_list)} communities in {location_name}:")
            
            for community in result_list:
                keyboard = [[InlineKeyboardButton("Join Group", url=community["link"])]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Track click
                communities.update_one(
                    {"_id": community["_id"]},
                    {"$inc": {"metrics.clicks": 1}}
                )
                
                await query.message.reply_text(
                    f"📱 *{community['name']}*\n"
                    f"📝 {community['description']}\n"
                    f"👥 Members: {community['members']:,}\n"
                    f"🗣️ Language: {community['language'].capitalize()}\n"
                    f"🏷️ Category: {community['category'].capitalize()}",
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"Location filter error: {e}")
            await query.message.reply_text("Sorry, an error occurred. Please try again later.")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages as search queries"""
    # Update last active timestamp
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$set": {"lastActive": update.message.date}}
    )
    
    # Record search query in user's history
    users.update_one(
        {"telegramId": update.effective_user.id},
        {"$push": {"searchHistory": {"query": update.message.text, "timestamp": update.message.date}}}
    )
    
    await perform_search(update, update.message.text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    """Start the bot"""
    try:
        # Create application
        application = ApplicationBuilder().token(config.BOT_TOKEN).build()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("categories", categories))
        application.add_handler(CommandHandler("search", search_command))
        application.add_handler(CommandHandler("submit", submit_community))
        application.add_handler(CommandHandler("add", add_community))
        application.add_handler(CommandHandler("location", location_filter))
        
        # Register callback handler for buttons
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        # Handle text messages (for search queries without command)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        # Register error handler
        application.add_error_handler(error_handler)
        
        # Start the Bot
        logger.info("Starting bot...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    main()