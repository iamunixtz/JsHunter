# JSHunter - High-Performance JavaScript Security Scanner

A blazing-fast JavaScript security scanner that can process **1 million URLs in ~5 hours** using advanced parallel processing and async operations.

## Performance Features

- **Async Downloads**: 200+ concurrent HTTP downloads with connection pooling
- **Batch Scanning**: TruffleHog processes multiple files simultaneously
- **Parallel Processing**: 50+ worker threads for maximum throughput
- **Memory Efficient**: Chunked processing to handle massive datasets
- **Progress Tracking**: Real-time progress with ETA and rate monitoring
- **Resume Capability**: Built-in error handling and recovery

## JSHunter Workflow

```mermaid
graph TB
    %% User Input Layer
    A[User Input] --> B{Input Type}
    B -->|CLI| C[Command Line Interface]
    B -->|Telegram| D[Telegram Bot]
    B -->|Discord| E[Discord Bot]
    B -->|Web GUI| F[Web Interface]
    
    %% Configuration Layer
    G[Configuration] --> H[Bot Tokens]
    G --> I[Performance Settings]
    G --> J[Discord Webhook]
    
    %% Core Processing Layer
    C --> K[JSHunter Core Engine]
    D --> K
    E --> K
    F --> K
    
    %% High-Performance Processing
    K --> L{Performance Mode}
    L -->|High-Performance| M[Async Download Manager]
    L -->|Legacy| N[Sequential Processing]
    
    %% Download & Processing
    M --> O[Concurrent Downloads<br/>200+ simultaneous]
    O --> P[Batch File Processing]
    P --> Q[TruffleHog Scanner<br/>Parallel Execution]
    
    %% Secret Detection
    Q --> R[Secret Detection Engine]
    R --> S{Secret Found?}
    S -->|Yes| T[Verify Secret]
    S -->|No| U[Continue Processing]
    
    %% Verification & Classification
    T --> V{Verification Status}
    V -->|Verified| W[High-Confidence Secret]
    V -->|Unverified| X[Potential Secret]
    
    %% Result Processing
    W --> Y[Result Aggregation]
    X --> Y
    U --> Y
    
    %% Output Generation
    Y --> Z[Generate Results]
    Z --> AA[Verified Results JSON]
    Z --> BB[Unverified Results JSON]
    Z --> CC[Formatted Messages]
    
    %% Notification Layer
    AA --> DD{Notification Type}
    BB --> DD
    CC --> DD
    
    DD -->|Discord| EE[Discord Webhook<br/>Immediate Alerts]
    DD -->|Telegram| FF[Telegram Messages<br/>File Attachments]
    DD -->|CLI| GG[Console Output<br/>Progress Tracking]
    DD -->|Web| HH[Web Dashboard<br/>Real-time Updates]
    
    %% File Management
    EE --> II[File Cleanup]
    FF --> II
    GG --> II
    HH --> II
    
    %% Performance Monitoring
    K --> JJ[Progress Tracker]
    JJ --> KK[Real-time Stats<br/>ETA Calculation<br/>Rate Monitoring]
    
    %% Error Handling
    M --> LL[Error Recovery]
    N --> LL
    LL --> MM[Retry Logic<br/>Fallback Processing]
    
    %% Styling
    classDef userInput fill:#e1f5fe
    classDef processing fill:#f3e5f5
    classDef output fill:#e8f5e8
    classDef notification fill:#fff3e0
    classDef performance fill:#fce4ec
    
    class A,B,C,D,E,F userInput
    class K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,AA,BB,CC processing
    class DD,EE,FF,GG,HH output
    class II,LL,MM notification
    class JJ,KK performance
```

## Performance Benchmarks

| URLs | Legacy Mode | High-Performance Mode | Speedup |
|------|-------------|----------------------|---------|
| 100  | 5-15 min    | 30-60 sec           | 10x     |
| 1K   | 1-3 hours   | 3-8 min             | 20x     |
| 10K  | 14-42 hours | 15-45 min           | 30x     |
| 100K | 6-17 days   | 2.5-7.5 hours       | 40x     |
| 1M   | 2-6 months  | 4-12 hours          | 50x     |

