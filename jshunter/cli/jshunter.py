#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import asyncio
import aiofiles
import aiohttp
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from urllib.parse import urlparse
import requests
from typing import List, Dict, Optional, Tuple
import signal
import threading
from dataclasses import dataclass

# ========== ASCII BANNER ==========
BANNER = r"""
   __     ______        __  __     __  __     __   __     ______   ______     ______
  /\ \   /\  ___\      /\ \_\ \   /\ \/\ \   /\ "-.\ \   /\__  _\ /\  ___\   /\  == \
 _\_\ \  \ \___  \     \ \  __ \  \ \ \_\ \  \ \ \-.  \  \/_/\ \/ \ \  __\   \ \  __<
/\_____\  \/\_____\     \ \_\ \_\  \ \_____\  \ \_\\"\_\    \ \_\  \ \_____\  \ \_\ \_\
\/_____/   \/_____/      \/_/\/_/   \/_____/   \/_/ \/_/     \/_/   \/_____/   \/_/ /_/

"""

# ========== CONSTANTS ==========
SCRIPT_DIR = Path(__file__).resolve().parent
BIN_DIR = SCRIPT_DIR / ".bin"
DOWNLOAD_DIR = SCRIPT_DIR / "downloaded_js"
RESULTS_DIR = SCRIPT_DIR / "results"
TRUFFLEHOG_ENV = os.environ.get("TRUFFLEHOG_PATH", "")
GITHUB_API_LATEST = "https://api.github.com/repos/trufflesecurity/trufflehog/releases/latest"

# Performance constants
DEFAULT_MAX_WORKERS = 50
DEFAULT_BATCH_SIZE = 100
DEFAULT_CONCURRENT_DOWNLOADS = 200
DEFAULT_CONNECTION_LIMIT = 100
DEFAULT_TIMEOUT = 30
PROGRESS_UPDATE_INTERVAL = 100

# Quiet SSL warnings (only when user chooses --ignore-ssl)
try:
    requests.packages.urllib3.disable_warnings() # type: ignore[attr-defined]
except Exception:
    pass

# ========== PERFORMANCE DATA STRUCTURES ==========
@dataclass
class ScanResult:
    url: str
    file_path: Optional[Path]
    findings: List[Dict]
    download_time: float
    scan_time: float
    success: bool
    error: Optional[str] = None
    verified_findings: List[Dict] = None
    unverified_findings: List[Dict] = None
    
    def __post_init__(self):
        if self.verified_findings is None:
            self.verified_findings = [f for f in self.findings if f.get("Verified", False)]
        if self.unverified_findings is None:
            self.unverified_findings = [f for f in self.findings if not f.get("Verified", False)]

class ProgressTracker:
    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.failed = 0
        self.verified_count = 0
        self.unverified_count = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def update(self, success: bool = True, verified: int = 0, unverified: int = 0):
        with self.lock:
            if success:
                self.completed += 1
            else:
                self.failed += 1
            
            self.verified_count += verified
            self.unverified_count += unverified
            
            if (self.completed + self.failed) % PROGRESS_UPDATE_INTERVAL == 0:
                self.print_progress()
    
    def print_progress(self):
        elapsed = time.time() - self.start_time
        processed = self.completed + self.failed
        rate = processed / elapsed if elapsed > 0 else 0
        eta = (self.total - processed) / rate if rate > 0 else 0
        
        print(f"[PROGRESS] {processed}/{self.total} ({processed/self.total*100:.1f}%) | "
              f"Rate: {rate:.1f}/s | ETA: {eta/60:.1f}m | "
              f"Success: {self.completed} | Failed: {self.failed} | "
              f"Verified: {self.verified_count} | Unverified: {self.unverified_count}")

# Global progress tracker
progress_tracker: Optional[ProgressTracker] = None

