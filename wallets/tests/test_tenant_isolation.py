import pytest

from tenants.models import Tenant
from wallets.tests.conftest import create_wallet, deposit


@pytest.mark.django_db
def test_cross_tenant_wallet_access_blocked(db, api_client):
    tenant_a, key_a = Tenant.create_with_key("Tenant A")
    tenant_b, key_b = Tenant.create_with_key("Tenant B")

    api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {key_a}")
    wallet_a = create_wallet(api_client, "user-a")

    api_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {key_b}")
    response = api_client.get(f"/api/v1/wallets/{wallet_a['id']}/")
    assert response.status_code == 404

    deposit_response = api_client.post(
        f"/api/v1/wallets/{wallet_a['id']}/deposit/",
        {"amount_minor": 1000},
        HTTP_IDEMPOTENCY_KEY="cross-dep",
        format="json",
    )
    assert deposit_response.status_code == 404

    assert tenant_a.id != tenant_b.id
