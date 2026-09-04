
from django import forms

from .models import UpdatePfasResult, UpdateFlowRate, UpdateMaxFlowRate


class PFASUpdateForm(forms.ModelForm):
    supporting_file = forms.FileField(required=True, label="Supporting Document")

    class Meta:
        model = UpdatePfasResult

        fields = [
            "analyte",
            "result_ppt",
            "lab",
            "lab_sample_id",
            "sample_collected_by",
            "analysis_method",
            "sampling_date",
            "analysis_date"
        ]

    def __init__(self, *args, **kwargs):
        self.min_result = kwargs.pop("min_result", None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True

    def clean_result_ppt(self):
        result_ppt = self.cleaned_data.get("result_ppt")

        if result_ppt is not None and result_ppt < 0:
            raise forms.ValidationError(
                "Result cannot be negative."
            )

        if result_ppt is not None and self.min_result is not None:
            if result_ppt < float(self.min_result):
                raise forms.ValidationError(
                    f"New result cannot be less than the current value of {self.min_result} ng/L."
                )

        return result_ppt

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


class AFUpdateForm(forms.ModelForm):
    supporting_file = forms.FileField(required=True, label="Supporting Document")

    class Meta:
        model = UpdateFlowRate
        fields = [
            "flow_rate",
            "unit",
            "flow_rate_reduced",
            "existed",
        ]
        widgets = {
            "flow_rate_reduced": forms.Select(choices=[(False, 'No'), (True, 'Yes')]),
            "existed": forms.Select(choices=[(False, 'No'), (True, 'Yes')]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ["flow_rate_reduced", "existed"]:
                field.required = False
            else:
                field.required = True

    def clean_flow_rate(self):
        flow_rate = self.cleaned_data.get("flow_rate")
        if flow_rate is not None and flow_rate < 0:
            raise forms.ValidationError("Flow rate cannot be negative.")
        return flow_rate


class MFUpdateForm(forms.ModelForm):
    supporting_file = forms.FileField(required=True, label="Supporting Document")

    class Meta:
        model = UpdateMaxFlowRate
        fields = [
            "flow_rate",
            "unit",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True

    def clean_flow_rate(self):
        flow_rate = self.cleaned_data.get("flow_rate")
        if flow_rate is not None and flow_rate < 0:
            raise forms.ValidationError("Flow rate cannot be negative.")
        return flow_rate

