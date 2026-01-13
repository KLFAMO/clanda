from django.urls import path
from .views import NodePathView

app_name = "network"

urlpatterns = [
    path("nodes/", NodePathView.as_view(), name="node_path"),
]
