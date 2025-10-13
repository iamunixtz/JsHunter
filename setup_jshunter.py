#!/usr/bin/env python3
"""
JSHunter Setup Script
Run this script after installing JSHunter to configure your environment
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

def check_jshunter_installed():
    """Check if JSHunter is installed and where."""
    try:
        result = subprocess.run([sys.executable, '-c', 'import jshunter; print(jshunter.__file__)'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
    except:
        pass
    return False, None

def find_jshunter_executable():
    """Find the JSHunter executable."""
    possible_paths = [
        os.path.expanduser('~/.local/bin/jshunter'),
        '/usr/local/bin/jshunter',
        '/usr/bin/jshunter',
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    # Try to find it in PATH
    try:
        result = subprocess.run(['which', 'jshunter'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

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

def test_jshunter():
    """Test if JSHunter command works."""
    try:
        result = subprocess.run(['jshunter', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def main():
    """Main setup routine."""
    print("🔧 JSHunter Setup Script")
    print("=" * 50)
    
    # Check if JSHunter is installed
    installed, location = check_jshunter_installed()
    if not installed:
        print("❌ JSHunter is not installed!")
        print("💡 Install it with: pip install jshunter")
        return
    
    print(f"✅ JSHunter is installed at: {location}")
    
    # Find executable
    exec_path = find_jshunter_executable()
    if exec_path:
        print(f"✅ JSHunter executable found: {exec_path}")
    else:
        print("⚠️  JSHunter executable not found in PATH")
    
    # Test command
    works, output = test_jshunter()
    if works:
        print(f"✅ JSHunter command works: {output}")
        print("\n🎉 Setup complete! You can now use:")
        print("   jshunter --help")
        print("   jshunter --version")
    else:
        print(f"⚠️  JSHunter command not working: {output}")
        
        # Try to fix PATH
        print("\n🔧 Attempting to fix PATH...")
        success, message = add_to_path()
        if success:
            print(f"✅ {message}")
            print(f"\n📝 To apply changes, run:")
            print(f"   source {get_shell_profile()}")
            print(f"\n🚀 Then try: jshunter --version")
        else:
            print(f"❌ {message}")
            print(f"\n💡 Manual setup:")
            print(f"   echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.bashrc")
            print(f"   source ~/.bashrc")
    
    print(f"\n📚 Documentation: https://github.com/iamunixtz/JsHunter")
    print(f"🐍 PyPI Package: https://pypi.org/project/jshunter/")
    print("=" * 50)

if __name__ == "__main__":
    main()
