#!/bin/bash
# JSHunter PATH Setup Script
# Run this script after installing JSHunter to automatically configure your PATH

echo "🔧 JSHunter PATH Setup Script"
echo "=============================="

# Determine shell profile
if [ -n "$ZSH_VERSION" ]; then
    PROFILE="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    PROFILE="$HOME/.bashrc"
else
    PROFILE="$HOME/.profile"
fi

echo "📁 Using profile: $PROFILE"

# Check if PATH export already exists
PATH_EXPORT='export PATH="$HOME/.local/bin:$PATH"'

if [ -f "$PROFILE" ] && grep -q "$PATH_EXPORT" "$PROFILE"; then
    echo "✅ PATH already configured in $PROFILE"
else
    echo "🔧 Adding JSHunter to PATH..."
    echo "" >> "$PROFILE"
    echo "# JSHunter PATH configuration" >> "$PROFILE"
    echo "$PATH_EXPORT" >> "$PROFILE"
    echo "✅ Added to $PROFILE"
fi

# Check if jshunter executable exists
JSHUNTER_PATH="$HOME/.local/bin/jshunter"

if [ -f "$JSHUNTER_PATH" ]; then
    echo "✅ JSHunter executable found: $JSHUNTER_PATH"
    
    # Make it executable
    chmod +x "$JSHUNTER_PATH"
    
    # Test the command
    echo "🧪 Testing JSHunter..."
    if "$JSHUNTER_PATH" --version >/dev/null 2>&1; then
        echo "✅ JSHunter is working correctly!"
        echo ""
        echo "🚀 You can now use:"
        echo "   jshunter --help"
        echo "   jshunter --version"
    else
        echo "⚠️  JSHunter executable found but not working properly"
        echo "💡 Try running: python3 -m jshunter --help"
    fi
else
    echo "❌ JSHunter executable not found in ~/.local/bin/"
    echo "💡 Try running: python3 -m jshunter --help"
fi

echo ""
echo "📝 To apply changes, run:"
echo "   source $PROFILE"
echo ""
echo "📚 Documentation: https://github.com/iamunixtz/JsHunter"
echo "🐍 PyPI Package: https://pypi.org/project/jshunter/"
echo "=============================="
