from django.views import View
from django.http import HttpResponse


class ComparatorsDashboardView(View):
    """
    Minimal dashboard view for the timeseries app.
    """
    def get(self, request, *args, **kwargs):
        return HttpResponse("Comparators dashboard")