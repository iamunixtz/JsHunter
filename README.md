# JS Ninja - JavaScript Security Scanner Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TruffleHog](https://img.shields.io/badge/powered%20by-TruffleHog-green.svg)](https://github.com/trufflesecurity/trufflehog)

JS Ninja is a comprehensive security scanner suite designed to detect secrets, API keys, and sensitive information in JavaScript files. It provides three different interfaces to suit various workflows and integration needs.

## Features

- **Advanced Secret Detection**: Powered by TruffleHog's robust detection engine
- **Multi-Format Support**: Supports `.js`, `.jsx`, `.ts`, `.tsx` files
- **Multiple Interfaces**: CLI, Telegram Bot, and Discord Bot
- **URL Scanning**: Direct scanning of JavaScript files from URLs
- **Auto-Installation**: Automatic TruffleHog setup and management
- **Detailed Reports**: JSON output with verification status and line numbers
- **Access Control**: User authorization for bot versions
- **Zero False Positives**: Advanced filtering and verification
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Cross-Platform**: Runs on Windows, Linux, and macOS

## Project Structure

```
js-ninja/
├── cli/                    # Command Line Interface
│   ├── jsninja.py         # Main CLI application
│   ├── Dockerfile         # CLI Docker configuration
│   └── requirements.txt   # CLI dependencies
├── telegram-bot/          # Telegram Bot Interface
│   ├── jsninja_bot.py    # Telegram bot implementation
│   ├── config.py         # Bot configuration
│   ├── Dockerfile        # Telegram bot Docker configuration
│   └── requirements.txt  # Telegram bot dependencies
├── discord-bot/           # Discord Bot Interface
│   ├── jsninja_discord.py # Discord bot implementation
│   ├── config.py         # Bot configuration
│   ├── Dockerfile        # Discord bot Docker configuration
│   └── requirements.txt  # Discord bot dependencies
├── jsninja/              # PyPI Package
│   ├── __init__.py      # Package initialization
│   ├── cli/             # CLI module
│   └── web/             # Web Interface
│       ├── main.py      # FastAPI application
│       ├── templates/   # HTML templates
│       └── static/      # Static assets
├── .github/              # GitHub Configuration
│   └── workflows/       # GitHub Actions workflows
├── setup.py             # Package configuration
├── docker-compose.yml   # Docker Compose configuration
└── README.md            # This file
```

## Installation from PyPI

The easiest way to install JS Ninja is through pip:

```bash
pip install jsninja-scanner
```

This will install both the CLI tool and the web interface.

## Tool Descriptions

### 1. Web Interface

**Functionality**: Modern web interface for scanning JavaScript files and URLs.

**Key Features**:
- File upload and URL scanning
- Modern, responsive UI
- IP-based result tracking
- Automatic deployment on GitHub Pages
- Results saved per user session
- Buy Me a Coffee integration

