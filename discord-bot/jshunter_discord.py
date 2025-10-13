#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import tempfile
import time
import subprocess
from pathlib import Path
import logging
from typing import Optional
import re
import requests
from urllib.parse import urlparse

import discord
from discord.ext import commands
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

def run_jshunter_file_scan(file_path: str) -> list[dict]:
    """Run jshunter scan on a local file and return results."""
    try:
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
            logger.error(f"JSHunter file scan failed: {result.stderr}")
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
        logger.error(f"Error running jshunter on file: {e}")
        return []

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
# Disable privileged intents to avoid permission issues
intents.presences = False
intents.members = False
bot = commands.Bot(command_prefix='!', intents=intents)

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

def format_findings_embed(findings: list[dict], filename: str) -> discord.Embed:
    """Format findings into a Discord embed."""
    if not findings:
        embed = discord.Embed(
            title="✅ Scan Complete",
            description=f"No secrets or sensitive information found in `{filename}`.",
            color=discord.Color.green()
        )
        return embed
    
    embed = discord.Embed(
        title="🚨 Secrets Found!",
        description=f"Found {len(findings)} potential secret(s) in `{filename}`",
        color=discord.Color.red()
    )
    
    verified_count = sum(1 for f in findings if f.get("Verified", False))
    embed.add_field(
        name="Summary",
        value=f"Total: {len(findings)}\nVerified: {verified_count}",
        inline=True
    )
    
    # Add findings (limit to first 10 to avoid embed limits)
    for i, f in enumerate(findings[:10]):
        det = f.get("DetectorName", "Unknown")
        verified = "✅ Verified" if f.get("Verified", False) else "❓ Unverified"
        
        # Get raw value or redacted version
        raw = f.get("Raw") or f.get("Redacted") or f.get("RawV2") or ""
        # Show full API key instead of truncating
        redacted = raw if raw else "(redacted)"
        
        # Try to get line number
        line_no = None
        try:
            line_no = f["SourceMetadata"]["Data"]["Filesystem"].get("line")
        except Exception:
            pass
        
        line_info = f" (Line {line_no})" if line_no else ""
        
        embed.add_field(
            name=f"[{det}]{line_info}",
            value=f"`{redacted}`\n{verified}",
            inline=False
        )
    
    if len(findings) > 10:
        embed.add_field(
            name="Note",
            value=f"Showing first 10 results. Total: {len(findings)}",
            inline=False
        )
    
    return embed

def format_url_findings_message(findings, url):
    """Format findings for URL scanning into a message."""
    if not findings:
        return f"✅ No secrets found in {url}"
    
    # Group findings by type
    findings_by_type = {}
    for finding in findings:
        secret_type = finding.get('DetectorName', 'Unknown')
        if secret_type not in findings_by_type:
            findings_by_type[secret_type] = []
        findings_by_type[secret_type].append(finding)
    
    # Create message content
    message_content = f"🔍 **Verified Secrets found in {url}**\n\n"
    
    for secret_type, type_findings in findings_by_type.items():
        for finding in type_findings:
            raw_value = finding.get('Raw', '')
            verified = finding.get('Verified', False)
            status = "✅ Verified" if verified else "❓ Unverified"
            
            # Show full API key with backticks for easy copying
            message_content += f"**[{secret_type}]** `{raw_value}` {status}\n"
    
    return message_content

@bot.event
async def on_ready():
    print(f'🚀 JSHunter Discord Bot is ready! Logged in as {bot.user}')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.command(name='scan')
