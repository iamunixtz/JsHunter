# JS Ninja CLI Tool

Command-line interface for scanning JavaScript files from URLs for potential secrets and sensitive information.

## Features

- Scan JavaScript files from URLs
- Batch processing from URL lists
- SSL certificate bypass option
- Discord webhook integration
- JSON result export
- Automatic TruffleHog installation

## Installation

```bash
pip install -r requirements.txt
python jsninja.py --setup  # Install TruffleHog
```
## Usage

### Basic Scanning

```bash
# Scan a single JavaScript URL
python jsninja.py -u "https://example.com/app.js"

# Scan multiple URLs from a file
python jsninja.py -f urls.txt
```

### Advanced Options

```bash
# Ignore SSL certificate errors
python jsninja.py -u "https://example.com/app.js" --ignore-ssl

# Send results to Discord webhook
python jsninja.py -u "https://example.com/app.js" --discord-webhook "your-webhook-url"

# Export results to JSON file
python jsninja.py -u "https://example.com/app.js" --output results.json

# Install/update TruffleHog
python jsninja.py --setup
```
```

### URL File Format

Create a text file with one URL per line:

```
https://example.com/js/app.js
https://another-site.com/bundle.js
https://cdn.example.com/library.min.js
```

## Command Line Arguments

- `-u, --url`: Single JavaScript URL to scan
- `-f, --file`: Path to file containing URLs (one per line)
- `--ignore-ssl`: Ignore SSL certificate errors
- `--setup`: Download and install TruffleHog
- `--discord-webhook`: Discord webhook URL for notifications

## Output

The tool creates several output files:

- `downloaded_js/`: Downloaded JavaScript files
- `results/`: JSON scan results
- `.bin/`: TruffleHog binary (auto-installed)

### Result Format

Each scan produces:

1. **Console Output**: Summary of findings
2. **JSON File**: Detailed results in `results/` directory

Example console output:
```
[+] Secrets found in https://example.com/app.js:
 [AWS] AKIA... (verified=True, line=42)
 [GitHub] ghp_... (verified=False, line=156)
```

## Configuration

### Environment Variables

- `TRUFFLEHOG_PATH`: Custom path to TruffleHog binary

### Supported File Types

- `.js` - JavaScript
- `.jsx` - React JSX
- `.ts` - TypeScript
- `.tsx` - TypeScript JSX

## Use Cases

- **Bug Bounty Hunting**: Scan target applications for exposed secrets
- **Security Audits**: Automated scanning of web applications
- **CI/CD Integration**: Include in security pipelines
- **Penetration Testing**: Quick reconnaissance of JavaScript assets

## Troubleshooting

### TruffleHog Issues

```bash
# Reinstall TruffleHog
python jsninja.py --setup

# Check if TruffleHog is working
.bin/trufflehog --help
```

### SSL Certificate Errors

```bash
# Bypass SSL verification (use with caution)
python jsninja.py -u "https://example.com/app.js" --ignore-ssl
```

### Permission Errors

Ensure you have write permissions in the current directory for:
- `.bin/` (TruffleHog installation)
- `downloaded_js/` (temporary files)
- `results/` (scan results)

## Security Notes

- Downloaded files are stored temporarily and should be cleaned up
- Use `--ignore-ssl` only when necessary and with trusted sources
- Scan results may contain sensitive information - handle appropriately
- Always ensure you have permission to scan the target URLs