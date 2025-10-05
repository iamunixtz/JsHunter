#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
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
from pathlib import Path
from urllib.parse import urlparse
import requests

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

# Quiet SSL warnings (only when user chooses --ignore-ssl)
try:
    requests.packages.urllib3.disable_warnings() # type: ignore[attr-defined]
except Exception:
    pass

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

def download_js(url: str, ignore_ssl: bool) -> Path | None:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(url, timeout=30, verify=not ignore_ssl)
        r.raise_for_status()
        fname = safe_filename_from_url(url)
        fpath = DOWNLOAD_DIR / fname
        with open(fpath, "w", encoding="utf-8", errors="ignore") as f:
            f.write(r.text)
        print(f"[+] Downloaded {url} -> {fpath}")
        return fpath
    except requests.exceptions.SSLError:
        print(f"[!] SSL error for {url}. Re-run with --ignore-ssl if you want to bypass.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Failed to download {url}: {e}")
    return None

def run_trufflehog(tr_bin: str, file_path: Path) -> list[dict]:
    """Run trufflehog filesystem --json on file and return list of JSON objects."""
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

def print_summary(url: str, findings: list[dict]) -> None:
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

def save_results(url: str, findings: list[dict]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fname_base = safe_filename_from_url(url).rsplit(".js", 1)[0]
    json_path = RESULTS_DIR / f"{fname_base}_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        for obj in findings:
            f.write(json.dumps(obj) + "\n")
    print(f"[+] Raw JSON saved → {json_path}")

# ========== MAIN ==========
def main():
    print(BANNER)
    ap = argparse.ArgumentParser(description="Scan JavaScript URLs with trufflehog (Go v3+) and map results back to the URL.")
    ap.add_argument("-u", "--url", help="Single JavaScript URL to scan")
    ap.add_argument("-f", "--file", help="Path to a file of JavaScript URLs (one per line)")
    ap.add_argument("--ignore-ssl", action="store_true", help="Ignore SSL certificate errors while downloading")
    ap.add_argument("--setup", action="store_true", help="Download and install the latest Go trufflehog binary into ./.bin")
    ap.add_argument("--discord-webhook", help="Discord webhook URL to send verified findings")
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

    # Process URLs
    for url in urls:
        fpath = download_js(url, ignore_ssl=args.ignore_ssl)
        if not fpath:
            continue
        findings = run_trufflehog(tr_bin, fpath)
        print_summary(url, findings)
        save_results(url, findings)
        if args.discord_webhook:
            send_to_discord(args.discord_webhook, url, findings)

if __name__ == "__main__":
    main()
