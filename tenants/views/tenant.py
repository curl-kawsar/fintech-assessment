from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from tenants.models import Tenant
from tenants.serializers import TenantCreateSerializer


class TenantCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TenantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant, raw_key = Tenant.create_with_key(name=serializer.validated_data["name"])
        return Response(
            {
                "id": tenant.id,
                "name": tenant.name,
                "api_key": raw_key,
            },
            status=status.HTTP_201_CREATED,
        )
