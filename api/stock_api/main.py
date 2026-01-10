from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from stock_service import get_stock_data_with_features

app = FastAPI(title="China Stock Data API", version="1.0.0")


class StockRequest(BaseModel):
    stock_code: str = Field(..., examples=["600519", "000001", "600519.SH"])
    interval: str | int = Field("365d", examples=["30d", "6m", "1y", 365])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stocks/{stock_code}")
def get_stock(stock_code: str, interval: str = Query("365d", description="e.g. 30d / 6m / 1y / 365")):
    return get_stock_data_with_features(stock_code=stock_code, interval=interval)


@app.post("/stocks")
def post_stock(req: StockRequest):
    return get_stock_data_with_features(stock_code=req.stock_code, interval=req.interval)
