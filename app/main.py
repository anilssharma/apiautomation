import os
import logging
from time import perf_counter
from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterator, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.engine import Connection
from sqlalchemy.sql.elements import ColumnElement

from app.config import DATABASE_URL
from app.database import create_database_engine, get_connection, initialize_database
from app.models import order_status_history, orders
from app.schemas import OrderStatusList


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("order_api")
logger.setLevel(logging.INFO)


def _read_statuses(
    connection: Connection,
    conditions: List[ColumnElement[bool]],
    limit: int,
    offset: int,
) -> OrderStatusList:
    joined_tables = order_status_history.join(
        orders, order_status_history.c.order_id == orders.c.id
    )
    count_query = select(func.count()).select_from(joined_tables)
    status_query = (
        select(
            orders.c.order_number,
            orders.c.user_id,
            order_status_history.c.status,
            order_status_history.c.changed_at,
        )
        .select_from(joined_tables)
        .order_by(order_status_history.c.changed_at, order_status_history.c.id)
        .limit(limit)
        .offset(offset)
    )
    if conditions:
        count_query = count_query.where(*conditions)
        status_query = status_query.where(*conditions)

    total = connection.execute(count_query).scalar_one()
    rows = connection.execute(status_query).mappings().all()
    items = []
    for row in rows:
        item = dict(row)
        if item["changed_at"].tzinfo is None:
            item["changed_at"] = item["changed_at"].replace(tzinfo=timezone.utc)
        items.append(item)
    return OrderStatusList(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


def create_app(database_url: Optional[str] = None) -> FastAPI:
    resolved_url = database_url or DATABASE_URL

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> Iterator[None]:
        if not resolved_url:
            raise RuntimeError("Set ORDER_API_DATABASE_URL in the project .env file")
        engine = create_database_engine(resolved_url)
        application.state.engine = engine
        logger.info("Initializing database schema")
        initialize_database(engine)
        logger.info("API ready database_dialect=%s", engine.dialect.name)
        try:
            yield
        finally:
            engine.dispose()
            logger.info("API shutdown complete")

    application = FastAPI(
        title="Order Management API",
        version="1.0.0",
        description="Read order status history by order, user, or date range.",
        lifespan=lifespan,
    )

    @application.middleware("http")
    async def log_request_progress(request, call_next):
        started_at = perf_counter()
        logger.info("Request started method=%s", request.method)
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (perf_counter() - started_at) * 1000
            logger.exception(
                "Request failed method=%s elapsed_ms=%.2f",
                request.method,
                elapsed_ms,
            )
            raise
        elapsed_ms = (perf_counter() - started_at) * 1000
        logger.info(
            "Request completed method=%s status=%s elapsed_ms=%.2f",
            request.method,
            response.status_code,
            elapsed_ms,
        )
        return response

    @application.get("/api/v1/order-statuses", response_model=OrderStatusList)
    def get_all_statuses(
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
        connection: Connection = Depends(get_connection),
    ) -> OrderStatusList:
        return _read_statuses(connection, [], limit, offset)

    @application.get(
        "/api/v1/orders/{order_number}/statuses", response_model=OrderStatusList
    )
    def get_order_statuses(
        order_number: str,
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
        connection: Connection = Depends(get_connection),
    ) -> OrderStatusList:
        order_id = connection.execute(
            select(orders.c.id).where(orders.c.order_number == order_number)
        ).scalar_one_or_none()
        if order_id is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return _read_statuses(
            connection, [orders.c.order_number == order_number], limit, offset
        )

    @application.get(
        "/api/v1/users/{user_id}/order-statuses", response_model=OrderStatusList
    )
    def get_user_statuses(
        user_id: str,
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
        connection: Connection = Depends(get_connection),
    ) -> OrderStatusList:
        return _read_statuses(connection, [orders.c.user_id == user_id], limit, offset)

    @application.get(
        "/api/v1/order-statuses/by-date-range", response_model=OrderStatusList
    )
    def get_statuses_by_date_range(
        start_date: date,
        end_date: date,
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
        connection: Connection = Depends(get_connection),
    ) -> OrderStatusList:
        if start_date > end_date:
            raise HTTPException(
                status_code=422, detail="start_date must be on or before end_date"
            )
        range_start = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        range_end = datetime.combine(
            end_date + timedelta(days=1), time.min, tzinfo=timezone.utc
        )
        return _read_statuses(
            connection,
            [
                order_status_history.c.changed_at >= range_start,
                order_status_history.c.changed_at < range_end,
            ],
            limit,
            offset,
        )

    return application


app = create_app()