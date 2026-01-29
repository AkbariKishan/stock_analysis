from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import stock, sentiment, analysis

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
