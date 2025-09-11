from django import forms

from .models import ProductTechSpec


def _format_value_for_input(value):
    """
    Convert stored JSON value into a friendly string for the admin input:
    - [{"name": "Alpha", "value": "12%"}, ...] -> "Alpha: 12%, Beta: 4.5%"
    - ["Red", "Blue"] -> "Red, Blue"
    - "USA" -> "USA"
    """
    if isinstance(value, list):
        if value and all(
            isinstance(it, dict) and "name" in it and "value" in it for it in value
        ):
            return ", ".join(f"{it['name']}: {it['value']}" for it in value)
        return ", ".join(str(it) for it in value)
    return "" if value is None else str(value)


def _parse_value_from_input(raw):
    """
    Parse the admin text input into one of:
    - list[{"name","value"}] if there are "name: value" pairs,
    - list[str] if there are commas but no colon pairs,
    - str otherwise (single plain value).
    """
    if not raw:
        return ""

    raw = raw.strip()
    if ":" in raw:
        pairs = []
        for chunk in raw.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if ":" in chunk:
                k, v = chunk.split(":", 1)
                pairs.append({"name": k.strip(), "value": v.strip()})
        if pairs:
            return pairs
        # fallback to raw if we didn't parse anything sensible
        return raw

    if "," in raw:
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if parts:
            return parts

    return raw


class ProductTechSpecJSONForm(forms.ModelForm):
    """
    Inline form that exposes ProductTechSpec.tech_spec as two friendly fields:
    - spec_name (required)
    - spec_value (optional), supports:
        * plain string
        * comma-separated list => ["a","b"]
        * "k:v, k:v" => [{"name":k,"value":v}, ...]
    """

    spec_name = forms.CharField(label="Name", required=True)
    spec_value = forms.CharField(label="Value", required=False)

    class Meta:
        model = ProductTechSpec
        fields = []  # We handle serialization into tech_spec ourselves.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate initial values from instance.tech_spec for display
        ts = getattr(self.instance, "tech_spec", None) or {}
        name = ts.get("name", "")
        value = ts.get("value", "")

        self.fields["spec_name"].initial = name
        self.fields["spec_value"].initial = _format_value_for_input(value)

    def has_changed(self):
        """
        Default has_changed() would be False because Meta.fields is empty.
        We must consider our custom fields so extra inline rows are saved.
        """
        if super().has_changed():
            return True

        # When bound, Django prefixes fields with something like "tech_specs-0-..."
        name = (
            (self.data.get(f"{self.prefix}-spec_name") or "").strip()
            if self.is_bound
            else ""
        )
        value = (
            (self.data.get(f"{self.prefix}-spec_value") or "").strip()
            if self.is_bound
            else ""
        )

        # Also consider initial (for existing objects)
        initial_name = (self.fields["spec_name"].initial or "").strip()
        initial_value = (self.fields["spec_value"].initial or "").strip()

        return (name != initial_name) or (value != initial_value)

    def clean(self):
        cleaned = super().clean()
        name = (cleaned.get("spec_name") or "").strip()
        raw_value = (cleaned.get("spec_value") or "").strip()

        if not name:
            self.add_error("spec_name", "This field is required.")

        parsed_value = _parse_value_from_input(raw_value)
        # Stash into instance; InlineFormSet will call form.save()
        self.instance.tech_spec = {"name": name, "value": parsed_value}
        return cleaned

    def save(self, commit=True):
        # Rely on default inline save_new/save_existing flow
        instance = super().save(commit=False)
        # tech_spec already set in clean()
        if commit:
            instance.save()
        return instance
