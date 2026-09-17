
from django import forms
from django.utils import timezone

from .models import UpdatePfasResult, UpdateAnnualFlowRate, UpdateMaxFlowRate, AddNewSource


class AddNewSourceForm(forms.ModelForm):
    pfas_file_1 = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "pfas-form-control", "style": "padding: 10px;"}))
    pfas_file_2 = forms.FileField(required=False, widget=forms.FileInput(attrs={"class": "pfas-form-control", "style": "padding: 10px;"}))

    class Meta:
        model = AddNewSource
        fields = [
            "source_name",
            "source_type",
            "source_other",
            "pfas_tested",
            "pfas_detected",
            "pws_own_source",
            "pws_operate_source",
            "co_owners",
            "pws_own_source_explanation",
            "co_owners_explanation",
            "pws_operate_source_explanation",
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
            "source_other": forms.TextInput(attrs={"class": "pfas-form-control", "placeholder": "Please specify other source type"}),
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
            "pws_own_source_explanation": forms.Textarea(attrs={"class": "pfas-form-control", "placeholder": "Please provide explanation for not owning the source", "rows": 2}),
            "co_owners_explanation": forms.Textarea(attrs={"class": "pfas-form-control", "placeholder": "Please provide explanation for co-owners", "rows": 2}),
            "pws_operate_source_explanation": forms.Textarea(attrs={"class": "pfas-form-control", "placeholder": "Who operates this source? (PWSID and PWS Name)", "rows": 2}),
            "comments": forms.Textarea(attrs={"class": "pfas-form-control", "placeholder": "Enter any additional comments here", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ["comments", "pfas_file_1", "pfas_file_2", "source_other", "pws_own_source_explanation", "co_owners_explanation", "pws_operate_source_explanation"]:
                field.required = True
            else:
                field.required = False

    def clean(self):
        cleaned_data = super().clean()
        source_type = cleaned_data.get("source_type")
        source_other = cleaned_data.get("source_other")
        pfas_tested = cleaned_data.get("pfas_tested")
        pfas_detected = cleaned_data.get("pfas_detected")
        pfas_file_1 = cleaned_data.get("pfas_file_1")
        pfas_file_2 = cleaned_data.get("pfas_file_2")
        pws_own_source = cleaned_data.get("pws_own_source")
        pws_own_source_explanation = cleaned_data.get("pws_own_source_explanation")
        pws_operate_source = cleaned_data.get("pws_operate_source")
        pws_operate_source_explanation = cleaned_data.get("pws_operate_source_explanation")
        co_owners = cleaned_data.get("co_owners")
        co_owners_explanation = cleaned_data.get("co_owners_explanation")

        if source_type == "Other" and not source_other:
            self.add_error("source_other", "Please provide explanation for Other source type.")

        if pws_own_source == "No" and not pws_own_source_explanation:
            self.add_error("pws_own_source_explanation", "Please provide explanation for not owning the source.")

        if pws_operate_source == "No" and not pws_operate_source_explanation:
            self.add_error("pws_operate_source_explanation", "Who operates this source? (PWSID and PWS Name)")

        if co_owners == "Yes" and not co_owners_explanation:
            self.add_error("co_owners_explanation", "Please provide explanation for co-owners.")

        if pfas_tested == "No" and pfas_detected == "Yes":
            self.add_error("pfas_detected", "PFAS cannot be detected if it was not tested.")

        if pfas_tested == "Yes" and not pfas_file_1 and not pfas_file_2:
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

        lab = cleaned_data.get("lab")
        lab_other = self.data.get("lab_other")
        analysis_method = cleaned_data.get("analysis_method")
        analysis_method_other = self.data.get("analysis_method_other")

        if lab == "Other":
            if not lab_other:
                self.add_error("lab", "Please provide the laboratory name.")
            else:
                cleaned_data["lab"] = lab_other

        if analysis_method == "Other":
            if not analysis_method_other:
                self.add_error("analysis_method", "Please provide the analysis method.")
            else:
                cleaned_data["analysis_method"] = analysis_method_other

        sampling_date = cleaned_data.get("sampling_date")
        analysis_date = cleaned_data.get("analysis_date")

        today = timezone.localdate()

        if sampling_date and sampling_date > today:
            self.add_error("sampling_date", "Sampling date cannot be in the future.")

        if analysis_date and analysis_date > today:
            self.add_error("analysis_date", "Analysis date cannot be in the future.")

        # Analysis date cannot occur before the sampling date.
        if sampling_date and analysis_date:
            if analysis_date < sampling_date:
                self.add_error(
                    "analysis_date",
                    "Analysis date cannot be before sampling date."
                )

        return cleaned_data


class HazardIndexUpdateForm(forms.Form):
    pfhxs_result = forms.FloatField(required=True, label="PFHxS Result (ng/L)", min_value=0)
    hfpo_da_result = forms.FloatField(required=True, label="HFPO-DA (GenX) Result (ng/L)", min_value=0)
    pfna_result = forms.FloatField(required=True, label="PFNA Result (ng/L)", min_value=0)
    pfbs_result = forms.FloatField(required=True, label="PFBS Result (ng/L)", min_value=0)

    lab = forms.ChoiceField(
        choices=[
            ('', 'Select laboratory'),
            ('Eurofins', 'Eurofins'),
            ('Pace Analytical', 'Pace Analytical'),
            ('ALS', 'ALS'),
            ('SGS', 'SGS'),
            ('TestAmerica', 'TestAmerica'),
            ('Other', 'Other')
        ],
        required=True
    )
    lab_sample_id = forms.CharField(required=True, label="Lab Sample ID")
    analysis_method = forms.ChoiceField(
        choices=[
            ('', 'Select analysis method'),
            ('EPA 537.1', 'EPA 537.1'),
            ('EPA 533', 'EPA 533'),
            ('EPA 1633', 'EPA 1633'),
            ('Other', 'Other')
        ],
        required=True
    )
    sampling_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    analysis_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    supporting_file = forms.FileField(required=True, label="Supporting Document")

    def __init__(self, *args, **kwargs):
        self.min_hi = kwargs.pop("min_hi", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        lab = cleaned_data.get("lab")
        lab_other = self.data.get("lab_other")
        analysis_method = cleaned_data.get("analysis_method")
        analysis_method_other = self.data.get("analysis_method_other")

        if lab == "Other":
            if not lab_other:
                self.add_error("lab", "Please provide the laboratory name.")
            else:
                cleaned_data["lab"] = lab_other

        if analysis_method == "Other":
            if not analysis_method_other:
                self.add_error("analysis_method", "Please provide the analysis method.")
            else:
                cleaned_data["analysis_method"] = analysis_method_other

        sampling_date = cleaned_data.get("sampling_date")
        analysis_date = cleaned_data.get("analysis_date")

        today = timezone.localdate()

        if sampling_date and sampling_date > today:
            self.add_error("sampling_date", "Sampling date cannot be in the future.")

        if analysis_date and analysis_date > today:
            self.add_error("analysis_date", "Analysis date cannot be in the future.")

        if sampling_date and analysis_date and analysis_date < sampling_date:
            self.add_error("analysis_date", "Analysis date cannot be before sampling date.")

        # Calculate HI for validation if all results are present
        pfhxs = cleaned_data.get("pfhxs_result")
        hfpo_da = cleaned_data.get("hfpo_da_result")
        pfna = cleaned_data.get("pfna_result")
        pfbs = cleaned_data.get("pfbs_result")

        if all(x is not None for x in [pfhxs, hfpo_da, pfna, pfbs]):
            hi = round((pfhxs / 9.0) + (hfpo_da / 10.0) + (pfna / 10.0) + (pfbs / 2000.0), 2)
            if self.min_hi is not None:
                min_hi_val = round(float(self.min_hi), 2)
                if hi <= min_hi_val:
                    raise forms.ValidationError(
                        f"New Hazard Index ({hi:.2f}) must be greater than the current maximum value of {min_hi_val:.2f}."
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

