from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

app = FastAPI(
    title="JSHunter Web Scanner",
    description="Web interface for JSHunter High-Performance JavaScript security scanner",
    version="2.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="jshunter/web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="jshunter/web/templates")

# Store results by IP (in memory for demo, use proper database in production)
scan_results = {}

# Helper functions for the enhanced jshunter
def run_jshunter_scan(url: str) -> List[Dict]:
    """Run jshunter scan on a URL and return results."""
    try:
        # Use the enhanced jshunter CLI
        result = subprocess.run([
            "python3", "jshunter/cli/jshunter", 
            "--high-performance", 
            "-u", url
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return []
        
        # Parse results from the output (simplified for web interface)
        findings = []
        lines = result.stdout.split('\n')
        for line in lines:
            if '[Infura]' in line or '[GitHub]' in line or '[AWS]' in line:
                # Parse finding line
                parts = line.split(']')
                if len(parts) >= 2:
                    detector = parts[0].replace('[', '').strip()
                    rest = parts[1].strip()
                    verified = 'verified=True' in rest
                    findings.append({
                        "detector": detector,
                        "verified": verified,
                        "raw": rest.split('(')[0].strip() if '(' in rest else rest
                    })
        
        return findings
    except Exception as e:
        print(f"Error running jshunter: {e}")
        return []

def run_jshunter_file_scan(file_path: str) -> List[Dict]:
    """Run jshunter scan on a local file and return results."""
    try:
        # Create a temporary URL file
        temp_url_file = f"/tmp/url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(temp_url_file, 'w') as f:
            f.write(f"file://{file_path}")
        
        result = subprocess.run([
            "python3", "jshunter/cli/jshunter", 
            "--high-performance", 
            "-f", temp_url_file
        ], capture_output=True, text=True, timeout=60)
        
        # Cleanup
        if os.path.exists(temp_url_file):
            os.remove(temp_url_file)
        
        if result.returncode != 0:
            return []
        
        # Parse results (same as URL scan)
        findings = []
        lines = result.stdout.split('\n')
        for line in lines:
            if '[Infura]' in line or '[GitHub]' in line or '[AWS]' in line:
                parts = line.split(']')
                if len(parts) >= 2:
                    detector = parts[0].replace('[', '').strip()
                    rest = parts[1].strip()
                    verified = 'verified=True' in rest
                    findings.append({
                        "detector": detector,
                        "verified": verified,
                        "raw": rest.split('(')[0].strip() if '(' in rest else rest
                    })
        
        return findings
    except Exception as e:
        print(f"Error running jshunter on file: {e}")
        return []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/scan/file")
async def scan_file(request: Request, file: UploadFile = File(...)):
    client_ip = request.client.host
    
    # Create temporary directory for the file
    temp_dir = Path("temp") / datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = temp_dir / file.filename
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Run scan using enhanced jshunter
        results = run_jshunter_file_scan(str(file_path))
        
        # Store results for this IP
        if client_ip not in scan_results:
            scan_results[client_ip] = []
        scan_results[client_ip].append({
            "timestamp": datetime.now().isoformat(),
            "filename": file.filename,
            "results": results
        })
        
        return JSONResponse(content={"results": results})
        
    finally:
        # Cleanup
        if file_path.exists():
            file_path.unlink()
        if temp_dir.exists():
            temp_dir.rmdir()

@app.post("/scan/url")
async def scan_url(request: Request, url: str = Form(...)):
    client_ip = request.client.host
    
    # Create temporary directory
    temp_dir = Path("temp") / datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run scan using enhanced jshunter (it handles downloading internally)
        results = run_jshunter_scan(url)
        
        # Store results for this IP
        if client_ip not in scan_results:
            scan_results[client_ip] = []
        scan_results[client_ip].append({
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "results": results
        })
        
        return JSONResponse(content={"results": results})
        
    finally:
        # Cleanup
        if temp_dir.exists():
            for file in temp_dir.glob("*"):
                file.unlink()
            temp_dir.rmdir()

@app.get("/results")
async def get_results(request: Request):
    client_ip = request.client.host
    return JSONResponse(content={
        "results": scan_results.get(client_ip, [])
    })

def main():
    uvicorn.run(
        "jshunter.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
