import json
import logging
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config.settings import settings
from src.core.models.scheme import User, Product
from src.db.table import ProductDB, UserDB, MostExpensive, OdsUser

logger = logging.getLogger(__name__)
logger.propagate = False

Base = declarative_base()


async def init_db():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def load_products(session, products: [Product]):
    for product in products:
        db_product = ProductDB(
            id=product.id,
            title=product.title,
            image=product.image,
            price=product.price,
            description=product.description,
            brand=product.brand,
            model=product.model,
            color=product.color,
            category=product.category,
            discount=product.discount,
            popular=product.popular,
            on_sale=product.onSale,
        )
        session.add(db_product)
    await session.commit()


async def load_users(session, users: [User]):
    for user in users:
        db_user = UserDB(
            id=user.id,
            email=user.email,
            username=user.username,
            password=user.password,
            name={"firstname": user.name.firstname, "lastname": user.name.lastname},
            address=json.loads(user.address.json()),
            phone=user.phone,
        )
        session.add(db_user)
    await session.commit()


async def create_most_expensive_table_orm(db_session: AsyncSession):
    try:
        async with db_session.begin():
            await db_session.run_sync(Base.metadata.create_all, tables=[MostExpensive.__table__])

        stmt = select(ProductDB).order_by(desc(ProductDB.price)).limit(10)
        result = await db_session.execute(stmt)
        top_products = result.scalars().all()

        expensive_products = [
            MostExpensive(
                product_name=product.title,
                price=product.price,
                category=product.category
            )
            for product in top_products
        ]

        db_session.add_all(expensive_products)
        await db_session.commit()
        logger.info("ORM: Created most_expensive table with top 10 products")

    except Exception as e:
        await db_session.rollback()
        logger.error(f"ORM Error creating most_expensive table: {str(e)}")
        raise


async def create_ods_users_table_orm(db_session: AsyncSession):
    try:
        async with db_session.begin():
            await db_session.run_sync(Base.metadata.create_all, tables=[OdsUser.__table__])

        stmt = select(UserDB)
        result = await db_session.execute(stmt)
        all_users = result.scalars().all()

        ods_users = []
        for user in all_users:
            address = json.loads(user.address) if isinstance(user.address, str) else user.address

            ods_users.append(OdsUser(
                user_id=user.id,
                firstname=user.name['firstname'],
                lastname=user.name['lastname'],
                lat=address.get('lat'),
                long=address.get('long'),
                street_number=address.get('number'),
                street_name=address.get('street'),
                zipcode=address.get('zipcode'),
                original_email=user.email
            ))

        db_session.add_all(ods_users)
        await db_session.commit()
        logger.info("ORM: Created ods_users table with transformed user data")

    except Exception as e:
        await db_session.rollback()
        logger.error(f"ORM Error creating ods_users table: {str(e)}")
        raise


