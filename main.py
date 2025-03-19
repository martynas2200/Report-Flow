from config import DATA_FOLDER, HOST, PORT, SSL_KEYFILE, SSL_CERTFILE
from datetime import datetime
from fastapi import FastAPI, Request, Query, Depends, Response
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, conint
import os
import uvicorn

app = FastAPI()
# define encoding
app.encoding = 'utf-8'
# sudo cat /var/log/auth.log

templates = Jinja2Templates(directory="templates")

class ReportQueryParams(BaseModel):
    week: conint(ge=1, le=52) = Query(..., description="Week number (1-52)")
    year: conint(ge=2024) = Query(..., description="Year (2024 or later)")
    download: bool = Query(False, description="Download the report")

@app.get("/report")
async def report(request: Request, query_params: ReportQueryParams = Depends()):
    week = query_params.week
    year = query_params.year
    download = query_params.download
    if download:
        return await serve_file(f"Nukainavimai_{year}_{week}_savaite.xlsx")
    else:
        return await serve_file(f"report_{year}_{week}.html")

@app.get("/files/{filename}")
async def serve_file(filename: str):
    if not os.path.exists(os.path.join(DATA_FOLDER, filename)):
        return "File not found", 404
    return FileResponse(os.path.join(DATA_FOLDER, filename))

@app.get("/")
async def index(request: Request):
    current_date = datetime.now()
    current_year = current_date.year
    return templates.TemplateResponse("index.html", {"request": request, "year": current_year})

# Start FastAPI server
if __name__ == "__main__":
    uvicorn.run(app = app, host=HOST, port=PORT, ssl_keyfile=SSL_KEYFILE,  ssl_certfile=SSL_CERTFILE)