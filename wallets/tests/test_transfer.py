import threading

import pytest

from wallets.models import Transaction
from wallets.services import transfer as transfer_service
from wallets.tests.conftest import create_wallet, deposit


@pytest.mark.django_db(transaction=True)
def test_concurrent_transfers_only_one_succeeds(auth_client):
    client, tenant, _ = auth_client
    wallet_a = create_wallet(client, "user-a")
    wallet_b = create_wallet(client, "user-b")
    deposit(client, wallet_a["id"], 10000, "dep-t1")

    results = []

    def do_transfer(key):
        from django.db import connection

        connection.close()
        status_code, _ = transfer_service.transfer(
            tenant=tenant,
            from_wallet_id=wallet_a["id"],
            to_wallet_id=wallet_b["id"],
            amount_minor=7000,
            idempotency_key=key,
        )
        results.append(status_code)

    thread_1 = threading.Thread(target=do_transfer, args=("xfer-1",))
    thread_2 = threading.Thread(target=do_transfer, args=("xfer-2",))
    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()

    assert 201 in results
    assert 400 in results
    assert Transaction.objects.filter(tenant=tenant, type="TRANSFER_OUT").count() == 1


@pytest.mark.django_db
def test_transfer_duplicate_idempotency(auth_client):
    client, tenant, _ = auth_client
    wallet_a = create_wallet(client, "user-c")
    wallet_b = create_wallet(client, "user-d")
    deposit(client, wallet_a["id"], 10000, "dep-t2")

    payload = {
        "from_wallet_id": wallet_a["id"],
        "to_wallet_id": wallet_b["id"],
        "amount_minor": 2000,
    }
    first = client.post(
        "/api/v1/transfers/",
        payload,
        HTTP_IDEMPOTENCY_KEY="xfer-dup",
        format="json",
    )
    second = client.post(
        "/api/v1/transfers/",
        payload,
        HTTP_IDEMPOTENCY_KEY="xfer-dup",
        format="json",
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == second.json()
    assert Transaction.objects.filter(tenant=tenant, type="TRANSFER_OUT").count() == 1
