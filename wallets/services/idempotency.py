import hashlib
import json

import redis
from django.conf import settings
from django.db import transaction

from wallets.exceptions import ConflictError, IdempotencyInProgressError, WalletServiceError
from wallets.models import IdempotencyRecord


def _get_redis_client():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)


def _redis_key(tenant_id, idempotency_key):
    return f"idem:{tenant_id}:{idempotency_key}"


def hash_request_body(body: dict) -> str:
    payload = json.dumps(body, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_cached_response(tenant_id, idempotency_key, request_hash):
    if not idempotency_key:
        return None

    try:
        client = _get_redis_client()
        cached = client.get(_redis_key(tenant_id, idempotency_key))
    except Exception:
        return None

    if not cached:
        return None

    data = json.loads(cached)
    if data.get("request_hash") != request_hash:
        raise ConflictError("Idempotency key reused with different request body")

    return data["status"], data["body"]


def save_response_to_redis(tenant_id, idempotency_key, request_hash, status_code, body):
    if not idempotency_key:
        return

    try:
        client = _get_redis_client()
        payload = json.dumps({"request_hash": request_hash, "status": status_code, "body": body})
        client.setex(
            _redis_key(tenant_id, idempotency_key),
            settings.IDEMPOTENCY_REDIS_TTL_SECONDS,
            payload,
        )
    except Exception:
        pass


def _complete_record(record, status_code, response_body):
    record.status = IdempotencyRecord.Status.COMPLETED
    record.response_status = status_code
    record.response_body = response_body
    record.save(update_fields=["status", "response_status", "response_body"])


def run_idempotent(tenant, idempotency_key, request_body, handler):
    if not idempotency_key:
        raise ConflictError("idempotency_key is required (header Idempotency-Key or body field)")

    request_hash = hash_request_body(request_body)

    cached = get_cached_response(tenant.id, idempotency_key, request_hash)
    if cached:
        return cached

    with transaction.atomic():
        record, created = IdempotencyRecord.objects.select_for_update().get_or_create(
            tenant=tenant,
            idempotency_key=idempotency_key,
            defaults={
                "request_hash": request_hash,
                "status": IdempotencyRecord.Status.PROCESSING,
            },
        )

        if not created:
            if record.request_hash != request_hash:
                raise ConflictError("Idempotency key reused with different request body")

            if record.status == IdempotencyRecord.Status.COMPLETED:
                save_response_to_redis(
                    tenant.id,
                    idempotency_key,
                    request_hash,
                    record.response_status,
                    record.response_body,
                )
                return record.response_status, record.response_body

            raise IdempotencyInProgressError()

        try:
            status_code, response_body = handler()
        except WalletServiceError as exc:
            status_code = exc.status_code
            response_body = {"error": exc.message}
            _complete_record(record, status_code, response_body)
            save_response_to_redis(tenant.id, idempotency_key, request_hash, status_code, response_body)
            return status_code, response_body

        _complete_record(record, status_code, response_body)

    save_response_to_redis(tenant.id, idempotency_key, request_hash, status_code, response_body)
    return status_code, response_body
