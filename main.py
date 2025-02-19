"""
Asynchronous API Data Aggregator
"""
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import from specific module files to avoid any confusion
from api_clients import (
    fetch_weather_data,
    fetch_news_data,
    fetch_stock_data,
    fetch_all_data,
)
from utils.cache import AsyncCacheManager
from utils.rate_limiter import RateLimiter
from utils.logging_config import setup_logging

# Setup logging
logger = setup_logging()

app = FastAPI(
    title="Asynchronous API Data Aggregator",
    description="An API that aggregates data from multiple external APIs concurrently",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize cache and rate limiter
cache_manager = AsyncCacheManager()
rate_limiter = RateLimiter(max_requests=60, time_window=60)  # 60 requests per minute


@app.on_event("startup")
async def startup_event():
    """Initialize async resources on startup"""
    await cache_manager.start()
    logger.info("Application started, background tasks initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    cache_manager.stop()
    logger.info("Application shutdown, resources cleaned up")


# Dependency to enforce rate limiting
async def check_rate_limit():
    if not await rate_limiter.is_allowed():
        logger.warning("Rate limit exceeded")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


# Response models
class WeatherResponse(BaseModel):
    location: str
    temperature: float
    conditions: str
    humidity: Optional[int] = None
    timestamp: str


class NewsResponse(BaseModel):
    articles: List[Dict[str, Any]]
    source: str
    total_results: int


class StockResponse(BaseModel):
    symbol: str
    price: float
    change: float
    volume: int
    timestamp: str


class AggregatedResponse(BaseModel):
    weather: Optional[WeatherResponse] = None
    news: Optional[NewsResponse] = None
    stocks: Optional[StockResponse] = None
    fetched_at: str
    execution_time: float


@app.get("/")
async def root():
    return {"message": "Welcome to the Asynchronous API Data Aggregator"}


@app.get("/api/weather", response_model=WeatherResponse)
async def get_weather(
    location: str = Query(..., description="City name or coordinates"),
    dependencies=[Depends(check_rate_limit)],
):
    # Check cache first
    cache_key = f"weather_{location}"
    cached_data = await cache_manager.get(cache_key)
    if cached_data:
        logger.info(f"Returning cached weather data for {location}")
        return cached_data

    try:
        start_time = time.time()
        data = await fetch_weather_data(location)
        end_time = time.time()
        logger.info(f"Weather data fetched in {end_time - start_time:.2f} seconds")

        # Store in cache (valid for 30 minutes)
        await cache_manager.set(cache_key, data, expiry=1800)
        return data
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching weather data: {str(e)}"
        )


@app.get("/api/news", response_model=NewsResponse)
async def get_news(
    query: str = Query(..., description="News search query"),
    dependencies=[Depends(check_rate_limit)],
):
    cache_key = f"news_{query}"
    cached_data = await cache_manager.get(cache_key)
    if cached_data:
        logger.info(f"Returning cached news data for query: {query}")
        return cached_data

    try:
        start_time = time.time()
        data = await fetch_news_data(query)
        end_time = time.time()
        logger.info(f"News data fetched in {end_time - start_time:.2f} seconds")

        # Store in cache (valid for 15 minutes)
        await cache_manager.set(cache_key, data, expiry=900)
        return data
    except Exception as e:
        logger.error(f"Error fetching news data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching news data: {str(e)}"
        )


@app.get("/api/stocks", response_model=StockResponse)
async def get_stocks(
    symbol: str = Query(..., description="Stock ticker symbol"),
    dependencies=[Depends(check_rate_limit)],
):
    cache_key = f"stocks_{symbol}"
    cached_data = await cache_manager.get(cache_key)
    if cached_data:
        logger.info(f"Returning cached stock data for {symbol}")
        return cached_data

    try:
        start_time = time.time()
        data = await fetch_stock_data(symbol)
        end_time = time.time()
        logger.info(f"Stock data fetched in {end_time - start_time:.2f} seconds")

        # Store in cache (valid for 5 minutes for market data)
        await cache_manager.set(cache_key, data, expiry=300)
        return data
    except Exception as e:
        logger.error(f"Error fetching stock data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching stock data: {str(e)}"
        )


@app.get("/api/aggregate", response_model=AggregatedResponse)
async def get_aggregated_data(
    location: str = Query(..., description="City name for weather data"),
    news_query: str = Query(..., description="News search query"),
    stock_symbol: str = Query(..., description="Stock ticker symbol"),
    dependencies=[Depends(check_rate_limit)],
):
    # Generate a unique cache key for this combination of parameters
    cache_key = f"aggregate_{location}_{news_query}_{stock_symbol}"
    cached_data = await cache_manager.get(cache_key)
    if cached_data:
        logger.info(f"Returning cached aggregated data for {cache_key}")
        return cached_data

    try:
        start_time = time.time()
        weather_data, news_data, stock_data = await fetch_all_data(
            location, news_query, stock_symbol
        )
        end_time = time.time()
        execution_time = end_time - start_time

        response = AggregatedResponse(
            weather=weather_data,
            news=news_data,
            stocks=stock_data,
            fetched_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            execution_time=execution_time,
        )

        logger.info(f"Aggregated data fetched in {execution_time:.2f} seconds")

        # Cache the aggregated response for 5 minutes (300 seconds)
        await cache_manager.set(cache_key, response.dict(), expiry=300)
        return response
    except Exception as e:
        logger.error(f"Error fetching aggregated data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching aggregated data: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)