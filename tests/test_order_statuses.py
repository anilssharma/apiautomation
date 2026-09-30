import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient
from app.sample_data import seed_sample_data
def test_sample_data_loader_is_idempotent(client: TestClient) -> None:
    with client.app.state.engine.begin() as connection:
        seed_sample_data(connection)

    response = client.get("/api/v1/order-statuses")

    assert response.status_code == 200
    assert response.json()["total"] == 12


def test_get_all_statuses_returns_paginated_history(client: TestClient) -> None:
    response = client.get("/api/v1/order-statuses")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 12
    assert len(body["items"]) == 12
    assert body["items"][0] == {
        "order_number": "ORD-1001",
        "user_id": "USER-101",
        "status": "PENDING",
        "changed_at": "2026-06-01T09:00:00Z",
    }


def test_get_statuses_by_order_number(client: TestClient) -> None:
    response = client.get("/api/v1/orders/ORD-1001/statuses")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 4
    assert {item["status"] for item in body["items"]} == {
        "PENDING",
        "PROCESSING",
        "SHIPPED",
        "DELIVERED",
    }


def test_get_statuses_by_user(client: TestClient) -> None:
    response = client.get("/api/v1/users/USER-101/order-statuses")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 7
    assert {item["order_number"] for item in body["items"]} == {
        "ORD-1001",
        "ORD-1002",
    }


def test_get_statuses_by_inclusive_date_range(client: TestClient) -> None:
    response = client.get(
        "/api/v1/order-statuses/by-date-range",
        params={"start_date": "2026-06-02", "end_date": "2026-06-03"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 6
    assert all("2026-06-02" <= item["changed_at"][:10] <= "2026-06-03" for item in body["items"])


def test_pagination_preserves_filtered_total(client: TestClient) -> None:
    response = client.get(
        "/api/v1/order-statuses", params={"limit": 2, "offset": 2}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 12
    assert body["limit"] == 2
    assert body["offset"] == 2
    assert len(body["items"]) == 2


def test_unknown_order_returns_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/orders/ORD-DOES-NOT-EXIST/statuses")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_reversed_date_range_is_rejected(client: TestClient) -> None:
    response = client.get(
        "/api/v1/order-statuses/by-date-range",
        params={"start_date": "2026-06-04", "end_date": "2026-06-02"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "start_date must be on or before end_date"


def test_invalid_pagination_is_rejected(client: TestClient) -> None:
    response = client.get("/api/v1/order-statuses", params={"limit": 0})

    assert response.status_code == 422