# ========== DISCORD WEBHOOK ==========
def send_to_discord(webhook_url: str, url: str, findings: list[dict]) -> None:
    """Send verified findings to Discord webhook in the specified format."""
    verified_findings = [f for f in findings if f.get("Verified", False)]
    if not verified_findings or not webhook_url:
        return

    # Build the message content
    message_lines = [f"🔍 **Verified Secrets found in {url}**"]
    for finding in verified_findings:
        det = finding.get("DetectorName", "Unknown")
        raw = finding.get("Raw") or finding.get("Redacted") or finding.get("RawV2") or ""
        redacted = (raw[:20] + "...") if raw else "(redacted)"
        message_lines.append(f"**[{det}]** `{redacted}` ✅ Verified")

    payload = {
        "content": "\n".join(message_lines),
        "username": "jscannerx Bot",
        "avatar_url": "https://i.imgur.com/4M34hi2.png"
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        print(f"[+] Sent {len(verified_findings)} verified findings to Discord for {url}")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to send to Discord webhook: {e}")

def send_verified_immediately(webhook_url: str, result: ScanResult) -> None:
    """Send verified findings immediately as they are found."""
    if result.verified_findings and webhook_url:
        send_to_discord(webhook_url, result.url, result.verified_findings)

# ========== TRUFFLEHOG DISCOVERY / SETUP ==========
def _supports_filesystem(tr_bin: str) -> bool:
    """Return True if this trufflehog binary supports 'filesystem' subcommand (Go v3+)."""
    try:
        # 'help' or '-h' prints available commands in Go-based trufflehog
        p = subprocess.run([tr_bin, "help"], capture_output=True, text=True)
        out = (p.stdout or "") + (p.stderr or "")
        return "filesystem" in out.lower()
    except Exception:
        return False

def _find_trufflehog() -> str | None:
    """Find a usable trufflehog binary (env → .bin → PATH) that supports 'filesystem'."""
    # 1) Env var
    if TRUFFLEHOG_ENV:
        if Path(TRUFFLEHOG_ENV).is_file() and os.access(TRUFFLEHOG_ENV, os.X_OK):
            if _supports_filesystem(TRUFFLEHOG_ENV):
                return TRUFFLEHOG_ENV
    # 2) Local .bin
    local = BIN_DIR / ("trufflehog.exe" if os.name == "nt" else "trufflehog")
    if local.is_file() and os.access(local, os.X_OK):
        if _supports_filesystem(str(local)):
            return str(local)
    # 3) PATH
    path_bin = shutil.which("trufflehog")
    if path_bin and _supports_filesystem(path_bin):
        return path_bin
    return None

def setup_trufflehog() -> str:
    """Download latest Go-based trufflehog release to ./.bin and return its path."""
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    os_name = platform.system().lower() # 'linux', 'darwin', 'windows'
    arch = platform.machine().lower() # 'x86_64', 'amd64', 'arm64', 'aarch64', ...
    # Normalize arch tokens used in release assets
    arch_candidates = []
    if arch in ["x86_64", "amd64"]:
        arch_candidates = ["x86_64", "amd64"]
    elif arch in ["aarch64", "arm64"]:
        arch_candidates = ["arm64", "aarch64"]
    elif arch.startswith("arm"):
        arch_candidates = ["arm", "armv7", "armv6"]
    else:
        arch_candidates = [arch]

    print("[*] Fetching latest trufflehog release metadata...")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "jscannerx"}
    r = requests.get(GITHUB_API_LATEST, headers=headers, timeout=60)
    r.raise_for_status()
    release = r.json()
    assets = release.get("assets", [])

    def matches(a_name: str) -> bool:
        n = a_name.lower()
        # OS filter
        if os_name not in n:
            return False
        # Archive type
        if os_name == "windows":
            if not n.endswith(".zip"):
                return False
        else:
            if not (n.endswith(".tar.gz") or n.endswith(".tgz")):
                return False
        # Arch match
        return any(a in n for a in arch_candidates)

    asset = next((a for a in assets if matches(a.get("name", ""))), None)
    if not asset or not asset.get("browser_download_url"):
        raise RuntimeError("Could not find a matching trufflehog release asset for your platform.")

    url = asset["browser_download_url"]
    exe_name = "trufflehog.exe" if os_name == "windows" else "trufflehog"
    dest_path = BIN_DIR / exe_name

    print(f"[*] Downloading {asset['name']} ...")
    with tempfile.TemporaryDirectory() as td:
        archive_path = Path(td) / asset["name"]
        with requests.get(url, stream=True, timeout=180) as resp:
            resp.raise_for_status()
            with open(archive_path, "wb") as f:
                for chunk in resp.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)

        # Extract binary
        extracted_path = None
        if str(archive_path).endswith((".tar.gz", ".tgz")):
            with tarfile.open(archive_path, "r:gz") as tar:
                member = next((m for m in tar.getmembers() if os.path.basename(m.name) == exe_name), None)
                if not member:
                    member = next((m for m in tar.getmembers() if m.name.endswith(exe_name)), None)
                if not member:
                    raise RuntimeError("trufflehog binary not found in archive.")
                tar.extract(member, path=td)
                extracted_path = Path(td) / member.name
        elif str(archive_path).endswith(".zip"):
            with zipfile.ZipFile(archive_path, "r") as z:
                member = next((n for n in z.namelist() if os.path.basename(n) == exe_name or n.endswith(exe_name)), None)
                if not member:
                    raise RuntimeError("trufflehog binary not found in archive.")
                z.extract(member, path=td)
                extracted_path = Path(td) / member

        if not extracted_path or not extracted_path.exists():
            raise RuntimeError("Failed to extract trufflehog binary.")

        shutil.move(str(extracted_path), str(dest_path))
        # Make executable
        st = os.stat(dest_path)
        os.chmod(dest_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"[✔] Installed trufflehog → {dest_path}")
    print("[i] Optional: add this to your PATH:")
    print(f" export PATH=\"{BIN_DIR}:${{PATH}}\"")
    return str(dest_path)

