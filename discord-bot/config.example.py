# JSHunter Discord Bot Configuration Template
# Copy this file to config.py and fill in your actual values

# Discord Bot Configuration
DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"  # Get from Discord Developer Portal
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"  # Optional: Discord webhook URL

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
