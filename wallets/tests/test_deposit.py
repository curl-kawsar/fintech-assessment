import pytest

from wallets.models import Transaction
from wallets.tests.conftest import create_wallet, deposit


@pytest.mark.django_db
def test_deposit_increases_balance(auth_client):
    client, tenant, _ = auth_client
    wallet = create_wallet(client)
    response = deposit(client, wallet["id"], 10000, "dep-1")
    assert response.status_code == 201
    assert response.json()["balance_minor"] == 10000
    assert Transaction.objects.filter(tenant=tenant).count() == 1


@pytest.mark.django_db
def test_duplicate_idempotency_key_no_double_charge(auth_client):
    client, tenant, _ = auth_client
    wallet = create_wallet(client)

    first = deposit(client, wallet["id"], 5000, "dep-dup")
    second = deposit(client, wallet["id"], 5000, "dep-dup")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()
    assert Transaction.objects.filter(tenant=tenant, idempotency_key="dep-dup").count() == 1
