from django.views.generic import TemplateView
from django.views import View

from dataio.mts import get_data_names, list_available_mjds
from django.http import Http404, HttpResponse

from dataio.mts import get_data_single_mjd


class CleaningHomeView(TemplateView):
    template_name = "timeseries/cleaning_home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["data_names"] = get_data_names()
        ctx["selected_dataset"] = self.request.GET.get("dataset") or ""
        return ctx


class CleaningDatasetView(TemplateView):
    template_name = "timeseries/cleaning_dataset.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        dataset = kwargs["dataset"]

        if dataset not in set(get_data_names()):
            raise Http404(f"Unknown dataset: {dataset}")

        mjds = list_available_mjds(dataset)

        selected = self.request.GET.get("mjd", "")
        options = [{"value": f"{m:g}", "label": f"{m:g}"} for m in mjds]

        ctx.update(
            {
                "dataset": dataset,
                "mjd_options": options,
                "selected_mjd": selected,
            }
        )
        return ctx

class PlotMtsApiView(View):

    def get(self, request):
        name = request.GET.get("name")
        mjd = request.GET.get("mjd")
        if not name or not mjd:
            return Http404("Missing 'name' or 'mjd' parameter.")
        
        mts = get_data_single_mjd(name, int(mjd))
        mts.split()

        return HttpResponse(
            mts.to_json(),
            content_type="application/json",
        )
