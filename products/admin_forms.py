from django import forms
from django.forms.models import BaseInlineFormSet

from .models import ProductTechSpec


def _parse_value(v):
    """
    Accepts:
      - "Alpha: 12%, Beta: 4.5%" -> [{"name": "Alpha","value":"12%"}, {"name":"Beta","value":"4.5%"}]
      - "Red, Blue"               -> ["Red", "Blue"]
      - "USA"                     -> "USA"
    """
    if not isinstance(v, str):
        return v

    raw = v.strip()
    if not raw:
        return ""

    # name:value pairs => list of {"name": k, "value": v}
    if ":" in raw:
        pairs = []
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                k, _, val = part.partition(":")
                pairs.append({"name": k.strip(), "value": val.strip()})
            else:
                # tolerate stray tokens without a colon
                pairs.append({"name": part, "value": ""})
        if pairs:
            return pairs

    # comma-separated list => ["A", "B", ...]
    if "," in raw:
        items = [s.strip() for s in raw.split(",") if s.strip()]
        if items:
            return items

    # plain string
    return raw


class ProductTechSpecJSONForm(forms.ModelForm):
    spec_name = forms.CharField(label="Name", required=True)
    spec_value = forms.CharField(label="Value", required=False)

    class Meta:
        model = ProductTechSpec
        fields = []  # we manage JSON ourselves

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate fields when editing an existing row
        if (
            self.instance
            and self.instance.pk
            and isinstance(self.instance.tech_spec, dict)
        ):
            self.fields["spec_name"].initial = self.instance.tech_spec.get("name", "")
            val = self.instance.tech_spec.get("value", "")
            # Render lists nicely
            if isinstance(val, list):
                if (
                    val
                    and isinstance(val[0], dict)
                    and "name" in val[0]
                    and "value" in val[0]
                ):
                    # [{"name":"A","value":"1"}, ...] -> "A: 1, B: 2"
                    val = ", ".join(
                        f'{d.get("name","")}: {d.get("value","")}' for d in val
                    )
                else:
                    # ["Red","Blue"] -> "Red, Blue"
                    val = ", ".join(str(x) for x in val)
            self.fields["spec_value"].initial = val

    def has_changed(self):
        """
        Because Meta.fields is empty, Django would think the form never changes.
        Decide based on our custom inputs.
        """
        if super().has_changed():
            return True
        # For inline forms, prefix looks like "<prefix>-<index>"
        name = (self.data.get(f"{self.prefix}-spec_name") or "").strip()
        value = (self.data.get(f"{self.prefix}-spec_value") or "").strip()
        return bool(name or value)

    def clean(self):
        cleaned = super().clean()
        name = (cleaned.get("spec_name") or "").strip()
        raw = (cleaned.get("spec_value") or "").strip()

        if not name:
            self.add_error("spec_name", "This field is required.")

        parsed = _parse_value(raw) if raw else ""
        # Stash on instance; the formset will save it
        self.instance.tech_spec = {"name": name, "value": parsed}
        return cleaned

    def save(self, commit=True):
        """
        Let the inline formset control the FK binding and saving order.
        Still return an instance with tech_spec already populated.
        """
        inst = super().save(commit=False)
        # self.instance.tech_spec has been set in clean()
        if commit:
            inst.save()
        return inst


class ProductTechSpecInlineFormSet(BaseInlineFormSet):
    """
    Inline formset that saves ProductTechSpec from custom non-model fields:
    `spec_name` and `spec_value`, and provides admin-friendly bookkeeping.
    """

    def save(self, commit=True):
        self.new_objects = []
        self.changed_objects = []
        self.deleted_objects = []

        parent = self.instance  # Product

        # Handle deletions first (mirrors Django's typical pattern)
        for form in self.forms:
            if not form.is_valid():
                continue
            if form.cleaned_data.get("DELETE"):
                obj = form.cleaned_data.get("id")
                if obj and obj.pk:
                    if commit:
                        obj.delete()
                    self.deleted_objects.append(obj)

        # Create / update
        for form in self.forms:
            if not form.is_valid() or form.cleaned_data.get("DELETE"):
                continue

            if not form.has_changed():
                continue  # skip untouched extra rows

            name = (form.cleaned_data.get("spec_name") or "").strip()
            raw_value = (form.cleaned_data.get("spec_value") or "").strip()

            # Skip truly empty
            if not name and not raw_value:
                continue

            parsed_value = _parse_value(raw_value)

            obj = form.cleaned_data.get("id")
            if obj and getattr(obj, "pk", None):
                # update existing
                obj.product = parent
                obj.tech_spec = {"name": name, "value": parsed_value}
                if commit:
                    obj.save()
                # Provide a minimal change dict for admin messages
                self.changed_objects.append((obj, {"tech_spec": ("(old)", "(new)")}))
            else:
                # create new
                obj = ProductTechSpec(
                    product=parent,
                    tech_spec={"name": name, "value": parsed_value},
                )
                if commit:
                    obj.save()
                self.new_objects.append(obj)

        # Return the list of all affected instances as Django does
        return self.new_objects + [obj for (obj, _changes) in self.changed_objects]
