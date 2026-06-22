from rest_framework.response import Response
from rest_framework.views import APIView

from wallets.serializers.transfer import TransferSerializer
from wallets.services import transfer as transfer_service
from wallets.views.helpers import get_idempotency_key, get_tenant


class TransferView(APIView):
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_code, result = transfer_service.transfer(
            tenant=get_tenant(request),
            from_wallet_id=serializer.validated_data["from_wallet_id"],
            to_wallet_id=serializer.validated_data["to_wallet_id"],
            amount_minor=serializer.validated_data["amount_minor"],
            idempotency_key=get_idempotency_key(request, serializer),
            reference=serializer.validated_data.get("reference", ""),
        )
        return Response(result, status=status_code)
