from rest_framework import serializers


class WithdrawSerializer(serializers.Serializer):
    amount_minor = serializers.IntegerField(min_value=1)
    reference = serializers.CharField(required=False, allow_blank=True, default="")
    idempotency_key = serializers.CharField(required=False, allow_blank=True)
