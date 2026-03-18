from django.contrib import admin
from django.urls import path, include

from employees.views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path("employees/", include("employees.urls")),
]

