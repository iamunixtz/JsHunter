from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys
import subprocess

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        self.post_install()

    def post_install(self):
        """Post-installation script to ensure PATH is set correctly."""
        try:
            # Run the post-install script
            script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'post_install.py')
            if os.path.exists(script_path):
                subprocess.run([sys.executable, script_path], check=False)
            else:
                # Fallback to basic setup
                self.basic_post_install()
        except Exception as e:
            print(f"⚠️  Post-install script failed: {e}")
            self.basic_post_install()
    
    def basic_post_install(self):
        """Basic post-installation information."""
        user_bin = os.path.expanduser("~/.local/bin")
        jshunter_path = os.path.join(user_bin, "jshunter")
        
        print(f"\n" + "="*60)
        print(f"🎉 JSHunter v2.0.1 installed successfully!")
        print(f"="*60)
        
        if os.path.exists(jshunter_path):
            print(f"📁 Executable location: {jshunter_path}")
            print(f"\n🔧 To use 'jshunter' command, add this to your shell profile:")
            print(f"   export PATH=\"$HOME/.local/bin:$PATH\"")
            print(f"\n📝 Quick setup commands:")
            print(f"   echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.bashrc")
            print(f"   source ~/.bashrc")
            print(f"\n🚀 Then you can use: jshunter --help")
        else:
            print(f"⚠️  JSHunter installed but executable not found in {user_bin}")
            print(f"💡 Try running: python3 -m jshunter --help")
        
        print(f"\n📚 Documentation: https://github.com/iamunixtz/JsHunter")
        print(f"🐍 PyPI Package: https://pypi.org/project/jshunter/")
        print(f"="*60)

setup(
    name="jshunter",
    version="2.0.1",
    author="iamunixtz",
    author_email="iamunixtz@example.com",
    description="High-Performance JavaScript Security Scanner - Process 1M URLs in ~5 hours with advanced parallel processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamunixtz/JsHunter",
    packages=find_packages(),
    keywords="security, javascript, scanner, trufflehog, secrets, api-keys, penetration-testing, bug-bounty",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.1",
        "aiohttp>=3.8.0",
        "aiofiles>=23.0.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
    ],
    entry_points={
        "console_scripts": [
            "jshunter=jshunter.cli.jshunter:main",
            "jshunter-web=jshunter.web.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jshunter": [
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
            "web/static/img/*.svg",
        ],
    },
    data_files=[
        ("scripts", ["scripts/post_install.py"]),
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
)