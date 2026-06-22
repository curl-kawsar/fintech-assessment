import pytest

from wallets.models import Transaction
from wallets.tests.conftest import create_wallet, deposit


@pytest.mark.django_db
def test_withdraw_insufficient_funds(auth_client):
    client, tenant, _ = auth_client
    wallet = create_wallet(client)
    deposit(client, wallet["id"], 1000, "dep-w1")

    response = client.post(
        f"/api/v1/wallets/{wallet['id']}/withdraw/",
        {"amount_minor": 5000},
        HTTP_IDEMPOTENCY_KEY="wd-1",
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Insufficient funds"
    assert Transaction.objects.filter(tenant=tenant, type="WITHDRAW").count() == 0
