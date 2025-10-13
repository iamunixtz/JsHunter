# JSHunter Discord Bot

A high-performance Discord bot for JavaScript security scanning with JSHunter.

## Features

- **High-Performance Scanning**: Uses JSHunter's async processing capabilities
- **File Upload Support**: Scan JavaScript files directly via Discord
- **URL Scanning**: Scan remote JavaScript files with `!scanurl`
- **Rich Embeds**: Beautiful formatted results with full API key display
- **File Attachments**: Sends detailed JSON result files
- **Webhook Integration**: Optional webhook notifications

## Setup

### 1. Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token

### 2. Set Bot Permissions

1. Go to "OAuth2" → "URL Generator"
2. Select "bot" scope
3. Select permissions: Send Messages, Attach Files, Read Message History
4. Use the generated URL to invite bot to your server

### 3. Configure the Bot

Edit `config.py` and set your bot token:

```python
# Discord Bot Configuration
DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"

# Optional: Restrict access to specific users
ALLOWED_USER_IDS = [123456789012345678, 987654321098765432]  # Discord user IDs

# File limits
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = ['.js', '.jsx', '.ts', '.tsx', '.mjs']
```

### 4. Run the Bot

```bash
# Install dependencies
pip install -r requirements.txt

# Start the bot
python3 jshunter_discord.py
```

## Commands

- `!status` - Check bot status and capabilities
- `!jshunter_help` - Show detailed command usage
- `!scanurl <URL>` - Scan a JavaScript URL
- `!scan` - Upload a file to scan (reply to message with file attachment)

## Example Usage

```
!scanurl https://example.com/app.js
```

The bot will:
1. Download the JavaScript file
2. Scan it using JSHunter's high-performance engine
3. Display results with full API keys in backticks for easy copying
4. Send detailed JSON result files as attachments

## Message Format

Results are displayed in a clean format:

```
🔍 **Verified Secrets found in https://example.com/app.js**

**[Infura]** `0e71fe0b60644078acfa6b3f08e61ed2` ✅ Verified
**[AWS]** `AKIAIOSFODNN7EXAMPLE` ✅ Verified
**[GitHub]** `ghp_xxxxxxxxxxxxxxxxxxxx` ❓ Unverified
```

## Webhook Scanner

For simple notifications without a full bot, use the webhook scanner:

```bash
python3 jshunter_webhook.py "https://example.com/app.js"
```

## Docker Support

```bash
# Build and run with Docker
docker build -t jshunter-discord .
docker run -e DISCORD_BOT_TOKEN=your_token_here jshunter-discord
```

## Security Notes

- Never commit your bot token to version control
- Use environment variables for sensitive configuration
- Restrict bot permissions to only what's necessary
- Monitor bot usage and set up rate limiting if needed