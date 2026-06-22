from django.db.models import Sum

from wallets.models import Transaction


def get_balance(wallet):
    result = Transaction.objects.filter(wallet=wallet).aggregate(total=Sum("amount_minor"))
    return result["total"] or 0
