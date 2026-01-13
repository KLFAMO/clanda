from pathlib import Path
from django.conf import settings

from django import forms
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from django.views.generic import TemplateView


from cmpa import (
    discover_comparators,
    build_connection_graph,
    find_path_nodes,
    path_to_edges,
    calc_nodes_ratio,
)


class PathPickForm(forms.Form):
    start = forms.ChoiceField(choices=[], required=True, label="Start node")
    goal = forms.ChoiceField(choices=[], required=True, label="Goal node")
    fmjd = forms.IntegerField(required=True, label="fmjd (int)")
    tmjd = forms.IntegerField(required=True, label="tmjd (int)")

    def __init__(self, *args, node_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        node_choices = node_choices or []
        self.fields["start"].choices = node_choices
        self.fields["goal"].choices = node_choices

    def clean(self):
        cleaned = super().clean()
        fmjd = cleaned.get("fmjd")
        tmjd = cleaned.get("tmjd")
        if fmjd is not None and tmjd is not None and fmjd > tmjd:
            self.add_error("tmjd", "tmjd musi być >= fmjd.")
        return cleaned


class NodePathView(TemplateView):
    template_name = "network/node_path.html"

    def _build_graph(self):
        root = Path(settings.CMPA_DATA_DIR)
        d = discover_comparators(root)
        g = build_connection_graph(d)
        return d, g

    def get(self, request, *args, **kwargs):
        d, g = self._build_graph()

        nodes = sorted(str(n) for n in g.nodes)
        node_choices = [(n, n) for n in nodes]

        # Form zawsze "bound" do GET, żeby pola NIE znikały po odświeżeniu
        form = PathPickForm(request.GET or None, node_choices=node_choices)

        path_nodes = None
        path_edges = None
        error = None

        # Ścieżkę liczymy TYLKO po kliknięciu Find path
        do_path = request.GET.get("action") == "path"

        if do_path:
            if form.is_valid():
                start = form.cleaned_data["start"]
                goal = form.cleaned_data["goal"]
                try:
                    pn = find_path_nodes(g, start, goal)
                    pe = path_to_edges(g, pn)
                    path_nodes = pn
                    path_edges = pe
                except Exception as e:
                    error = f"Nie udało się wyznaczyć ścieżki: {e}"
            else:
                # błędy formularza pokażą się w template
                pass

        ctx = {
            "form": form,
            "path_nodes": path_nodes,
            "path_edges": path_edges,
            "error": error,
        }
        return self.render_to_response(ctx)


class RatioApiView(View):
    """
    GET /api/ratio/?start=...&goal=...&fmjd=...&tmjd=...
    Zwraca: x_tab, y_tab (listy float) do wykresu
    """

    def get(self, request):
        start = request.GET.get("start")
        goal = request.GET.get("goal")
        fmjd = request.GET.get("fmjd")
        tmjd = request.GET.get("tmjd")

        if not all([start, goal, fmjd, tmjd]):
            return HttpResponseBadRequest("Missing start/goal/fmjd/tmjd")

        try:
            fmjd = int(fmjd)
            tmjd = int(tmjd)
        except ValueError:
            return HttpResponseBadRequest("fmjd/tmjd must be integers")

        if fmjd > tmjd:
            return HttpResponseBadRequest("fmjd must be <= tmjd")

        mts = calc_nodes_ratio(
            fmjd=fmjd,
            tmjd=tmjd,
            start_node=start,
            goal_node=goal,
        )

        x_tab = [float(v) for v in mts.mjd_tab()]
        y_tab = [float(v) for v in mts.val_tab()]

        return JsonResponse({
            "x_tab": x_tab,
            "y_tab": y_tab,
            "meta": {
                "start": start,
                "goal": goal,
                "fmjd": fmjd,
                "tmjd": tmjd,
                "series": "final",
            }
        })
