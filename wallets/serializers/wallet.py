from rest_framework import serializers


class WalletCreateSerializer(serializers.Serializer):
    user_ref = serializers.CharField(max_length=255)
    currency = serializers.CharField(max_length=3, required=False, default="BDT")


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        from wallets.models import Transaction

        model = Transaction
        fields = [
            "id",
            "type",
            "amount_minor",
            "reference",
            "idempotency_key",
            "transfer_group_id",
            "created_at",
        ]
