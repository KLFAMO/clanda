from django.urls import path
from .views import ComparatorsDashboardView

app_name = "comparators"

urlpatterns = [
    path("", ComparatorsDashboardView.as_view(), name="comparators_dashboard"),
]