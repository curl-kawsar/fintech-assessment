from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, "tenant"):
            request.tenant = None
