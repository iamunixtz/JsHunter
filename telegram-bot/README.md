# JS Ninja Telegram Bot

Interactive Telegram bot for scanning JavaScript files for potential secrets and sensitive information.

## Features

- Mobile-friendly file scanning
- User access control
- Real-time scan results
- File size and type validation
- Formatted result messages
- JSON report generation
- Automatic TruffleHog installation

## Installation

### Prerequisites

1. Create a Telegram bot:
   - Message [@BotFather](https://t.me/botfather)
   - Use `/newbot` command
   - Choose a name and username
   - Save the bot token

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Edit `config.py` and set your bot token:

```python
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# Optional: Restrict access to specific users
ALLOWED_USER_IDS = [123456789, 987654321]  # Telegram user IDs

# File limits
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx"]
```

### Running the Bot

```bash
python jsninja_bot.py
```

## Usage

### Bot Commands

- `/start` - Show welcome message and help
- `/status` - Check bot and TruffleHog status

### Scanning Files

1. Start a chat with your bot
2. Send any JavaScript file as an attachment
3. Wait for the scan results
4. Download detailed JSON report if secrets are found

### Example Conversation

```
User: /start
Bot: Welcome to JS Ninja Bot!
     
     I can help you scan JavaScript files for potential secrets...

User: [Uploads app.js file]
Bot: Downloading file...
     Scanning file...
     Found potential secrets:
     
     • [AWS] (line 42)
       ✓ `AKIA1234567890EXAMPLE...`
     
     • [GitHub] (line 156)
       ? `ghp_abcdefghijklmnop...`
```
## Configuration Options

### Access Control

```python
# Allow everyone (empty list)
ALLOWED_USER_IDS = []

# Restrict to specific users
ALLOWED_USER_IDS = [123456789, 987654321]
```

### File Limits

```python
# Maximum file size in MB
MAX_FILE_SIZE_MB = 10

# Supported file extensions
ALLOWED_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx"]
```

### Storage Directories

```python
# Temporary file storage
TEMP_DIR = "temp"

# Scan results storage
RESULTS_DIR = "results"
```

## Security Features

### User Authorization

The bot checks user IDs before processing requests:

```python
def is_user_authorized(user_id: int) -> bool:
    return len(config.ALLOWED_USER_IDS) == 0 or user_id in config.ALLOWED_USER_IDS
```

### File Validation

- File extension checking
- File size limits
- Automatic cleanup of temporary files

### Result Formatting

- Redacted sensitive values in messages
- Full details available in JSON reports
- Verification status indicators

## Deployment

### Local Development

```bash
python jsninja_bot.py
```

### Production Deployment

1. **VPS/Server**:
   ```bash
   # Use screen or tmux for persistent sessions
   screen -S jsninja-bot
   python jsninja_bot.py
   # Ctrl+A, D to detach
   ```

2. **Docker** (create Dockerfile):
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "jsninja_bot.py"]
   ```

3. **Systemd Service** (Linux):
   ```ini
   [Unit]
   Description=JS Ninja Telegram Bot
   After=network.target
   
   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/telegram-bot
   ExecStart=/usr/bin/python3 jsninja_bot.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

## Troubleshooting

### Bot Not Responding

1. Check bot token in `config.py`
2. Verify bot is running: `python jsninja_bot.py`
3. Check network connectivity
4. Review console logs for errors

### TruffleHog Issues

```bash
# The bot will auto-install TruffleHog, but you can manually install:
cd ../cli/
python jsninja.py --setup
```

### Permission Errors

Ensure write permissions for:
- `temp/` directory
- `results/` directory
- `.bin/` directory (for TruffleHog)

### File Upload Issues

- Check file size limits
- Verify file extension is supported
- Ensure user is authorized

## Use Cases

- **Mobile Security Testing**: Quick file analysis on mobile devices
- **Team Collaboration**: Share scan results with team members
- **Educational**: Teaching security concepts
- **Remote Analysis**: Scan files without local setup
- **Quick Triage**: Fast initial assessment of JavaScript files

## Privacy & Security

- Files are processed locally and deleted after scanning
- Bot tokens should be kept secure
- Consider using access control in production
- Monitor bot usage and logs
- Results may contain sensitive information - handle appropriately

## GitHub Repository

### Pushing to GitHub

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit of JS Ninja Telegram Bot"

# Add remote repository
git remote add origin https://github.com/yourusername/jsninja-telegram-bot.git

# Push to GitHub
git push -u origin main
```

Visit the repository at https://github.com/yourusername/jsninja-telegram-bot to manage issues, pull requests, and documentation.