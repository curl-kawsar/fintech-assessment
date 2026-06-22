from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from tenants.models import Tenant


class TenantUser:
    is_authenticated = True

    def __init__(self, tenant):
        self.tenant = tenant


class TenantAPIKeyAuthentication(BaseAuthentication):
    keyword = "Api-Key"

    def authenticate(self, request):
        raw_key = self._get_raw_key(request)
        if not raw_key:
            return None

        tenant = Tenant.find_by_raw_key(raw_key)
        if tenant is None:
            raise AuthenticationFailed("Invalid API key.")

        tenant_id_header = request.headers.get("X-Tenant-ID")
        if tenant_id_header and str(tenant.id) != str(tenant_id_header):
            raise AuthenticationFailed("API key does not match X-Tenant-ID header.")

        request.tenant = tenant
        return (TenantUser(tenant), raw_key)

    def _get_raw_key(self, request):
        direct_key = request.headers.get("Api-Key") or request.headers.get("X-API-Key")
        if direct_key:
            return direct_key.strip()

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith(f"{self.keyword} "):
            return auth_header[len(self.keyword) + 1 :].strip()
        if auth_header.startswith("Bearer "):
            return auth_header[len("Bearer ") :].strip()
        return None
