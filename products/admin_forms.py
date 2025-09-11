from django import forms
from .models import ProductTechSpec


class ProductTechSpecJSONForm(forms.ModelForm):
    spec_name = forms.CharField(label="Name")
    spec_value = forms.CharField(label="Value", required=False)

    class Meta:
        model = ProductTechSpec
        fields = ("spec_name", "spec_value")

    def clean_spec_name(self):
        name = self.cleaned_data["spec_name"].strip()
        if not name:
            raise forms.ValidationError("This field is required.")
        return name

    def clean_spec_value(self):
        raw = (self.cleaned_data.get("spec_value") or "").strip()
        if not raw:
            return ""  # allow blank

        parts = [p.strip() for p in raw.split(",") if p.strip()]
        if any(":" in p for p in parts):
            pairs = []
            for p in parts:
                if ":" in p:
                    k, v = p.split(":", 1)
                    pairs.append({"name": k.strip(), "value": v.strip()})
                else:
                    pairs.append({"name": p.strip(), "value": ""})
            return pairs

        if "," in raw:
            return [x.strip() for x in raw.split(",") if x.strip()]

        return raw

    def save(self, commit=True):
        inst = super().save(commit=False)
        inst.tech_spec = {
            "name": self.cleaned_data["spec_name"],
            "value": self.cleaned_data["spec_value"],
        }
        if commit:
            inst.save()
        return inst
