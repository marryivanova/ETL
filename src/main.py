import sys
import logging
import uvicorn
import asyncio

from fastapi import FastAPI

from src.config.database import AsyncSessionLocal
from src.core.data_loader import load_all_data
from src.core.data_transform import run_transformations
from src.core.service import routers

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = logging.getLogger(__name__)
logger.propagate = False


app = FastAPI()
app.include_router(routers.router)


async def main():
    async with AsyncSessionLocal() as session:
        success = await load_all_data(session)
        await run_transformations(session)

        if success:
            logger.info("Data loading completed successfully")
        else:
            logger.error("Data loading encountered errors")


if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run(app, host="127.0.0.1", port=8000)
