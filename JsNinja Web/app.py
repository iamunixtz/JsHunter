#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import re
import json
import os
import uuid
from urllib.parse import urlparse, urljoin
import jsbeautifier
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import logging
import hashlib
import time
import urllib3
import threading
import schedule
import csv
import io
import difflib
from typing import Dict, List, Optional
import random

# Disable SSL warnings if needed (better to fix SSL issues properly)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'rezon-default-secret-key-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rezon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['EXPORT_FOLDER'] = 'exports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['EXPORT_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

db = SQLAlchemy(app)

# --- Logging Configuration ---
log_file_path = 'rezon.log'
logging.basicConfig(
    filename=log_file_path, 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
app.logger.addHandler(console_handler)

# --- Authentication Configuration ---
ADMIN_USERNAME = os.environ.get('JSNINJA_ADMIN_USERNAME', 'rezon')
ADMIN_PASSWORD_HASH = os.environ.get('JSNINJA_ADMIN_PASSWORD_HASH', generate_password_hash('rezon'))

# --- User Agents Pool ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
]

# Simple in-memory rate limiting for login attempts
LOGIN_ATTEMPTS = {}
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300 # 5 minutes

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Database Models ---
class Project(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    scans = db.relationship('Scan', backref='project', lazy=True, cascade='all, delete-orphan')
    monitors = db.relationship('JSMonitor', backref='project', lazy=True, cascade='all, delete-orphan')

class Scan(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    url = db.Column(db.String(500))
    filename = db.Column(db.String(200))
    scan_type = db.Column(db.String(20), nullable=False)  # 'url', 'file', 'code', 'bulk_urls'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    total_secrets = db.Column(db.Integer, default=0)
    total_urls = db.Column(db.Integer, default=0)
    total_api_endpoints = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime)
    secrets = db.relationship('Secret', backref='scan', lazy=True, cascade='all, delete-orphan')
    urls = db.relationship('ExtractedUrl', backref='scan', lazy=True, cascade='all, delete-orphan')
    api_endpoints = db.relationship('ApiEndpoint', backref='scan', lazy=True, cascade='all, delete-orphan')

class Secret(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = db.Column(db.String(36), db.ForeignKey('scan.id'), nullable=False)
    secret_type = db.Column(db.String(100), nullable=False)
    secret_value = db.Column(db.Text, nullable=False)
    line_number = db.Column(db.Integer)
    context = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')
    source_url = db.Column(db.String(500))  # For bulk URL scans
    created_at = db.Column(db.DateTime, default=datetime.now)

class ExtractedUrl(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = db.Column(db.String(36), db.ForeignKey('scan.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class ApiEndpoint(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = db.Column(db.String(36), db.ForeignKey('scan.id'), nullable=False)
    endpoint = db.Column(db.String(500), nullable=False)
    context = db.Column(db.Text)
    source_url = db.Column(db.String(500))  # For bulk URL scans
    created_at = db.Column(db.DateTime, default=datetime.now)

class JSMonitor(db.Model):
    __tablename__ = 'js_monitor'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    check_interval = db.Column(db.Integer, default=300)  # seconds
    last_check = db.Column(db.DateTime)
    last_content_hash = db.Column(db.String(64))
    status = db.Column(db.String(20), default='active')  # 'active', 'paused', 'error'
    telegram_enabled = db.Column(db.Boolean, default=False)
    discord_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    changes = db.relationship('JSChange', backref='monitor', lazy=True, cascade='all, delete-orphan')

class JSChange(db.Model):
    __tablename__ = 'js_change'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    monitor_id = db.Column(db.String(36), db.ForeignKey('js_monitor.id'), nullable=False)
    old_content_hash = db.Column(db.String(64))
    new_content_hash = db.Column(db.String(64))
    old_content = db.Column(db.Text)  # Store actual old content for diff
    new_content = db.Column(db.Text)  # Store actual new content for diff
    diff_content = db.Column(db.Text)  # Store the diff
    change_summary = db.Column(db.Text)
    detected_at = db.Column(db.DateTime, default=datetime.now)
    notified = db.Column(db.Boolean, default=False)

class NotificationSettings(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_bot_token = db.Column(db.String(200))
    telegram_chat_id = db.Column(db.String(100))
    discord_webhook_url = db.Column(db.String(500))
    scan_notifications = db.Column(db.Boolean, default=True)  # Notify on scan completion
    finding_notifications = db.Column(db.Boolean, default=True)  # Notify on findings
    monitor_notifications = db.Column(db.Boolean, default=True)  # Notify on monitor changes
    created_at = db.Column(db.DateTime, default=datetime.now)

# --- Enhanced Secret patterns ---
SECRET_PATTERNS = {
    'AWS Access Key ID': r'(?i)(?:aws.{0,20})?(?:access.{0,20}key.{0,20}id|access.key)[\'"\s]*[:=]\s*[\'"]?([A-Z0-9]{20})[\'"]?',
    'AWS Secret Access Key': r'(?i)(?:aws.{0,20})?(?:secret.{0,20}access.{0,20}key|secret.key)[\'"\s]*[:=]\s*[\'"]?([A-Za-z0-9/+=]{40})[\'"]?',
    'GitHub Token': r'(?i)(?:github.{0,20})?(?:token|pat)[\'"\s]*[:=]\s*[\'"]?(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82})[\'"]?',
    'GitHub Client Secret': r'(?i)(?:github.{0,20})?(?:client.{0,20}secret)[\'"\s]*[:=]\s*[\'"]?([A-Za-z0-9]{40})[\'"]?',
    'Google API Key': r'(?i)(?:google.{0,20})?(?:api.{0,20}key)[\'"\s]*[:=]\s*[\'"]?(AIza[A-Za-z0-9_-]{35})[\'"]?',
    'Firebase API Key': r'(?i)(?:firebase.{0,20})?(?:api.{0,20}key)[\'"\s]*[:=]\s*[\'"]?(AIza[A-Za-z0-9_-]{35})[\'"]?',
    'Stripe Live Token': r'sk_live_[A-Za-z0-9]{24}',
    'Stripe Test Token': r'(?:sk_test_|pk_test_)[A-Za-z0-9]{24}',
    'Twilio API Key': r'SK[A-Za-z0-9]{32}',
    'Twilio Account SID': r'AC[A-Za-z0-9]{32}',
    'Slack API Token': r'xox[bpars]-[A-Za-z0-9-]{10,48}',
    'Discord Bot Token': r'[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}',
    'Discord Webhook': r'https://discord(?:app)?\.com/api/webhooks/\d+/[\w-]+',
    'Telegram Bot Token': r'\d{8,10}:[A-Za-z0-9_-]{35}',
    'JWT Token': r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
    'Private Key': r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
    'SSH Private Key': r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----[\s\S]*?-----END\s+OPENSSH\s+PRIVATE\s+KEY-----',
    'Database URL': r'(mongodb|mysql|postgresql|postgres|redis):\/\/[^\s\'"]+',
    'Connection String': r'(?:Server|Data Source|Host)=[^;\'\"]+;.*(?:Password|Pwd)=[^;\'\"]+',
    'API Key': r'(?i)(?:api.{0,20}key|apikey)[\'"\s]*[:=]\s*[\'"]?([A-Za-z0-9_-]{20,})[\'"]?',
    'Secret Key': r'(?i)(?:secret.{0,20}key|secretkey)[\'"\s]*[:=]\s*[\'"]?([A-Za-z0-9_-]{20,})[\'"]?',
    'Access Token': r'(?i)(?:access.{0,20}token|accesstoken)[\'"\s]*[:=]\s*[\'"]?([A-Za-z0-9_.-]{32,})[\'"]?',
    'Bearer Token': r'Bearer\s+([A-Za-z0-9_.-]{20,})',
    'Authorization Header': r'(?i)authorization[\'"\s]*[:=]\s*[\'"]?(Bearer\s+[A-Za-z0-9_.-]{20,}|Basic\s+[A-Za-z0-9+/=]+)[\'"]?',
}

# Severity mapping
SEVERITY_MAP = {
    'AWS Access Key ID': 'critical',
    'AWS Secret Access Key': 'critical',
    'GitHub Token': 'high',
    'GitHub Client Secret': 'high',
    'Google API Key': 'high',
    'Firebase API Key': 'high',
    'Stripe Live Token': 'critical',
    'Stripe Test Token': 'medium',
    'Twilio API Key': 'high',
    'Twilio Account SID': 'medium',
    'Slack API Token': 'high',
    'Discord Bot Token': 'high',
    'Discord Webhook': 'medium',
    'Telegram Bot Token': 'high',
    'JWT Token': 'medium',
    'Private Key': 'critical',
    'SSH Private Key': 'critical',
    'Database URL': 'high',
    'Connection String': 'high',
    'API Key': 'medium',
    'Secret Key': 'high',
    'Access Token': 'medium',
    'Bearer Token': 'medium',
    'Authorization Header': 'high',
}

# API endpoint patterns
API_ENDPOINT_PATTERNS = {
    'API Endpoint': r'[\'"`]([/](?:api|rest|graphql|v\d+)[/][^\'"`\s]*)[\'"`]',
    'REST Endpoint': r'[\'"`]([/](?:users|auth|login|register|admin)[/]?[^\'"`\s]*)[\'"`]',
    'GraphQL Endpoint': r'[\'"`]([/]graphql[^\'"`\s]*)[\'"`]',
    'Webhook Endpoint': r'[\'"`]([/](?:webhook|hook|callback)[^\'"`\s]*)[\'"`]',
}

# URL patterns
URL_PATTERNS = [
    r'https?://[^\s\'"<>]+',
    r'[\'"`](https?://[^\'"`\s]+)[\'"`]',
    r'[\'"`](\/[^\'"`\s]*)[\'"`]',
]

def get_random_user_agent():
    """Get a random user agent from the pool"""
    return random.choice(USER_AGENTS)

def extract_secrets(content, line_offset=0, source_url=None):
    """Extract secrets from content using regex patterns"""
    secrets = []
    lines = content.split('\n')
    
    for pattern_name, pattern in SECRET_PATTERNS.items():
        try:
            for line_num, line in enumerate(lines, start=line_offset + 1):
                matches = re.finditer(pattern, line)
                for match in matches:
                    secret_value = match.group(1) if match.groups() else match.group(0)
                    if len(secret_value) > 8:  # Filter out very short matches
                        severity = SEVERITY_MAP.get(pattern_name, 'medium')
                        secrets.append({
                            'type': pattern_name,
                            'value': secret_value,
                            'line': line_num,
                            'context': line.strip()[:200],
                            'severity': severity,
                            'source_url': source_url
                        })
        except re.error as e:
            app.logger.warning(f"Regex error in pattern {pattern_name}: {e}")
            continue
    
    return secrets

def extract_urls(content, base_url=None):
    """Extract URLs from content with proper validation"""
    urls = set()
    
    for pattern in URL_PATTERNS:
        try:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                url = match.group(1) if match.groups() else match.group(0)
                if url and len(url) > 3:
                    url = url.strip()
                    
                    # Handle relative URLs
                    if url.startswith('/') and base_url:
                        url = urljoin(base_url, url)
                    
                    # Validate URL and filter out suspicious patterns
                    if (url.startswith(('http://', 'https://')) and 
                        '/null/null/' not in url and 
                        not url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.ico'))):
                        urls.add(url)
                        app.logger.debug(f"Extracted URL: {url}")
        except re.error as e:
            app.logger.warning(f"Regex error in URL pattern {pattern}: {e}")
            continue
    
    return list(urls)

def extract_api_endpoints(content, source_url=None):
    """Extract API endpoints from content"""
    endpoints = []
    
    for pattern_name, pattern in API_ENDPOINT_PATTERNS.items():
        try:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                endpoint = match.group(1) if match.groups() else match.group(0)
                if endpoint and len(endpoint) > 1:
                    endpoint = endpoint.strip()
                    if endpoint.startswith('/'):
                        endpoints.append({
                            'endpoint': endpoint,
                            'source_url': source_url
                        })
        except re.error as e:
            app.logger.warning(f"Regex error in API endpoint pattern {pattern_name}: {e}")
            continue
    
    return endpoints

def fetch_js_content(url, use_random_ua=True):
    """Enhanced JavaScript content fetching with rotating user agents"""
    try:
        # Enhanced headers to better mimic a real browser
        headers = {
            'User-Agent': get_random_user_agent() if use_random_ua else USER_AGENTS[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add referer if possible
        parsed_url = urlparse(url)
        if parsed_url.netloc:
            headers['Referer'] = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        
        # Create session for better connection handling
        session = requests.Session()
        session.headers.update(headers)
        
        # Try with SSL verification first
        try:
            response = session.get(url, timeout=30, verify=True)
            response.raise_for_status()
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            # Fallback to no SSL verification if needed
            app.logger.warning(f"SSL verification failed for {url}, trying without verification")
            response = session.get(url, timeout=30, verify=False)
            response.raise_for_status()
        
        # Check if content is actually JavaScript
        content_type = response.headers.get('content-type', '').lower()
        if 'javascript' not in content_type and 'text' not in content_type:
            app.logger.warning(f"URL {url} may not contain JavaScript content (Content-Type: {content_type})")
        
        content = response.text
        
        # Try to beautify JavaScript if possible
        try:
            if len(content) > 100:  # Only beautify if content is substantial
                content = jsbeautifier.beautify(content)
        except Exception as beautify_error:
            app.logger.debug(f"Could not beautify JavaScript from {url}: {beautify_error}")
            # Keep original content if beautification fails
        
        app.logger.info(f"Successfully fetched {len(content)} characters from {url}")
        return content
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            app.logger.error(f"Access forbidden (403) for {url} - server may be blocking automated requests")
        elif e.response.status_code == 404:
            app.logger.error(f"URL not found (404): {url}")
        else:
            app.logger.error(f"HTTP error {e.response.status_code} fetching {url}: {e}")
        return None
    except requests.exceptions.Timeout:
        app.logger.error(f"Timeout fetching {url}")
        return None
    except requests.exceptions.ConnectionError as e:
        app.logger.error(f"Connection error fetching {url}: {e}")
        return None
    except Exception as e:
        app.logger.error(f"Unexpected error fetching {url}: {e}")
        return None

def send_telegram_notification(message: str, bot_token: str = None, chat_id: str = None):
    """Send notification to Telegram with improved error handling"""
    try:
        # Get settings from database if not provided
        if not bot_token or not chat_id:
            settings = NotificationSettings.query.first()
            if settings:
                bot_token = bot_token or settings.telegram_bot_token
                chat_id = chat_id or settings.telegram_chat_id
        
        if not bot_token or not chat_id:
            app.logger.warning("Telegram bot token or chat ID not configured")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        app.logger.info("Telegram notification sent successfully")
        return True
        
    except requests.exceptions.HTTPError as e:
        app.logger.error(f"Telegram API error: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        app.logger.error(f"Failed to send Telegram notification: {e}")
        return False

def send_discord_notification(message: str, webhook_url: str = None):
    """Send notification to Discord with improved error handling"""
    try:
        # Get settings from database if not provided
        if not webhook_url:
            settings = NotificationSettings.query.first()
            if settings:
                webhook_url = settings.discord_webhook_url
        
        if not webhook_url:
            app.logger.warning("Discord webhook URL not configured")
            return False
        
        # Fix Discord URL if it's using the old domain
        if 'discordapp.com' in webhook_url:
            webhook_url = webhook_url.replace('discordapp.com', 'discord.com')
        
        data = {
            'content': message,
            'username': 'Rezon Scanner',
            'avatar_url': 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f6e1.png'
        }
        
        response = requests.post(webhook_url, json=data, timeout=15)
        response.raise_for_status()
        
        app.logger.info("Discord notification sent successfully")
        return True
        
    except requests.exceptions.HTTPError as e:
        app.logger.error(f"Discord webhook error: {e.response.status_code} - {e.response.text}")
        return False
    except requests.exceptions.Timeout:
        app.logger.error("Discord notification timeout")
        return False
    except Exception as e:
        app.logger.error(f"Failed to send Discord notification: {e}")
        return False

def calculate_content_hash(content: str) -> str:
    """Calculate SHA-256 hash of content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def generate_diff(old_content: str, new_content: str) -> str:
    """Generate diff between old and new content"""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        old_lines, 
        new_lines, 
        fromfile='old_version', 
        tofile='new_version',
        lineterm=''
    )
    
    return ''.join(diff)

def check_js_monitor(monitor_id: str):
    """Check a single JS monitor for changes with enhanced diff generation"""
    with app.app_context():
        try:
            monitor = db.session.get(JSMonitor, monitor_id)
            if not monitor or monitor.status != 'active':
                return
            
            # Fetch current content
            current_content = fetch_js_content(monitor.url)
            if not current_content:
                app.logger.error(f"Failed to fetch content for monitor {monitor.name}")
                monitor.status = 'error'
                db.session.commit()
                return
            
            current_hash = calculate_content_hash(current_content)
            
            # Check if content has changed
            if monitor.last_content_hash and monitor.last_content_hash != current_hash:
                # Get the last change to get old content
                last_change = JSChange.query.filter_by(monitor_id=monitor.id).order_by(JSChange.detected_at.desc()).first()
                old_content = last_change.new_content if last_change else ""
                
                # Generate proper diff
                diff_content = generate_diff(old_content, current_content)
                
                # Content has changed, create change record
                change = JSChange(
                    monitor_id=monitor.id,
                    old_content_hash=monitor.last_content_hash,
                    new_content_hash=current_hash,
                    old_content=old_content[:10000],  # Limit storage size
                    new_content=current_content[:10000],  # Limit storage size
                    diff_content=diff_content,
                    change_summary=f"JavaScript file {monitor.name} has been modified"
                )
                db.session.add(change)
                
                # Send notifications if enabled
                settings = NotificationSettings.query.first()
                if settings and settings.monitor_notifications:
                    if monitor.telegram_enabled:
                        message = f"🚨 *JavaScript Change Detected*\n\n"
                        message += f"**Monitor:** {monitor.name}\n"
                        message += f"**URL:** {monitor.url}\n"
                        message += f"**Project:** {monitor.project.name}\n"
                        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
                        message += f"**Change Summary:** Content hash changed from `{monitor.last_content_hash[:16]}...` to `{current_hash[:16]}...`"
                        
                        send_telegram_notification(message)
                    
                    if monitor.discord_enabled:
                        message = f"🚨 **JavaScript Change Detected**\n\n"
                        message += f"**Monitor:** {monitor.name}\n"
                        message += f"**URL:** {monitor.url}\n"
                        message += f"**Project:** {monitor.project.name}\n"
                        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
                        message += f"**Change Summary:** Content hash changed from `{monitor.last_content_hash[:16]}...` to `{current_hash[:16]}...`"
                        
                        send_discord_notification(message)
                    
                    change.notified = True
                
                app.logger.info(f"Change detected for monitor {monitor.name}")
            
            # Update monitor
            monitor.last_check = datetime.now()
            monitor.last_content_hash = current_hash
            db.session.commit()
            
        except Exception as e:
            app.logger.error(f"Error checking monitor {monitor_id}: {e}")

def run_js_monitors():
    """Run all active JS monitors"""
    try:
        with app.app_context():
            monitors = JSMonitor.query.filter_by(status='active').all()
            for monitor in monitors:
                # Check if it's time to check this monitor
                if (not monitor.last_check or 
                    (datetime.now() - monitor.last_check).total_seconds() >= monitor.check_interval):
                    check_js_monitor(monitor.id)
                    time.sleep(1)  # Small delay between checks
    except Exception as e:
        app.logger.error(f"Error running JS monitors: {e}")

def perform_scan(scan_id):
    """Perform the actual scanning with enhanced error handling and notifications"""
    with app.app_context():
        scan = db.session.get(Scan, scan_id)
        if not scan:
            return

        try:
            scan.status = 'running'
            db.session.commit()
            
            all_secrets = []
            all_urls = []
            all_endpoints = []
            
            if scan.scan_type == 'url':
                content = fetch_js_content(scan.url)
                if not content:
                    scan.status = 'failed'
                    db.session.commit()
                    return
                
                # Extract data from single URL
                secrets = extract_secrets(content, source_url=scan.url)
                urls = extract_urls(content, base_url=scan.url)
                endpoints = extract_api_endpoints(content, source_url=scan.url)
                
                all_secrets.extend(secrets)
                all_urls.extend(urls)
                all_endpoints.extend(endpoints)
                
            elif scan.scan_type == 'bulk_urls':
                # Handle bulk URL scanning from uploaded file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], scan.filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        urls_to_scan = [line.strip() for line in f if line.strip()]
                    
                    successful_scans = 0
                    for i, url in enumerate(urls_to_scan):
                        try:
                            app.logger.info(f"Scanning URL {i+1}/{len(urls_to_scan)}: {url}")
                            content = fetch_js_content(url)
                            if content:
                                secrets = extract_secrets(content, source_url=url)
                                urls = extract_urls(content, base_url=url)
                                endpoints = extract_api_endpoints(content, source_url=url)
                                
                                all_secrets.extend(secrets)
                                all_urls.extend(urls)
                                all_endpoints.extend(endpoints)
                                successful_scans += 1
                            
                            # Add small delay to be respectful to servers
                            time.sleep(0.5)
                            
                        except Exception as e:
                            app.logger.error(f"Error scanning URL {url}: {e}")
                            continue
                    
                    app.logger.info(f"Bulk scan completed: {successful_scans}/{len(urls_to_scan)} URLs successfully scanned")
            
            elif scan.scan_type == 'code':
                # Handle direct code input - this would need the code content passed somehow
                # For now, we'll skip this as it requires additional implementation
                pass
            
            # Save all extracted data
            for secret in all_secrets:
                secret_obj = Secret(
                    scan_id=scan.id,
                    secret_type=secret['type'],
                    secret_value=secret['value'],
                    line_number=secret['line'],
                    context=secret['context'],
                    severity=secret['severity'],
                    source_url=secret.get('source_url')
                )
                db.session.add(secret_obj)
            
            for url in all_urls:
                url_obj = ExtractedUrl(
                    scan_id=scan.id,
                    url=url
                )
                db.session.add(url_obj)
            
            for endpoint in all_endpoints:
                endpoint_obj = ApiEndpoint(
                    scan_id=scan.id,
                    endpoint=endpoint['endpoint'],
                    context=f"Found in JavaScript content",
                    source_url=endpoint.get('source_url')
                )
                db.session.add(endpoint_obj)
            
            # Update scan statistics
            scan.total_secrets = len(all_secrets)
            scan.total_urls = len(all_urls)
            scan.total_api_endpoints = len(all_endpoints)
            scan.status = 'completed'
            scan.completed_at = datetime.now()
            
            db.session.commit()
            
            # Send notifications if enabled
            settings = NotificationSettings.query.first()
            if settings:
                # Scan completion notification
                if settings.scan_notifications:
                    message = f"✅ *Scan Completed*\n\n"
                    message += f"**Project:** {scan.project.name}\n"
                    message += f"**Scan Type:** {scan.scan_type.upper()}\n"
                    message += f"**URL:** {scan.url or 'Multiple URLs'}\n"
                    message += f"**Results:** {len(all_secrets)} secrets, {len(all_urls)} URLs, {len(all_endpoints)} endpoints\n"
                    message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                    
                    send_telegram_notification(message)
                    send_discord_notification(message.replace('*', '**'))
                
                # Finding notifications for critical/high severity secrets
                if settings.finding_notifications and all_secrets:
                    critical_secrets = [s for s in all_secrets if s['severity'] == 'critical']
                    high_secrets = [s for s in all_secrets if s['severity'] == 'high']
                    
                    if critical_secrets or high_secrets:
                        message = f"🚨 *Critical Findings Detected*\n\n"
                        message += f"**Project:** {scan.project.name}\n"
                        message += f"**URL:** {scan.url or 'Multiple URLs'}\n"
                        message += f"**Critical Secrets:** {len(critical_secrets)}\n"
                        message += f"**High Severity:** {len(high_secrets)}\n"
                        message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
                        
                        # Add details for critical secrets
                        if critical_secrets:
                            message += "**Critical Secrets Found:**\n"
                            for secret in critical_secrets[:3]:  # Limit to first 3
                                message += f"• {secret['type']}: `{secret['value'][:20]}...`\n"
                            if len(critical_secrets) > 3:
                                message += f"• ... and {len(critical_secrets) - 3} more\n"
                        
                        send_telegram_notification(message)
                        send_discord_notification(message.replace('*', '**'))
            
            app.logger.info(f"Scan {scan_id} completed: {len(all_secrets)} secrets, {len(all_urls)} URLs, {len(all_endpoints)} API endpoints")
            
        except Exception as e:
            app.logger.error(f"Error during scan {scan_id}: {e}")
            scan.status = 'failed'
            db.session.commit()

# --- Export Functions ---
def export_scan_results_csv(scan_id: str) -> str:
    """Export scan results to CSV format"""
    scan = db.session.get(Scan, scan_id)
    if not scan:
        return None
    
    filename = f"scan_results_{scan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(app.config['EXPORT_FOLDER'], filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write headers
        writer.writerow(['Type', 'Secret Type', 'Secret Value', 'Severity', 'Line Number', 'Context', 'Source URL', 'Found At'])
        
        # Write secrets
        for secret in scan.secrets:
            writer.writerow([
                'Secret',
                secret.secret_type,
                secret.secret_value,
                secret.severity,
                secret.line_number or '',
                secret.context or '',
                secret.source_url or scan.url or '',
                secret.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Write URLs
        for url in scan.urls:
            writer.writerow([
                'URL',
                'Extracted URL',
                url.url,
                'info',
                '',
                '',
                scan.url or '',
                url.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Write API endpoints
        for endpoint in scan.api_endpoints:
            writer.writerow([
                'API Endpoint',
                'API Endpoint',
                endpoint.endpoint,
                'info',
                '',
                endpoint.context or '',
                endpoint.source_url or scan.url or '',
                endpoint.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    return filepath

def export_scan_results_json(scan_id: str) -> str:
    """Export scan results to JSON format"""
    scan = db.session.get(Scan, scan_id)
    if not scan:
        return None
    
    filename = f"scan_results_{scan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(app.config['EXPORT_FOLDER'], filename)
    
    data = {
        'scan_info': {
            'id': scan.id,
            'project_name': scan.project.name,
            'url': scan.url,
            'filename': scan.filename,
            'scan_type': scan.scan_type,
            'status': scan.status,
            'created_at': scan.created_at.isoformat(),
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
            'total_secrets': scan.total_secrets,
            'total_urls': scan.total_urls,
            'total_api_endpoints': scan.total_api_endpoints
        },
        'secrets': [
            {
                'id': secret.id,
                'type': secret.secret_type,
                'value': secret.secret_value,
                'severity': secret.severity,
                'line_number': secret.line_number,
                'context': secret.context,
                'source_url': secret.source_url,
                'created_at': secret.created_at.isoformat()
            }
            for secret in scan.secrets
        ],
        'urls': [
            {
                'id': url.id,
                'url': url.url,
                'created_at': url.created_at.isoformat()
            }
            for url in scan.urls
        ],
        'api_endpoints': [
            {
                'id': endpoint.id,
                'endpoint': endpoint.endpoint,
                'context': endpoint.context,
                'source_url': endpoint.source_url,
                'created_at': endpoint.created_at.isoformat()
            }
            for endpoint in scan.api_endpoints
        ]
    }
    
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    return filepath

# --- Routes (keeping existing routes and adding new ones) ---
@app.route('/')
def index():
    # Get statistics for the homepage
    total_projects = Project.query.count()
    total_scans = Scan.query.count()
    total_secrets = Secret.query.count()
    critical_secrets = Secret.query.filter_by(severity='critical').count()
    
    stats = {
        'total_projects': total_projects,
        'total_scans': total_scans,
        'total_secrets': total_secrets,
        'critical_secrets': critical_secrets
    }
    
    # Get recent projects for display
    projects = Project.query.order_by(Project.created_at.desc()).limit(6).all()
    
    return render_template('index.html', stats=stats, projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        client_ip = request.remote_addr
        
        # Check rate limiting
        if client_ip in LOGIN_ATTEMPTS:
            attempts, last_attempt = LOGIN_ATTEMPTS[client_ip]
            if attempts >= MAX_LOGIN_ATTEMPTS and time.time() - last_attempt < LOCKOUT_TIME:
                flash(f'Too many login attempts. Please try again in {int((LOCKOUT_TIME - (time.time() - last_attempt)) / 60)} minutes.', 'error')
                return render_template('login.html')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['logged_in'] = True
            # Reset login attempts on successful login
            if client_ip in LOGIN_ATTEMPTS:
                del LOGIN_ATTEMPTS[client_ip]
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Track failed login attempts
            if client_ip not in LOGIN_ATTEMPTS:
                LOGIN_ATTEMPTS[client_ip] = [1, time.time()]
            else:
                LOGIN_ATTEMPTS[client_ip][0] += 1
                LOGIN_ATTEMPTS[client_ip][1] = time.time()
            
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent scans
    recent_scans = Scan.query.order_by(Scan.created_at.desc()).limit(10).all()
    
    # Get statistics
    total_projects = Project.query.count()
    total_scans = Scan.query.count()
    total_secrets = Secret.query.count()
    total_urls = ExtractedUrl.query.count()
    total_endpoints = ApiEndpoint.query.count()
    total_monitors = JSMonitor.query.count()
    active_monitors = JSMonitor.query.filter_by(status='active').count()
    
    stats = {
        'total_projects': total_projects,
        'total_scans': total_scans,
        'total_secrets': total_secrets,
        'total_urls': total_urls,
        'total_endpoints': total_endpoints,
        'total_monitors': total_monitors,
        'active_monitors': active_monitors
    }
    
    return render_template('dashboard.html', recent_scans=recent_scans, stats=stats)

@app.route('/projects')
@login_required
def projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=projects)

@app.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('Project name is required.', 'error')
            return render_template('create_project.html')
        
        project = Project(name=name, description=description)
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('projects'))
    
    return render_template('create_project.html')

@app.route('/projects/<project_id>')
@login_required
def project_detail(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects'))
    
    scans = Scan.query.filter_by(project_id=project_id).order_by(Scan.created_at.desc()).all()
    monitors = JSMonitor.query.filter_by(project_id=project_id).order_by(JSMonitor.created_at.desc()).all()
    return render_template('project_detail.html', project=project, scans=scans, monitors=monitors)

@app.route('/projects/<project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects'))
    
    try:
        # Delete the project (cascading will delete associated scans, secrets, etc.)
        db.session.delete(project)
        db.session.commit()
        
        flash(f'Project "{project.name}" has been deleted successfully.', 'success')
        app.logger.info(f"Project {project_id} deleted successfully")
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete project. Please try again.', 'error')
        app.logger.error(f"Error deleting project {project_id}: {e}")
    
    return redirect(url_for('projects'))

@app.route('/scan')
@app.route('/scan/<project_id>')
@login_required
def scan(project_id=None):
    projects = Project.query.all()
    selected_project = None
    
    if project_id:
        selected_project = db.session.get(Project, project_id)
    
    # Handle quick scan parameters from homepage
    url = request.args.get('url')
    code = request.args.get('code')
    
    return render_template('scan.html', projects=projects, project=selected_project, 
                         quick_url=url, quick_code=code)

@app.route('/scan/execute', methods=['POST'])
@login_required
def execute_scan():
    try:
        # Handle both form data and JSON data
        if request.is_json:
            data = request.get_json()
            project_id = data.get('project_id')
            scan_type = data.get('scan_type')
            url = data.get('url')
            content = data.get('content')
        else:
            project_id = request.form.get('project_id')
            scan_type = request.form.get('scan_type')
            url = request.form.get('url')
            content = request.form.get('content')
        
        if not project_id:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Please select a project.'})
            flash('Please select a project.', 'error')
            return redirect(url_for('scan'))
        
        project = db.session.get(Project, project_id)
        if not project:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Invalid project selected.'})
            flash('Invalid project selected.', 'error')
            return redirect(url_for('scan'))
        
        scan = Scan(project_id=project_id, scan_type=scan_type)
        
        if scan_type == 'url':
            if not url:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'URL is required for URL scan.'})
                flash('URL is required for URL scan.', 'error')
                return redirect(url_for('scan'))
            scan.url = url
            
        elif scan_type == 'file':
            # Handle file upload for bulk URLs
            if 'file' not in request.files:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'No file uploaded.'})
                flash('No file uploaded.', 'error')
                return redirect(url_for('scan'))
            
            file = request.files['file']
            if file.filename == '':
                if request.is_json:
                    return jsonify({'success': False, 'error': 'No file selected.'})
                flash('No file selected.', 'error')
                return redirect(url_for('scan'))
            
            if file and file.filename.endswith('.txt'):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                scan.filename = filename
                scan.scan_type = 'bulk_urls'
        
        db.session.add(scan)
        db.session.commit()
        
        # Start scanning in background
        threading.Thread(target=perform_scan, args=(scan.id,), daemon=True).start()
        
        if request.is_json:
            return jsonify({'success': True, 'scan_id': scan.id})
        else:
            flash('Scan started successfully!', 'success')
            return redirect(url_for('scan_results', scan_id=scan.id))
            
    except Exception as e:
        app.logger.error(f"Error in execute_scan: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)})
        else:
            flash(f'Scan failed: {str(e)}', 'error')
            return redirect(url_for('scan'))

@app.route('/scan/<scan_id>/results')
@login_required
def scan_results(scan_id):
    scan = db.session.get(Scan, scan_id)
    if not scan:
        flash('Scan not found.', 'error')
        return redirect(url_for('dashboard'))
    
    secrets = Secret.query.filter_by(scan_id=scan_id).all()
    urls = ExtractedUrl.query.filter_by(scan_id=scan_id).all()
    endpoints = ApiEndpoint.query.filter_by(scan_id=scan_id).all()
    
    return render_template('scan_results.html', scan=scan, secrets=secrets, urls=urls, endpoints=endpoints)

@app.route('/scan/<scan_id>/export/<format>')
@login_required
def export_scan_results(scan_id, format):
    """Export scan results in specified format"""
    try:
        if format == 'csv':
            filepath = export_scan_results_csv(scan_id)
        elif format == 'json':
            filepath = export_scan_results_json(scan_id)
        else:
            flash('Invalid export format.', 'error')
            return redirect(url_for('scan_results', scan_id=scan_id))
        
        if not filepath or not os.path.exists(filepath):
            flash('Failed to generate export file.', 'error')
            return redirect(url_for('scan_results', scan_id=scan_id))
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        app.logger.error(f"Error exporting scan results: {e}")
        flash('Failed to export scan results.', 'error')
        return redirect(url_for('scan_results', scan_id=scan_id))

# --- JS Monitoring Routes ---
@app.route('/monitors')
@login_required
def monitors():
    monitors = JSMonitor.query.order_by(JSMonitor.created_at.desc()).all()
    return render_template('monitors.html', monitors=monitors)

@app.route('/monitors/create', methods=['GET', 'POST'])
@login_required
def create_monitor():
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        name = request.form.get('name')
        url = request.form.get('url')
        check_interval = int(request.form.get('check_interval', 300))
        telegram_enabled = 'telegram_enabled' in request.form
        discord_enabled = 'discord_enabled' in request.form
        
        if not all([project_id, name, url]):
            flash('All fields are required.', 'error')
            return render_template('create_monitor.html', projects=Project.query.all())
        
        # Validate URL
        try:
            content = fetch_js_content(url)
            if not content:
                flash('Unable to fetch content from the provided URL.', 'error')
                return render_template('create_monitor.html', projects=Project.query.all())
        except Exception as e:
            flash(f'Error validating URL: {str(e)}', 'error')
            return render_template('create_monitor.html', projects=Project.query.all())
        
        monitor = JSMonitor(
            project_id=project_id,
            name=name,
            url=url,
            check_interval=check_interval,
            telegram_enabled=telegram_enabled,
            discord_enabled=discord_enabled,
            last_content_hash=calculate_content_hash(content)
        )
        
        # Store initial content for future diff generation
        initial_change = JSChange(
            monitor_id=monitor.id,
            old_content_hash="",
            new_content_hash=calculate_content_hash(content),
            old_content="",
            new_content=content[:10000],  # Limit storage size
            diff_content="Initial content capture",
            change_summary="Monitor created - initial content captured"
        )
        
        db.session.add(monitor)
        db.session.flush()  # Get the monitor ID
        initial_change.monitor_id = monitor.id
        db.session.add(initial_change)
        db.session.commit()
        
        flash('Monitor created successfully!', 'success')
        return redirect(url_for('monitors'))
    
    projects = Project.query.all()
    return render_template('create_monitor.html', projects=projects)

@app.route('/monitors/<monitor_id>')
@login_required
def monitor_detail(monitor_id):
    monitor = db.session.get(JSMonitor, monitor_id)
    if not monitor:
        flash('Monitor not found.', 'error')
        return redirect(url_for('monitors'))
    
    changes = JSChange.query.filter_by(monitor_id=monitor_id).order_by(JSChange.detected_at.desc()).limit(50).all()
    return render_template('monitor_detail.html', monitor=monitor, changes=changes)

@app.route('/monitors/<monitor_id>/toggle', methods=['POST'])
@login_required
def toggle_monitor(monitor_id):
    monitor = db.session.get(JSMonitor, monitor_id)
    if not monitor:
        flash('Monitor not found.', 'error')
        return redirect(url_for('monitors'))
    
    monitor.status = 'paused' if monitor.status == 'active' else 'active'
    db.session.commit()
    
    flash(f'Monitor {monitor.status}.', 'success')
    return redirect(url_for('monitor_detail', monitor_id=monitor_id))

@app.route('/monitors/<monitor_id>/delete', methods=['POST'])
@login_required
def delete_monitor(monitor_id):
    monitor = db.session.get(JSMonitor, monitor_id)
    if not monitor:
        flash('Monitor not found.', 'error')
        return redirect(url_for('monitors'))
    
    try:
        db.session.delete(monitor)
        db.session.commit()
        flash('Monitor deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete monitor.', 'error')
        app.logger.error(f"Error deleting monitor {monitor_id}: {e}")
    
    return redirect(url_for('monitors'))

@app.route('/monitors/<monitor_id>/check', methods=['POST'])
@login_required
def manual_check_monitor(monitor_id):
    """Manually trigger a monitor check"""
    try:
        check_js_monitor(monitor_id)
        flash('Monitor check completed.', 'success')
    except Exception as e:
        flash(f'Monitor check failed: {str(e)}', 'error')
    
    return redirect(url_for('monitor_detail', monitor_id=monitor_id))

# --- Settings Routes ---
@app.route('/settings')
@login_required
def settings():
    settings = NotificationSettings.query.first()
    return render_template('settings.html', settings=settings)

@app.route('/settings/notifications', methods=['POST'])
@login_required
def update_notification_settings():
    try:
        settings = NotificationSettings.query.first()
        if not settings:
            settings = NotificationSettings()
            db.session.add(settings)
        
        settings.telegram_bot_token = request.form.get('telegram_bot_token', '')
        settings.telegram_chat_id = request.form.get('telegram_chat_id', '')
        settings.discord_webhook_url = request.form.get('discord_webhook_url', '')
        settings.scan_notifications = 'scan_notifications' in request.form
        settings.finding_notifications = 'finding_notifications' in request.form
        settings.monitor_notifications = 'monitor_notifications' in request.form
        
        db.session.commit()
        flash('Notification settings updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to update notification settings.', 'error')
        app.logger.error(f"Error updating notification settings: {e}")
    
    return redirect(url_for('settings'))

@app.route('/settings/test-telegram', methods=['POST'])
@login_required
def test_telegram():
    """Test Telegram notification"""
    bot_token = request.form.get('telegram_bot_token')
    chat_id = request.form.get('telegram_chat_id')
    
    if send_telegram_notification("🧪 Test notification from Rezon Scanner", bot_token, chat_id):
        flash('Telegram test notification sent successfully!', 'success')
    else:
        flash('Failed to send Telegram test notification.', 'error')
    
    return redirect(url_for('settings'))

@app.route('/settings/test-discord', methods=['POST'])
@login_required
def test_discord():
    """Test Discord notification"""
    webhook_url = request.form.get('discord_webhook_url')
    
    if send_discord_notification("🧪 Test notification from Rezon Scanner", webhook_url):
        flash('Discord test notification sent successfully!', 'success')
    else:
        flash('Failed to send Discord test notification.', 'error')
    
    return redirect(url_for('settings'))

# --- API Routes ---
@app.route('/api/scan/<scan_id>/status')
@login_required
def scan_status(scan_id):
    scan = db.session.get(Scan, scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404
    
    return jsonify({
        'status': scan.status,
        'total_secrets': scan.total_secrets,
        'total_urls': scan.total_urls,
        'total_api_endpoints': scan.total_api_endpoints,
        'completed_at': scan.completed_at.isoformat() if scan.completed_at else None
    })

@app.route('/api/dashboard_stats')
@login_required
def dashboard_stats():
    # Get secret types distribution
    secret_types = db.session.query(
        Secret.secret_type, 
        db.func.count(Secret.id).label('count')
    ).group_by(Secret.secret_type).order_by(db.func.count(Secret.id).desc()).limit(10).all()
    
    # Get severity distribution
    severity_distribution = db.session.query(
        Secret.severity,
        db.func.count(Secret.id).label('count')
    ).group_by(Secret.severity).all()
    
    return jsonify({
        'secret_types': [{'type': st[0], 'count': st[1]} for st in secret_types],
        'severity_distribution': [{'severity': sd[0], 'count': sd[1]} for sd in severity_distribution]
    })

@app.route('/api/monitors/stats')
@login_required
def monitor_stats():
    """Get monitor statistics"""
    total_monitors = JSMonitor.query.count()
    active_monitors = JSMonitor.query.filter_by(status='active').count()
    paused_monitors = JSMonitor.query.filter_by(status='paused').count()
    error_monitors = JSMonitor.query.filter_by(status='error').count()
    
    # Recent changes
    recent_changes = JSChange.query.order_by(JSChange.detected_at.desc()).limit(10).all()
    
    return jsonify({
        'total_monitors': total_monitors,
        'active_monitors': active_monitors,
        'paused_monitors': paused_monitors,
        'error_monitors': error_monitors,
        'recent_changes': [
            {
                'id': change.id,
                'monitor_name': change.monitor.name,
                'monitor_url': change.monitor.url,
                'detected_at': change.detected_at.isoformat(),
                'change_summary': change.change_summary
            }
            for change in recent_changes
        ]
    })

# --- Background Tasks ---
def start_monitor_scheduler():
    """Start the background scheduler for JS monitors"""
    def run_scheduler():
        while True:
            try:
                run_js_monitors()
                time.sleep(60)  # Check every minute
            except Exception as e:
                app.logger.error(f"Error in monitor scheduler: {e}")
                time.sleep(60)
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    app.logger.info("JS Monitor scheduler started")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.logger.info("Database initialized successfully")
        
        # Start background monitor scheduler
        start_monitor_scheduler()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
