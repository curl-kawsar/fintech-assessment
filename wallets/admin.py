from django.contrib import admin

from wallets.models import IdempotencyRecord, Transaction, Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "user_ref", "currency", "created_at")
    list_filter = ("tenant",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "wallet", "type", "amount_minor", "created_at")
    list_filter = ("type", "tenant")


@admin.register(IdempotencyRecord)
class IdempotencyRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "idempotency_key", "status", "response_status", "created_at")
    list_filter = ("status", "tenant")
