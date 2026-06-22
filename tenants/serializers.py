from rest_framework import serializers


class TenantCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