# ========== DOWNLOADING & SCANNING ==========
def safe_filename_from_url(url: str) -> str:
    """Create a filesystem-safe filename from a URL."""
    p = urlparse(url)
    base = (p.netloc or "host").replace(":", "_")
    path = (p.path or "/").replace("/", "_")
    fname = (base + path) or "download.js"
    if not fname.endswith(".js"):
        fname += ".js"
    # Also collapse any duplicate underscores
    fname = re.sub(r"_+", "_", fname).strip("_")
    return fname

# ========== HIGH-PERFORMANCE ASYNC DOWNLOADS ==========
async def download_js_async(session: aiohttp.ClientSession, url: str, ignore_ssl: bool) -> Tuple[Optional[Path], float]:
    """Async download with timing."""
    start_time = time.time()
    try:
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        async with session.get(url, timeout=timeout, ssl=not ignore_ssl) as response:
            if response.status == 200:
                content = await response.text()
                fname = safe_filename_from_url(url)
                fpath = DOWNLOAD_DIR / fname
                
                async with aiofiles.open(fpath, "w", encoding="utf-8", errors="ignore") as f:
                    await f.write(content)
                
                return fpath, time.time() - start_time
            else:
                return None, time.time() - start_time
    except Exception:
        return None, time.time() - start_time

