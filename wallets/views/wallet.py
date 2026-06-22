from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from wallets.serializers.wallet import WalletCreateSerializer, TransactionSerializer
from wallets.services import wallet as wallet_service
from wallets.views.helpers import get_tenant


class WalletListCreateView(APIView):
    def post(self, request):
        serializer = WalletCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = wallet_service.create_wallet(
            tenant=get_tenant(request),
            user_ref=serializer.validated_data["user_ref"],
            currency=serializer.validated_data.get("currency", "BDT"),
        )
        return Response(result, status=status.HTTP_201_CREATED)


class WalletDetailView(APIView):
    def get(self, request, pk):
        result = wallet_service.get_wallet_detail(tenant=get_tenant(request), wallet_id=pk)
        return Response(result)


class WalletTransactionListView(APIView):
    def get(self, request, pk):
        from wallets.exceptions import NotFoundError
        from wallets.models import Transaction, Wallet

        tenant = get_tenant(request)
        wallet = Wallet.objects.filter(tenant=tenant, pk=pk).first()
        if wallet is None:
            raise NotFoundError("Wallet not found")

        queryset = Transaction.objects.filter(tenant=tenant, wallet=wallet)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            from rest_framework.pagination import PageNumberPagination

            self._paginator = PageNumberPagination()
        return self._paginator

    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)
