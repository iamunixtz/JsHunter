from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
from datetime import datetime
from pathlib import Path
from ..cli.jsninja import run_trufflehog, download_js, print_summary

app = FastAPI(
    title="JS Ninja Web Scanner",
    description="Web interface for JS Ninja JavaScript security scanner",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="jsninja/web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="jsninja/web/templates")

# Store results by IP (in memory for demo, use proper database in production)
scan_results = {}

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
        
        # Run scan
        results = run_trufflehog(str(file_path))
        
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
        # Download and scan file
        file_path = download_js(url, str(temp_dir))
        if not file_path:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to download JavaScript file"}
            )
        
        # Run scan
        results = run_trufflehog(file_path)
        
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
        "jsninja.web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()