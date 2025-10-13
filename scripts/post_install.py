#!/usr/bin/env python3
"""
Post-installation script for JSHunter
Automatically configures PATH and provides setup instructions
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def get_shell_profile():
    """Determine the user's shell profile file."""
    shell = os.environ.get('SHELL', '/bin/bash')
    
    if 'zsh' in shell:
        return os.path.expanduser('~/.zshrc')
    elif 'bash' in shell:
        return os.path.expanduser('~/.bashrc')
    else:
        return os.path.expanduser('~/.profile')

def add_to_path():
    """Add ~/.local/bin to PATH if not already present."""
    profile_file = get_shell_profile()
    path_export = 'export PATH="$HOME/.local/bin:$PATH"'
    
    # Check if PATH export already exists
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            content = f.read()
            if path_export in content:
                return True, "PATH already configured"
    
    # Add PATH export to profile
    try:
        with open(profile_file, 'a') as f:
            f.write(f'\n# JSHunter PATH configuration\n{path_export}\n')
        return True, f"Added to {profile_file}"
    except Exception as e:
        return False, f"Failed to write to {profile_file}: {e}"

def check_executable():
    """Check if jshunter executable exists and is accessible."""
    user_bin = os.path.expanduser("~/.local/bin")
    jshunter_path = os.path.join(user_bin, "jshunter")
    
    if os.path.exists(jshunter_path):
        # Check if it's executable
        if os.access(jshunter_path, os.X_OK):
            return True, jshunter_path
        else:
            # Make it executable
            os.chmod(jshunter_path, 0o755)
            return True, jshunter_path
    return False, None

def main():
    """Main post-installation routine."""
    print("\n" + "="*70)
    print("🎉 JSHunter v2.0.1 Post-Installation Setup")
    print("="*70)
    
    # Check executable
    exec_exists, exec_path = check_executable()
    
    if exec_exists:
        print(f"✅ Executable found: {exec_path}")
        
        # Try to add to PATH
        success, message = add_to_path()
        if success:
            print(f"✅ PATH configuration: {message}")
        else:
            print(f"⚠️  PATH configuration: {message}")
        
        print(f"\n🚀 Setup complete! You can now use:")
        print(f"   jshunter --help")
        print(f"   jshunter --version")
        
        # Test the command
        try:
            result = subprocess.run([exec_path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"\n✅ Test successful: {result.stdout.strip()}")
            else:
                print(f"\n⚠️  Test failed: {result.stderr}")
        except Exception as e:
            print(f"\n⚠️  Could not test executable: {e}")
            
    else:
        print("❌ JSHunter executable not found in ~/.local/bin/")
        print("💡 Try running: python3 -m jshunter --help")
    
    print(f"\n📚 Documentation: https://github.com/iamunixtz/JsHunter")
    print(f"🐍 PyPI Package: https://pypi.org/project/jshunter/")
    print("="*70)

if __name__ == "__main__":
    main()
