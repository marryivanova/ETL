import json
import logging
import typing as t
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.core.data_extraction import BaseDataLoader
from src.db.table import ProductDB, UserDB

logger = logging.getLogger(__name__)
logger.propagate = False


class ProductDataLoader(BaseDataLoader):
    """Data loader for product information"""

    def __init__(self):
        super().__init__(settings.API_PRODUCTS)
        self.data_key = 'products'

    async def transform_data(self, raw_data: t.List[t.Dict[str, t.Any]]) -> t.List[t.Dict[str, t.Any]]:
        """Transform product data to database format"""
        return [
            {
                "id": item['id'],
                "title": item['title'],
                "image": item['image'],
                "price": float(item['price']),
                "description": item['description'],
                "brand": item['brand'],
                "model": item['model'],
                "color": item.get('color'),
                "category": item['category'],
                "discount": item.get('discount'),
                "popular": item.get('popular', False),
                "on_sale": item.get('onSale', False),
            }
            for item in raw_data
        ]


class UserDataLoader(BaseDataLoader):
    """Data loader for user information"""

    def __init__(self):
        super().__init__(settings.API_USERS)
        self.data_key = 'users'

    async def transform_data(self, raw_data: t.List[t.Dict[str, t.Any]]) -> t.List[t.Dict[str, t.Any]]:
        """Transform user data to database format"""
        return [
            {
                "id": item['id'],
                "email": item['email'],
                "username": item['username'],
                "password": item['password'],
                "name": {
                    "firstname": item['name']['firstname'],
                    "lastname": item['name']['lastname']
                },
                "address": json.loads(item['address']) if isinstance(item['address'], str) else item['address'],
                "phone": item['phone'],
            }
            for item in raw_data
        ]


async def load_all_data(db_session: AsyncSession) -> bool:
    """Main data loading function that handles both products and users"""
    try:
        product_loader = ProductDataLoader()
        user_loader = UserDataLoader()

        raw_products = await product_loader.fetch_data()
        products = await product_loader.transform_data(raw_products)
        await product_loader.upsert_data(db_session, ProductDB.__table__, products)

        raw_users = await user_loader.fetch_data()
        users = await user_loader.transform_data(raw_users)
        await user_loader.upsert_data(db_session, UserDB.__table__, users)

        return True

    except Exception as e:
        await db_session.rollback()
        logger.error(f"Data loading failed: {str(e)}", exc_info=True)
        return False