**Access**: Visit [https://yourusername.github.io/jsninja](https://yourusername.github.io/jsninja)

To run the web interface locally:
```bash
jsninja-web
```

### 2. CLI Tool (`cli/jsninja.py`)

**Functionality**: Command-line interface for scanning JavaScript files from URLs or local file lists.

**Key Features**:
- Scan single or multiple JavaScript URLs
- Batch processing from file lists
- SSL certificate bypass option
- Discord webhook integration
- Automatic file download and cleanup
- JSON result export

**Use Cases**:
- Bug bounty hunting
- Security audits
- CI/CD pipeline integration
- Automated security testing

### 2. Telegram Bot (`telegram-bot/jsninja_bot.py`)

**Functionality**: Interactive Telegram bot that accepts JavaScript files and returns scan results.

**Key Features**:
- File upload via Telegram
- Real-time scan results
- User access control
- File size and type validation
- Formatted result messages
- JSON report generation

**Use Cases**:
- Quick file analysis on mobile
- Team collaboration
- Remote security assessments
- Educational purposes

### 3. Discord Bot (`discord-bot/jsninja_discord.py`)

**Functionality**: Discord bot with rich embed formatting and server integration capabilities.

**Key Features**:
- Rich embed result formatting
- Server-wide deployment
- Command-based interface (`!scan`, `!status`, `!help`)
- File attachment processing
- Multi-guild support
- Detailed status reporting

**Use Cases**:
- Security team collaboration
- Community security analysis
- Educational workshops
- CTF competitions

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- Internet connection (for TruffleHog download)
- Docker and Docker Compose (optional, for containerized deployment)

### Option 1: Docker Deployment (Recommended)

The easiest way to run JS Ninja is using Docker and Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/js-ninja.git
   cd js-ninja
   ```

2. Create a `.env` file with your bot tokens:
   ```bash
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   DISCORD_BOT_TOKEN=your_discord_bot_token
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

This will start all components (CLI, Telegram bot, and Discord bot) in separate containers with proper volume mapping and networking.

### Option 2: Manual Installation

#### CLI Tool Setup

```bash
cd cli/
pip install -r requirements.txt
python jsninja.py --setup  # Install TruffleHog
```

#### Telegram Bot Setup

1. Set up the environment:
   ```bash
   cd telegram-bot
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. Create a bot with [@BotFather](https://t.me/botfather):
   - Send `/newbot` to BotFather
   - Choose a name for your bot
   - Choose a username ending in 'bot'
   - Copy the provided token

3. Configure the bot:
   - Edit `config.py` and set your bot token
   - Optionally set `ALLOWED_USER_IDS` for access control

4. Start the bot:
   ```bash
   python jsninja_bot.py
   ```

#### Discord Bot Setup

1. Set up the environment:
   ```bash
   cd discord-bot
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. Create a Discord application:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and name it
   - Go to "Bot" section and click "Add Bot"
   - Copy the bot token
   - Enable necessary Privileged Gateway Intents

3. Configure the bot:
   - Edit `config.py` and set your bot token
   - Optionally set `ALLOWED_USER_IDS` for access control

4. Invite the bot to your server:
   - Go to OAuth2 > URL Generator
   - Select "bot" scope and required permissions
   - Copy and open the generated URL
   - Choose your server and authorize

5. Start the bot:
   ```bash
   python jsninja_discord.py
   ```

## Usage Examples

### CLI Usage

```bash
# Scan a single URL
python jsninja.py -u "https://example.com/app.js"

# Scan multiple URLs from file
python jsninja.py -f urls.txt

# Ignore SSL errors
python jsninja.py -u "https://example.com/app.js" --ignore-ssl

# Send results to Discord webhook
python jsninja.py -u "https://example.com/app.js" --discord-webhook "webhook-url"
```

### Telegram Bot Usage

1. Start chat with your bot
2. Send `/start` for help
3. Either:
   - Upload a JavaScript file
   - Use `/scanurl <URL>` to scan a JavaScript file from URL
4. Receive scan results instantly

Available commands:
```
/start         # Show welcome message and help
/status        # Check bot status and supported features
/scanurl       # Scan JavaScript file from URL
/help          # Show available commands
```

### Discord Bot Usage

Available commands:
```
!help          # Show available commands
!status        # Check bot status
!scan          # Attach a file and use this command
!scanurl       # Scan JavaScript file from URL (!scanurl <URL>)
```

Example URL scanning:
```
# Telegram Bot
/scanurl https://example.com/app.js

# Discord Bot
!scanurl https://example.com/app.js
```

## Detection Capabilities

JS Ninja can detect various types of sensitive information:

- **API Keys**: AWS, Google, GitHub, etc.
- **Database Credentials**: MySQL, PostgreSQL, MongoDB
- **Authentication Tokens**: JWT, OAuth, Bearer tokens
- **Private Keys**: RSA, SSH, PGP keys
- **Webhooks**: Slack, Discord, Teams
- **Cloud Credentials**: Azure, GCP, DigitalOcean
- **Custom Patterns**: Configurable detection rules

## Output Format

All tools provide consistent output with:

- **Detector Name**: Type of secret detected
- **Verification Status**: Whether the secret is verified as active
- **Line Number**: Location in the source file
- **Redacted Value**: Safe preview of the detected secret
- **Raw JSON**: Complete detection metadata

## Security Considerations

- **Bot Tokens**: Keep your bot tokens secure and never commit them
- **Access Control**: Use `ALLOWED_USER_IDS` in production environments
- **File Cleanup**: Temporary files are automatically cleaned up
- **Rate Limiting**: Consider implementing rate limits for public bots
- **Logging**: Monitor bot usage and scan results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/yourusername/js-ninja.git
cd js-ninja
# Set up each component as needed
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - The powerful secret scanning engine
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper

## Support

If you encounter any issues or have questions:

1. Check the documentation in each component's folder
2. Search existing issues on GitHub
3. Create a new issue with detailed information

**Disclaimer**: This tool is for educational and authorized security testing purposes only. Always ensure you have permission before scanning any systems or files that don't belong to you.


   - Use environment variables for sensitive configuration
   - Review code for hardcoded credentials before pushing
