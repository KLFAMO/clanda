from pathlib import Path

from django import forms
from django.conf import settings
from django.views.generic.edit import FormView

from cmpa.discovery import discover_comparators
from cmpa.graph import build_connection_graph


class NodePickForm(forms.Form):
    nodes = forms.MultipleChoiceField(
        choices=[],
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label="Wybierz dokładnie dwa nody",
    )

    def __init__(self, *args, nodes_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        # choices przekazujemy z widoku, żeby były zawsze „świeże”
        self.fields["nodes"].choices = nodes_choices or []

    def clean_nodes(self):
        nodes = self.cleaned_data["nodes"]
        if len(nodes) != 2:
            raise forms.ValidationError("Wybierz dokładnie dwa nody.")
        return nodes


class NodePickerView(FormView):
    template_name = "network/node_picker.html"
    form_class = NodePickForm
    success_url = "/nodes/"  # na razie zostajemy na tej samej stronie

    def get_nodes(self):
        """
        Zawsze budowane na świeżo przy otwarciu/odświeżeniu strony.
        """
        data_dir = Path(settings.CMPA_DATA_DIR).resolve()
        d = discover_comparators(data_dir)
        g = build_connection_graph(d)
        nodes = sorted(str(n) for n in g.nodes)
        return [(n, n) for n in nodes]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["nodes_choices"] = self.get_nodes()
        return kwargs

    def form_valid(self, form):
        # Na razie tylko pokazujemy, co wybrano, bez przejścia dalej
        self.selected = form.cleaned_data["nodes"]
        return self.render_to_response(self.get_context_data(form=form, selected=self.selected))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # jeśli po POST mamy selected, pokaż je
        ctx.setdefault("selected", getattr(self, "selected", None))
        return ctx
