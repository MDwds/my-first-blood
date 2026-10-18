from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("portal/", include("employees.urls")),
    path("", RedirectView.as_view(pattern_name="employees:home", permanent=False)),
]
