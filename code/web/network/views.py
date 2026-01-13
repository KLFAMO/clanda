from pathlib import Path

from django import forms
from django.conf import settings
from django.views.generic import TemplateView

from cmpa.discovery import discover_comparators
from cmpa.graph import build_connection_graph, find_path_nodes, path_to_edges


class PathPickForm(forms.Form):
    start = forms.ChoiceField(choices=[], required=True, label="Start node")
    goal = forms.ChoiceField(choices=[], required=True, label="Goal node")
    t0_mjd = forms.FloatField(required=False, label="t0 (MJD)")
    t1_mjd = forms.FloatField(required=False, label="t1 (MJD)")

    def __init__(self, *args, node_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        node_choices = node_choices or []
        self.fields["start"].choices = node_choices
        self.fields["goal"].choices = node_choices

    def clean(self):
        cleaned = super().clean()
        t0 = cleaned.get("t0_mjd")
        t1 = cleaned.get("t1_mjd")
        if (t0 is not None) and (t1 is not None) and (t0 >= t1):
            self.add_error("t1_mjd", "t1 musi być większe niż t0.")
        return cleaned


class NodePathView(TemplateView):
    template_name = "network/node_path.html"

    def build_graph(self):
        data_dir = Path(settings.CMPA_DATA_DIR).resolve()
        d = discover_comparators(data_dir)
        g = build_connection_graph(d)
        return g

    def get_node_choices(self, g):
        nodes = sorted(str(n) for n in g.nodes)
        return [(n, n) for n in nodes]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        g = self.build_graph()
        node_choices = self.get_node_choices(g)

        # Form działa na GET, żeby odświeżenie było "automatyczne" po zmianie pól
        form = PathPickForm(self.request.GET or None, node_choices=node_choices)

        path_nodes = None
        path_edges = None
        error = None

        if form.is_bound and form.is_valid():
            start = form.cleaned_data["start"]
            goal = form.cleaned_data["goal"]

            try:
                pn = find_path_nodes(g, start, goal)   # lista nodów na ścieżce
                pe = path_to_edges(g, pn)              # lista krawędzi (u, v, cids)
                path_nodes = pn
                path_edges = pe
            except Exception as e:
                # Jeśli nie ma ścieżki albo Twoje funkcje rzucają wyjątek
                error = f"Nie udało się wyznaczyć ścieżki: {e}"

        ctx["form"] = form
        ctx["path_nodes"] = path_nodes
        ctx["path_edges"] = path_edges
        ctx["error"] = error
        return ctx
