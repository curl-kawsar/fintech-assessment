import uuid

from django.db import transaction

from wallets.exceptions import InsufficientFundsError, NotFoundError, WalletServiceError
from wallets.models import Transaction, Wallet
from wallets.services.balance import get_balance
from wallets.services.idempotency import run_idempotent
from wallets.tasks import log_transaction_async


def transfer(tenant, from_wallet_id, to_wallet_id, amount_minor, idempotency_key, reference=""):
    request_body = {
        "from_wallet_id": from_wallet_id,
        "to_wallet_id": to_wallet_id,
        "amount_minor": amount_minor,
        "reference": reference,
    }

    def handler():
        if from_wallet_id == to_wallet_id:
            raise WalletServiceError("Cannot transfer to the same wallet")

        with transaction.atomic():
            wallet_ids = sorted([from_wallet_id, to_wallet_id])
            wallets = {
                w.id: w
                for w in Wallet.objects.select_for_update().filter(
                    tenant=tenant,
                    pk__in=wallet_ids,
                )
            }

            from_wallet = wallets.get(from_wallet_id)
            to_wallet = wallets.get(to_wallet_id)

            if from_wallet is None or to_wallet is None:
                raise NotFoundError("One or both wallets not found")

            if from_wallet.tenant_id != to_wallet.tenant_id:
                raise WalletServiceError("Transfers across tenants are not allowed", status_code=403)

            current_balance = get_balance(from_wallet)
            if current_balance < amount_minor:
                raise InsufficientFundsError()

            transfer_group_id = uuid.uuid4()

            out_txn = Transaction.objects.create(
                tenant=tenant,
                wallet=from_wallet,
                type=Transaction.Type.TRANSFER_OUT,
                amount_minor=-amount_minor,
                reference=reference,
                idempotency_key=idempotency_key,
                transfer_group_id=transfer_group_id,
            )
            in_txn = Transaction.objects.create(
                tenant=tenant,
                wallet=to_wallet,
                type=Transaction.Type.TRANSFER_IN,
                amount_minor=amount_minor,
                reference=reference,
                idempotency_key=idempotency_key,
                transfer_group_id=transfer_group_id,
            )

        log_transaction_async.delay(out_txn.id)
        log_transaction_async.delay(in_txn.id)

        return 201, {
            "transfer_group_id": str(transfer_group_id),
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount_minor": amount_minor,
            "from_balance_minor": get_balance(from_wallet),
            "to_balance_minor": get_balance(to_wallet),
            "transactions": [
                {"id": out_txn.id, "type": out_txn.type},
                {"id": in_txn.id, "type": in_txn.type},
            ],
        }

    return run_idempotent(tenant, idempotency_key, request_body, handler)
