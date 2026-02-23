from django import forms
from django.utils import timezone
from .models import FlowRate, PfasResult

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