# JS Ninja Discord Bot

Discord bot with rich embed formatting for scanning JavaScript files for potential secrets and sensitive information.

## Features

- Rich embed result formatting
- Multi-guild support
- Command-based interface
- File attachment processing
- User access control
- Detailed status reporting
- Automatic TruffleHog installation

## Installation

### Prerequisites

1. Create a Discord application:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Go to "Bot" section
   - Click "Add Bot"
   - Copy the bot token
   - Enable necessary intents (Message Content Intent)

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Edit `config.py` and set your bot token:

```python
# Discord Bot Configuration
DISCORD_BOT_TOKEN = "MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz"

# Optional: Restrict access to specific users
ALLOWED_USER_IDS = [123456789012345678, 987654321098765432]  # Discord user IDs

# File limits
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx"]
```

### Bot Permissions

When inviting the bot to your server, ensure it has these permissions:

- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Use Slash Commands (optional)

### Running the Bot

```bash
python jsninja_discord.py
```

## Usage

### Bot Commands

- `!help` - Show available commands and usage
- `!status` - Check bot and TruffleHog status
- `!scan` - Attach a JavaScript file and use this command to scan it

### Scanning Files

1. Upload a JavaScript file to any channel where the bot has access
2. Use the `!scan` command in the same message or after uploading
3. Wait for the scan results in a rich embed format
4. Download detailed JSON report if secrets are found

### Example Usage

```
User: [Uploads app.js] !scan
Bot: [Rich Embed]
     ALERT: Secrets Found!
     Found 2 potential secret(s) in app.js
     
     Summary
     Total: 2
     Verified: 1
     
     [AWS] (Line 42)
     `AKIA1234567890EXAMPLE...`
     [Verified]
     
     [GitHub] (Line 156)
     `ghp_abcdefghijklmnop...`
     [Unverified]
```

## Commands Reference

### !help

Shows comprehensive help information:

```
JS Ninja Bot Help
Scan JavaScript files for potential secrets and vulnerabilities.

!scan - Attach a JavaScript file and use this command to scan it
!status - Check bot and TruffleHog status
!help - Show this help message

Supported Files: .js, .jsx, .ts, .tsx (max 10MB)
```

### !status

Displays bot and system status:

```
JS Ninja Bot Status

TruffleHog: Active
Found at: /path/to/trufflehog

Max File Size: 10MB
Supported Extensions: .js, .jsx, .ts, .tsx
Guilds: 3
```

### !scan

Processes attached JavaScript files:

- Validates file type and size
- Downloads and scans the file
- Returns results in rich embed format
- Provides detailed JSON report for complex findings

## Configuration Options

### Access Control

```python
# Allow everyone (empty list)
ALLOWED_USER_IDS = []

# Restrict to specific users (Discord user IDs)
ALLOWED_USER_IDS = [123456789012345678, 987654321098765432]
```

### File Limits

```python
# Maximum file size in MB
MAX_FILE_SIZE_MB = 10

# Supported file extensions
ALLOWED_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx"]
```

### Storage Configuration

```python
# Temporary file storage
TEMP_DIR = "temp"

# Scan results storage
RESULTS_DIR = "results"
```

## Rich Embed Features

### Success Embed (No Secrets)

- Green color scheme
- Clear "no secrets found" message

### Alert Embed (Secrets Found)

- Red color scheme
- Summary statistics
- Individual finding details
- Verification status indicators

### Status Embed

- Blue color scheme
- System information
- Configuration details
- Multi-guild statistics

## Deployment

### Local Development

```bash
python jsninja_discord.py
```

### Production Deployment

1. **VPS/Server**:
   ```bash
   # Use screen or tmux for persistent sessions
   screen -S jsninja-discord
   python jsninja_discord.py
   # Ctrl+A, D to detach
   ```

2. **Docker**:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "jsninja_discord.py"]
   ```

3. **Systemd Service**:
   ```ini
   [Unit]
   Description=JS Ninja Discord Bot
   After=network.target
   
   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/discord-bot
   ExecStart=/usr/bin/python3 jsninja_discord.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

### Bot Invitation

Generate an invitation link with required permissions:

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=274877908032&scope=bot
```

Replace `YOUR_BOT_CLIENT_ID` with your bot's client ID from the Discord Developer Portal.

## Advanced Features

### Multi-Guild Support

The bot can operate in multiple Discord servers simultaneously:

- Separate access control per server (if needed)
- Shared TruffleHog installation
- Centralized logging and monitoring

### Error Handling

- Graceful handling of file processing errors
- User-friendly error messages
- Automatic cleanup of temporary files
- Detailed logging for debugging

### Rate Limiting

Consider implementing rate limiting for production use:

```python
from discord.ext import commands

@commands.cooldown(1, 60, commands.BucketType.user)  # 1 scan per minute per user
@bot.command(name='scan')
async def scan_command(ctx):
    # ... existing code ...
```

## Troubleshooting

### Bot Not Responding

1. Check bot token in `config.py`
2. Verify bot has necessary permissions
3. Check Message Content Intent is enabled
4. Review console logs for errors

### Permission Issues

- Ensure bot has "Send Messages" permission
- Check "Embed Links" permission for rich embeds
- Verify "Attach Files" for JSON reports

### File Processing Errors

- Check file size limits
- Verify supported file extensions
- Ensure user authorization
- Review temporary directory permissions

## GitHub Repository Setup

To push this project to GitHub:

1. Initialize a Git repository:
   ```bash
   git init
   ```

2. Add all files to the repository:
   ```bash
   git add .
   ```

3. Commit the changes:
   ```bash
   git commit -m "Initial commit of JS Ninja Discord Bot"
   ```

4. Create a new repository on GitHub

5. Add the remote origin:
   ```bash
   git remote add origin https://github.com/yourusername/jsninja-discord-bot.git
   ```

6. Push to GitHub:
   ```bash
   git push -u origin main
   ```

### Important Considerations

- Ensure your `config.py` is added to `.gitignore` to prevent exposing your bot token
- Consider using environment variables for sensitive information
- Add a `.gitignore` file to exclude temporary files and directories