from django.urls import path
from .views import BudgetDashboardView

app_name = "budget"

urlpatterns = [
    path("", BudgetDashboardView.as_view(), name="budget_dashboard"),
]