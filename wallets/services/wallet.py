from wallets.exceptions import NotFoundError
from wallets.models import Wallet
from wallets.services.balance import get_balance


def create_wallet(tenant, user_ref, currency="BDT"):
    wallet, _ = Wallet.objects.get_or_create(
        tenant=tenant,
        user_ref=user_ref,
        defaults={"currency": currency},
    )
    return wallet_to_dict(wallet)


def get_wallet_detail(tenant, wallet_id):
    wallet = Wallet.objects.filter(tenant=tenant, pk=wallet_id).first()
    if wallet is None:
        raise NotFoundError("Wallet not found")
    return wallet_to_dict(wallet)


def wallet_to_dict(wallet):
    return {
        "id": wallet.id,
        "user_ref": wallet.user_ref,
        "currency": wallet.currency,
        "balance_minor": get_balance(wallet),
        "created_at": wallet.created_at.isoformat(),
    }
