from django.urls import path
from .views import NodePickerView

urlpatterns = [
    path("nodes/", NodePickerView.as_view(), name="node_picker"),
]
