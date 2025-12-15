"""Simple test script to verify server functionality."""

import asyncio
import httpx
import sys
import time
import logging
import threading
import uvicorn
from pathlib import Path
from datetime import datetime

# Configure logging to file
log_file = f"test_server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test")


async def test_server():
    """Test the CIP server endpoints."""
    base_url = "http://localhost:8420"
    
    # Wait for server to be ready
    logger.info("Waiting for server to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{base_url}/health")
                if response.status_code == 200:
                    logger.info("Server is ready!")
                    break
        except (httpx.ConnectError, httpx.TimeoutException):
            if i < max_retries - 1:
                await asyncio.sleep(1)
            else:
                logger.error("Server did not start in time")
                return False
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Test health check
        logger.info("Testing health check...")
        response = await client.get(f"{base_url}/health")
        logger.info(f"Health: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        
        # Test indexing a small directory
        logger.info("\nTesting indexing...")
        cip_core_path = str(Path(__file__).parent.parent)
        response = await client.post(
            f"{base_url}/api/index/repo",
            json={"path": cip_core_path, "force": True}
        )
        logger.info(f"Index: {response.status_code}")
        result = response.json()
        logger.info(f"Result: {result}")
        job_id = result.get("job_id")
        
        # Wait a bit for indexing to start
        await asyncio.sleep(5)
        
        # Wait for indexing to complete (poll every 10s for up to 3 minutes)
        logger.info("\nWaiting for indexing to complete...")
        max_wait = 180  # 3 minutes
        start = time.time()
        while time.time() - start < max_wait:
            try:
                # Check sync status
                response = await client.get(f"{base_url}/api/index/status/cip-core", timeout=10.0)
                status_data = response.json()
                nodes = status_data.get("nodes_count", 0)
                edges = status_data.get("edges_count", 0)
                status = status_data.get("status", "unknown")
                logger.info(f"Status: {status}, Nodes: {nodes}, Edges: {edges}")
                
                if status == "synced" and nodes > 0:
                    logger.info("Indexing complete!")
                    break
            except Exception as e:
                logger.warning(f"Status check failed: {e}")
            
            await asyncio.sleep(10)
        else:
            logger.warning("Indexing did not complete in time, continuing...")
        
        # Final status check
        logger.info("\nFinal sync status...")
        response = await client.get(f"{base_url}/api/index/status/cip-core")
        logger.info(f"Response: {response.json()}")
        
        # Test queue status
        logger.info("\nTesting queue status...")
        try:
            response = await client.get(f"{base_url}/api/index/queue", timeout=10.0)
            logger.info(f"Queue: {response.status_code}")
            logger.info(f"Response: {response.json()}")
        except Exception as e:
            logger.warning(f"Queue status check failed: {e}")
        
        # Test query
        logger.info("\nTesting query...")
        response = await client.post(
            f"{base_url}/api/graph/query",
            json={"query": "validation", "limit": 5}
        )
        logger.info(f"Query: {response.status_code}")
        results = response.json()
        logger.info(f"Found {results.get('count', 0)} results")
        for i, result in enumerate(results.get('results', [])[:3]):
            logger.info(f"\n{i+1}. Type: {result.get('type')}")
            logger.info(f"   Path: {result.get('path')}")
            logger.info(f"   Content: {result.get('content', '')[:100]}...")
        
        logger.info("\n[SUCCESS] All tests completed!")
        return True


def run_server():
    """Run the server in a thread."""
    import os
    os.chdir(Path(__file__).parent)
    
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8420,
        log_level="info",
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.FileHandler",
                    "filename": log_file,
                    "formatter": "default",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["file"],
            },
        }
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    logger.info("="*60)
    logger.info("CIP Server End-to-End Test")
    logger.info("="*60)
    logger.info(f"Logs will be written to: {log_file}")
    logger.info("")
    
    # Start server in a thread
    logger.info("Starting server in background thread...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(2)
    
    try:
        # Run tests
        success = asyncio.run(test_server())
        
        if success:
            logger.info("\n[SUCCESS] All tests passed!")
            logger.info(f"Full logs available in: {log_file}")
            sys.exit(0)
        else:
            logger.error("\n[FAILED] Tests failed!")
            logger.info(f"Full logs available in: {log_file}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"\n[ERROR] Error: {e}", exc_info=True)
        logger.info(f"Full logs available in: {log_file}")
        sys.exit(1)
    finally:
        logger.info("\nShutting down server...")
        # Server thread is daemon, so it will be killed when main exits
