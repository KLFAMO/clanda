from django.urls import path
from .views import CleaningHomeView, CleaningDatasetView, PlotMtsApiView

urlpatterns = [
    path("cleaning/", CleaningHomeView.as_view(), name="cleaning-home"),
    path("cleaning/<str:dataset>/", CleaningDatasetView.as_view(), name="cleaning-dataset"),
    path("api/plot_mts/", PlotMtsApiView.as_view(), name="api-plot-mts"),
]
