#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
from pathlib import Path
import logging
from typing import Optional
import tempfile
import json
import requests
import re
import subprocess
from urllib.parse import urlparse

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ensure directories exist
Path(config.TEMP_DIR).mkdir(parents=True, exist_ok=True)
Path(config.RESULTS_DIR).mkdir(parents=True, exist_ok=True)

# Helper functions for the enhanced jshunter
def run_jshunter_scan(url: str) -> list[dict]:
    """Run jshunter scan on a URL and return results."""
    try:
        result = subprocess.run([
            "python3", "../cli/jshunter", 
            "--high-performance", 
            "-u", url
        ], capture_output=True, text=True, timeout=120, cwd=Path(__file__).parent)
        
        if result.returncode != 0:
            logger.error(f"JSHunter scan failed: {result.stderr}")
            return []
        
        # JSHunter saves results to JSON files, not stdout
        # Look for the most recent result files
        results_dir = Path(__file__).parent.parent / "cli" / "results"
        if not results_dir.exists():
            return []
        
        # Find the most recent verified and unverified result files
        verified_files = list(results_dir.glob("verified_results_*.json"))
        unverified_files = list(results_dir.glob("unverified_results_*.json"))
        
        findings = []
        
        # Read verified findings
        if verified_files:
            latest_verified = max(verified_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest_verified, 'r') as f:
                    for line in f:
                        if line.strip():
                            finding = json.loads(line.strip())
                            finding["Verified"] = True
                            findings.append(finding)
            except Exception as e:
                logger.error(f"Error reading verified results: {e}")
        
        # Read unverified findings
        if unverified_files:
            latest_unverified = max(unverified_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest_unverified, 'r') as f:
                    for line in f:
                        if line.strip():
                            finding = json.loads(line.strip())
                            finding["Verified"] = False
                            findings.append(finding)
            except Exception as e:
                logger.error(f"Error reading unverified results: {e}")
        
        return findings
    except Exception as e:
        logger.error(f"Error running jshunter: {e}")
        return []

