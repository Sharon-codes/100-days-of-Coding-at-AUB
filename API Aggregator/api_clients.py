"""
API Client functions for fetching data from external services
"""
import asyncio
import logging
import time
from typing import Dict, Any, Tuple, List, Optional, AsyncGenerator
from datetime import datetime

import httpx
from httpx import AsyncClient, Timeout, Limits
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Constants
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_API_KEY = "4c4c7a7be8e065b7d4c0fc6fa9522df5"  

NEWS_API_URL = "https://newsapi.org/v2/everything"
NEWS_API_KEY = "37456e610904406284f6edcd5e9ed5e4"  # Replace with actual key

STOCK_API_URL = "https://www.alphavantage.co/query"
STOCK_API_KEY = "XLXXX60LPJVF9NRS"  # Replace with actual key

# Common HTTP client configuration
timeout = Timeout(10.0, connect=5.0)  # 10 seconds total, 5 seconds for connection
limits = Limits(max_keepalive_connections=5, max_connections=10)


async def get_client() -> AsyncClient:
    """Create and return a configured HTTP client"""
    return AsyncClient(timeout=timeout, limits=limits)


async def fetch_with_retry(
    client: AsyncClient,
    url: str,
    params: Dict[str, Any],
    max_retries: int = 3,
    backoff_factor: float = 0.5,
) -> Dict[str, Any]:
    """
    Fetch data from URL with automatic retries and exponential backoff
    """
    retries = 0
    last_exception = None

    while retries < max_retries:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Too Many Requests
                retries += 1
                wait_time = backoff_factor * (2 ** retries)
                logger.warning(
                    f"Rate limit hit, retrying after {wait_time:.1f} seconds..."
                )
                await asyncio.sleep(wait_time)
                last_exception = e
            else:
                # If it's a different HTTP error, don't retry
                logger.error(
                    f"HTTP error {e.response.status_code} when requesting {url}"
                )
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"External API error: {e.response.text}",
                )
        except httpx.RequestError as e:
            # For network-related errors, retry
            retries += 1
            wait_time = backoff_factor * (2 ** retries)
            logger.warning(
                f"Request error: {str(e)}. Retrying after {wait_time:.1f} seconds..."
            )
            await asyncio.sleep(wait_time)
            last_exception = e
        except Exception as e:
            logger.error(f"Unexpected error when requesting {url}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Unexpected error: {str(e)}"
            )

    # If we've exhausted retries, raise the last exception
    logger.error(f"Max retries reached for {url}")
    if isinstance(last_exception, httpx.HTTPStatusError):
        raise HTTPException(
            status_code=last_exception.response.status_code,
            detail=f"External API error after max retries: {last_exception.response.text}",
        )
    raise HTTPException(
        status_code=500,
        detail=f"Failed after {max_retries} retries: {str(last_exception)}",
    )


async def fetch_weather_data(location: str) -> Dict[str, Any]:
    """Fetch weather data for a specific location"""
    async with get_client() as client:
        params = {
            "q": location,
            "units": "metric",
            "appid": WEATHER_API_KEY,
        }
        try:
            raw_data = await fetch_with_retry(client, WEATHER_API_URL, params)
            
            # Transform the raw data into the expected response format
            weather_data = {
                "location": location,
                "temperature": raw_data["main"]["temp"],
                "conditions": raw_data["weather"][0]["description"],
                "humidity": raw_data["main"]["humidity"],
                "timestamp": datetime.now().isoformat(),
            }
            return weather_data
        except Exception as e:
            logger.error(f"Error in fetch_weather_data: {str(e)}")
            raise


async def fetch_news_data(query: str) -> Dict[str, Any]:
    """Fetch news articles based on a search query"""
    async with get_client() as client:
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "apiKey": NEWS_API_KEY,
        }
        try:
            raw_data = await fetch_with_retry(client, NEWS_API_URL, params)
            
            # Transform the raw data
            news_data = {
                "articles": raw_data["articles"][:10],  # Limit to top 10 articles
                "source": "NewsAPI",
                "total_results": raw_data["totalResults"]
            }
            return news_data
        except Exception as e:
            logger.error(f"Error in fetch_news_data: {str(e)}")
            raise


async def fetch_stock_data(symbol: str) -> Dict[str, Any]:
    """Fetch stock market data for a specific symbol"""
    async with get_client() as client:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": STOCK_API_KEY,
        }
        try:
            raw_data = await fetch_with_retry(client, STOCK_API_URL, params)
            
            # Transform the raw data
            quote = raw_data.get("Global Quote", {})
            if not quote:
                raise HTTPException(status_code=404, detail=f"Stock symbol {symbol} not found")
                
            stock_data = {
                "symbol": symbol,
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "volume": int(quote.get("06. volume", 0)),
                "timestamp": datetime.now().isoformat(),
            }
            return stock_data
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in fetch_stock_data: {str(e)}")
            raise


async def fetch_all_data(
    location: str, news_query: str, stock_symbol: str
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Fetch data from all APIs concurrently
    Returns a tuple of (weather_data, news_data, stock_data)
    """
    try:
        # Run all API fetches concurrently
        weather_task = asyncio.create_task(fetch_weather_data(location))
        news_task = asyncio.create_task(fetch_news_data(news_query))
        stock_task = asyncio.create_task(fetch_stock_data(stock_symbol))
        
        # Wait for all tasks to complete
        weather_data, news_data, stock_data = await asyncio.gather(
            weather_task, news_task, stock_task
        )
        
        return weather_data, news_data, stock_data
    except Exception as e:
        logger.error(f"Error in fetch_all_data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error aggregating data from multiple APIs: {str(e)}",
        )


async def stream_large_dataset(query: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Example of an async generator that could be used for streaming large datasets
    This is just a placeholder implementation
    """
    # In a real implementation, you might use pagination to fetch large datasets incrementally
    page = 1
    page_size = 10
    total_results = None
    
    async with get_client() as client:
        while total_results is None or (page - 1) * page_size < total_results:
            params = {
                "q": query,
                "page": page,
                "pageSize": page_size,
                "apiKey": NEWS_API_KEY,
            }
            
            try:
                data = await fetch_with_retry(client, NEWS_API_URL, params)
                if total_results is None:
                    total_results = data["totalResults"]
                
                # Yield batch of results
                yield {
                    "page": page,
                    "articles": data["articles"],
                    "total_pages": (total_results + page_size - 1) // page_size
                }
                
                # No more results, stop iteration
                if not data["articles"]:
                    break
                    
                page += 1
                
            except Exception as e:
                logger.error(f"Error streaming large dataset: {str(e)}")
                raise