from rest_framework.response import Response
from rest_framework.views import APIView

from wallets.serializers.deposit import DepositSerializer
from wallets.services import deposit as deposit_service
from wallets.views.helpers import get_idempotency_key, get_tenant


class DepositView(APIView):
    def post(self, request, wallet_id):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_code, result = deposit_service.deposit(
            tenant=get_tenant(request),
            wallet_id=wallet_id,
            amount_minor=serializer.validated_data["amount_minor"],
            idempotency_key=get_idempotency_key(request, serializer),
            reference=serializer.validated_data.get("reference", ""),
        )
        return Response(result, status=status_code)
