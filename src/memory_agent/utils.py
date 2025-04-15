"""Utility functions used in our graph."""

import logging
import os
from typing import Dict, Optional, List, Any


def split_model_and_provider(fully_specified_name: str) -> dict:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name
    return {"model": model, "provider": provider}


def setup_async_logging():
    """Set up enhanced logging for asyncio debugging."""
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Configure specific loggers for asyncio and related components
    loggers = [
        "asyncio", 
        "uvicorn", 
        "httpx", 
        "langgraph", 
        "memory_agent",
        "langchain"
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level))
    
    # Enable asyncio debug if requested
    if os.environ.get("PYTHONASYNCIODEBUG") == "1":
        import asyncio
        try:
            # Pokus o získání a nastavení event loopu, ale pouze pokud je dostupný
            loop = asyncio.get_event_loop()
            loop.set_debug(True)
        except RuntimeError:
            # Ignorujeme chybu, pokud není event loop dostupný
            # To se může stát, když je kód volán z ThreadPoolExecutor
            pass


async def safe_async_gather(*tasks) -> List[Any]:
    """Safe wrapper around asyncio.gather that catches and logs exceptions."""
    import asyncio
    
    logger = logging.getLogger(__name__)
    
    # Create list to hold results/errors
    results = []
    
    # Process each task individually
    for i, task in enumerate(tasks):
        try:
            result = await task
            results.append(result)
        except Exception as e:
            logger.error(f"Error in task {i}: {str(e)}", exc_info=True)
            results.append(None)
    
    return results
