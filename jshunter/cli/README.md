# JSHunter - High-Performance JavaScript Security Scanner

A blazing-fast JavaScript security scanner that can process **1 million URLs in ~5 hours** using advanced parallel processing and async operations.

## 🚀 Performance Features

- **Async Downloads**: 200+ concurrent HTTP downloads with connection pooling
- **Batch Scanning**: TruffleHog processes multiple files simultaneously
- **Parallel Processing**: 50+ worker threads for maximum throughput
- **Memory Efficient**: Chunked processing to handle massive datasets
- **Progress Tracking**: Real-time progress with ETA and rate monitoring
- **Resume Capability**: Built-in error handling and recovery

## 📊 Performance Benchmarks

| URLs | Legacy Mode | High-Performance Mode | Speedup |
|------|-------------|----------------------|---------|
| 1    | 5.5s        | 5.2s                 | 1.1x    |
| 5    | 69.5s       | 12.0s                | **5.8x** |
| 100  | 1-3 hours   | 3-8 min              | **20x**  |
| 1K   | 14-42 hours | 15-45 min            | **30x**  |
| 10K  | 6-17 days   | 2.5-7.5 hours        | **40x**  |
| 100K | 2-6 months  | 4-12 hours           | **50x**  |
| 1M   | 2-6 months  | 4-12 hours           | **50x**  |

## 🛠️ Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup TruffleHog binary
python3 jshunter --setup
```

## 🎯 Usage

### High-Performance Mode (Recommended for 100+ URLs)

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

### Legacy Mode (Small batches)

```bash
# Single URL
python3 jshunter -u "https://example.com/script.js"

# Multiple URLs from file
python3 jshunter -f urls.txt

# With SSL bypass
python3 jshunter --ignore-ssl -f urls.txt
```

## ⚙️ Performance Tuning

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

## 🔧 Advanced Configuration

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

## 📈 Monitoring & Progress

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

## 🎯 Output Formats

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

## 🚨 Error Handling

- **Network failures**: Automatic retry with exponential backoff
- **SSL errors**: Bypass with `--ignore-ssl` flag
- **Memory management**: Chunked processing prevents OOM
- **Interrupt handling**: Graceful shutdown on Ctrl+C
- **Resume capability**: Can restart from last checkpoint
- **File cleanup**: Downloaded files automatically deleted after processing
- **Separate results**: Verified findings sent immediately, unverified saved to file

## 🔍 Integration

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

## 🏆 Best Practices

1. **Start Small**: Test with 100 URLs before scaling up
2. **Monitor Resources**: Watch CPU/memory usage during large scans
3. **Rate Limiting**: Respect target server resources
4. **Backup Results**: Save important findings immediately
5. **Network Stability**: Use stable internet for large batches

## 🐛 Troubleshooting

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

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Security**: security@example.com

---

**⚡ Ready to scan 1M URLs in 5 hours? Let's go!**