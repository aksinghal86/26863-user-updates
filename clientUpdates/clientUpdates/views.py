from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
from .models import Pws, PfasResult, FlowRate, ClaimPws, ClaimSource, ClaimFlowRate, ClaimPfasResult
from .forms import MaxFlowRateUpdateForm, AnnualProductionForm, PfasResultUpdateForm, ContactForm
import logging
# These are the custom functions in utils.py 
from .utils import *


logger = logging.getLogger('clientUpdates')
class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('dashboard')

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else: 
        return redirect('login')

@login_required
def dashboard(request):
    # Retrieve the PWS associated with the logged-in user; otherwise, throw an error.
    pws_record = Pws.objects.get(form_userid=request.user.username)
    if not pws_record: 
        return redirect('some-error-page') 
    
    # Pull all the sources filed in the claims portal
    sources = ClaimSource.objects.filter(pwsid=pws_record.pwsid)

    # TODO:  @Elizabeth Hora, please add a column "all_nds" to the claim_source table. 

    context = {
        'pws': pws_record,
        'sources': sources,
    }

    return render(request, 'dashboard.html', context)


# The logic: 
    ## 1. Get relevant rows from the Claims table and any rows from the EHE table that have been updated by the user. See point 4 below. 
    ## 2. Combine the two tables, sort in decreasing order by result per analyte per source and keep only the max result per analyte per source. 
    ## 3a. For PFAS results show PFOA, PFOS, and max other analyte. 
    ## 3b. Max Flow Rate
    ## 3c. Annual Production
    ## 4. If the user updates any value, this is pushed to EHE tables where the updated_by_water_provider column is updated to True. 
    ## 5. Repeat the process from 1 to 4. 
# Note: steps 1 to 3 are processed in source_detail_view. The updates are processed in the relevant update functions below. 



@login_required
def source_detail_view(request, pwsid, source_name):
    source = get_object_or_404(ClaimSource, pwsid=pwsid, source_name=source_name)

    #### PFAS Results ####
    columns = ['pwsid', 'water_source_id', 'source_name', 'analyte', 'result_ppt', 'sampling_date', 'analysis_date', 'lab_sample_id', 'data_origin']
    claim_pfas_results = ClaimPfasResult.objects.filter(pwsid=source.pwsid, source_name=source_name).exclude(analyte__isnull=True)
    updated_pfas_results = PfasResult.objects.filter(pwsid=source.pwsid, source_name=source_name, updated_by_water_provider=True)
    combined_pfas_results = get_combined_results(claim_pfas_results, updated_pfas_results, columns)
    max_pfas_results = get_max_results_by_analyte(combined_pfas_results)
    pfas_results = add_pfoas_if_missing(max_pfas_results, source.pwsid, source.water_source_id, source.source_name)
    max_other_threshold = get_max_other_threshold(pfas_results)
    
    impacted = True if not source.all_nds or updated_pfas_results else False

    #### Max Flow Rate ####
    columns_flow = ['pwsid', 'water_source_id', 'source_name', 'source_variable', 'year', 'flow_rate', 'unit', 'flow_rate_gpm', 'data_origin']
    claim_max_flow_rate = ClaimFlowRate.objects.filter(pwsid=source.pwsid, source_name=source_name, source_variable='VFR')
    updated_max_flow_rate = FlowRate.objects.filter(pwsid=source.pwsid, source_name=source_name, source_variable='VFR', updated_by_water_provider=True)
    combined_max_flow_rate = get_combined_results(claim_max_flow_rate, updated_max_flow_rate, columns_flow)
    max_flow_rate = get_max_entry(combined_max_flow_rate, 'flow_rate_gpm')

    #### Annual Production ####
    claim_annuals = ClaimFlowRate.objects.filter(pwsid=source.pwsid, source_name=source_name, source_variable='AFR')
    updated_annuals = FlowRate.objects.filter(pwsid=source.pwsid, source_name=source_name, source_variable='AFR', updated_by_water_provider=True)
    combined_annuals = get_combined_results(claim_annuals, updated_annuals, columns_flow)
    filtered_annuals = get_filtered_annuals(combined_annuals, source.all_nds)
    annuals = get_max_annuals_by_year(filtered_annuals)

    # Prepare context for rendering
    context = {
        'source': source,
        'impacted': impacted,
        'max_flow_rate': max_flow_rate,
        'annuals': annuals,
        'pfas_results': pfas_results,
        'max_other_threshold': max_other_threshold
    }

    return render(request, 'source_detail.html', context)

@login_required
def update_pfas_result_view(request):
    def calc_pfas_fields(instance, cleaned_data):
        instance.result = float(cleaned_data['result'])
        instance.unit = cleaned_data['unit']
        instance.result_ppt = calc_ppt_result(instance.result, instance.unit)

    return handle_update(
        request,
        form_class=PfasResultUpdateForm,
        extra_fields={
            'analyte': 'analyte',
            'sampling_date': 'sampling_date',
            'analysis_date': 'analysis_date',
            'lab': 'lab',
            'analysis_method': 'analysis_method',
            'lab_sample_id': 'lab_sample_id', 
            'comments': 'comments'
        },
        calc_func=calc_pfas_fields,
        source_variable=None
    )

@login_required
def update_max_flow_rate_view(request):
    def calc_max_flow_rate_fields(instance, cleaned_data):
        instance.flow_rate = cleaned_data['flow_rate']
        instance.unit = cleaned_data['unit']
        instance.flow_rate_gpm = calc_gpm_flow_rate(instance.flow_rate, instance.unit)

    return handle_update(
        request,
        form_class=MaxFlowRateUpdateForm,
        extra_fields={
            'comments': 'comments'
        },
        calc_func=calc_max_flow_rate_fields,
        source_variable='VFR'
    )

@login_required
def update_annual_production_view(request):
    def calc_annual_production_fields(instance, cleaned_data):
        instance.flow_rate = cleaned_data['flow_rate']
        instance.unit = cleaned_data['unit']
        instance.flow_rate_gpm = calc_gpm_flow_rate(instance.flow_rate, instance.unit)
        instance.year = cleaned_data['year']

    return handle_update(
        request,
        form_class=AnnualProductionForm,
        extra_fields={
            'comments': 'comments'
        },
        calc_func=calc_annual_production_fields,
        source_variable='AFR'
    )

@login_required
def contact_view(request):
    pwsid = request.user.username
    recipients = settings.EMAIL_RECIPIENTS
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            full_message = f"From: {name}\n\n{message}"

            email_message = EmailMessage(
                subject=f"{subject} (from {pwsid})",
                body=full_message,
                from_email=settings.EMAIL_HOST_USER,  
                to=recipients,
                reply_to=[email], 
            )
            email_message.send(fail_silently=False)

            # Return a JSON response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Email sent successfully.'})

            return render(request, 'dashboard.html')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Invalid form submission'}, status=400)
        
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})