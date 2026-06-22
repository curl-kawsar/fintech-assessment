import hashlib
import secrets

from django.db import models


def generate_api_key():
    return secrets.token_urlsafe(32)


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    api_key_hash = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenants"

    def __str__(self):
        return self.name

    @classmethod
    def create_with_key(cls, name: str):
        raw_key = generate_api_key()
        tenant = cls.objects.create(name=name, api_key_hash=hash_api_key(raw_key))
        return tenant, raw_key

    @classmethod
    def find_by_raw_key(cls, raw_key: str):
        if not raw_key:
            return None
        return cls.objects.filter(
            api_key_hash=hash_api_key(raw_key),
            is_active=True,
        ).first()
