
from django import forms

from .models import UpdatePfasResult, UpdateAnnualFlowRate, UpdateMaxFlowRate, AddNewSource


class AddNewSourceForm(forms.ModelForm):
    pfas_file_1 = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "pfas-form-control", "style": "padding: 10px;"}))
    pfas_file_2 = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "pfas-form-control", "style": "padding: 10px;"}))

    class Meta:
        model = AddNewSource
        fields = [
            "source_name",
            "source_type",
            "pfas_tested",
            "pfas_detected",
            "pws_own_source",
            "pws_operate_source",
            "co_owners",
            "drinking_water",
            "idws",
            "comments",
        ]
        widgets = {
            "source_name": forms.TextInput(attrs={"class": "pfas-form-control", "placeholder": "Enter source name"}),
            "source_type": forms.Select(attrs={"class": "pfas-form-control"}, choices=[
                ("", "Select source type"),
                ("Groundwater Well", "Groundwater Well"),
                ("Surface Water", "Surface Water"),
                ("Interconnection", "Interconnection"),
                ("Other", "Other"),
            ]),
            "pfas_tested": forms.Select(attrs={"class": "pfas-form-control"}, choices=[
                ("", ""),
                ("No", "No"),
                ("Yes", "Yes"),
            ]),
            "pfas_detected": forms.Select(attrs={"class": "pfas-form-control"}, choices=[
                ("", ""),
                ("No", "No"),
                ("Yes", "Yes"),
            ]),
            "pws_own_source": forms.Select(attrs={"class": "pfas-form-control"}, choices=[
                ("", ""),
                ("Yes", "Yes"),
                ("No", "No"),
            ]),
            "pws_operate_source": forms.Select(attrs={"class": "pfas-form-control"}, choices=[
                ("", ""),
                ("Yes", "Yes"),
                ("No", "No"),
            ]),
            "co_owners": forms.Select(attrs={"class": "pfas-form-control"}, choices=[
                ("", ""),
                ("No", "No"),
                ("Yes", "Yes"),
            ]),
            "drinking_water": forms.Select(attrs={"class": "pfas-form-control"}, choices=[
                ("", ""),
                ("Yes", "Yes"),
                ("No", "No"),
            ]),
            "idws": forms.Select(attrs={"class": "pfas-form-control"}, choices=[
                ("", ""),
                ("No", "No"),
                ("Yes", "Yes"),
            ]),
            "comments": forms.Textarea(attrs={"class": "pfas-form-control", "placeholder": "Enter any additional comments here", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ["comments", "pfas_file_1", "pfas_file_2"]:
                field.required = True
            else:
                field.required = False

    def clean(self):
        cleaned_data = super().clean()
        pfas_tested = cleaned_data.get("pfas_tested")
        pfas_detected = cleaned_data.get("pfas_detected")
        pfas_file_1 = cleaned_data.get("pfas_file_1")
        pfas_file_2 = cleaned_data.get("pfas_file_2")

        if pfas_tested == "No" and pfas_detected == "Yes":
            self.add_error("pfas_detected", "PFAS cannot be detected if it was not tested.")

        if not pfas_file_1 and not pfas_file_2:
            self.add_error("pfas_file_1", "At least one PFAS data file must be uploaded.")

        return cleaned_data


class PFASUpdateForm(forms.ModelForm):
    supporting_file = forms.FileField(
        required=True,
        label="Supporting Document",
        error_messages={'required': 'A file must be uploaded'}
    )

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
            if result_ppt <= float(self.min_result):
                raise forms.ValidationError(
                    f"New result must be greater than the current value of {self.min_result} ng/L."
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
    supporting_file = forms.FileField(
        required=True,
        label="Supporting Document",
        error_messages={'required': 'A file must be uploaded'}
    )

    class Meta:
        model = UpdateAnnualFlowRate
        fields = [
            "flow_rate",
            "unit",
            "flow_rate_reduced",
            "existed",
        ]
        widgets = {
            "flow_rate_reduced": forms.Select(choices=[('', 'Select one'), ('No', 'No'), ('Yes', 'Yes')]),
            "existed": forms.Select(choices=[('', 'Select one'), ('No', 'No'), ('Yes', 'Yes')]),
        }

    def __init__(self, *args, **kwargs):
        self.existing_flow_gpm = kwargs.pop("existing_flow_gpm", None)
        super().__init__(*args, **kwargs)
        
        # Default to None so "Select one" is shown instead of model defaults
        if not self.instance.pk:
            self.initial['flow_rate_reduced'] = None
            self.initial['existed'] = None

        for field_name, field in self.fields.items():
            field.required = True

    def clean_flow_rate(self):
        flow_rate = self.cleaned_data.get("flow_rate")
        unit = self.cleaned_data.get("unit")
        
        if flow_rate is not None and flow_rate < 0:
            raise forms.ValidationError("Flow rate cannot be negative.")
        
        if flow_rate is not None and unit and self.existing_flow_gpm is not None:
            from clientUpdates.utils.calculations import calc_gpm_flow_rate
            new_flow_gpm = calc_gpm_flow_rate(flow_rate, unit.lower())
            
            if new_flow_gpm <= float(self.existing_flow_gpm):
                raise forms.ValidationError(
                    f"New flow rate must be greater than the current value of {self.existing_flow_gpm:.1f} GPM."
                )
                
        return flow_rate


class MFUpdateForm(forms.ModelForm):
    supporting_file = forms.FileField(
        required=True,
        label="Supporting Document",
        error_messages={'required': 'A file must be uploaded'}
    )

    class Meta:
        model = UpdateMaxFlowRate
        fields = [
            "flow_rate",
            "unit",
            "method_determined",
        ]

    def __init__(self, *args, **kwargs):
        self.existing_max_flow_gpm = kwargs.pop("existing_max_flow_gpm", None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True

    def clean_flow_rate(self):
        flow_rate = self.cleaned_data.get("flow_rate")
        unit = self.cleaned_data.get("unit")
        
        if flow_rate is not None and flow_rate < 0:
            raise forms.ValidationError("Flow rate cannot be negative.")

        if flow_rate is not None and unit and self.existing_max_flow_gpm is not None:
            from clientUpdates.utils.calculations import calc_gpm_flow_rate
            new_flow_gpm = calc_gpm_flow_rate(flow_rate, unit.lower())
            
            if new_flow_gpm <= float(self.existing_max_flow_gpm):
                raise forms.ValidationError(
                    f"New flow rate must be greater than the current value of {self.existing_max_flow_gpm:.1f} GPM."
                )
                
        return flow_rate

