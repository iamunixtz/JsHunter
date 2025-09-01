#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
import logging
from typing import Optional
import tempfile

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
from jsninja import run_trufflehog, _find_trufflehog, setup_trufflehog, print_summary

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ensure directories exist
Path(config.TEMP_DIR).mkdir(parents=True, exist_ok=True)
Path(config.RESULTS_DIR).mkdir(parents=True, exist_ok=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    
    welcome_text = """
🥷 Welcome to JS Ninja Bot! 🥷

I can help you scan JavaScript files for potential secrets and vulnerabilities.

Just send me a JavaScript file (supported extensions: .js, .jsx, .ts, .tsx) and I'll scan it using TruffleHog.

Commands:
/start - Show this help message
/status - Check bot and TruffleHog status
"""
    await update.message.reply_text(welcome_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check the status of TruffleHog and bot configuration."""
    if not is_user_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    tr_bin = _find_trufflehog()
    status_text = "🤖 JS Ninja Bot Status:\n\n"
    
    if tr_bin:
        status_text += f"✅ TruffleHog: Found at {tr_bin}\n"
    else:
        status_text += "❌ TruffleHog: Not found (will attempt auto-install)\n"
    
    status_text += f"📁 Max file size: {config.MAX_FILE_SIZE_MB}MB\n"
    status_text += f"🔍 Supported extensions: {', '.join(config.ALLOWED_EXTENSIONS)}\n"
    
    await update.message.reply_text(status_text)

def is_user_authorized(user_id: int) -> bool:
    """Check if a user is authorized to use the bot."""
    return len(config.ALLOWED_USER_IDS) == 0 or user_id in config.ALLOWED_USER_IDS

def format_findings_message(findings: list[dict]) -> str:
    """Format findings into a Telegram message."""
    if not findings:
        return "✅ No secrets or sensitive information found in the file."
    
    message = "🚨 Found potential secrets:\n\n"
    for f in findings:
        det = f.get("DetectorName", "Unknown")
        verified = "✅" if f.get("Verified", False) else "❓"
        
        # Get raw value or redacted version
        raw = f.get("Raw") or f.get("Redacted") or f.get("RawV2") or ""
        redacted = (raw[:20] + "...") if raw else "(redacted)"
        
        # Try to get line number
        line_no = None
        try:
            line_no = f["SourceMetadata"]["Data"]["Filesystem"].get("line")
        except Exception:
            pass
        
        line_info = f" (line {line_no})" if line_no else ""
        message += f"• [{det}]{line_info}\n  {verified} `{redacted}`\n\n"
    
    return message

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
            
            # Ensure we have trufflehog
            tr_bin = _find_trufflehog()
            if not tr_bin:
                await update.message.reply_text("🔄 TruffleHog not found. Installing...")
                try:
                    tr_bin = setup_trufflehog()
                except Exception as e:
                    await update.message.reply_text(f"❌ Failed to install TruffleHog: {e}")
                    return
            
            # Scan the file
            await update.message.reply_text("🔍 Scanning file...")
            findings = run_trufflehog(tr_bin, file_path)
            
            # Send results
            message = format_findings_message(findings)
            await update.message.reply_text(message, parse_mode='MarkdownV2')
            
            # Save results if any found
            if findings:
                result_file = Path(config.RESULTS_DIR) / f"{file.file_name}_results.json"
                with open(result_file, "w", encoding="utf-8") as f:
                    for finding in findings:
                        f.write(json.dumps(finding) + "\n")
                
                # Send results file
                await update.message.reply_document(
                    document=result_file,
                    caption="📄 Detailed scan results in JSON format"
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
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Start the bot
    print("🥷 JS Ninja Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()