## Installation

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/iamunixtz/JsHunter.git
cd JsHunter

# Install dependencies
pip install -r requirements.txt

# Setup TruffleHog binary
python3 jshunter --setup
```

### Bot Configuration

#### Telegram Bot Setup

1. **Create a Telegram Bot:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command and follow instructions
   - Save the bot token

2. **Get Your Chat ID:**
   - Message [@userinfobot](https://t.me/userinfobot) to get your chat ID

3. **Configure the Bot:**
   ```bash
   cd JsHunter/telegram-bot
   cp config.example.py config.py
   # Edit config.py with your bot token and chat ID
   ```

#### Discord Bot Setup

1. **Create a Discord Application:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to "Bot" section and click "Add Bot"
   - Copy the bot token

2. **Set Bot Permissions:**
   - Go to "OAuth2" → "URL Generator"
   - Select "bot" scope
   - Select permissions: Send Messages, Attach Files, Read Message History
   - Use the generated URL to invite bot to your server

3. **Configure the Bot:**
   ```bash
   cd JsHunter/discord-bot
   cp config.example.py config.py
   # Edit config.py with your bot token
   ```

4. **Optional - Discord Webhook:**
   - Create a webhook in your Discord channel
   - Add the webhook URL to config.py for additional notifications

## Usage

### CLI Usage

#### High-Performance Mode (Recommended for 100+ URLs)

```bash
# Basic high-performance scan
python3 jshunter --high-performance -f urls.txt

# Custom performance tuning
python3 jshunter --high-performance \
  --max-workers 100 \
  --concurrent-downloads 500 \
  --batch-size 200 \
  -f urls.txt

# With Discord notifications
python3 jshunter --high-performance \
  --discord-webhook "https://discord.com/api/webhooks/..." \
  -f urls.txt
```

### Bot Usage

#### Telegram Bot Commands

```bash
# Start the Telegram bot
cd JsHunter/telegram-bot
python3 jshunter_bot.py
```

**Available Commands:**
- `/start` - Welcome message and bot info
- `/help` - Show all available commands
- `/status` - Check bot status and capabilities
- `/scanurl <URL>` - Scan a JavaScript URL
- `/batch` - Upload a file with multiple URLs to scan
- Send any `.js` file directly to scan it

#### Discord Bot Commands

```bash
# Start the Discord bot
cd JsHunter/discord-bot
python3 jshunter_discord.py
```

**Available Commands:**
- `!status` - Check bot status and capabilities
- `!jshunter_help` - Show all available commands
- `!scanurl <URL>` - Scan a JavaScript URL
- `!scan` - Upload a file to scan (reply to a message with file attachment)

#### Webhook Scanner

```bash
# Use webhook scanner for simple notifications
cd JsHunter/discord-bot
python3 jshunter_webhook.py "https://example.com/script.js"
```

### Legacy Mode (Small batches)

```bash
# Single URL
python3 jshunter -u "https://example.com/script.js"

# Multiple URLs from file
python3 jshunter -f urls.txt

