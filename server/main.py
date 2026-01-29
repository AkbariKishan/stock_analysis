from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import stock, sentiment, analysis
from dotenv import load_dotenv, find_dotenv
import os

# Explicitly find and load .env from project root
# This fixes issue where uvicorn running from different cwd fails to find .env
load_dotenv(find_dotenv())

app = FastAPI(title="Stock Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stock.router)
app.include_router(sentiment.router)
app.include_router(analysis.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Stock Analysis API is running"}
