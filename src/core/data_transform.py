import logging
from typing import Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exception import (
    MostExpensiveTransformationError,
    OdsUsersTransformationError,
    UserProcessingError,
)
from src.db.table import ProductDB, UserDB
from src.db.table import MostExpensive, OdsUser

logger = logging.getLogger(__name__)
logger.propagate = False


class MostExpensiveTransformer:
    """Transforms product data to identify and store the most expensive products."""

    @staticmethod
    async def transform(db_session: AsyncSession) -> int:
        """
        Extracts, transforms and loads the 10 most expensive products.

        Returns:
            int: Number of successfully processed products

        Raises:
            MostExpensiveTransformationError: If any step of the transformation fails
        """
        try:
            try:
                await db_session.execute(MostExpensive.__table__.delete())
            except Exception as e:
                raise MostExpensiveTransformationError(
                    f"Failed to clear MostExpensive table: {str(e)}"
                ) from e

            try:
                stmt = (
                    select(
                        ProductDB.title.label("product_name"),
                        ProductDB.price,
                        ProductDB.category,
                    )
                    .order_by(ProductDB.price.desc())
                    .limit(10)
                )

                result = await db_session.execute(stmt)
                products = result.mappings().all()
            except Exception as e:
                raise MostExpensiveTransformationError(
                    f"Failed to fetch most expensive products: {str(e)}"
                ) from e

            try:
                for product in products:
                    db_session.add(
                        MostExpensive(
                            product_name=product["product_name"],
                            price=product["price"],
                            category=product["category"],
                        )
                    )

                await db_session.commit()
                return len(products)
            except Exception as e:
                await db_session.rollback()
                raise MostExpensiveTransformationError(
                    f"Failed to insert most expensive products: {str(e)}"
                ) from e

        except MostExpensiveTransformationError:
            raise
        except Exception as e:
            await db_session.rollback()
            raise MostExpensiveTransformationError(
                f"Unexpected error in MostExpensive transform: {str(e)}"
            ) from e


class OdsUsersTransformer:
    """
    Transforms user data for storage in the Operational Data Store (ODS).

    Methods:
        transform: Performs the complete ETL process for user data
    """

    @staticmethod
    async def transform(db_session: AsyncSession) -> int:
        """
        Extracts, transforms and loads user data into the ODS table.

        Returns:
            int: Number of successfully processed users

        Raises:
            OdsUsersTransformationError: If any step of the transformation fails
            UserProcessingError: If processing of an individual user fails (logged but doesn't stop processing)
        """
        try:
            try:
                await db_session.execute(OdsUser.__table__.delete())
            except Exception as e:
                raise OdsUsersTransformationError(
                    f"Failed to clear OdsUser table: {str(e)}"
                ) from e

            try:
                stmt = select(UserDB)
                result = await db_session.execute(stmt)
                users = result.scalars().all()
            except Exception as e:
                raise OdsUsersTransformationError(
                    f"Failed to fetch users: {str(e)}"
                ) from e

            count = 0
            for user in users:
                try:
                    try:
                        name_data = user.name
                        firstname = name_data.get("firstname", "")
                        lastname = name_data.get("lastname", "")

                        address_data = user.address
                        geolocation = address_data.get("geolocation", {})

                        db_session.add(
                            OdsUser(
                                user_id=user.id,
                                firstname=firstname,
                                lastname=lastname,
                                lat=float(geolocation.get("lat", 0.0)),
                                long=float(geolocation.get("long", 0.0)),
                                street_number=str(address_data.get("number", "")),
                                street=str(address_data.get("street", "")),
                                zipcode=str(address_data.get("zipcode", "")),
                                city=str(address_data.get("city", "")),
                            )
                        )
                        count += 1
                    except (ValueError, AttributeError, KeyError) as e:
                        raise UserProcessingError(
                            f"Invalid data structure for user {user.id}: {str(e)}"
                        ) from e
                    except Exception as e:
                        raise UserProcessingError(
                            f"Unexpected error processing user {user.id}: {str(e)}"
                        ) from e

                except UserProcessingError as e:
                    logger.warning(str(e))
                    continue

            try:
                await db_session.commit()
                return count
            except Exception as e:
                await db_session.rollback()
                raise OdsUsersTransformationError(
                    f"Failed to commit OdsUser changes: {str(e)}"
                ) from e

        except OdsUsersTransformationError:
            raise
        except Exception as e:
            await db_session.rollback()
            raise OdsUsersTransformationError(
                f"Unexpected error in OdsUsers transform: {str(e)}"
            ) from e


async def run_transformations(db_session: AsyncSession) -> Dict[str, int]:
    """
    Executes all data transformations and returns processing statistics.

    Returns:
        Dict[str, int]: Dictionary with transformation results:
           - "most_expensive": count of processed products
           - "ods_users": count of processed users
           (values will be 0 if transformation failed)
    """
    results: dict[str, int] = {}

    try:
        results["most_expensive"] = await MostExpensiveTransformer.transform(db_session)
    except MostExpensiveTransformationError as e:
        logger.error(str(e))
        results["most_expensive"] = 0

    try:
        results["ods_users"] = await OdsUsersTransformer.transform(db_session)
    except OdsUsersTransformationError as e:
        logger.error(str(e))
        results["ods_users"] = 0

    return results
