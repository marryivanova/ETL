import math
import logging

from pathlib import Path
from sqlalchemy import select, func
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Request, Query, HTTPException

from src.config.database import AsyncSessionLocal
from src.core.models.scheme import TableTemplateContext
from src.db.table import TABLES

logger = logging.getLogger(__name__)
logger.propagate = False

router = APIRouter()

templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))


@router.get("/", response_class=HTMLResponse)
async def show_tables(request: Request):
    try:
        return templates.TemplateResponse(
            "tables.html", {"request": request, "tables": list(TABLES.keys())}
        )
    except Exception as e:
        logger.error(f"Error rendering tables page: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/table/{table_name}", response_class=HTMLResponse)
async def show_table(
    request: Request,
    table_name: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    sort_by: str = None,
    sort_order: str = "asc",
):
    if table_name not in TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    model = TABLES[table_name]

    try:
        async with AsyncSessionLocal() as session:
            try:
                query = select(model)

                if sort_by:
                    if not hasattr(model, sort_by):
                        raise HTTPException(
                            status_code=400, detail=f"Invalid sort column '{sort_by}'"
                        )
                    column = getattr(model, sort_by)
                    query = query.order_by(
                        column.asc() if sort_order == "asc" else column.desc()
                    )

                try:
                    total_items = await session.scalar(
                        select(func.count()).select_from(model.__table__)
                    )
                    total_pages = math.ceil(total_items / per_page)
                except SQLAlchemyError as e:
                    logger.error(f"Count query failed: {str(e)}")
                    raise HTTPException(
                        status_code=500, detail="Failed to get record count"
                    )

                query = query.limit(per_page).offset((page - 1) * per_page)

                try:
                    result = await session.execute(query)
                    items = result.scalars().all()
                except SQLAlchemyError as e:
                    logger.error(f"Data query failed: {str(e)}")
                    raise HTTPException(
                        status_code=500, detail="Failed to fetch table data"
                    )

                columns = [column.key for column in model.__table__.columns]

                try:
                    context = TableTemplateContext(
                        request=request,
                        table_name=table_name,
                        columns=columns,
                        data=items,
                        page=page,
                        per_page=per_page,
                        total_pages=total_pages,
                        total_items=total_items,
                        sort_by=sort_by,
                        sort_order=sort_order,
                    )

                    return templates.TemplateResponse("table.html", context.dict())
                except Exception as e:
                    logger.error(f"Template rendering failed: {str(e)}")
                    raise HTTPException(status_code=500, detail="Failed to render page")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")

    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unavailable")
