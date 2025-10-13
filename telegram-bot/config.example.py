# JSHunter Telegram Bot Configuration Template
# Copy this file to config.py and fill in your actual values

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # Get from @BotFather
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID_HERE"  # Your Telegram chat ID

# Bot Settings
ALLOWED_USER_IDS = []  # Empty list means all users are allowed
MAX_FILE_SIZE_MB = 10  # Maximum file size in MB
ALLOWED_EXTENSIONS = ['.js', '.jsx', '.ts', '.tsx', '.mjs']

# Directories
TEMP_DIR = "temp"
RESULTS_DIR = "results"

# JSHunter CLI Path
JSHUNTER_PATH = "../cli/jshunter"

# High-Performance Settings
HIGH_PERFORMANCE_MODE = True
MAX_CONCURRENT_DOWNLOADS = 50
BATCH_SIZE = 20
