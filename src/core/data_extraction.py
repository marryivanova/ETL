import httpx
import json
import logging

import typing as t
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Table


logger = logging.getLogger(__name__)
logger.propagate = False


class BaseDataLoader:
    """Base class for data loading operations"""

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.data_key = 'items'

    async def fetch_data(self) -> t.List[t.Dict[str, t.Any]]:
        """Fetch data from API endpoint"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.api_url)
                response.raise_for_status()
                data = response.json()
                return data.get(self.data_key, [])
        except httpx.HTTPError as e:
            logger.error(f"API request failed: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            return []

    async def transform_data(self, raw_data: t.List[t.Dict[str, t.Any]]) -> t.List[t.Dict[str, t.Any]]:
        """Transform API data to database format"""
        raise NotImplementedError("Subclasses must implement this method")

    async def upsert_data(
            self,
            db_session: AsyncSession,
            table: Table,
            data: t.List[t.Dict[str, t.Any]],
            conflict_index: str = 'id',
            exclude_fields: t.List[str] = None
    ) -> int:
        """
        Perform bulk upsert operation (insert or update on conflict)

        Args:
            db_session: Database session
            table: SQLAlchemy table object
            data: List of dictionaries with data
            conflict_index: Column name for conflict resolution
            exclude_fields: Fields to exclude from updates

        Returns:
            Number of affected rows
        """
        if not data:
            logger.warning(f"No {self.data_key} received from API")
            return 0

        if exclude_fields is None:
            exclude_fields = []

        update_mapping = {
            col.name: getattr(insert(table).excluded, col.name)
            for col in table.columns
            if col.name != conflict_index and col.name not in exclude_fields
        }

        stmt = insert(table).values(data)
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[conflict_index],
            set_=update_mapping
        )

        result = await db_session.execute(upsert_stmt)
        await db_session.commit()
        logger.info(f"Successfully upserted {len(data)} {self.data_key}")
        return len(data)

