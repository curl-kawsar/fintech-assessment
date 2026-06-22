from django.urls import path

from wallets.views.deposit import DepositView
from wallets.views.transfer import TransferView
from wallets.views.wallet import WalletDetailView, WalletListCreateView, WalletTransactionListView
from wallets.views.withdraw import WithdrawView

urlpatterns = [
    path("wallets/", WalletListCreateView.as_view(), name="wallet-list-create"),
    path("wallets/<int:pk>/", WalletDetailView.as_view(), name="wallet-detail"),
    path("wallets/<int:pk>/transactions/", WalletTransactionListView.as_view(), name="wallet-transactions"),
    path("wallets/<int:wallet_id>/deposit/", DepositView.as_view(), name="wallet-deposit"),
    path("wallets/<int:wallet_id>/withdraw/", WithdrawView.as_view(), name="wallet-withdraw"),
    path("transfers/", TransferView.as_view(), name="transfer"),
]