async def scan_command(ctx):
    """Scan a JavaScript file for secrets."""
    if not is_user_authorized(ctx.author.id):
        await ctx.send("❌ You are not authorized to use this bot.")
        return
    
    if not ctx.message.attachments:
        embed = discord.Embed(
            title="📎 No File Attached",
            description="Please attach a JavaScript file to scan.",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="Supported Extensions",
            value="`.js`, `.jsx`, `.ts`, `.tsx`",
            inline=True
        )
        embed.add_field(
            name="Max File Size",
            value=f"{config.MAX_FILE_SIZE_MB}MB",
            inline=True
        )
        await ctx.send(embed=embed)
        return
    
    attachment = ctx.message.attachments[0]
    
    # Check file extension
    if not any(attachment.filename.lower().endswith(ext) for ext in config.ALLOWED_EXTENSIONS):
        embed = discord.Embed(
            title="❌ Unsupported File Type",
            description=f"File type not supported: `{Path(attachment.filename).suffix}`",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Supported Extensions",
            value="`.js`, `.jsx`, `.ts`, `.tsx`",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Check file size
    if attachment.size > (config.MAX_FILE_SIZE_MB * 1024 * 1024):
        embed = discord.Embed(
            title="❌ File Too Large",
            description=f"File size: {attachment.size / (1024*1024):.1f}MB\nMax allowed: {config.MAX_FILE_SIZE_MB}MB",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Send initial response
    embed = discord.Embed(
        title="📥 Processing File",
        description=f"Downloading and scanning `{attachment.filename}`...",
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=embed)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(attachment.filename).suffix) as temp_file:
        file_path = Path(temp_file.name)
        try:
            # Download the file
            await attachment.save(file_path)
            
            # Check JSHunter availability
            jshunter_path = Path(__file__).parent.parent / "cli" / "jshunter"
            if not jshunter_path.exists():
                embed = discord.Embed(
                    title="❌ JSHunter Not Found",
                    description="JSHunter CLI not found. Please contact administrator.",
                    color=discord.Color.red()
                )
                await message.edit(embed=embed)
                return
            
            # Update status
            embed = discord.Embed(
                title="🚀 Scanning File",
                description=f"Running high-performance security scan on `{attachment.filename}`...",
                color=discord.Color.blue()
            )
            await message.edit(embed=embed)
            
            # Scan the file using enhanced jshunter
            findings = run_jshunter_file_scan(str(file_path))
            
            # Send results
            result_embed = format_findings_embed(findings, attachment.filename)
            await message.edit(embed=result_embed)
            
            # Send detailed results files if any found
            if findings:
                results_dir = Path(__file__).parent.parent / "cli" / "results"
                verified_files = list(results_dir.glob("verified_results_*.json"))
                unverified_files = list(results_dir.glob("unverified_results_*.json"))
                
                if verified_files:
                    latest_verified = max(verified_files, key=lambda x: x.stat().st_mtime)
                    await ctx.send(
                        "📄 Verified findings:",
                        file=discord.File(latest_verified, filename=f"verified_findings_{int(time.time())}.json")
                    )
                
                if unverified_files:
                    latest_unverified = max(unverified_files, key=lambda x: x.stat().st_mtime)
                    await ctx.send(
                        "📄 Unverified findings:",
                        file=discord.File(latest_unverified, filename=f"unverified_findings_{int(time.time())}.json")
                    )
        
        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            embed = discord.Embed(
                title="❌ Processing Error",
                description=f"Error processing file: {str(e)}",
                color=discord.Color.red()
            )
            await message.edit(embed=embed)
        
        finally:
            # Cleanup
            try:
                os.unlink(file_path)
            except Exception:
                pass

@bot.command(name='status')
async def status_command(ctx):
    """Check the status of the bot and JSHunter."""
    if not is_user_authorized(ctx.author.id):
        await ctx.send("❌ You are not authorized to use this bot.")
        return
    
    jshunter_path = Path(__file__).parent.parent / "cli" / "jshunter"
    
    embed = discord.Embed(
        title="🚀 JSHunter Bot Status",
        color=discord.Color.blue()
    )
    
    if jshunter_path.exists():
        embed.add_field(
            name="✅ JSHunter",
            value=f"Found at: `{jshunter_path}`",
            inline=False
        )
        embed.add_field(
            name="🚀 High-Performance Mode",
            value="Available",
            inline=True
        )
    else:
        embed.add_field(
            name="❌ JSHunter",
            value="Not found",
            inline=False
        )
    
    embed.add_field(
        name="📁 Max File Size",
        value=f"{config.MAX_FILE_SIZE_MB}MB",
        inline=True
    )
    
    embed.add_field(
        name="🔍 Supported Extensions",
        value="`.js`, `.jsx`, `.ts`, `.tsx`",
        inline=True
    )
    
    embed.add_field(
        name="🏠 Guilds",
        value=str(len(bot.guilds)),
        inline=True
    )
    
    await ctx.send(embed=embed)

@bot.command(name='scanurl')
async def scanurl_command(ctx, url: str = None):
    """Scan a JavaScript file from URL for secrets."""
    if not is_user_authorized(ctx.author.id):
        await ctx.send("❌ You are not authorized to use this bot.")
        return
    
    if not url:
        embed = discord.Embed(
            title="❌ Missing URL",
            description="Please provide a URL to scan.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Usage",
            value="`!scanurl <URL>`",
            inline=False
        )
        embed.add_field(
            name="Example",
            value="`!scanurl https://example.com/script.js`",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            embed = discord.Embed(
                title="❌ Invalid URL",
                description="Please provide a valid HTTP/HTTPS URL.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
    except Exception:
        embed = discord.Embed(
            title="❌ Invalid URL Format",
            description="The provided URL format is invalid.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Send initial response
    embed = discord.Embed(
        title="📥 Processing URL",
        description=f"Downloading and scanning: `{url}`",
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=embed)
    
    try:
        # Check JSHunter availability
        jshunter_path = Path(__file__).parent.parent / "cli" / "jshunter"
        if not jshunter_path.exists():
            embed = discord.Embed(
                title="❌ JSHunter Not Found",
                description="JSHunter CLI not found. Please contact administrator.",
                color=discord.Color.red()
            )
            await message.edit(embed=embed)
            return
        
        # Update status
        embed = discord.Embed(
            title="🚀 Scanning URL",
            description=f"Running high-performance security scan on: `{url}`",
            color=discord.Color.blue()
        )
        await message.edit(embed=embed)
        
        # Scan using enhanced jshunter
        findings = run_jshunter_scan(url)
        
        # Send results
        filename = safe_filename_from_url(url)
        result_message = format_url_findings_message(findings, url)
        await message.edit(content=result_message, embed=None)
        
        # Send detailed results files if findings exist
        if findings:
            results_dir = Path(__file__).parent.parent / "cli" / "results"
            verified_files = list(results_dir.glob("verified_results_*.json"))
            unverified_files = list(results_dir.glob("unverified_results_*.json"))
            
            if verified_files:
                latest_verified = max(verified_files, key=lambda x: x.stat().st_mtime)
                await ctx.send(
                    "📄 Verified findings:",
                    file=discord.File(latest_verified, filename=f"verified_findings_{int(time.time())}.json")
                )
            
            if unverified_files:
                latest_unverified = max(unverified_files, key=lambda x: x.stat().st_mtime)
                await ctx.send(
                    "📄 Unverified findings:",
                    file=discord.File(latest_unverified, filename=f"unverified_findings_{int(time.time())}.json")
                )
        
        # Cleanup - no temp files to clean up for URL scanning
            
    except Exception as e:
        logger.error(f"Error scanning URL {url}: {e}")
        embed = discord.Embed(
            title="❌ Scan Error",
            description=f"Error processing URL: {str(e)}",
            color=discord.Color.red()
        )
        await message.edit(embed=embed)

@bot.command(name='jshunter_help')
async def help_command(ctx):
    """Show help information."""
    embed = discord.Embed(
        title="🚀 JSHunter Bot Help",
        description="High-performance JavaScript security scanner with parallel processing.",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="!scan",
        value="Attach a JavaScript file and use this command to scan it for secrets.",
        inline=False
    )
    
    embed.add_field(
        name="!scanurl <URL>",
        value="Scan a JavaScript file from a URL for secrets.",
        inline=False
    )
    
    embed.add_field(
        name="!status",
        value="Check bot and TruffleHog status.",
        inline=False
    )
    
    embed.add_field(
        name="!jshunter_help",
        value="Show this help message.",
        inline=False
    )
    
    embed.add_field(
        name="Supported Files",
        value="`.js`, `.jsx`, `.ts`, `.tsx` (max {config.MAX_FILE_SIZE_MB}MB)",
        inline=False
    )
    
    await ctx.send(embed=embed)

def main():
    """Start the Discord bot."""
    if not config.DISCORD_BOT_TOKEN or config.DISCORD_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Error: Please set your Discord bot token in config.py")
        sys.exit(1)
    
    print("🚀 Starting JSHunter Discord Bot...")
    bot.run(config.DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    main()