async def download_batch_async(urls: List[str], ignore_ssl: bool, max_concurrent: int = DEFAULT_CONCURRENT_DOWNLOADS) -> List[Tuple[str, Optional[Path], float]]:
    """Download multiple URLs concurrently."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    connector = aiohttp.TCPConnector(limit=DEFAULT_CONNECTION_LIMIT, limit_per_host=10)
    timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(url):
            async with semaphore:
                file_path, download_time = await download_js_async(session, url, ignore_ssl)
                return url, file_path, download_time
        
        tasks = [download_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append((urls[results.index(result)], None, 0.0))
            else:
                processed_results.append(result)
        
        return processed_results

def download_js(url: str, ignore_ssl: bool) -> Path | None:
    """Legacy sync download function for backward compatibility."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(url, timeout=30, verify=not ignore_ssl)
        r.raise_for_status()
        fname = safe_filename_from_url(url)
        fpath = DOWNLOAD_DIR / fname
        with open(fpath, "w", encoding="utf-8", errors="ignore") as f:
            f.write(r.text)
        # Only print if not being called from rezon
        if not any('rezon' in arg for arg in sys.argv):
            print(f"[+] Downloaded {url} -> {fpath}")
        return fpath
    except requests.exceptions.SSLError:
        print(f"[!] SSL error for {url}. Re-run with --ignore-ssl if you want to bypass.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to download {url}: {e}")
    return None

