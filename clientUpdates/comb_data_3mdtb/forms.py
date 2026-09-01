
from django import forms

from .models import UpdatePfasResult


class PFASUpdateForm(forms.ModelForm):
    supporting_file = forms.FileField(required=True, label="Supporting Document")

    class Meta:
        model = UpdatePfasResult

        fields = [
            "analyte",
            "result",
            "unit",
            "lab",
            "lab_sample_id",
            "sample_collected_by",
            "analysis_method",
            "sampling_date",
            "analysis_date"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True

    def clean_result(self):
        result = self.cleaned_data.get("result")

        if result is not None and result < 0:
            raise forms.ValidationError(
                "Result cannot be negative."
            )

        return result

    def clean(self):
        cleaned_data = super().clean()

        sampling_date = cleaned_data.get("sampling_date")
        analysis_date = cleaned_data.get("analysis_date")

        # Analysis date cannot occur before the sampling date.
        if sampling_date and analysis_date:
            if analysis_date < sampling_date:
                self.add_error(
                    "analysis_date",
                    "Analysis date cannot be before sampling date."
                )

        return cleaned_data

