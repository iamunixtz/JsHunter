#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import tempfile
import time
import subprocess
import requests
from pathlib import Path
import logging
from typing import Optional
import re
from urllib.parse import urlparse

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

def send_webhook_message(content: str, files: list = None):
    """Send a message to Discord webhook."""
    try:
        webhook_url = config.DISCORD_WEBHOOK_URL
        
        if files:
            # Send files with message
            files_data = []
            for file_path in files:
                files_data.append(('file', (file_path.name, open(file_path, 'rb'), 'application/json')))
            
            data = {
                'content': content
            }
            
            response = requests.post(webhook_url, data=data, files=files_data)
            
            # Close file handles
            for _, file_tuple in files_data:
                file_tuple[1].close()
        else:
            # Send text message only
            data = {
                'content': content
            }
            response = requests.post(webhook_url, json=data)
        
        if response.status_code == 204:
            logger.info("Webhook message sent successfully")
            return True
        else:
            logger.error(f"Webhook failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending webhook: {e}")
        return False

def format_findings_message(findings: list[dict], url: str) -> str:
    """Format findings into a Discord message."""
    if not findings:
        return f"✅ **No secrets found in {url}**"
    
    verified_count = sum(1 for f in findings if f.get("Verified", False))
    unverified_count = len(findings) - verified_count
    
    message = f"🚨 **Secrets Found in {url}**\n\n"
    message += f"📊 **Summary:** {len(findings)} total findings\n"
    message += f"✅ Verified: {verified_count}\n"
    message += f"❓ Unverified: {unverified_count}\n\n"
    
    # Show first 10 findings
    for i, f in enumerate(findings[:10]):
        det = f.get("DetectorName", "Unknown")
        verified = "✅" if f.get("Verified", False) else "❓"
        
        # Get raw value
        raw = f.get("Raw") or f.get("Redacted") or f.get("RawV2") or ""
        
        # Try to get line number
        line_no = None
        try:
            line_no = f["SourceMetadata"]["Data"]["Filesystem"].get("line")
        except Exception:
            pass
        
        line_info = f" (Line {line_no})" if line_no else ""
        message += f"• **[{det}]{line_info}**\n  {verified} `{raw}`\n\n"
    
    if len(findings) > 10:
        message += f"... and {len(findings) - 10} more findings\n"
    
    return message

def scan_url(url: str):
    """Scan a URL and send results to Discord webhook."""
    try:
        # Send initial message
        send_webhook_message(f"🚀 **Starting JSHunter scan**\n\nScanning: `{url}`\nPlease wait...")
        
        # Run scan
        findings = run_jshunter_scan(url)
        
        # Format and send results
        if findings:
            message = format_findings_message(findings, url)
            send_webhook_message(message)
            
            # Send result files
            results_dir = Path(__file__).parent.parent / "cli" / "results"
            verified_files = list(results_dir.glob("verified_results_*.json"))
            unverified_files = list(results_dir.glob("unverified_results_*.json"))
            
            files_to_send = []
            
            if verified_files:
                latest_verified = max(verified_files, key=lambda x: x.stat().st_mtime)
                files_to_send.append(latest_verified)
            
            if unverified_files:
                latest_unverified = max(unverified_files, key=lambda x: x.stat().st_mtime)
                files_to_send.append(latest_unverified)
            
            if files_to_send:
                send_webhook_message("📄 **Detailed Results Files:**", files_to_send)
        else:
            send_webhook_message(f"✅ **No secrets found in {url}**")
            
    except Exception as e:
        logger.error(f"Error scanning URL {url}: {e}")
        send_webhook_message(f"❌ **Error scanning URL:** {str(e)}")

def main():
    """Main function for webhook-based scanning."""
    if len(sys.argv) < 2:
        print("Usage: python3 jshunter_webhook.py <URL>")
        print("Example: python3 jshunter_webhook.py https://example.com/script.js")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            print("❌ Invalid URL format. Please provide a valid HTTP/HTTPS URL.")
            sys.exit(1)
    except Exception:
        print("❌ Invalid URL format.")
        sys.exit(1)
    
    print(f"🚀 Starting JSHunter webhook scan for: {url}")
    scan_url(url)
    print("✅ Scan completed and results sent to Discord webhook")

if __name__ == '__main__':
    main()