# With SSL bypass
python3 jshunter --ignore-ssl -f urls.txt
```

## Performance Tuning

### Recommended Settings by Scale

**Small (100-1K URLs):**
```bash
--max-workers 20 --concurrent-downloads 50 --batch-size 25
```

**Medium (1K-10K URLs):**
```bash
--max-workers 50 --concurrent-downloads 200 --batch-size 100
```

**Large (10K-100K URLs):**
```bash
--max-workers 100 --concurrent-downloads 500 --batch-size 200
```

**Massive (100K+ URLs):**
```bash
--max-workers 200 --concurrent-downloads 1000 --batch-size 500
```

### System Requirements

- **CPU**: 4+ cores recommended (8+ for massive scans)
- **RAM**: 4GB minimum (8GB+ for large batches)
- **Network**: Stable internet connection
- **Disk**: 1GB+ free space for downloads

## Advanced Configuration

### Environment Variables

```bash
export TRUFFLEHOG_PATH="/path/to/trufflehog"  # Custom TruffleHog binary
```

### Command Line Options

```
--high-performance     Enable parallel processing mode
--max-workers N        Number of worker threads (default: 50)
--concurrent-downloads N  Max concurrent downloads (default: 200)
--batch-size N         TruffleHog batch size (default: 100)
--connection-limit N   HTTP connection limit (default: 100)
--ignore-ssl          Bypass SSL certificate errors
--discord-webhook URL Send findings to Discord
--output FILE         Save results to specific file
```

## Monitoring & Progress

The tool provides real-time progress tracking with verified/unverified counts:

```
[PROGRESS] 5000/10000 (50.0%) | Rate: 55.2/s | ETA: 1.5m | Success: 4850 | Failed: 150 | Verified: 25 | Unverified: 180
```

### Final Summary
```
[+] Scan Summary:
    Total URLs: 10000
    Successful scans: 9500
    Failed scans: 500
    Verified findings: 45
    Unverified findings: 320
    Total findings: 365
```

## Output Formats

### Separate Verified/Unverified Files
The tool now automatically separates results into different files:

- **`verified_results_TIMESTAMP.json`** - Only verified findings (sent immediately to Discord)
- **`unverified_results_TIMESTAMP.json`** - Only unverified findings (saved after scan completes)
- **`combined_results.json`** - All findings together (if using `--output`)

### JSON Results
```json
{
  "DetectorName": "GitHub",
  "Verified": true,
  "Raw": "ghp_xxxxxxxxxxxxxxxxxxxx",
  "source_url": "https://example.com/script.js",
  "SourceMetadata": {
    "Data": {
      "Filesystem": {
        "file": "/path/to/file.js",
        "line": 42
      }
    }
  }
}
```

### Discord Notifications
**Verified findings are sent immediately as they are found:**
```
🔍 **Verified Secrets found in https://example.com/script.js**
**[GitHub]** `ghp_xxxxxxxxxxxxxxxxxxxx` ✅ Verified
**[AWS]** `AKIAIOSFODNN7EXAMPLE` ✅ Verified
```

**Unverified findings are saved to file after scan completion.**

## Error Handling

- **Network failures**: Automatic retry with exponential backoff
- **SSL errors**: Bypass with `--ignore-ssl` flag
- **Memory management**: Chunked processing prevents OOM
- **Interrupt handling**: Graceful shutdown on Ctrl+C
- **Resume capability**: Can restart from last checkpoint
- **File cleanup**: Downloaded files automatically deleted after processing
- **Separate results**: Verified findings sent immediately, unverified saved to file

## Integration

### With Other Tools

```bash
# From rezon (silent mode)
rezon | python3 jshunter --high-performance

# From subfinder
subfinder -d example.com | python3 jshunter --high-performance
```

### API Integration

```python
import asyncio
from jshunter import process_urls_high_performance

async def scan_urls(urls):
    results = await process_urls_high_performance(
        urls=urls,
        tr_bin="/path/to/trufflehog",
        max_concurrent_downloads=200,
        batch_size=100
    )
    return results
```

## Best Practices

1. **Start Small**: Test with 100 URLs before scaling up
2. **Monitor Resources**: Watch CPU/memory usage during large scans
3. **Rate Limiting**: Respect target server resources
4. **Backup Results**: Save important findings immediately
5. **Network Stability**: Use stable internet for large batches

## Troubleshooting

### Common Issues

**"Too many open files"**
```bash
ulimit -n 65536  # Increase file descriptor limit
```

**"Connection refused"**
```bash
--concurrent-downloads 50  # Reduce concurrent connections
```

**"Out of memory"**
```bash
--batch-size 25  # Reduce batch size
```

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Security**: security@example.com

---

**Ready to scan 1M URLs in 5 hours? Let's go!**