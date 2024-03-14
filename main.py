from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
from time import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from fastapi.logger import logger as fastapi_logger
from contextlib import asynccontextmanager
import sqlite3
from datetime import datetime, timedelta
import pytz  # Make sure to install the 'pytz' library if you haven't already


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    global cur,con
    con = sqlite3.connect("apiLogs.db")
    cur = con.cursor()  
    cur.execute("""CREATE TABLE IF NOT EXISTS apilogging (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time DATETIME,
    apiname TEXT,
    executiontime INTEGER,
    status TEXT
    );""")
    yield
    con.close()


app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time()
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    response = await call_next(request)
    fastapi_logger.info(
                f"""
                "status": "success",
                'hostname': {request.url.hostname}
                'ip_address': {request.client.host}
                'path': {request.url}
                'method': {request.method}
                'status': {response.status_code}
                'response_time': {int((time() - start)*1000)} MS
                """)
    # Insert data into the table
    data_to_insert = (current_time, str(request.url), int((time() - start)*1000), str(response.status_code))
    insert_query = "INSERT INTO apilogging (time, apiname, executiontime, status) VALUES ( ?, ?, ?, ?)"
    cur.execute(insert_query, data_to_insert)

    # Commit the changes to the database
    con.commit()
    return response

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/route")
def read_root():
    return {"Hello": "route"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000,log_config="log.ini")
