from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("network.urls")),
    path("network/", include("network.urls")),
    path("timeseries/", include("timeseries.urls")),
    path("comparators/", include("comparators.urls")),
    path("budget/", include("budget.urls")),
]
