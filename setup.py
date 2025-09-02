from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jsninja-scanner",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive JavaScript security scanner for detecting secrets and sensitive information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jsninja",
    packages=find_packages(include=['jsninja', 'jsninja.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.1",
        "trufflehog>=3.0.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "aiofiles>=0.8.0",
        "jinja2>=3.0.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
    ],
    entry_points={
        "console_scripts": [
            "jsninja=jsninja.cli.jsninja:main",
            "jsninja-web=jsninja.web.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jsninja": [
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
            "web/static/img/*.svg",
        ],
    },
)