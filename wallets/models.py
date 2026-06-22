import uuid

from django.db import models

from tenants.models import Tenant


class Wallet(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="wallets")
    user_ref = models.CharField(max_length=255)
    currency = models.CharField(max_length=3, default="BDT")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wallets"
        unique_together = ("tenant", "user_ref")

    def __str__(self):
        return f"Wallet {self.id} ({self.user_ref})"


class Transaction(models.Model):
    class Type(models.TextChoices):
        DEPOSIT = "DEPOSIT", "Deposit"
        WITHDRAW = "WITHDRAW", "Withdraw"
        TRANSFER_IN = "TRANSFER_IN", "Transfer In"
        TRANSFER_OUT = "TRANSFER_OUT", "Transfer Out"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="transactions")
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=20, choices=Type.choices)
    amount_minor = models.BigIntegerField()
    reference = models.CharField(max_length=255, blank=True, default="")
    idempotency_key = models.CharField(max_length=255)
    transfer_group_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type} {self.amount_minor} wallet={self.wallet_id}"


class IdempotencyRecord(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="idempotency_records")
    idempotency_key = models.CharField(max_length=255)
    request_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROCESSING)
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "idempotency_records"
        unique_together = ("tenant", "idempotency_key")

    def __str__(self):
        return f"{self.tenant_id}:{self.idempotency_key}"