def run_jshunter_batch_scan(urls: list[str]) -> dict:
    """Run jshunter batch scan on multiple URLs."""
    try:
        # Create temporary URL file
        temp_url_file = Path(config.TEMP_DIR) / f"urls_{int(time.time())}.txt"
        with open(temp_url_file, 'w') as f:
            for url in urls:
                f.write(f"{url}\n")
        
        result = subprocess.run([
            "python3", "../cli/jshunter", 
            "--high-performance", 
            "-f", str(temp_url_file)
        ], capture_output=True, text=True, timeout=300, cwd=Path(__file__).parent)
        
        # Cleanup
        if temp_url_file.exists():
            temp_url_file.unlink()
        
        if result.returncode != 0:
            logger.error(f"JSHunter batch scan failed: {result.stderr}")
            return {"success": False, "error": result.stderr}
        
        # JSHunter saves results to JSON files, not stdout
        # Look for the most recent result files
        results_dir = Path(__file__).parent.parent / "cli" / "results"
        if not results_dir.exists():
            return {"success": True, "findings": []}
        
        # Find the most recent verified and unverified result files
        verified_files = list(results_dir.glob("verified_results_*.json"))
        unverified_files = list(results_dir.glob("unverified_results_*.json"))
        
        findings = []
        
        # Read verified findings
        if verified_files:
            latest_verified = max(verified_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest_verified, 'r') as f:
                    for line in f:
                        if line.strip():
                            finding = json.loads(line.strip())
                            finding["Verified"] = True
                            findings.append(finding)
            except Exception as e:
                logger.error(f"Error reading verified results: {e}")
        
        # Read unverified findings
        if unverified_files:
            latest_unverified = max(unverified_files, key=lambda x: x.stat().st_mtime)
            try:
                with open(latest_unverified, 'r') as f:
                    for line in f:
                        if line.strip():
                            finding = json.loads(line.strip())
                            finding["Verified"] = False
                            findings.append(finding)
            except Exception as e:
                logger.error(f"Error reading unverified results: {e}")
        
        return {"success": True, "findings": findings}
    except Exception as e:
        logger.error(f"Error running jshunter batch scan: {e}")
        return {"success": False, "error": str(e)}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    
    welcome_text = """
🚀 Welcome to JSHunter Bot! 🚀

I can help you scan JavaScript files for potential secrets and vulnerabilities using high-performance parallel processing.

You can:
• Send me a JavaScript file (supported extensions: .js, .jsx, .ts, .tsx)
• Use /scanurl <URL> to scan a JavaScript file from a URL
• Use /batch <URL1> <URL2> ... to scan multiple URLs

Commands:
/start - Show this help message
/help - Show detailed command usage
/status - Check bot and JSHunter status
/scanurl <URL> - Scan a JavaScript file from URL
/batch <URL1> <URL2> ... - Scan multiple URLs (high-performance mode)
"""
    await update.message.reply_text(welcome_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check the status of JSHunter and bot configuration."""
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    status_text = "🚀 JSHunter Bot Status:\n\n"
    
    # Check if jshunter CLI exists
    jshunter_path = Path(__file__).parent.parent / "cli" / "jshunter"
    if jshunter_path.exists():
        status_text += f"✅ JSHunter: Found at {jshunter_path}\n"
        status_text += "🚀 High-Performance Mode: Available\n"
    else:
        status_text += "❌ JSHunter: Not found\n"
    
    status_text += f"📁 Max file size: {config.MAX_FILE_SIZE_MB}MB\n"
    status_text += f"🔍 Supported extensions: {', '.join(config.ALLOWED_EXTENSIONS)}\n"
    status_text += "⚡ Features: Parallel processing, Discord integration, Auto-cleanup\n"
    
    await update.message.reply_text(status_text)

async def scanurl_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /scanurl command."""
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a URL to scan.\nUsage: /scanurl <URL>")
        return
    
    url = context.args[0]
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            await update.message.reply_text("❌ Invalid URL format. Please provide a valid HTTP/HTTPS URL.")
            return
    except Exception:
        await update.message.reply_text("❌ Invalid URL format.")
        return
    
    # Check JSHunter availability
    jshunter_path = Path(__file__).parent.parent / "cli" / "jshunter"
    if not jshunter_path.exists():
        await update.message.reply_text("❌ JSHunter not found. Please contact administrator.")
        return
    
    await update.message.reply_text(f"🚀 Scanning with high-performance mode: {url}\nPlease wait...")
    
    try:
        # Scan using enhanced jshunter
        findings = run_jshunter_scan(url)
        
        # Format and send results
        if findings:
            message = format_findings_message(findings, url)
            await update.message.reply_text(message)
            
            # Send detailed results files
            results_dir = Path(__file__).parent.parent / "cli" / "results"
            verified_files = list(results_dir.glob("verified_results_*.json"))
            unverified_files = list(results_dir.glob("unverified_results_*.json"))
            
            if verified_files:
                latest_verified = max(verified_files, key=lambda x: x.stat().st_mtime)
                await update.message.reply_document(
                    document=latest_verified,
                    caption="📄 Verified findings (JSON format)"
                )
            
            if unverified_files:
                latest_unverified = max(unverified_files, key=lambda x: x.stat().st_mtime)
                await update.message.reply_document(
                    document=latest_unverified,
                    caption="📄 Unverified findings (JSON format)"
                )
        else:
            await update.message.reply_text(f"✅ No secrets found in {url}")
        
    except Exception as e:
        logger.error(f"Error scanning URL {url}: {e}")
        await update.message.reply_text(f"❌ Error scanning URL: {str(e)}")

async def batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /batch command for multiple URLs."""
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Please provide at least 2 URLs to scan.\nUsage: /batch <URL1> <URL2> [URL3] ...")
        return
    
    urls = context.args[:10]  # Limit to 10 URLs for safety
    
    # Validate URLs
    valid_urls = []
    for url in urls:
        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                valid_urls.append(url)
            else:
                await update.message.reply_text(f"❌ Invalid URL: {url}")
                return
        except Exception:
            await update.message.reply_text(f"❌ Invalid URL format: {url}")
            return
    
    # Check JSHunter availability
    jshunter_path = Path(__file__).parent.parent / "cli" / "jshunter"
    if not jshunter_path.exists():
        await update.message.reply_text("❌ JSHunter not found. Please contact administrator.")
        return
    
    await update.message.reply_text(f"🚀 High-performance batch scan of {len(valid_urls)} URLs...\nPlease wait...")
    
    try:
        # Run batch scan
        result = run_jshunter_batch_scan(valid_urls)
        
        if not result["success"]:
            await update.message.reply_text(f"❌ Batch scan failed: {result.get('error', 'Unknown error')}")
            return
        
        findings = result["findings"]
        
        if findings:
            message = f"🔍 **Batch Scan Results**\n\n"
            message += f"📊 Scanned {len(valid_urls)} URLs\n"
            message += f"🔍 Found {len(findings)} potential secrets\n\n"
            message += format_findings_message(findings)
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(f"✅ Batch scan completed. No secrets found in {len(valid_urls)} URLs.")
            
    except Exception as e:
        logger.error(f"Error in batch scan: {e}")
        await update.message.reply_text(f"❌ Error in batch scan: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed help information."""
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    
    help_text = """
🚀 **JSHunter Bot - Detailed Help** 🚀

**Available Commands:**

🔹 **/start** - Show welcome message and basic info

🔹 **/help** - Show this detailed help message

🔹 **/status** - Check bot and JSHunter system status

🔹 **/scanurl <URL>** - Scan a single JavaScript file from URL
   • Example: `/scanurl https://example.com/script.js`
   • Uses high-performance mode for fast scanning

🔹 **/batch <URL1> <URL2> ...** - Scan multiple URLs simultaneously
   • Example: `/batch https://site1.com/app.js https://site2.com/main.js`
   • Limited to 10 URLs for safety
   • Uses parallel processing for maximum speed

**File Upload:**
📎 Send JavaScript files directly to the bot
• Supported: `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`
• Max size: 10MB
• Automatically scanned for secrets

**Features:**
⚡ High-performance parallel processing
🔍 TruffleHog v3+ integration
✅ Verified and unverified findings
📊 Real-time progress tracking
🧹 Automatic file cleanup
📄 Detailed JSON results

**Security:**
🛡️ Finds API keys, tokens, passwords
🔐 Detects AWS, GitHub, Infura secrets
✅ Verification status for each finding
📋 Line-by-line analysis

**Performance:**
🚀 10x faster than legacy scanning
⚡ Parallel downloads and processing
📈 Batch processing for efficiency
🔄 Real-time progress updates
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

def is_user_authorized(user_id: int) -> bool:
    """Check if a user is authorized to use the bot."""
    return len(config.ALLOWED_USER_IDS) == 0 or user_id in config.ALLOWED_USER_IDS

def safe_filename_from_url(url: str) -> str:
    """Generate a safe filename from URL."""
    parsed = urlparse(url)
    fname = parsed.path.split("/")[-1] or "downloaded"
    fname = re.sub(r"[^\w.-]", "_", fname)
    if not fname.endswith(".js"):
        fname += ".js"
    fname = re.sub(r"_+", "_", fname).strip("_")
    return fname

def download_js_from_url(url: str) -> Path | None:
    """Download JavaScript file from URL."""
    try:
        response = requests.get(url, timeout=30, verify=True)
        response.raise_for_status()
        
        # Create temp file
        fname = safe_filename_from_url(url)
        temp_file = Path(config.TEMP_DIR) / fname
        
        with open(temp_file, "w", encoding="utf-8", errors="ignore") as f:
            f.write(response.text)
        
        return temp_file
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        return None

def format_findings_message(findings: list[dict], url: str = None) -> str:
    """Format findings into a Telegram message."""
    if not findings:
        if url:
            return f"✅ No secrets found in {url}"
        return "✅ No secrets or sensitive information found in the file."
    
    # Group findings by type
    findings_by_type = {}
    for finding in findings:
        secret_type = finding.get('DetectorName', 'Unknown')
        if secret_type not in findings_by_type:
            findings_by_type[secret_type] = []
        findings_by_type[secret_type].append(finding)
    
    # Create message content
    if url:
        message_content = f"🔍 *Verified Secrets found in {url}*\n\n"
    else:
        message_content = "🔍 *Verified Secrets found*\n\n"
    
    for secret_type, type_findings in findings_by_type.items():
        for finding in type_findings:
            raw_value = finding.get('Raw', '')
            verified = finding.get('Verified', False)
            status = "✅ Verified" if verified else "❓ Unverified"
            
            # Show full API key with backticks for easy copying
            message_content += f"*[{secret_type}]* `{raw_value}` {status}\n"
    
    return message_content

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming files."""
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    # Check if we received a file
    if not update.message.document:
        await update.message.reply_text("Please send me a JavaScript file to scan.")
        return
    
    file = update.message.document
    
    # Check file extension
    if not any(file.file_name.lower().endswith(ext) for ext in config.ALLOWED_EXTENSIONS):
        await update.message.reply_text(
            f"❌ Unsupported file type. Supported extensions: {', '.join(config.ALLOWED_EXTENSIONS)}"
        )
        return
    
    # Check file size
    if file.file_size > (config.MAX_FILE_SIZE_MB * 1024 * 1024):
        await update.message.reply_text(
            f"❌ File too large. Maximum size: {config.MAX_FILE_SIZE_MB}MB"
        )
        return
    
    # Download file
    await update.message.reply_text("📥 Downloading file...")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.file_name).suffix) as temp_file:
        file_path = Path(temp_file.name)
        try:
            # Download the file
            tg_file = await context.bot.get_file(file.file_id)
            await tg_file.download_to_drive(file_path)
            
            # Check JSHunter availability
            jshunter_path = Path(__file__).parent.parent / "cli" / "jshunter"
            if not jshunter_path.exists():
                await update.message.reply_text("❌ JSHunter not found. Please contact administrator.")
                return
            
            # Scan the file using jshunter
            await update.message.reply_text("🚀 Scanning file with high-performance mode...")
            
            # Create temporary URL file for the local file
            temp_url_file = Path(config.TEMP_DIR) / f"file_{int(time.time())}.txt"
            with open(temp_url_file, 'w') as f:
                f.write(f"file://{file_path}")
            
            result = subprocess.run([
                "python3", "../cli/jshunter", 
                "--high-performance", 
                "-f", str(temp_url_file)
            ], capture_output=True, text=True, timeout=120, cwd=Path(__file__).parent)
            
            # Cleanup temp URL file
            if temp_url_file.exists():
                temp_url_file.unlink()
            
            if result.returncode != 0:
                await update.message.reply_text(f"❌ Scan failed: {result.stderr}")
                return
            
            # JSHunter saves results to JSON files, not stdout
            # Look for the most recent result files
            results_dir = Path(__file__).parent.parent / "cli" / "results"
            findings = []
            
            if results_dir.exists():
                # Find the most recent verified and unverified result files
                verified_files = list(results_dir.glob("verified_results_*.json"))
                unverified_files = list(results_dir.glob("unverified_results_*.json"))
                
                # Read verified findings
                if verified_files:
                    latest_verified = max(verified_files, key=lambda x: x.stat().st_mtime)
                    try:
                        with open(latest_verified, 'r') as f:
                            for line in f:
                                if line.strip():
                                    finding = json.loads(line.strip())
                                    finding["Verified"] = True
                                    findings.append(finding)
                    except Exception as e:
                        logger.error(f"Error reading verified results: {e}")
                
                # Read unverified findings
                if unverified_files:
                    latest_unverified = max(unverified_files, key=lambda x: x.stat().st_mtime)
                    try:
                        with open(latest_unverified, 'r') as f:
                            for line in f:
                                if line.strip():
                                    finding = json.loads(line.strip())
                                    finding["Verified"] = False
                                    findings.append(finding)
                    except Exception as e:
                        logger.error(f"Error reading unverified results: {e}")
            
            # Send results
            message = format_findings_message(findings)
            await update.message.reply_text(message, parse_mode='MarkdownV2')
            
            # Save results if any found
            if findings:
                results_dir = Path(__file__).parent.parent / "cli" / "results"
                verified_files = list(results_dir.glob("verified_results_*.json"))
                unverified_files = list(results_dir.glob("unverified_results_*.json"))
                
                if verified_files:
                    latest_verified = max(verified_files, key=lambda x: x.stat().st_mtime)
                    await update.message.reply_document(
                        document=latest_verified,
                        caption="📄 Verified findings (JSON format)"
                    )
                
                if unverified_files:
                    latest_unverified = max(unverified_files, key=lambda x: x.stat().st_mtime)
                    await update.message.reply_document(
                        document=latest_unverified,
                        caption="📄 Unverified findings (JSON format)"
                    )
        
        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Error processing file: {str(e)}")
        
        finally:
            # Cleanup
            try:
                os.unlink(file_path)
            except Exception:
                pass

def main() -> None:
    """Start the bot."""
    if not config.TELEGRAM_BOT_TOKEN or config.TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Error: Please set your Telegram bot token in config.py")
        sys.exit(1)
    
    # Create the Application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("scanurl", scanurl_command))
    application.add_handler(CommandHandler("batch", batch_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Start the bot
    print("🚀 JSHunter Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()