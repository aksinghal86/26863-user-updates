from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Pws, Source, PfasResult, FlowRate, ClaimPws, ClaimSource, ClaimFlowRate, ClaimPfasResult
from .forms import MaxFlowRateUpdateForm, AnnualProductionForm, PfasResultUpdateForm
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
        'max_flow_rate': max_flow_rate,
        'annuals': annuals,
        'pfas_results': pfas_results,
        'max_other_threshold': max_other_threshold
    }

    return render(request, 'source_detail.html', context)



@login_required
def update_pfas_result_view(request):
    
    if request.method == 'POST':
        pwsid = request.POST.get('pwsid')
        source_name = request.POST.get('source_name')
        form = PfasResultUpdateForm(request.POST, request.FILES)
        
        if form.is_valid():
            logger.debug("Received valid form data: %s", form.cleaned_data)
            
            # Save form instance without committing immediately
            pfas_result = form.save(commit=False)

            pfas_result.pwsid = pwsid
            pfas_result.source_name = source_name
            pfas_result.sample_id = source_name
            pfas_result.submit_date = timezone.now()
            pfas_result.analyte = form.cleaned_data['analyte']
            
            # Calculate result in ppt based on unit and value provided
            pfas_result.result = float(form.cleaned_data['result'])
            pfas_result.unit = form.cleaned_data['unit']
            pfas_result.result_ppt = calc_ppt_result(pfas_result.result, pfas_result.unit)

            pfas_result.sampling_date = form.cleaned_data['sampling_date']
            pfas_result.analysis_date = form.cleaned_data['analysis_date']
            pfas_result.lab = form.cleaned_data['lab']
            pfas_result.analysis_method = form.cleaned_data['analysis_method']
            pfas_result.lab_sample_id = form.cleaned_data['lab_sample_id']
            pfas_result.filename = form.cleaned_data['filename']
            pfas_result.data_origin = "EHE Update Portal"
            pfas_result.updated_by_water_provider = True
            pfas_result.detected = detected(pfas_result.result)
            
            # TODO: Unhash this when ready to make changes to database
            # saves to the database
            pfas_result.save()

            logger.info("Added or updated %s result of %s ppt for %s in the 'pfas-result' table.", 
                        pfas_result.analyte, 
                        pfas_result.result_ppt, 
                        pfas_result.source_name)
            
            messages.success(request, 'PFAS result updated successfully.')

            file = request.FILES.get('filename')
            upload_to_dropbox(file, pwsid)

            return redirect('source-detail', pwsid=pwsid, source_name=source_name)
        else:
            logger.error("Form validation failed with errors: %s", form.errors)
            messages.error(request, "Form validation failed. Please correct the errors below.")
            return redirect('source-detail', pwsid=pwsid, source_name=source_name)

    # Handle GET request to render form with existing data
    form = PfasResultUpdateForm(instance=pfas_result)
    logger.debug("Rendering the form for PFAS result input")
    messages.error(request, "Invalid request.")
    return render(request, 'update_pfas_result_modal.html', {'form': form, 'pfas_result': pfas_result})



@login_required
def update_max_flow_rate_view(request, row_names):
    max_flow_rate = get_object_or_404(ClaimFlowRate, row_names=row_names)
    
    if request.method == 'POST':
        form = MaxFlowRateUpdateForm(request.POST)
        if form.is_valid():
            new_unit = form.cleaned_data['unit']
            new_flow_rate = form.cleaned_data['flow_rate']
            flow_rate_gpm = calc_gpm_flow_rate(new_flow_rate, new_unit)

            # Print/log the updates instead of saving during development phase
            logger.info(f"Updating flow_rate_gpm for row {row_names}:")
            logger.info(f"Old flow rate: {max_flow_rate.flow_rate} {max_flow_rate.unit}, New flow rate: {new_flow_rate} {new_unit}")

            max_flow_rate.flow_rate = new_flow_rate
            max_flow_rate.unit = new_unit
            max_flow_rate.flow_rate_gpm = flow_rate_gpm
            # max_flow_rate.save()
            messages.success(request, f"Max flow rate updated successfully.")
            return redirect('source-detail', pwsid=max_flow_rate.pwsid, source_name=max_flow_rate.source_name)
    else:
        form = MaxFlowRateUpdateForm(instance=max_flow_rate)

    return redirect('source-detail', pwsid=max_flow_rate.pwsid, source_name=max_flow_rate.source_name)




@login_required
def update_annual_production_view(request):
    if request.method == 'POST':
        pwsid = request.POST.get('pwsid')
        source_name = request.POST.get('source_name')
        form = AnnualProductionForm(request.POST)
        
        if form.is_valid():
            logger.debug("Received valid form data: %s", form.cleaned_data)

            # Save form instance without committing immediately
            annual_production = form.save(commit=False)

            annual_production.pwsid = pwsid
            annual_production.source_name = source_name
            annual_production.submit_date = timezone.now()
            annual_production.year = form.cleaned_data['year']

            # Calculate annual production in GPM based on unit and value provided
            annual_production.flow_rate = form.cleaned_data['flow_rate']
            annual_production.unit = form.cleaned_data['unit']
            annual_production.flow_rate_gpm = calc_gpm_flow_rate(annual_production.flow_rate, annual_production.unit)

            annual_production.source_variable = 'AFR'
            annual_production.filename = form.cleaned_data['filename']
            annual_production.data_origin = "EHE Update Portal"
            annual_production.updated_by_water_provider = True

            # TODO: Unhash this when ready to make changes to database
            # annual_production.save()

            logger.info("Added or updated %s annual production of %s GPM for %s in the 'flow-rate' table.", 
                        annual_production.year, 
                        annual_production.flow_rate_gpm, 
                        annual_production.source_name)
            
            messages.success(request, f"Annual production updated successfully.")

            # TODO: needs to be done. 
            # file = request.FILES.get('filename')
            # upload_to_dropbox(file, pwsid) 

            return redirect('source-detail', pwsid=pwsid, source_name=source_name)
        else:
            # Log form errors if form validation fails
            logger.error("Form validation failed with errors: %s", form.errors)
            messages.error(request, "Form validation failed. Please correct the errors below.")
            return redirect('source-detail', pwsid=pwsid, source_name=source_name)

    # Handle GET request to render form with existing data
    form = AnnualProductionForm(instance=annual_production)
    logger.debug(f"Rendering the form for Annual Production input")
    messages.error(request, "Invalid request.")
    return render(request, 'updated_annual_production_modal.html', {'form': form, 'annual_production': annual_production})