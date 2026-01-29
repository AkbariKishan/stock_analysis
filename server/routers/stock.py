from fastapi import APIRouter, HTTPException
from ..services.market_data import MarketDataService

router = APIRouter(prefix="/api/stock", tags=["stock"])

@router.get("/{symbol}/history")
async def get_stock_history(symbol: str, period: str = "1y", interval: str = "1d"):
    """
    Get historical stock data with price and volume.
    """
    result = MarketDataService.get_stock_history(symbol, period, interval)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/{symbol}/info")
async def get_stock_info(symbol: str):
    """
    Get company fundamental information.
    """
    result = MarketDataService.get_company_info(symbol)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
