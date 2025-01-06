from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import os
from config import FOLDER, HOST, PORT, SSL_KEYFILE, SSL_CERTFILE

app = FastAPI()
# define encoding
app.encoding = 'utf-8'
# sudo cat /var/log/auth.log
# Route to download a file
@app.get("/report")
async def report():
    filename=os.path.join(FOLDER, "last_report.html")
    if not os.path.exists(filename):
        # nothing has changed, 204
        return "No report available", 204
    return FileResponse(filename)

@app.get("/files/<filename>")
async def download_file(filename: str):
    if not os.path.exists(os.path.join(FOLDER, filename)):
        return "File not found", 404
    return FileResponse(os.path.join(FOLDER, filename))

# Start FastAPI server
if __name__ == "__main__":
    uvicorn.run(app = app, host=HOST, port=PORT, ssl_keyfile=SSL_KEYFILE,  ssl_certfile=SSL_CERTFILE)