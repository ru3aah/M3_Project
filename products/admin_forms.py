from django import forms
from .models import ProductTechSpec


def _stringify_value(value):
    """
    For existing instances: convert JSON value into a single string for the form.
    - [{"name": "A", "value": "x"}, {"name": "B", "value": "y"}] -> "A: x, B: y"
    - ["Red", "Blue"] -> "Red, Blue"
    - "USA" -> "USA"
    """
    if isinstance(value, list):
        if (
            value
            and isinstance(value[0], dict)
            and "name" in value[0]
            and "value" in value[0]
        ):
            return ", ".join(
                f"{item.get('name', '')}: {item.get('value', '')}" for item in value
            )
        return ", ".join(str(x) for x in value)
    return "" if value is None else str(value)


def _parse_value(raw):
    """
    From a single input string to JSON shape:
    - "A: x, B: y"  -> [{"name": "A", "value": "x"}, {"name": "B", "value": "y"}]
    - "Red, Blue"   -> ["Red", "Blue"]
    - "USA"         -> "USA"
    """
    raw = (raw or "").strip()
    if not raw:
        return ""

    # name:value pairs => list of dicts
    if ":" in raw:
        pairs = []
        for chunk in raw.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            name, _, val = chunk.partition(":")
            pairs.append({"name": name.strip(), "value": val.strip()})
        if pairs:
            return pairs

    # simple comma-separated list
    if "," in raw:
        items = [s.strip() for s in raw.split(",") if s.strip()]
        if items:
            return items

    # plain string
    return raw


class ProductTechSpecJSONForm(forms.ModelForm):
    """
    Inline ModelForm that exposes JSON as (spec_name, spec_value).
    NOTE: spec_name is not required at field level so that existing rows
    validate without typing anything; we enforce required for *new* rows in clean().
    """

    spec_name = forms.CharField(label="Name", required=False)
    spec_value = forms.CharField(label="Value", required=False)

    class Meta:
        model = ProductTechSpec
        fields = []  # manage tech_spec ourselves

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill from instance.tech_spec for existing rows
        if getattr(self.instance, "pk", None) and isinstance(
            self.instance.tech_spec, dict
        ):
            name = self.instance.tech_spec.get("name", "")
            value = self.instance.tech_spec.get("value", "")
            self.fields["spec_name"].initial = name
            self.fields["spec_value"].initial = _stringify_value(value)

    def has_changed(self):
        """
        Because Meta.fields is empty, default has_changed() would be False for extra rows.
        We consider our custom fields.
        """
        if super().has_changed():
            return True
        name = (self.data.get(f"{self.prefix}-spec_name") or "").strip()
        value = (self.data.get(f"{self.prefix}-spec_value") or "").strip()
        return bool(name or value)

    def clean(self):
        cleaned = super().clean()

        # Existing instance posted with no change — keep original tech_spec as-is
        init_name = self.fields["spec_name"].initial or ""
        init_value = self.fields["spec_value"].initial or ""

        name = (cleaned.get("spec_name") or "").strip()
        raw_value = (cleaned.get("spec_value") or "").strip()

        if self.instance.pk and not name and not raw_value:
            # Keep prior values
            prior = self.instance.tech_spec or {}
            self.instance.tech_spec = {
                "name": prior.get("name", ""),
                "value": prior.get("value", ""),
            }
            return cleaned

        # For *new* rows, name is required
        if not self.instance.pk and not name:
            self.add_error("spec_name", "This field is required.")

        # Parse and store JSON on instance
        self.instance.tech_spec = {"name": name, "value": _parse_value(raw_value)}
        return cleaned
