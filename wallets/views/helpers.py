def get_tenant(request):
    return request.user.tenant


def get_idempotency_key(request, serializer):
    header_key = request.headers.get("Idempotency-Key")
    body_key = serializer.validated_data.get("idempotency_key")
    return header_key or body_key
