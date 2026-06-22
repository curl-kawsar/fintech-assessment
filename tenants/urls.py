from django.urls import path

from tenants.views.tenant import TenantCreateView

urlpatterns = [
    path("tenants/", TenantCreateView.as_view(), name="tenant-create"),
]
