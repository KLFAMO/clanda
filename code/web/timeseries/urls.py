from django.urls import path
from .views import TimeseriesDashboardView

app_name = "timeseries"

urlpatterns = [
    path("", TimeseriesDashboardView.as_view(), name="dashboard"),
]
