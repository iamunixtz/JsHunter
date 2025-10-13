from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jshunter",
    version="2.0.0",
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
)