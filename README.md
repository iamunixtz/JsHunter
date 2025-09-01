# JS Ninja - JavaScript Security Scanner Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TruffleHog](https://img.shields.io/badge/powered%20by-TruffleHog-green.svg)](https://github.com/trufflesecurity/trufflehog)

JS Ninja is a comprehensive security scanner suite designed to detect secrets, API keys, and sensitive information in JavaScript files. It provides three different interfaces to suit various workflows and integration needs.

## Features

- **Advanced Secret Detection**: Powered by TruffleHog's robust detection engine
- **Multi-Format Support**: Supports `.js`, `.jsx`, `.ts`, `.tsx` files
- **Multiple Interfaces**: CLI, Telegram Bot, and Discord Bot
- **Auto-Installation**: Automatic TruffleHog setup and management
- **Detailed Reports**: JSON output with verification status and line numbers
- **Access Control**: User authorization for bot versions
- **Zero False Positives**: Advanced filtering and verification

## Project Structure

```
js-ninja/
├── cli/                    # Command Line Interface
│   ├── jsninja.py         # Main CLI application
│   └── requirements.txt   # CLI dependencies
├── telegram-bot/          # Telegram Bot Interface
│   ├── jsninja_bot.py    # Telegram bot implementation
│   ├── config.py         # Bot configuration
│   └── requirements.txt  # Telegram bot dependencies
├── discord-bot/           # Discord Bot Interface
│   ├── jsninja_discord.py # Discord bot implementation
│   ├── config.py         # Bot configuration
│   └── requirements.txt  # Discord bot dependencies
└── README.md             # This file
```

## Tool Descriptions

### 1. CLI Tool (`cli/jsninja.py`)

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
- Internet connection (for TruffleHog download)

### CLI Tool Setup

```bash
cd cli/
pip install -r requirements.txt
python jsninja.py --setup  # Install TruffleHog
```

### Telegram Bot Setup

1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Configure the bot:

```bash
cd telegram-bot/
pip install -r requirements.txt
# Edit config.py and set your bot token
python jsninja_bot.py
```

### Discord Bot Setup

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a bot and get the token
3. Configure the bot:

```bash
cd discord-bot/
pip install -r requirements.txt
# Edit config.py and set your bot token
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
3. Upload a JavaScript file
4. Receive scan results instantly

### Discord Bot Usage

```
!help          # Show available commands
!status        # Check bot status
!scan          # Attach a file and use this command
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
