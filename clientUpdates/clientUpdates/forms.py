from django import forms
from django.utils import timezone
from .models import FlowRate, PfasResult, phase2PwsInfo, phase2SourceInfo, phase2MaxFlow, phase2AnnualFlow, phase2PfasResults


class MaxFlowRateUpdateForm(forms.ModelForm):
    """
    Form for updating Max Flow Rate. 
    """
    class Meta:
        model = FlowRate
        fields = [
            'flow_rate', 
            'unit', 
            'filename',
            'comments'
        ]
        
    def clean_filename(self):
        filename = self.cleaned_data.get('filename')
        if not filename:
            raise forms.ValidationError("A file is required.")
        return filename

class AnnualProductionForm(forms.ModelForm):
    """
    Form for updating Annual production. 
    """
    class Meta:

        model = FlowRate

        fields = [
            'year',
            'flow_rate',
            'unit',
            'flow_rate_reduced',
            'filename',
            'comments'
        ]
        widgets = {
            'flow_rate_reduced': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    
    def clean_flow_rate(self):
        flow_rate = self.cleaned_data.get('flow_rate')
        if flow_rate is None:
            raise forms.ValidationError("Flow Rate is required and must be a valid number.")
        
        return flow_rate
    
    def clean_filename(self):
        filename = self.cleaned_data.get('filename')
        if not filename:
            raise forms.ValidationError("A file is required.")
        return filename

class PfasResultUpdateForm(forms.ModelForm):
    """
    Form for updating PFAS result details.
    Includes all relevant fields for PFAS data entry and editing.
    """
    class Meta:

        model = PfasResult

        fields = [
            'analyte',
            'result',
            'unit',
            'sampling_date',
            'analysis_date',
            'lab',
            'analysis_method',
            'lab_sample_id', 
            'filename',
            'comments'
        ]

        widgets = {
            'sampling_date': forms.DateInput(attrs={'type': 'date'}),
            'analysis_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_result(self):
        result = self.cleaned_data.get('result')
        if result is None:
            raise forms.ValidationError("Result is required and must be a valid number.")
        
        return result

    def clean_lab_sample_id(self):
        lab_sample_id = self.cleaned_data.get('lab_sample_id')
        if not lab_sample_id:
            raise forms.ValidationError("Lab Sample ID is required.")
        return lab_sample_id
    
    def clean_sampling_date(self):
        sampling_date = self.cleaned_data.get('sampling_date')
        if sampling_date and sampling_date > timezone.now().date():
            raise forms.ValidationError("Sampling date cannot be in the future.")
        return sampling_date

    def clean_analysis_date(self):
        analysis_date = self.cleaned_data.get('analysis_date')
        sampling_date = self.cleaned_data.get('sampling_date')

        if analysis_date:
            if sampling_date and analysis_date < sampling_date:
                raise forms.ValidationError("Analysis date cannot be before the sampling date.")
            if analysis_date > timezone.now().date():
                raise forms.ValidationError("Analysis date cannot be in the future.")
        return analysis_date
    
    def clean_filename(self):
        filename = self.cleaned_data.get('filename')
        if not filename:
            raise forms.ValidationError("A file is required.")
        return filename

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, label="Your Email")
    subject = forms.CharField(max_length=150, required=True, label="Subject")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Message")
    file_upload = forms.FileField(required=False)

    # def clean_file_upload(self):
    #     file = self.cleaned_data['file']
    #
    #     if file.size > 5 * 1024 * 1024:
    #         raise forms.ValidationError("File must be under 5MB.")
    #
    #     return file


class pwsInfoForm(forms.ModelForm):
    class Meta:

        model = phase2PwsInfo

        fields = [
            'pwsid',
            'pws_name',
            'ein',
            'facility_address',
            'facility_city',
            'facility_state',
            'facility_zip',
            'mailing_address',
            'mailing_city',
            'mailing_state',
            'mailing_zip',
            'primary_contact_name',
            'primary_contact_title',
            'primary_contact_telephone',
            'primary_contact_cell_phone',
            'primary_contact_email',
            'secondary_contact_name',
            'secondary_contact_title',
            'secondary_contact_telephone',
            'secondary_contact_cell_phone',
            'secondary_contact_email',
            'tertiary_contact_name',
            'tertiary_contact_title',
            'tertiary_contact_telephone',
            'tertiary_contact_cell_phone',
            'tertiary_contact_email',
            'ucmr5_required',
            'pfas_required_state',
            'connections_15',
            'residents_25',
            'pop_fewer_3300_062223',
            'pop_fewer_3300_063023',
            'pop_fewer_3300_051524',
            'pws_in_usa',
            'pws_owned_state_fed',
            'sdwis_owner_code',
            'sdwis_facility_code',
            'sdwis_activity_code',
            'pfas_detected_06222023',
            'pfas_detected_06302023',
            'pfas_detected_05152024',
            'comments'
        ]

class phase2SourceInfoForm(forms.ModelForm):
    class Meta:

        model = phase2SourceInfo

        exclude = [
            'id',
            'pwsid',
            'pws_name'
        ]

class phase2MaxFlowForm(forms.ModelForm):

    class Meta:
        model = phase2MaxFlow

        exclude = [
            'id',
            'pwsid',
            'pws_name'
        ]


class phase2AnnualFlowForm(forms.ModelForm):
    class Meta:
        model = phase2AnnualFlow

        fields = [
            'year',
            'source_name',
            'flow_rate',
            'units',
            'flow_rate_reduced',
            'did_not_exist',
            'file_name'
        ]

class phase2PfasResultsForm(forms.ModelForm):
    class Meta:
        model = phase2PfasResults
        fields = [
            'analyte',
            'result',
            'units',
            'sample_date',
            'file_name'
        ]

class formConstants(forms.Form):
    comments_annual_flow = forms.CharField(widget=forms.Textarea, required=False)
    comments_pfas = forms.CharField(widget=forms.Textarea, required=False)
    source_name = forms.CharField(max_length=150)

class annualFiles(forms.Form):
    annualFile1 = forms.FileField(required=False)
    annualFile2 = forms.FileField(required=False)
    annualFile3 = forms.FileField(required=False)
    annualFile4 = forms.FileField(required=False)
    annualFile5 = forms.FileField(required=False)
    annualFile6 = forms.FileField(required=False)
    annualFile7 = forms.FileField(required=False)
    annualFile8 = forms.FileField(required=False)
    annualFile9 = forms.FileField(required=False)
    annualFile10 = forms.FileField(required=False)
    annualFile11 = forms.FileField(required=False)
    annualFile12 = forms.FileField(required=False)
    annualFile13 = forms.FileField(required=False)

class pfasFiles(forms.Form):
    pfasFile1 = forms.FileField(required=False)
    pfasFile2 = forms.FileField(required=False)
    pfasFile3 = forms.FileField(required=False)
    pfasFile4 = forms.FileField(required=False)
    pfasFile5 = forms.FileField(required=False)
    pfasFile6 = forms.FileField(required=False)
    pfasFile7 = forms.FileField(required=False)

class maxFlowFile(forms.Form):
    maxFlowFile = forms.FileField(required=False)