# ========== HIGH-PERFORMANCE BATCH SCANNING ==========
def run_trufflehog_batch(tr_bin: str, file_paths: List[Path]) -> List[Tuple[Path, List[Dict]]]:
    """Run trufflehog on multiple files in a single command for efficiency."""
    if not file_paths:
        return []
    
    cmd = [tr_bin, "filesystem"] + [str(p) for p in file_paths] + ["--json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
        
        # Parse results and group by file
        results = {}
        for ln in lines:
            try:
                finding = json.loads(ln)
                # Extract file path from finding metadata
                file_path = None
                try:
                    file_path = Path(finding["SourceMetadata"]["Data"]["Filesystem"]["file"])
                except (KeyError, TypeError):
                    # Fallback: use first file if we can't determine which file
                    file_path = file_paths[0] if file_paths else None
                
                if file_path:
                    if file_path not in results:
                        results[file_path] = []
                    results[file_path].append(finding)
            except json.JSONDecodeError:
                continue
        
        # Return results for each file
        return [(file_path, results.get(file_path, [])) for file_path in file_paths]
        
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        if "unrecognized arguments" in stderr or "usage: trufflehog" in stderr.lower():
            print("[-] This looks like the OLD Python trufflehog (no 'filesystem' support).")
            print(" Run: python3 jscannerx.py --setup to install the modern binary.")
        else:
            print(f"[-] trufflehog error: {stderr or e}")
        return [(fp, []) for fp in file_paths]
    except FileNotFoundError:
        print("[-] trufflehog not found. Run: python3 jscannerx.py --setup")
        return [(fp, []) for fp in file_paths]

def run_trufflehog(tr_bin: str, file_path: Path) -> list[dict]:
    """Legacy single file scanning for backward compatibility."""
    cmd = [tr_bin, "filesystem", str(file_path), "--json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
        out = []
        for ln in lines:
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                # Ignore non-JSON noise
                pass
        return out
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        if "unrecognized arguments" in stderr or "usage: trufflehog" in stderr.lower():
            print("[-] This looks like the OLD Python trufflehog (no 'filesystem' support).")
            print(" Run: python3 jscannerx.py --setup to install the modern binary.")
        else:
            print(f"[-] trufflehog error: {stderr or e}")
        return []
    except FileNotFoundError:
        print("[-] trufflehog not found. Run: python3 jscannerx.py --setup")
        return []

def process_scan_batch(tr_bin: str, download_results: List[Tuple[str, Optional[Path], float]], batch_size: int = DEFAULT_BATCH_SIZE, discord_webhook: Optional[str] = None) -> List[ScanResult]:
    """Process a batch of downloaded files with TruffleHog scanning."""
    results = []
    
    # Group files into batches for efficient scanning
    file_batches = []
    current_batch = []
    
    for url, file_path, download_time in download_results:
        if file_path and file_path.exists():
            current_batch.append((url, file_path, download_time))
            if len(current_batch) >= batch_size:
                file_batches.append(current_batch)
                current_batch = []
    
    if current_batch:
        file_batches.append(current_batch)
    
    # Process each batch
    for batch in file_batches:
        file_paths = [item[1] for item in batch]
        scan_start = time.time()
        
        # Run TruffleHog on the batch
        scan_results = run_trufflehog_batch(tr_bin, file_paths)
        scan_time = time.time() - scan_start
        
        # Create ScanResult objects
        for i, (url, file_path, download_time) in enumerate(batch):
            findings = []
            if i < len(scan_results):
                _, findings = scan_results[i]
            
            result = ScanResult(
                url=url,
                file_path=file_path,
                findings=findings,
                download_time=download_time,
                scan_time=scan_time / len(batch),  # Average scan time per file
                success=file_path is not None and len(findings) >= 0
            )
            results.append(result)
            
            # Send verified findings immediately if Discord webhook is provided
            if discord_webhook and result.verified_findings:
                send_verified_immediately(discord_webhook, result)
    
    # Handle failed downloads
    for url, file_path, download_time in download_results:
        if file_path is None:
            result = ScanResult(
                url=url,
                file_path=None,
                findings=[],
                download_time=download_time,
                scan_time=0.0,
                success=False,
                error="Download failed"
            )
            results.append(result)
    
    return results

def print_summary(url: str, findings: list[dict]) -> None:
    # Only print if not being called from rezon
    if any('rezon' in arg for arg in sys.argv):
        return
        
    if not findings:
        print(f"[*] No secrets found in {url}")
        return
    print(f"[+] Secrets found in {url}:")
    for f in findings:
        det = f.get("DetectorName", "Unknown")
        verified = f.get("Verified", False)
        # Best effort to get line/file
        line_no = None
        try:
            line_no = f["SourceMetadata"]["Data"]["Filesystem"].get("line")
        except Exception:
            pass
        raw = f.get("Raw") or f.get("Redacted") or f.get("RawV2") or ""
        red = (raw[:20] + "...") if raw else "(redacted)"
        if line_no is not None:
            print(f" [{det}] {red} (verified={verified}, line={line_no})")
        else:
            print(f" [{det}] {red} (verified={verified})")

# ========== HIGH-PERFORMANCE PARALLEL PROCESSING ==========
async def process_urls_high_performance(
    urls: List[str], 
    tr_bin: str, 
    ignore_ssl: bool = False,
    max_concurrent_downloads: int = DEFAULT_CONCURRENT_DOWNLOADS,
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_workers: int = DEFAULT_MAX_WORKERS,
    discord_webhook: Optional[str] = None,
    output_file: Optional[str] = None
) -> List[ScanResult]:
    """High-performance parallel processing of URLs."""
    global progress_tracker
    progress_tracker = ProgressTracker(len(urls))
    
    print(f"[*] Starting high-performance scan of {len(urls)} URLs")
    print(f"[*] Configuration: {max_concurrent_downloads} concurrent downloads, {batch_size} batch size, {max_workers} workers")
    
    all_results = []
    
    # Process URLs in chunks to manage memory
    chunk_size = max_concurrent_downloads * 2  # Process 2x download capacity at once
    
    for i in range(0, len(urls), chunk_size):
        chunk_urls = urls[i:i + chunk_size]
        print(f"[*] Processing chunk {i//chunk_size + 1}/{(len(urls) + chunk_size - 1)//chunk_size} ({len(chunk_urls)} URLs)")
        
        # Download chunk
        download_results = await download_batch_async(chunk_urls, ignore_ssl, max_concurrent_downloads)
        
        # Process downloads in parallel batches
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Split download results into batches for parallel processing
            download_batches = [download_results[j:j + batch_size] for j in range(0, len(download_results), batch_size)]
            
            # Submit batch processing tasks
            future_to_batch = {
                executor.submit(process_scan_batch, tr_bin, batch, batch_size, discord_webhook): batch 
                for batch in download_batches
            }
            
            # Collect results
            for future in future_to_batch:
                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                    
                    # Update progress with verified/unverified counts
                    for result in batch_results:
                        progress_tracker.update(
                            result.success, 
                            len(result.verified_findings), 
                            len(result.unverified_findings)
                        )
                        
                except Exception as e:
                    print(f"[-] Error processing batch: {e}")
                    # Mark batch as failed
                    batch = future_to_batch[future]
                    for url, _, _ in batch:
                        progress_tracker.update(False)
    
    # Final progress report
    progress_tracker.print_progress()
    
    # Save results (verified and unverified separately)
    if output_file:
        verified_file_path, unverified_file_path = save_results_batch(all_results, output_file)
    else:
        verified_file_path, unverified_file_path = save_results_batch(all_results)
    
    # Send unverified findings file to Discord after scan completion
    if discord_webhook and unverified_file_path:
        send_unverified_file_to_discord(discord_webhook, unverified_file_path)
    
    # Clean up downloaded files
    cleanup_downloaded_files(all_results)
    
    # Print final summary
    total_verified = sum(len(r.verified_findings) for r in all_results)
    total_unverified = sum(len(r.unverified_findings) for r in all_results)
    successful_scans = sum(1 for r in all_results if r.success)
    
    print(f"\n[+] Scan Summary:")
    print(f"    Total URLs: {len(urls)}")
    print(f"    Successful scans: {successful_scans}")
    print(f"    Failed scans: {len(urls) - successful_scans}")
    print(f"    Verified findings: {total_verified}")
    print(f"    Unverified findings: {total_unverified}")
    print(f"    Total findings: {total_verified + total_unverified}")
    
    return all_results

def save_results_batch(results: List[ScanResult], output_file: Optional[str] = None) -> Tuple[Optional[Path], Optional[Path]]:
    """Save batch results efficiently with separate verified/unverified files."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    
    # Collect all verified and unverified findings
    all_verified = []
    all_unverified = []
    
    for result in results:
        if result.verified_findings:
            for finding in result.verified_findings:
                finding["source_url"] = result.url  # Add source URL for tracking
                all_verified.append(finding)
        
        if result.unverified_findings:
            for finding in result.unverified_findings:
                finding["source_url"] = result.url  # Add source URL for tracking
                all_unverified.append(finding)
    
    verified_file_path = None
    unverified_file_path = None
    
    # Save verified findings
    if all_verified:
        if output_file:
            verified_file = output_file.replace(".json", "_verified.json")
        else:
            verified_file = RESULTS_DIR / f"verified_results_{timestamp}.json"
        
        with open(verified_file, "w", encoding="utf-8") as f:
            for finding in all_verified:
                f.write(json.dumps(finding) + "\n")
        print(f"[+] Verified findings saved → {verified_file} ({len(all_verified)} findings)")
        verified_file_path = verified_file
    
    # Save unverified findings
    if all_unverified:
        if output_file:
            unverified_file = output_file.replace(".json", "_unverified.json")
        else:
            unverified_file = RESULTS_DIR / f"unverified_results_{timestamp}.json"
        
        with open(unverified_file, "w", encoding="utf-8") as f:
            for finding in all_unverified:
                f.write(json.dumps(finding) + "\n")
        print(f"[+] Unverified findings saved → {unverified_file} ({len(all_unverified)} findings)")
        unverified_file_path = unverified_file
    
    # Save combined results if requested
    if output_file and (all_verified or all_unverified):
        with open(output_file, "w", encoding="utf-8") as f:
            for finding in all_verified + all_unverified:
                f.write(json.dumps(finding) + "\n")
        print(f"[+] Combined results saved → {output_file}")
    
    if not all_verified and not all_unverified:
        print("[*] No findings to save")
    
    return verified_file_path, unverified_file_path

def cleanup_downloaded_files(results: List[ScanResult]) -> None:
    """Clean up downloaded JavaScript files after processing."""
    cleaned_count = 0
    for result in results:
        if result.file_path and result.file_path.exists():
            try:
                result.file_path.unlink()
                cleaned_count += 1
            except Exception as e:
                print(f"[-] Failed to delete {result.file_path}: {e}")
    
    if cleaned_count > 0:
        print(f"[+] Cleaned up {cleaned_count} downloaded files")

def send_discord_batch(webhook_url: str, results: List[ScanResult]) -> None:
    """Send batch results to Discord efficiently."""
    verified_findings = []
    for result in results:
        if result.findings:
            for finding in result.findings:
                if finding.get("Verified", False):
                    verified_findings.append((result.url, finding))
    
    if not verified_findings:
        return
    
    # Group by URL to avoid spam
    url_findings = {}
    for url, finding in verified_findings:
        if url not in url_findings:
            url_findings[url] = []
        url_findings[url].append(finding)
    
    # Send one message per URL with multiple findings
    for url, findings in url_findings.items():
        send_to_discord(webhook_url, url, findings)

def send_unverified_file_to_discord(webhook_url: str, unverified_file_path: Path) -> None:
    """Send unverified results file to Discord after scan completion."""
    if not unverified_file_path.exists() or not webhook_url:
        return
    
    try:
        # Read the unverified file content
        with open(unverified_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create Discord message with file attachment
        payload = {
            "content": f"📄 **Unverified Findings Report**\n\nScan completed. Here are the unverified findings that require manual review:",
            "username": "jscannerx Bot",
            "avatar_url": "https://i.imgur.com/4M34hi2.png"
        }
        
        # Send the message first
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        
        # Send the file as a follow-up message
        files = {
            'file': (unverified_file_path.name, content, 'application/json')
        }
        
        file_payload = {
            "content": f"📎 **Unverified findings file**: `{unverified_file_path.name}`",
            "username": "jscannerx Bot",
            "avatar_url": "https://i.imgur.com/4M34hi2.png"
        }
        
        response = requests.post(
            webhook_url,
            data=file_payload,
            files=files,
            timeout=30
        )
        response.raise_for_status()
        
        print(f"[+] Sent unverified findings file to Discord: {unverified_file_path.name}")
        
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to send unverified file to Discord: {e}")
    except Exception as e:
        print(f"[-] Error sending unverified file: {e}")

def save_results(url: str, findings: list[dict], output_file: str = None) -> None:
    """Legacy save function for backward compatibility."""
    if output_file:
        # Save to specified output file
        with open(output_file, "w", encoding="utf-8") as f:
            for obj in findings:
                f.write(json.dumps(obj) + "\n")
        # Only print if not being called from rezon
        if not any('rezon' in arg for arg in sys.argv):
            print(f"[+] Results saved → {output_file}")
    else:
        # Save to default results directory
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        fname_base = safe_filename_from_url(url).rsplit(".js", 1)[0]
        json_path = RESULTS_DIR / f"{fname_base}_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            for obj in findings:
                f.write(json.dumps(obj) + "\n")
        # Only print if not being called from rezon
        if not any('rezon' in arg for arg in sys.argv):
            print(f"[+] Raw JSON saved → {json_path}")

# ========== MAIN ==========
def main():
    # Only print banner if not being called from another script
    if not any('rezon' in arg for arg in sys.argv):
        print(BANNER)
    ap = argparse.ArgumentParser(description="High-performance JavaScript URL scanner with trufflehog (Go v3+)")
    ap.add_argument("-u", "--url", help="Single JavaScript URL to scan")
    ap.add_argument("-f", "--file", help="Path to a file of JavaScript URLs (one per line)")
    ap.add_argument("-o", "--output", help="Output file to save results")
    ap.add_argument("--ignore-ssl", action="store_true", help="Ignore SSL certificate errors while downloading")
    ap.add_argument("--setup", action="store_true", help="Download and install the latest Go trufflehog binary into ./.bin")
    ap.add_argument("--discord-webhook", help="Discord webhook URL to send verified findings")
    
    # High-performance options
    ap.add_argument("--high-performance", action="store_true", help="Enable high-performance parallel processing")
    ap.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS, help=f"Maximum number of worker threads (default: {DEFAULT_MAX_WORKERS})")
    ap.add_argument("--concurrent-downloads", type=int, default=DEFAULT_CONCURRENT_DOWNLOADS, help=f"Maximum concurrent downloads (default: {DEFAULT_CONCURRENT_DOWNLOADS})")
    ap.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help=f"Batch size for TruffleHog scanning (default: {DEFAULT_BATCH_SIZE})")
    ap.add_argument("--connection-limit", type=int, default=DEFAULT_CONNECTION_LIMIT, help=f"HTTP connection limit (default: {DEFAULT_CONNECTION_LIMIT})")
    ap.add_argument("-v", "--version", action="version", version="JSHunter 2.0.0")
    
    args = ap.parse_args()

    if args.setup:
        try:
            setup_trufflehog()
            print("[✔] Setup complete. Now run your scan, e.g.:")
            print(' python3 jscannerx.py -u "http://127.0.0.1:5000/static/demo.js"')
        except Exception as e:
            print(f"[-] Setup failed: {e}")
            sys.exit(2)
        return

    # Normal scan path: do NOT auto-install. Require a usable binary.
    tr_bin = _find_trufflehog()
    if not tr_bin:
        print("[-] No usable trufflehog (Go v3+) found on your system.")
        print(" Run setup first: python3 jscannerx.py --setup")
        sys.exit(1)

    # Build URL list
    urls: list[str] = []
    if args.url:
        urls.append(args.url.strip())
    if args.file:
        fpath = Path(args.file)
        if not fpath.is_file():
            print(f"[-] URLs file not found: {args.file}")
            sys.exit(1)
        with open(fpath, "r", encoding="utf-8") as f:
            urls.extend([ln.strip() for ln in f if ln.strip()])

    if not urls:
        ap.print_help()
        sys.exit(1)

    # Choose processing mode
    if args.high_performance or len(urls) > 100:
        # High-performance mode for large batches
        print(f"[*] Using high-performance mode for {len(urls)} URLs")
        print(f"[*] Performance settings: {args.max_workers} workers, {args.concurrent_downloads} concurrent downloads, {args.batch_size} batch size")
        
        # Run async high-performance processing
        try:
            results = asyncio.run(process_urls_high_performance(
                urls=urls,
                tr_bin=tr_bin,
                ignore_ssl=args.ignore_ssl,
                max_concurrent_downloads=args.concurrent_downloads,
                batch_size=args.batch_size,
                max_workers=args.max_workers,
                discord_webhook=args.discord_webhook,
                output_file=args.output
            ))
            
            # Print summary
            total_findings = sum(len(r.findings) for r in results)
            successful_scans = sum(1 for r in results if r.success)
            print(f"\n[+] Scan complete: {successful_scans}/{len(urls)} successful, {total_findings} total findings")
            
        except KeyboardInterrupt:
            print("\n[!] Scan interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"[-] High-performance scan failed: {e}")
            sys.exit(1)
    else:
        # Legacy sequential mode for small batches
        print(f"[*] Using legacy mode for {len(urls)} URLs")
        for url in urls:
            fpath = download_js(url, ignore_ssl=args.ignore_ssl)
            if not fpath:
                continue
            findings = run_trufflehog(tr_bin, fpath)
            print_summary(url, findings)
            save_results(url, findings, args.output)
            if args.discord_webhook:
                send_to_discord(args.discord_webhook, url, findings)

if __name__ == "__main__":
    main()
