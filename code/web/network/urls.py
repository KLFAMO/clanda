from django.urls import path
from .views import NodePathView, RatioApiView

app_name = "network"

urlpatterns = [
    path("nodes/", NodePathView.as_view(), name="node_path"),
    path("api/ratio/", RatioApiView.as_view(), name="api_ratio"),
]
