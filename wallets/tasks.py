import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def log_transaction_async(transaction_id):
    from wallets.models import Transaction

    txn = Transaction.objects.filter(pk=transaction_id).first()
    if txn:
        logger.info(
            "Transaction logged async: id=%s type=%s wallet=%s amount=%s",
            txn.id,
            txn.type,
            txn.wallet_id,
            txn.amount_minor,
        )
    return transaction_id
