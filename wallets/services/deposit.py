from django.db import transaction

from wallets.exceptions import NotFoundError
from wallets.models import Transaction, Wallet
from wallets.services.balance import get_balance
from wallets.services.idempotency import run_idempotent
from wallets.tasks import log_transaction_async


def deposit(tenant, wallet_id, amount_minor, idempotency_key, reference=""):
    request_body = {
        "wallet_id": wallet_id,
        "amount_minor": amount_minor,
        "reference": reference,
    }

    def handler():
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().filter(tenant=tenant, pk=wallet_id).first()
            if wallet is None:
                raise NotFoundError("Wallet not found")

            txn = Transaction.objects.create(
                tenant=tenant,
                wallet=wallet,
                type=Transaction.Type.DEPOSIT,
                amount_minor=amount_minor,
                reference=reference,
                idempotency_key=idempotency_key,
            )

        log_transaction_async.delay(txn.id)

        return 201, {
            "transaction_id": txn.id,
            "wallet_id": wallet.id,
            "type": txn.type,
            "amount_minor": amount_minor,
            "balance_minor": get_balance(wallet),
        }

    return run_idempotent(tenant, idempotency_key, request_body, handler)
