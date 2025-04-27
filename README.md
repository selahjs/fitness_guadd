# Ethiopian Telegram Communities Bot

Fitness Guadd -- A Telegram bot that helps users discover and join Ethiopian communities (groups and channels) based on interests, categories, language, location, and other relevant filters.

## 🌟 Project Vision

This bot aims to solve the problem of finding relevant Ethiopian Telegram communities that match specific interests like tech, fitness, education, and more. The default Telegram search functionality is limited, so this bot provides enhanced discovery mechanisms with Ethiopia-specific focus.

## 🔍 Key Features

### Phase 1: Basic Functionality ✅ [COMPLETED]
- Basic bot setup with essential commands
- Simple search by keywords
- Database structure for storing community information
- Initial data collection with sample communities

### Phase 2: Enhanced Discovery 🚧 [IN PROGRESS]
- Advanced category browsing with subcategories
- Location-based filtering (cities and regions in Ethiopia)
- Community submission system for users to add new groups/channels
- Hybrid search combining stored database and real-time Telegram search
- Support for both English and Amharic languages

### Phase 3: Advanced Features 📝 [PLANNED]
- User preferences and personalized recommendations
- Community ratings and popularity metrics
- Analytics on trending Ethiopian communities
- Verification badges for official/high-quality communities
- Admin dashboard for content moderation
- Weekly digests of new communities matching user interests

## 🛠️ Technical Implementation

### Stack
- **Python** with **python-telegram-bot** library
- **MongoDB** for flexible data storage
- **Telethon** for advanced Telegram API integration (real-time search)
- **Render/Other-free-hosting** for hosting

### Data Collection Methods
- User submissions through the bot
- Manual curation of Ethiopian communities
- Web scraping of public Telegram directories
- Real-time search for the latest communities

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- MongoDB database
- Telegram Bot API token (from BotFather)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ethiopian-telegram-communities-bot.git
cd ethiopian-telegram-communities-bot

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your bot token and MongoDB connection string

# Run the bot
python bot.py
```

### Environment Variables
Create a `.env` file with the following:

```
BOT_TOKEN=your_telegram_bot_token_here
MONGO_URI=your_mongodb_connection_string
TELEGRAM_API_ID=your_telegram_api_id  # For Telethon integration
TELEGRAM_API_HASH=your_telegram_api_hash  # For Telethon integration
ADMIN_IDS=comma_separated_list_of_admin_telegram_ids
```

## 🗂️ Database Schema

The bot uses MongoDB with the following collections:

- **communities**: Stores information about Telegram communities
- **users**: Tracks user interactions and preferences
- **pending_submissions**: Holds community submissions awaiting approval
- **analytics**: Stores usage statistics and trends

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Project Status

- **Phase 1**: Completed
- **Phase 2**: In active development
- **Phase 3**: Planning stage

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram bot API wrapper
- Ethiopian tech and fitness communities for inspiration
- All contributors and community submitters

---

Made with ❤️ for Ethiopian Telegram community discovery