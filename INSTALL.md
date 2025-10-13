# JSHunter Installation Guide

## Quick Installation

```bash
pip install jshunter
```

## Post-Installation Setup

After installing JSHunter, you need to ensure the `jshunter` command is available in your PATH.

### Option 1: Automatic PATH Setup (Recommended)

Run the setup script that comes with JSHunter:

```bash
# Find and run the post-install script
python3 -c "
import os
import subprocess
import sys

# Find the post-install script
script_path = None
for path in sys.path:
    potential_path = os.path.join(path, 'jshunter-2.0.1.data', 'data', 'scripts', 'post_install.py')
    if os.path.exists(potential_path):
        script_path = potential_path
        break

if script_path:
    subprocess.run([sys.executable, script_path])
else:
    print('Post-install script not found. Please use manual setup.')
"
```

### Option 2: Manual PATH Setup

Add JSHunter to your PATH by adding this line to your shell profile:

**For Bash:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**For Zsh:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**For Fish:**
```bash
echo 'set -gx PATH $HOME/.local/bin $PATH' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

### Option 3: Use Python Module

If you prefer not to modify your PATH, you can run JSHunter as a Python module:

```bash
python3 -m jshunter --help
python3 -m jshunter --version
```

## Verification

After setup, verify the installation:

```bash
jshunter --version
jshunter --help
```

You should see:
```
JSHunter 2.0.1
```

## Troubleshooting

### Command Not Found

If you get `jshunter: command not found`:

1. **Check if executable exists:**
   ```bash
   find ~/.local -name "jshunter" -type f 2>/dev/null
   ```

2. **Check your PATH:**
   ```bash
   echo $PATH
   ```

3. **Add to PATH manually:**
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

### Permission Issues

If you get permission errors:

```bash
# Make executable
chmod +x ~/.local/bin/jshunter
```

### Alternative Installation Methods

**System-wide installation (requires sudo):**
```bash
sudo pip install jshunter
```

**Virtual environment:**
```bash
python3 -m venv jshunter-env
source jshunter-env/bin/activate
pip install jshunter
```

## Features

- **High-Performance Scanning**: Process 1M URLs in ~5 hours
- **Parallel Processing**: Concurrent downloads and scanning
- **Discord Integration**: Real-time notifications
- **Multiple Output Formats**: JSON, console, file exports
- **Auto-cleanup**: Temporary file management
- **Cross-platform**: Works on Linux, macOS, Windows

## Getting Started

```bash
# Scan a single URL
jshunter -u https://example.com/script.js

# Scan multiple URLs from file
jshunter -f urls.txt

# High-performance mode
jshunter -f urls.txt --high-performance

# With Discord notifications
jshunter -f urls.txt --discord-webhook "YOUR_WEBHOOK_URL"
```

## Support

- **Documentation**: https://github.com/iamunixtz/JsHunter
- **PyPI Package**: https://pypi.org/project/jshunter/
- **Issues**: https://github.com/iamunixtz/JsHunter/issues
