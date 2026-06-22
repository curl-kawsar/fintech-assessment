import pytest
from rest_framework.test import APIClient

from tenants.models import Tenant


@pytest.fixture(autouse=True)
def clear_idempotency_cache():
    """Fresh test DB but Redis persists — clear idempotency keys between tests."""
    import redis
    from django.conf import settings

    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        for key in client.scan_iter("idem:*"):
            client.delete(key)
    except Exception:
        pass
    yield


@pytest.fixture(autouse=True)
def celery_eager():
    from myproject.celery import app

    app.conf.update(
        task_always_eager=True,
        task_store_eager_result=True,
        broker_url="memory://",
        result_backend="cache+memory://",
    )
    yield


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def tenant_with_key(db):
    tenant, raw_key = Tenant.create_with_key(name="Test Tenant")
    return tenant, raw_key


@pytest.fixture
def auth_client(api_client, tenant_with_key):
    tenant, raw_key = tenant_with_key
    api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {raw_key}")
    return api_client, tenant, raw_key


def create_wallet(client, user_ref="user-1"):
    response = client.post("/api/v1/wallets/", {"user_ref": user_ref}, format="json")
    assert response.status_code == 201
    return response.json()


def deposit(client, wallet_id, amount_minor, idempotency_key):
    return client.post(
        f"/api/v1/wallets/{wallet_id}/deposit/",
        {"amount_minor": amount_minor},
        HTTP_IDEMPOTENCY_KEY=idempotency_key,
        format="json",
    )
